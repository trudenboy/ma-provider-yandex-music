"""Streaming operations for Yandex Music."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, ClassVar

import aiohttp
from aiohttp import ClientPayloadError, ServerDisconnectedError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from music_assistant_models.enums import ContentType, StreamType
from music_assistant_models.errors import MediaNotFoundError
from music_assistant_models.media_items import AudioFormat
from music_assistant_models.streamdetails import StreamDetails

from music_assistant.helpers.throttle_retry import BYPASS_THROTTLER

from .constants import (
    CONF_CODECS,
    CONF_QUALITY,
    CONF_TRANSPORT,
    QUALITY_BALANCED,
    QUALITY_EFFICIENT,
    QUALITY_FILE_INFO_PARAMS,
    QUALITY_HIGH,
    QUALITY_SUPERB,
    RADIO_TRACK_ID_SEP,
    TRANSPORT_RAW,
)

if TYPE_CHECKING:
    from yandex_music import DownloadInfo

    from .provider import YandexMusicProvider


# Windowed-stream tuning constants
_CHUNK_SIZE = 16384  # smaller than default 65536 for faster first-byte after retry
_STREAM_TIMEOUT = aiohttp.ClientTimeout(total=None, sock_read=30)
# Yandex CDN drops TCP connections for slow consumers (observed at ~45s for raw transport
# at real-time playback rate ~200 KB/s). By capping each Range request to 4 MB we download
# each window quickly, preventing CDN drops for both raw and encrypted transports.
_RANGE_WINDOW = 4 * 1024 * 1024  # 4 MB per Range request
# Flat short delays for TCP drops (network glitches within a 4 MB window)
_TCP_DROP_DELAYS = (0.5, 1.0, 2.0)
# Exponential delays for true network stalls (read timeout)
_STALL_DELAYS = (2.0, 4.0, 8.0)


class YandexMusicStreamingManager:
    """Manages Yandex Music streaming operations."""

    def __init__(self, provider: YandexMusicProvider) -> None:
        """Initialize streaming manager.

        :param provider: The Yandex Music provider instance.
        """
        self.provider = provider
        self.client = provider.client
        self.mass = provider.mass
        self.logger = provider.logger

    def _track_id_from_item_id(self, item_id: str) -> str:
        """Extract API track ID from item_id (may be track_id@station_id for My Wave)."""
        if RADIO_TRACK_ID_SEP in item_id:
            return item_id.split(RADIO_TRACK_ID_SEP, 1)[0]
        return item_id

    async def get_stream_details(self, item_id: str) -> StreamDetails:
        """Get stream details for a track.

        Uses the unified /get-file-info endpoint for all quality tiers.
        Falls back to /tracks/{id}/download-info if get-file-info fails.

        :param item_id: Track ID or composite track_id@station_id for My Wave.
        :return: StreamDetails for the track (item_id preserved for on_streamed).
        :raises MediaNotFoundError: If stream URL cannot be obtained.
        """
        track_id = self._track_id_from_item_id(item_id)
        track = await self.provider.get_track(item_id)
        if not track:
            raise MediaNotFoundError(f"Track {item_id} not found")

        quality = (
            str(self.provider.config.get_value(CONF_QUALITY) or QUALITY_BALANCED).strip().lower()
        )
        transport = (
            str(self.provider.config.get_value(CONF_TRANSPORT) or TRANSPORT_RAW).strip().lower()
        )

        # Backward compatibility: old "lossless" config value
        if quality == "lossless":
            quality = QUALITY_SUPERB

        fi_params = QUALITY_FILE_INFO_PARAMS.get(
            quality, QUALITY_FILE_INFO_PARAMS[QUALITY_BALANCED]
        )

        # Allow advanced users to override codecs
        codecs_override = str(self.provider.config.get_value(CONF_CODECS) or "").strip()
        codecs = codecs_override or fi_params["codecs"]

        self.logger.debug(
            "Requesting stream for track %s: quality=%s, transport=%s, codecs=%s",
            track_id,
            quality,
            transport,
            codecs,
        )

        file_info = await self.client.get_track_file_info(
            track_id,
            quality=fi_params["quality"],
            codecs=codecs,
            transport=transport,
        )

        if file_info and file_info.get("url"):
            url = file_info["url"]
            codec = file_info.get("codec") or ""
            needs_decryption = file_info.get("needs_decryption", False)
            audio_format = self._build_audio_format(codec)

            # Always use StreamType.CUSTOM with windowed Range requests to prevent CDN drops.
            # can_seek=False: provider always streams from position 0;
            # allow_seek=True: ffmpeg handles seek with -ss input flag.
            data: dict[str, Any] = {
                "url": url,
                "codec": codec,
                "transport": transport,
                # Stored for URL refresh on 4xx:
                "fi_quality": fi_params["quality"],
                "fi_codecs": codecs,
            }
            if needs_decryption and "key" in file_info:
                data["decryption_key"] = file_info["key"]

            return StreamDetails(
                item_id=item_id,
                provider=self.provider.instance_id,
                audio_format=audio_format,
                stream_type=StreamType.CUSTOM,
                duration=track.duration,
                data=data,
                can_seek=False,
                allow_seek=True,
            )

        # Fallback: /tracks/{id}/download-info (defensive, should rarely trigger)
        self.logger.warning(
            "get-file-info failed for track %s, falling back to download-info", track_id
        )
        download_infos = await self.client.get_track_download_info(track_id, get_direct_links=True)
        if not download_infos:
            raise MediaNotFoundError(f"No stream info available for track {item_id}")

        selected_info = self._select_best_quality(download_infos, quality)
        if not selected_info or not selected_info.direct_link:
            raise MediaNotFoundError(f"No stream URL available for track {item_id}")

        self.logger.debug(
            "Fallback stream for track %s: codec=%s, bitrate=%s",
            track_id,
            getattr(selected_info, "codec", None),
            getattr(selected_info, "bitrate_in_kbps", None),
        )

        return StreamDetails(
            item_id=item_id,
            provider=self.provider.instance_id,
            audio_format=self._build_audio_format(
                selected_info.codec, bit_rate=selected_info.bitrate_in_kbps or 0
            ),
            stream_type=StreamType.HTTP,
            duration=track.duration,
            path=selected_info.direct_link,
            can_seek=True,
            allow_seek=True,
            expiration=50,  # download-info direct links expire after ~60s
        )

    def _select_best_quality(
        self, download_infos: list[Any], preferred_quality: str | None
    ) -> DownloadInfo | None:
        """Select the best quality download info based on user preference.

        Used as fallback when get-file-info is unavailable.

        :param download_infos: List of DownloadInfo objects.
        :param preferred_quality: User's quality preference (efficient/high/balanced/superb).
        :return: Best matching DownloadInfo or None.
        """
        if not download_infos:
            return None

        preferred_normalized = (preferred_quality or "").strip().lower()

        # Sort by bitrate descending
        sorted_infos = sorted(
            download_infos,
            key=lambda x: x.bitrate_in_kbps or 0,
            reverse=True,
        )

        # Superb: Prefer FLAC (backward compatibility with "lossless")
        if preferred_normalized == QUALITY_SUPERB or "lossless" in preferred_normalized:
            for codec in ("flac-mp4", "flac"):
                for info in sorted_infos:
                    if info.codec and info.codec.lower() == codec:
                        return info
            self.logger.warning(
                "Superb quality (FLAC) requested but not available; using best available"
            )
            return sorted_infos[0]

        # Efficient: Prefer lowest bitrate AAC/MP3
        if preferred_normalized == QUALITY_EFFICIENT:
            sorted_infos_asc = sorted(
                download_infos,
                key=lambda x: x.bitrate_in_kbps or 999,
            )
            for codec in ("aac-mp4", "aac", "he-aac-mp4", "he-aac", "mp3"):
                for info in sorted_infos_asc:
                    if info.codec and info.codec.lower() == codec:
                        return info
            return sorted_infos_asc[0]

        # High: Prefer high bitrate MP3 (~320kbps)
        if preferred_normalized == QUALITY_HIGH:
            high_quality_mp3 = [
                info
                for info in sorted_infos
                if info.codec
                and info.codec.lower() == "mp3"
                and info.bitrate_in_kbps
                and info.bitrate_in_kbps >= 256
            ]
            if high_quality_mp3:
                return high_quality_mp3[0]

            for info in sorted_infos:
                if info.codec and info.codec.lower() == "mp3":
                    return info

            for info in sorted_infos:
                if info.codec and info.codec.lower() not in ("flac", "flac-mp4"):
                    return info

            return sorted_infos[0]

        # Balanced (default): Prefer ~192kbps AAC
        balanced_infos = [
            info
            for info in sorted_infos
            if info.bitrate_in_kbps and 128 <= info.bitrate_in_kbps <= 256
        ]
        if balanced_infos:
            for codec in ("aac-mp4", "aac", "he-aac-mp4", "he-aac", "mp3"):
                for info in balanced_infos:
                    if info.codec and info.codec.lower() == codec:
                        return info
            return balanced_infos[0]

        return sorted_infos[0] if sorted_infos else None

    # Normalize Yandex codec names to MA ContentType values
    _CODEC_ALIASES: ClassVar[dict[str, str]] = {
        "he-aac": "aac",
        "mpeg": "mp3",
    }

    def _get_content_type(self, codec: str | None) -> tuple[ContentType, ContentType]:
        """Determine content_type and codec_type from Yandex API codec string.

        Parses the codec string automatically:
        - Simple codecs ("flac", "mp3", "aac") → (ContentType.<codec>, UNKNOWN)
        - Compound "codec-container" ("flac-mp4", "aac-mp4") →
          (ContentType.<codec>, ContentType.<codec>)

        content_type always reflects the audio codec (not the container),
        so MA's is_lossless() correctly identifies lossless streams and
        ffmpeg gets the right decoder name via codec_type.

        :param codec: Codec string from Yandex API (e.g. "flac-mp4", "mp3").
        :return: Tuple of (content_type, codec_type).
        """
        if not codec:
            return ContentType.UNKNOWN, ContentType.UNKNOWN

        codec_lower = codec.lower()

        # Strip container suffix: "flac-mp4" → "flac", "he-aac-mp4" → "he-aac"
        has_container = codec_lower.endswith("-mp4")
        audio_part = codec_lower[:-4] if has_container else codec_lower

        # Normalize aliases (he-aac → aac, mpeg → mp3)
        audio_part = self._CODEC_ALIASES.get(audio_part, audio_part)

        try:
            content_type = ContentType(audio_part)
        except ValueError:
            self.logger.debug("Unknown codec from Yandex API: %s", codec)
            return ContentType.UNKNOWN, ContentType.UNKNOWN

        # For compound formats, set codec_type so ffmpeg knows the decoder
        codec_type = content_type if has_container else ContentType.UNKNOWN
        return content_type, codec_type

    def _get_audio_params(self, codec: str | None) -> tuple[int, int]:
        """Return (sample_rate, bit_depth) defaults based on codec string.

        :param codec: Codec string from Yandex API.
        :return: Tuple of (sample_rate, bit_depth).
        """
        if codec and codec.lower() == "flac-mp4":
            return 48000, 24
        return 44100, 16

    def _build_audio_format(self, codec: str | None, bit_rate: int = 0) -> AudioFormat:
        """Build AudioFormat with content type and codec-based audio params.

        :param codec: Codec string from Yandex API.
        :param bit_rate: Bitrate in kbps (0 for variable/unknown).
        :return: Configured AudioFormat instance.
        """
        content_type, codec_type = self._get_content_type(codec)
        sample_rate, bit_depth = self._get_audio_params(codec)
        return AudioFormat(
            content_type=content_type,
            codec_type=codec_type,
            bit_rate=bit_rate,
            sample_rate=sample_rate,
            bit_depth=bit_depth,
        )

    async def _refresh_stream_url(
        self,
        streamdetails: StreamDetails,
        http_status: int,
        bytes_yielded: int,
        attempt: int,
        max_retries: int,
    ) -> bool:
        """Re-fetch an expired stream URL (works for both raw and encraw).

        Updates streamdetails.data in-place with new URL (and key for encraw).

        :return: True on success, False if retries exhausted.
        """
        if attempt >= max_retries:
            return False
        data = streamdetails.data
        track_id = self._track_id_from_item_id(streamdetails.item_id)
        self.logger.warning(
            "Stream URL expired (HTTP %d) at %d bytes (attempt %d/%d) — re-fetching",
            http_status,
            bytes_yielded,
            attempt + 1,
            max_retries,
        )
        token = BYPASS_THROTTLER.set(True)
        try:
            file_info = await self.client.get_track_file_info(
                track_id,
                quality=data["fi_quality"],
                codecs=data["fi_codecs"],
                transport=data.get("transport", TRANSPORT_RAW),
            )
        finally:
            BYPASS_THROTTLER.reset(token)
        if file_info and file_info.get("url"):
            data["url"] = file_info["url"]
            if "decryption_key" in data and file_info.get("key"):
                data["decryption_key"] = file_info["key"]
            return True
        return False

    async def _decrypt_response_stream(
        self,
        response: Any,
        key_bytes: bytes,
        block_size: int,
        bytes_delivered: int,
    ) -> AsyncGenerator[bytes, None]:
        """Decrypt one HTTP response and yield plaintext chunks.

        Aligns the AES-CTR counter to the correct block for resumption.
        If the server ignores a Range header (200 instead of 206), resets the
        counter to 0 and skips the already-delivered prefix transparently.

        :param response: aiohttp ClientResponse (open context manager).
        :param key_bytes: Raw AES key bytes.
        :param block_size: AES block size (16 for CTR mode).
        :param bytes_delivered: Total plaintext bytes already sent to the caller.
        :return: Async generator yielding decrypted audio bytes.
        """
        block_start = (bytes_delivered // block_size) * block_size
        block_skip = bytes_delivered - block_start

        if block_start > 0 and response.status == 200:
            self.logger.warning(
                "Server ignored Range header at %d bytes (200 instead of 206)"
                " — restarting decrypt from position 0, skipping %d already-sent bytes",
                block_start,
                bytes_delivered,
            )
            block_skip = bytes_delivered
            block_num = (0).to_bytes(block_size, "big")
        else:
            block_num = (block_start // block_size).to_bytes(block_size, "big")

        decryptor = Cipher(algorithms.AES(key_bytes), modes.CTR(block_num)).decryptor()
        carry_skip = block_skip
        async for chunk in response.content.iter_chunked(_CHUNK_SIZE):
            decrypted = decryptor.update(chunk)
            if carry_skip > 0:
                skip = min(carry_skip, len(decrypted))
                decrypted = decrypted[skip:]
                carry_skip -= skip
            if decrypted:
                yield decrypted
        final = decryptor.finalize()
        if final:
            yield final

    def _handle_stream_error(
        self,
        err: Exception,
        attempt: int,
        max_retries: int,
        bytes_yielded: int,
        delays: tuple[float, ...],
        label: str,
    ) -> tuple[int, float]:
        """Increment retry counter, log a warning, or raise if retries are exhausted.

        :param err: The exception that caused the retry.
        :param attempt: Current retry attempt count (0-based).
        :param max_retries: Maximum number of retries allowed.
        :param bytes_yielded: Bytes delivered so far (for log context).
        :param delays: Backoff delay sequence to pick from.
        :param label: Short verb describing the failure (e.g. "dropped", "stalled").
        :return: (new_attempt, retry_delay) tuple when retrying.
        :raises MediaNotFoundError: When attempt count exceeds max_retries.
        """
        delay = delays[min(attempt, len(delays) - 1)]
        attempt += 1
        if attempt <= max_retries:
            self.logger.warning(
                "Stream %s at %d bytes (attempt %d/%d) — retrying",
                label,
                bytes_yielded,
                attempt,
                max_retries,
            )
            return attempt, delay
        raise MediaNotFoundError(f"Stream {label} after retries were exhausted") from err

    @staticmethod
    def _is_content_range_eof(headers: Any, window_end: int) -> bool:
        """Return True when Content-Range indicates *window_end* reached the last file byte.

        Parses ``Content-Range: bytes start-end/total`` and checks whether
        ``window_end >= total - 1``.  Returns False on any malformed header so
        the caller falls back to the next window safely.
        """
        content_range = headers.get("Content-Range", "")
        if not content_range.startswith("bytes "):
            return False
        try:
            _, range_spec = content_range.split(" ", 1)
            _, total_str = range_spec.split("/", 1)
            total_str = total_str.strip()
            return total_str.isdigit() and window_end >= int(total_str) - 1
        except ValueError:
            return False

    async def get_audio_stream(  # noqa: PLR0915
        self, streamdetails: StreamDetails, seek_position: int = 0
    ) -> AsyncGenerator[bytes, None]:
        """Return the audio stream via windowed Range requests.

        Handles both raw (direct) and encraw (AES-CTR encrypted) transports.
        Downloads in windowed Range requests of _RANGE_WINDOW bytes each to prevent
        Yandex CDN from dropping slow-consumer TCP connections.

        On connection drop: flat short backoff (0.5s/1.0s/2.0s).
        On read stall: exponential backoff (2s/4s/8s).
        On URL expiry (HTTP 4xx): re-fetches URL and resumes from bytes_yielded.
        Retry counter resets after each successful window.

        :param streamdetails: Stream details with URL (and optional decryption key).
        :param seek_position: Always 0 (seeking delegated to ffmpeg via allow_seek=True).
        :return: Async generator yielding audio bytes.
        """
        data = streamdetails.data
        is_encrypted = "decryption_key" in data
        url: str = data["url"]

        if is_encrypted:
            key_hex: str = data["decryption_key"]
            key_bytes = bytes.fromhex(key_hex)
            if len(key_bytes) not in (16, 24, 32):
                raise MediaNotFoundError(f"Unsupported AES key length: {len(key_bytes)} bytes")
        else:
            key_bytes = None

        block_size = 16  # AES-CTR block size in bytes
        max_retries = 6
        bytes_yielded = 0  # total bytes delivered to caller
        attempt = 0  # retry counter; resets to 0 after each successful window
        retry_delay: float = 0.0

        while True:
            if attempt > 0:
                await asyncio.sleep(retry_delay)

            # For encrypted transport, align to AES block boundary for correct decryption.
            # For raw transport, start exactly where we left off.
            if is_encrypted:
                block_start = (bytes_yielded // block_size) * block_size
            else:
                block_start = bytes_yielded

            window_end = block_start + _RANGE_WINDOW - 1
            headers = {"Range": f"bytes={block_start}-{window_end}"}

            try:
                url = data["url"]  # re-read in case _refresh_stream_url updated it
                async with self.mass.http_session.get(
                    url, headers=headers, timeout=_STREAM_TIMEOUT
                ) as response:
                    if response.status in (401, 403, 410):
                        refreshed = await self._refresh_stream_url(
                            streamdetails,
                            response.status,
                            bytes_yielded,
                            attempt,
                            max_retries,
                        )
                        if not refreshed:
                            raise MediaNotFoundError(
                                f"Stream URL expired (HTTP {response.status}) "
                                "after retries exhausted"
                            )
                        if is_encrypted:
                            key_hex = data["decryption_key"]
                            key_bytes = bytes.fromhex(key_hex)
                        retry_delay = 0.0
                        attempt += 1
                        continue
                    try:
                        response.raise_for_status()
                    except Exception as err:
                        raise MediaNotFoundError(f"Failed to fetch stream: {err}") from err

                    bytes_before = bytes_yielded

                    if is_encrypted:
                        assert key_bytes is not None
                        block_skip = bytes_before - block_start
                        async for chunk in self._decrypt_response_stream(
                            response, key_bytes, block_size, bytes_yielded
                        ):
                            bytes_yielded += len(chunk)
                            yield chunk
                    else:
                        # If server ignored Range (200 instead of 206) and we've
                        # already delivered bytes, skip the already-yielded prefix.
                        range_ignored = response.status == 200 and block_start > 0
                        skip_bytes = bytes_before if range_ignored else 0
                        block_skip = skip_bytes
                        async for raw_chunk in response.content.iter_chunked(_CHUNK_SIZE):
                            if skip_bytes > 0:
                                if len(raw_chunk) <= skip_bytes:
                                    skip_bytes -= len(raw_chunk)
                                    continue
                                usable = raw_chunk[skip_bytes:]
                                skip_bytes = 0
                                bytes_yielded += len(usable)
                                yield usable
                                continue
                            bytes_yielded += len(raw_chunk)
                            yield raw_chunk

                    # Window complete — check if EOF
                    window_got = bytes_yielded - bytes_before
                    received = window_got + block_skip
                    if response.status == 200 or received < _RANGE_WINDOW:
                        return  # full file received or last partial window
                    if self._is_content_range_eof(response.headers, window_end):
                        return
                    # more data expected: advance to next window
                    attempt = 0
                    retry_delay = 0.0

            except asyncio.CancelledError:
                raise  # propagate cancellation immediately, do not retry
            except (ClientPayloadError, ServerDisconnectedError) as err:
                attempt, retry_delay = self._handle_stream_error(
                    err, attempt, max_retries, bytes_yielded, _TCP_DROP_DELAYS, "dropped"
                )
            except TimeoutError as err:
                attempt, retry_delay = self._handle_stream_error(
                    err, attempt, max_retries, bytes_yielded, _STALL_DELAYS, "stalled"
                )
