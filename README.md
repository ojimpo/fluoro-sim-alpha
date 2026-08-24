# Fluoroscopy Simulator (alpha)

A single-file, dependency-free PWA that mimics a fluoroscopy (X-ray) C-arm on a phone.
It reproduces the two-pedal setup of a real angiography system: an **observe** pedal
shows the live rear-camera feed only while it's held, and an **acquire** pedal records
a short cine run (up to 10 s) that then loops in a corner wipe. Built to rehearse
pedal-timed imaging without a real C-arm, then mirror the phone to an external monitor
via DP Alt Mode.

> **Note:** This is the *alpha* lane, where things are tried out and allowed to break.
> Production lives in `fluoro-sim`, which only takes changes that have been checked on a
> real device. Don't rely on this URL.

## Use

1. Open in mobile Safari (iOS 15+) or Chrome.
2. Tap **Start** to grant camera access.
3. Operate with two foot pedals (or the two on-screen pedals):
   - **観察 / Observe** — hold to show the live fluoro image; release and it goes black.
   - **撮影 / Acquire** — hold to record (max 10 s, auto-cut at the cap). On release the
     clip loops as a wipe in the top-right corner. Drag it to move, use the bottom-left
     handle to resize, tap **×** to clear it. The wipe is a reference view only and has no
     save path, the same as a real C-arm; use **Rec** below to keep footage.
   - `I` (or the **Mono / Inverted / Color** button) — cycle the image look:
     monochrome → monochrome inverted (X-ray-like) → full color.
4. **Rec** button (bottom bar) — records the whole session continuously, independent of the
   pedals. Tap to start (a "REC SESSION" badge shows), tap again to stop and save. Runs in
   parallel with the acquire pedal's clip recorder.

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
- `MediaRecorder` captures the cine run and replays it in a looping `<video>` wipe. A
  second, independent `MediaRecorder` handles the manual whole-session recording, which is
  the only thing that gets saved, via `navigator.share()` with a download fallback.
- A dependency-free ArUco detector (`DICT_4X4_50`) reads markers stuck to the model's
  corners and rectifies it onto the middle of the screen with a CSS `matrix3d`. Detection
  runs once, from the **Align** button, not per frame.
- CSS `filter: grayscale/contrast/invert` for the fluoroscopy look.

## Deploy

Static hosting on GitHub Pages (main branch, root). No server needed.

See the Cosense page *透視シミュレーターPWA 実装プラン* for design intent and the full plan.
