"""Common test helpers for Yandex Music provider tests."""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncGenerator

from music_assistant_models.enums import EventType
from music_assistant_models.event import MassEvent

from music_assistant.mass import MusicAssistant


@contextlib.asynccontextmanager
async def wait_for_sync_completion(mass: MusicAssistant) -> AsyncGenerator[None, None]:
    """Wait for a sync to finish."""
    flag = asyncio.Event()

    def _event(event: MassEvent) -> None:
        if not event.data:
            flag.set()

    release_cb = mass.subscribe(_event, EventType.SYNC_TASKS_UPDATED)

    try:
        yield
    finally:
        await flag.wait()
        release_cb()
