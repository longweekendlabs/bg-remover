# BG Remover — Deployment Reference

Everything a future Claude Code session needs to publish updates, fix the
GitHub Page, or update the branding — without asking the user any questions.

---

## 1. Repository

| Item | Value |
|---|---|
| GitHub org | `longweekendlabs` |
| Repo name | `bg-remover` |
| Repo URL | https://github.com/longweekendlabs/bg-remover |
| Clone URL | `https://github.com/longweekendlabs/bg-remover.git` |
| Local path | `/home/emre/AI/Claude/Project2/` |
| Default branch | `main` |

The `gh` CLI is authenticated as `longweekendlabs` (stored in system keyring).
Token scopes: `repo`, `workflow`, `delete_repo`, `gist`, `read:org`.
To verify: `gh auth status`

---

## 2. GitHub Pages

| Item | Value |
|---|---|
| Live URL | https://longweekendlabs.github.io/bg-remover/ |
| Source branch | `main` |
| Source folder | `/docs` (i.e. `Project2/docs/`) |
| Configured at | https://github.com/longweekendlabs/bg-remover/settings/pages |

**How it deploys:** GitHub Pages serves the `docs/` folder on `main` automatically.
There is no separate Pages workflow — just push to `main` and the page is live
within ~60 seconds.

**The only HTML file is:** `/home/emre/AI/Claude/Project2/docs/index.html`

---

## 3. GitHub Pages HTML Structure (`docs/index.html`)

```
<head>
  <style>          ← All CSS is inline (one file, no external sheets)
    :root { CSS variables for dark theme }
    nav, hero, features, models, download, more-section, footer styles
  </style>
</head>
<body>
  <nav>            ← Sticky top bar: brand + Features/Models/Download links + GitHub button
  <div.hero>       ← Version badge (auto-updated by JS), headline, two CTA buttons
  <section#features>  ← 8 feature cards (.feat grid)
  <section#models>    ← 6 model cards (.model-card grid)
  <section#download>  ← 3 download cards: Linux / Windows / Source
                        dl-linux and dl-windows divs are populated by JS fetch
  <div.more-section>  ← "More from Long Weekend Labs" cross-link to Speech Bubble Editor
  <footer>         ← Made with ♥ · GitHub · Releases links
  <script>         ← Fetches GitHub Releases API to populate download buttons
                     and update the version badge automatically
</body>
```

### CSS colour variables

```css
--bg:     #111318   /* page background */
--panel:  #1a1e26   /* nav / footer background */
--card:   #1f2430   /* feature/model/download cards */
--border: #2a2e3a   /* card borders */
--acc:    #2d6aff   /* primary blue (buttons, badge) */
--acc2:   #1e4ab0   /* blue hover */
--green:  #1a7a45   /* "Best" model badge */
--text:   #c8cdd8   /* body text */
--dim:    #6b7280   /* muted / secondary text */
--white:  #e8ebf0   /* headings */
```

### Dynamic download buttons

The `<script>` at the bottom fetches:
```
https://api.github.com/repos/longweekendlabs/bg-remover/releases/latest
```
It reads `assets[]` and populates `#dl-linux` and `#dl-windows` with real
download links and file sizes. If the fetch fails it keeps the static fallback
links already in the HTML. It also updates `.badge` with the tag name.

### Cross-link section (`.more-section`)

Located just before `<footer>`. Links to the sister app:
- **Speech Bubble Editor** → https://longweekendlabs.github.io/speech-bubble-editor/

That page in turn links back to BG Remover. Both pages must be kept in sync when a
new sister app is added.

---

## 4. Long Weekend Labs Branding

### Organisation name
`Long Weekend Labs`

### Logo file
| Location | Usage |
|---|---|
| `bg_remover_app/icons/LongWeekendLabs.logo.jpg` | Bundled in PyInstaller binary; shown in About dialog |
| Raw GitHub URL (used by Pages/web) | `https://raw.githubusercontent.com/longweekendlabs/bg-remover/main/icons/LongWeekendLabs.logo.jpg` |
| Original master copy | `/home/emre/AI/Claude/Project1/LongWeekendLabs.logo.jpg` |

The logo is a JPEG (rectangular, landscape orientation). In the About dialog it is
scaled to **200 px wide** with `SmoothTransformation`. In the GitHub Pages footer
of the sister app (speech-bubble-editor) it is displayed at 32×32 px, rounded.

### Where the logo appears in the app
- `bg_remover_app/about_dialog.py` — centred at the top of the About dialog,
  200 px wide, loaded via `_resource_path("icons/LongWeekendLabs.logo.jpg")`.

### Colours used in About dialog / UI
The app uses PyQt6's native OS theme (dark or light). No custom palette is applied
to the main window. The About dialog uses default system colours. The model-download
dialog (`model_download_dialog.py`) also uses native styling.

### App icon (window / taskbar)
- `bg_remover_app/icons/icon.png` — 256×256 PNG (programmatically generated scissors emoji render)
- `bg_remover_app/icons/icon.ico` — multi-size ICO for Windows
- Set in `main.py` via `app.setWindowIcon(QIcon(icon_path))`

---

## 5. CI/CD — Automated Releases

Releases are triggered by pushing a **version tag** (`v*`).
The workflow lives at `.github/workflows/release.yml`.

### What it builds

| Job | Runner | Output files |
|---|---|---|
| `build-linux` | `ubuntu-22.04` | `BGRemover-vX.Y.Z-x86_64.AppImage`, `bg-remover-X.Y.Z-1.x86_64.rpm`, `bg-remover_X.Y.Z_amd64.deb`, `BGRemover-vX.Y.Z-linux.tar.gz` |
| `build-windows` | `windows-latest` | `BGRemover-vX.Y.Z-win64-Setup.exe`, `BGRemover-vX.Y.Z-win64-portable.zip` |
| `publish` | `ubuntu-latest` | Creates GitHub Release, attaches all 6 files |

### Critical CI notes (hard-won fixes — do NOT revert)

1. **onnxruntime must be pinned to `1.19.2` on Windows.**
   Newer versions crash PyInstaller's analysis subprocess on GitHub Actions
   when any DLL is loaded. The pin is in the workflow `pip install` step, not
   in `requirements.txt`.

2. **Do NOT use `collect_submodules("onnxruntime")` in the spec.**
   It forces onnxruntime to import during analysis, triggering the DLL crash.
   The `pyinstaller-hooks-contrib` hook handles onnxruntime correctly without it.

3. **Add the onnxruntime `capi/` dir to `GITHUB_PATH` before PyInstaller runs
   on Windows** (see the "Add onnxruntime to PATH" step in the workflow).

4. **rpmbuild does not support reading spec from stdin (`-`) on Ubuntu.**
   The spec is written to `/tmp/bg_remover_${VERSION}.spec` and passed as a
   file argument.

5. **`copy_metadata("pymatting")` is required in the spec.**
   `pymatting/__init__.py` calls `importlib.metadata.version("pymatting")` at
   import time. Without the dist-info bundled, the app crashes on first run.

### No secrets to configure

The workflow uses the automatic `GITHUB_TOKEN` provided by GitHub Actions.
No repository secrets need to be set up. The `softprops/action-gh-release@v2`
action handles release creation with the default token.

---

## 6. Git Commands — Publishing Updates

### Update the GitHub Page only (no new app release)

```bash
cd /home/emre/AI/Claude/Project2
# edit docs/index.html
git add docs/index.html
git commit -m "docs: describe the change"
git push origin main
# Page is live at https://longweekendlabs.github.io/bg-remover/ within ~60s
```

### Release a new app version

```bash
cd /home/emre/AI/Claude/Project2

# 1. Bump version in ONE place only:
#    bg_remover_app/version.py  → __version__ = "X.Y.Z"
#    Also update the history block in that file.

# 2. Update the version badge in docs/index.html if desired
#    (the JS fetch will auto-update it, but the static fallback text is on line ~150)

# 3. Commit everything
git add bg_remover_app/version.py docs/index.html   # plus any other changed files
git commit -m "vX.Y.Z: summary of changes"

# 4. Tag and push — the tag push triggers CI
git tag vX.Y.Z
git push origin main
git push origin vX.Y.Z

# CI takes ~10-15 min. Monitor at:
# https://github.com/longweekendlabs/bg-remover/actions
```

### Push a branding or code change without a new release

```bash
git add <files>
git commit -m "describe change"
git push origin main
# No tag = no CI build = no new release
```

---

## 7. App File Map

```
Project2/
├── bg_remover_app/
│   ├── main.py                  # Entry point; sets app icon, theme, launches MainWindow
│   ├── main_window.py           # MainWindow: toolbar, queue, preview, progress bar, menu
│   ├── queue_panel.py           # Drag-and-drop file queue with retry/remove buttons
│   ├── preview_panel.py         # Before/after preview with checkerboard transparency
│   ├── processor.py             # ProcessorThread (rembg in QThread); emits signals
│   ├── model_download_dialog.py # Custom dialog: model name, size, path, download prompt
│   ├── about_dialog.py          # About dialog: LWL logo + app info + GitHub button
│   ├── settings.py              # MODELS, MODEL_LABELS, MODEL_SIZES_MB, DEFAULT_MODEL
│   ├── version.py               # __version__, __app_name__, __org_name__, __copyright__
│   ├── bg_remover_app.spec      # PyInstaller spec (used by CI and local builds)
│   ├── installer.iss            # Inno Setup script for Windows installer
│   ├── build_linux.sh           # Local Linux build script
│   ├── build_windows.bat        # Local Windows build script
│   └── icons/
│       ├── icon.png             # 256×256 app icon
│       ├── icon.ico             # Multi-size Windows icon
│       └── LongWeekendLabs.logo.jpg  # Branding logo (About dialog + bundled)
├── docs/
│   └── index.html               # GitHub Pages landing page (single file)
├── .github/
│   └── workflows/
│       └── release.yml          # CI/CD: builds + publishes release on v* tag push
├── .gitignore
├── README.md
└── DEPLOYMENT.md                # ← this file
```

---

## 8. Version Source of Truth

**`bg_remover_app/version.py`** is the single source of truth.
- `__version__` — used by PyInstaller spec, Inno Setup (`/DAppVersion` flag), and displayed in About dialog
- CI reads it at build time: `python -c "from version import __version__; print(__version__)"`
- The docs `index.html` version badge is updated automatically by the GitHub API JS fetch

---

## 9. Sister App — Speech Bubble Editor

The other Long Weekend Labs app lives at:
- Local path: `/home/emre/AI/Claude/Project1/Speech Bubble Generator v2/speech_bubble_v2/`
- GitHub: https://github.com/longweekendlabs/speech-bubble-editor
- Pages: https://longweekendlabs.github.io/speech-bubble-editor/
- Its `docs/index.html` has a "More from Long Weekend Labs" card linking back to BG Remover.

When adding a third app, add a cross-link card to **both** existing app Pages.
The `.more-section` / `.more-card` CSS pattern is consistent across both pages.

---

## 10. Local Test Run

```bash
cd /home/emre/AI/Claude/Project2/bg_remover_app
python main.py
```

Requirements: `pip install PyQt6 Pillow "rembg[cpu]"`

Stack: Python 3, PyQt6, rembg, Pillow, pymatting, scipy, onnxruntime

---

## 11. Connected Accounts and Services

| Service | Account | Notes |
|---|---|---|
| GitHub | `longweekendlabs` | Authenticated via `gh` CLI, token in system keyring |
| GitHub Pages | auto | Served from `docs/` on `main`, no extra config needed |
| GitHub Actions | auto | Uses built-in `GITHUB_TOKEN`, no secrets to configure |
| Inno Setup | n/a | Installed by CI via `choco install innosetup` on Windows runner |
| AppImageKit | n/a | Downloaded at CI build time from AppImage/AppImageKit releases |

No external APIs, paid services, CDNs, DNS, or third-party deployment platforms
are used. Everything runs on GitHub's free tier.
