# BG Remover

**Batch background removal, entirely offline.**

[![GitHub Release](https://img.shields.io/github/v/release/longweekendlabs/bg-remover?style=flat-square)](https://github.com/longweekendlabs/bg-remover/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-Windows%20x64%20%7C%20Linux%20x64-lightgrey?style=flat-square)](https://github.com/longweekendlabs/bg-remover/releases/latest)

Drag in a folder of character sprites and get clean transparent PNGs back. BG Remover was built for visual novel developers cutting out hundreds of sprites at a time, and it does that work on your own machine: no cloud API, no account, no per-image cost, no watermark.

### [Download for Windows and Linux](https://github.com/longweekendlabs/bg-remover/releases/latest)

## Feed it a folder, not one file at a time

Drag in individual images or whole folder trees. The queue takes hundreds of files and works through them while you do something else. Input is PNG, JPG, JPEG, or WEBP; output is always transparent PNG.

Test on one image first if you want. Single-file preview runs a model against one picture so you can judge the cutout before committing the batch.

## Six models, and switching between them is free

BiRefNet Portrait and BiRefNet General for the best quality, ISNet when the edges are fussy, U2Net Human and U2Net when you want speed, and Silueta for simple subjects on the fastest setting.

Results are cached per model. Once an image has been through BiRefNet, flipping the preview to ISNet and back costs nothing, so you can compare cutouts side by side against a checkerboard instead of guessing which model suits a sprite.

## Nothing leaves your machine

Each model downloads once, between 43 MB and 176 MB depending on which one, and is cached in `~/.u2net/`. After that the app never touches the network. Your artwork is never uploaded anywhere, because there is nowhere for it to go.

## The rest

Before and after preview with a checkerboard transparency view. A dark interface that does not glare at you through a long cutting session. Originals are never modified.

## Download

Windows and Linux x64 builds are on the [releases page](https://github.com/longweekendlabs/bg-remover/releases/latest): a Windows installer and portable zip, and an AppImage, RPM, DEB, and tar.gz for Linux.

## Feedback

[Open an issue](https://github.com/longweekendlabs/bg-remover/issues) for a bug or a request. To write privately, email [iemrecnl@gmail.com](mailto:iemrecnl@gmail.com?subject=BG%20Remover%20feedback) and mention your version.

## License

MIT License. See [LICENSE](LICENSE). Free and open source: no licence key, no trial, no subscription.

© 2026 Long Weekend Labs

---

Made with ♥ by **[Long Weekend Labs](https://github.com/longweekendlabs)**
