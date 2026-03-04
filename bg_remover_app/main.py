"""
main.py — BG Remover entry point.
"""

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from version import __version__, __app_name__
from main_window import MainWindow


def _apply_system_theme(app: QApplication) -> None:
    """On Windows, match the OS dark / light app-theme setting.

    Reads AppsUseLightTheme from the registry:
      dark  → Fusion style + dark QPalette
      light → native windowsvista style

    On Linux / macOS this is a no-op (the app ships its own dark stylesheet).
    """
    if sys.platform != "win32":
        return

    from PyQt6.QtGui import QPalette, QColor

    dark_mode = False
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        use_light, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        dark_mode = not bool(use_light)
    except Exception:
        pass

    if dark_mode:
        app.setStyle("Fusion")
        p = QPalette()
        bg      = QColor(30, 30, 30)
        panel   = QColor(45, 45, 45)
        ctrl    = QColor(53, 53, 53)
        fg      = QColor(220, 220, 220)
        hi      = QColor(42, 130, 218)
        hi_text = QColor(255, 255, 255)
        dim     = QColor(110, 110, 110)

        p.setColor(QPalette.ColorRole.Window,          bg)
        p.setColor(QPalette.ColorRole.WindowText,      fg)
        p.setColor(QPalette.ColorRole.Base,            panel)
        p.setColor(QPalette.ColorRole.AlternateBase,   ctrl)
        p.setColor(QPalette.ColorRole.ToolTipBase,     ctrl)
        p.setColor(QPalette.ColorRole.ToolTipText,     fg)
        p.setColor(QPalette.ColorRole.Text,            fg)
        p.setColor(QPalette.ColorRole.Button,          ctrl)
        p.setColor(QPalette.ColorRole.ButtonText,      fg)
        p.setColor(QPalette.ColorRole.BrightText,      QColor(255, 80, 80))
        p.setColor(QPalette.ColorRole.Link,            hi)
        p.setColor(QPalette.ColorRole.Highlight,       hi)
        p.setColor(QPalette.ColorRole.HighlightedText, hi_text)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,       dim)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, dim)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, dim)
        app.setPalette(p)
    else:
        app.setStyle("windowsvista")


def main():
    # Enable high-DPI scaling (important for Wayland / KDE Plasma)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Long Weekend Labs")

    _apply_system_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
