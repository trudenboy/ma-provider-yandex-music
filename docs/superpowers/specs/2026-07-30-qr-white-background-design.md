# QR login white-background design

## Problem

The QR login image is currently generated with `Segno.svg_data_uri(scale=4)`.
Segno leaves light modules transparent by default, so Music Assistant's dark
theme shows through the QR image and reduces the contrast needed for reliable
scanning.

## Design

Generate the existing SVG data URI with explicit QR colors and quiet zone:

- black dark modules (`dark="#000"`);
- opaque white light modules (`light="#fff"`);
- a four-module border (`border=4`), matching the standard QR quiet zone;
- the existing scale and medium error correction remain unchanged.

The setup-flow contract and image format stay unchanged. No frontend or model
changes are required, and the device-code image is unaffected.

## Testing

Add a focused regression test for `_qr_image` that decodes the SVG data URI and
asserts that it contains an opaque white background and black QR modules. Run
the setup-flow tests and the repository quality gate.

Restart the existing isolated Docker test container, start a fresh QR setup
flow, and verify that the updated provider imports successfully and produces a
black-on-white SVG with the four-module quiet zone. The container must retain
`UV_NO_BUILD=1` so no source distributions are built.

## Success criteria

- QR codes render with a fully opaque white background in light and dark themes.
- The four-module white quiet zone remains visible around the code.
- Existing setup-flow behavior, QR refresh, and authentication remain unchanged.
- Automated tests and the Docker smoke test pass.
