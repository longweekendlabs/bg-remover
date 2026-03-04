"""
version.py — Single source of truth for the application version.

History:
  v1.0.0 — Batch background removal with rembg AI (BiRefNet / U2Net / ISNet),
            PyQt6 dark UI, multi-model toggle buttons, per-model result caching,
            before/after preview panel, drag-and-drop queue, model download prompts
  v1.2.0 — Long Weekend Labs branding; About dialog; menu bar; comprehensive
            tooltips on every control; Windows OS dark/light theme detection
  v1.2.1 — Fix: bundle scipy (rembg → pymatting → scipy); was excluded from
            PyInstaller build causing crash on first processing job
"""

__version__  = "1.2.1"
__app_name__ = "BG Remover"
