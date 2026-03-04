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
  v1.2.2 — About dialog matches SBG v2 style (logo centred at top); custom
            model-download permission dialog with size/description; GitHub Pages
            portfolio; bundle pymatting dist-info (importlib.metadata crash fix)
"""

__version__   = "1.2.2"
__app_name__  = "BG Remover"
__org_name__  = "Long Weekend Labs"
__copyright__ = "© 2026 Long Weekend Labs"
