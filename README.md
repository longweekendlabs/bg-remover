# BG Remover

**AI-powered batch background removal — 100% offline.**

Drop your character sprites and artwork; get clean transparent PNGs without cloud APIs, subscriptions, or watermarks. Built for Visual Novel developers who need to process large numbers of sprites quickly.

[![GitHub Release](https://img.shields.io/github/v/release/longweekendlabs/bg-remover?style=flat-square)](https://github.com/longweekendlabs/bg-remover/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

## Features

- **Drag & drop** images or whole folders into the queue
- **6 AI models** — BiRefNet Portrait (best for sprites), BiRefNet General, ISNet, U2Net Human, U2Net, Silueta
- **Batch processing** — queue up hundreds of files, process while you work
- **Before / after preview** — checkerboard transparency view per model, side by side
- **Per-model result cache** — switch models on the preview without re-processing
- **Single-file preview** — test a model on one image before committing the batch
- **100% offline** — models download once (~175 MB), then no internet needed
- **Dark UI** — easy on the eyes for long sessions

## Download

| Platform | Package | Notes |
|---|---|---|
| Linux (any distro) | `.AppImage` | Run directly, no install |
| Fedora / RHEL | `.rpm` | `sudo dnf install bg-remover-*.rpm` |
| Ubuntu / Mint | `.deb` | `sudo dpkg -i bg-remover_*.deb` |
| Linux archive | `.tar.gz` | Extract and run |
| Windows (installer) | `-Setup.exe` | Installs to Start Menu |
| Windows (portable) | `-portable.zip` | No install, run anywhere |

**→ [Download latest release](https://github.com/longweekendlabs/bg-remover/releases/latest)**

## Supported formats

**Input:** PNG, JPG, JPEG, WEBP
**Output:** PNG (transparent)

## Running from source

```bash
git clone https://github.com/longweekendlabs/bg-remover.git
cd bg-remover/bg_remover_app
pip install PyQt6 Pillow "rembg[cpu]"
python main.py
```

> **Note:** On first run, rembg downloads the selected AI model (~175 MB). After that the app works fully offline.

## AI Models

| Model | Label | Best for | Download |
|---|---|---|---|
| `birefnet-portrait` | BiRefNet Portrait ★ | Character sprites & portraits (default) | ~175 MB |
| `birefnet-general` | BiRefNet General | General purpose, high quality | ~175 MB |
| `isnet-general-use` | ISNet | Detailed edges | ~100 MB |
| `u2net_human_seg` | U2Net Human | Human figures, faster | ~176 MB |
| `u2net` | U2Net | General purpose, faster | ~176 MB |
| `silueta` | Silueta | Simple subjects, fastest | ~43 MB |

Each model downloads once and is cached in `~/.u2net/`.

## Building

### Linux

```bash
pip install pyinstaller
bash build_linux.sh
# Outputs: lin/*.AppImage  lin/*.rpm  lin/*.deb  lin/*.tar.gz
```

### Windows

```bat
pip install pyinstaller
build_windows.bat
:: Outputs: win\*-portable.zip  win\*-Setup.exe (if Inno Setup installed)
```

## Release process

```bash
git tag v1.2.0
git push origin v1.2.0
```

GitHub Actions automatically builds all packages and creates a release.

---

Made with ♥ by **[Long Weekend Labs](https://github.com/longweekendlabs)**
