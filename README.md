# Fluoroscopy Simulator (alpha)

A single-file, dependency-free PWA that mimics a fluoroscopy (X-ray) C-arm on a phone.
Hold a foot switch (any key) and the rear-camera feed appears only while it's pressed —
release and the screen goes black. Built to rehearse pedal-timed imaging without a real
C-arm, then mirror the phone to an external monitor via DP Alt Mode.

> **Note:** This is a throwaway *alpha* deployment for testing. The production repo will
> be `fluoro-sim`. Don't rely on this URL.

## Use

1. Open in mobile Safari (iOS 15+) or Chrome.
2. Tap **Start** to grant camera access.
3. Press and hold any key (USB / Bluetooth foot switch) — image shows while held.
   - `R` — toggle recording (saved via the share sheet / download)
   - `I` — invert brightness (photo → X-ray-like look)

## Tech

- HTML + CSS + JS in one `index.html`, no framework, no build step.
- `getUserMedia` (`facingMode: environment`) for the camera.
- `keydown` / `keyup` drive exposure — any key works (foot-switch key mappings vary).
- `MediaRecorder` + `navigator.share()` for recording, with a download fallback.
- CSS `filter: grayscale/contrast/invert` for the fluoroscopy look.

## Deploy

Static hosting on GitHub Pages (main branch, root). No server needed.

See the Cosense page *透視シミュレーターPWA 実装プラン* for design intent and the full plan.
