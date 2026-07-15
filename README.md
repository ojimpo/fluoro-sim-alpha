# Fluoroscopy Simulator (alpha)

A single-file, dependency-free PWA that mimics a fluoroscopy (X-ray) C-arm on a phone.
It reproduces the two-pedal setup of a real angiography system: an **observe** pedal
shows the live rear-camera feed only while it's held, and an **acquire** pedal records
a short cine run (up to 10 s) that then loops in a corner wipe. Built to rehearse
pedal-timed imaging without a real C-arm, then mirror the phone to an external monitor
via DP Alt Mode.

> **Note:** This is a throwaway *alpha* deployment for testing. The production repo will
> be `fluoro-sim`. Don't rely on this URL.

## Use

1. Open in mobile Safari (iOS 15+) or Chrome.
2. Tap **Start** to grant camera access.
3. Operate with two foot pedals (or the two on-screen pedals):
   - **観察 / Observe** — hold to show the live fluoro image; release and it goes black.
   - **撮影 / Acquire** — hold to record (max 10 s, auto-cut at the cap). On release the
     clip loops as a wipe in the top-right corner. Tap the wipe to save it (share sheet /
     download); tap **×** to clear it.
   - `I` — invert brightness (photo → X-ray-like look).

### USB / Bluetooth foot switch

Any key acts as the **observe** pedal by default, so a single-pedal switch works out of
the box. A two-pedal switch sends a different key per pedal — open **USBペダルのキー割り当て**
on the start screen and register the **撮影 (acquire)** pedal (and optionally the observe
one). Bindings are stored in `localStorage`.

## Tech

- HTML + CSS + JS in one `index.html`, no framework, no build step.
- `getUserMedia` (`facingMode: environment`) for the camera.
- `keydown` / `keyup` drive both pedals; the acquire key is configurable, everything else
  falls back to observe (foot-switch key mappings vary).
- `MediaRecorder` captures the cine run; the clip is replayed with a looping `<video>`
  wipe and saved via `navigator.share()` with a download fallback.
- CSS `filter: grayscale/contrast/invert` for the fluoroscopy look.

## Deploy

Static hosting on GitHub Pages (main branch, root). No server needed.

See the Cosense page *透視シミュレーターPWA 実装プラン* for design intent and the full plan.
