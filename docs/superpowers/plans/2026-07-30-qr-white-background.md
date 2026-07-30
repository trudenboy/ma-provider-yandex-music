# QR Login White Background Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render the Yandex QR login code as an opaque black-on-white SVG with a four-module quiet zone.

**Architecture:** Keep the existing setup-flow image data-URI contract and configure Segno at the serialization boundary. A focused regression test decodes the real SVG and verifies both the white background and the four-module border before the implementation changes.

**Tech Stack:** Python 3.13+, pytest, Segno 1.6.6, Music Assistant setup flows, Docker.

## Global Constraints

- Keep SVG output and medium QR error correction.
- Use black dark modules (`dark="#000"`).
- Use opaque white light modules (`light="#fff"`).
- Use a four-module quiet zone (`border=4`).
- Do not change the device-code image or setup-flow contract.
- Keep `UV_NO_BUILD=1` in the Docker verification container.

---

### Task 1: Make the QR image opaque and scanner-friendly

**Files:**
- Modify: `tests/test_setup_flow.py`
- Modify: `provider/setup_flow.py:187-189`

**Interfaces:**
- Consumes: `provider.setup_flow._qr_image(qr_url: str) -> str`.
- Produces: the same SVG data-URI return type, now with an opaque white background and four-module quiet zone.

- [ ] **Step 1: Write the failing regression test**

Add the XML and URI decoding imports and this focused test to `tests/test_setup_flow.py`:

```python
from urllib.parse import unquote
from xml.etree import ElementTree


def test_qr_image_has_opaque_white_quiet_zone() -> None:
    """The QR remains high-contrast against Music Assistant's dark theme."""
    image = ym_flow._qr_image("https://passport.yandex.ru/qr/test")
    svg = unquote(image.split(",", 1)[1])
    root = ElementTree.fromstring(svg)
    paths = root.findall("{http://www.w3.org/2000/svg}path")

    background = next(path for path in paths if path.get("fill") == "#fff")
    modules = next(path for path in paths if path.get("stroke") == "#000")

    assert background.get("d") == "M0 0h37v37h-37z"
    assert modules.get("d", "").startswith("M4 4.5")
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
UV_CACHE_DIR=/private/tmp/ma-yandex-qr-uv-cache uv run pytest tests/test_setup_flow.py::test_qr_image_has_opaque_white_quiet_zone -q
```

Expected: FAIL because the current transparent SVG has no path whose `fill` is `#fff`.

- [ ] **Step 3: Implement the minimal Segno configuration**

Change `_qr_image` in `provider/setup_flow.py` to:

```python
def _qr_image(qr_url: str) -> str:
    """Render a high-contrast QR-login URL as an SVG data URI."""
    return segno.make(qr_url, error="m").svg_data_uri(
        scale=4,
        dark="#000",
        light="#fff",
        border=4,
    )
```

- [ ] **Step 4: Verify GREEN and the setup-flow suite**

Run:

```bash
UV_CACHE_DIR=/private/tmp/ma-yandex-qr-uv-cache uv run pytest tests/test_setup_flow.py -q
```

Expected: all setup-flow tests PASS.

- [ ] **Step 5: Run repository quality gates**

Run:

```bash
UV_CACHE_DIR=/private/tmp/ma-yandex-qr-uv-cache uv run pytest -q
UV_CACHE_DIR=/private/tmp/ma-yandex-qr-uv-cache uv run pre-commit run --all-files
```

Expected: all tests and hooks PASS without errors.

- [ ] **Step 6: Restart and verify the isolated Docker instance**

Restart `ma-yandex-functional-v385`, then execute `_qr_image` inside the container and decode its SVG. Assert the installed provider returns a `fill='#fff'` background, `stroke='#000'` modules, and a module path beginning at `M4 4.5`. Confirm `http://localhost:18095/` returns HTTP 200 and the container logs contain no new ERROR, CRITICAL, or traceback entries.

- [ ] **Step 7: Commit the implementation**

```bash
git add provider/setup_flow.py tests/test_setup_flow.py
git commit -m "fix: render QR login on white background"
```
