"""
about_dialog.py — About dialog, styled to match Speech Bubble Generator v2.
"""

import os
import sys
import subprocess
import webbrowser

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

from version import __version__, __app_name__, __org_name__, __copyright__

_GITHUB_URL = "https://github.com/longweekendlabs/bg-remover"


def _resource_path(relative: str) -> str:
    """Resolve path both from source and inside a PyInstaller bundle."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def _open_url(url: str):
    """Open URL in system browser with multiple fallbacks."""
    try:
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QDesktopServices
        if QDesktopServices.openUrl(QUrl(url)):
            return
    except Exception:
        pass
    try:
        webbrowser.open(url)
        return
    except Exception:
        pass
    try:
        if sys.platform == "win32":
            subprocess.Popen(["start", url], shell=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", url])
        else:
            subprocess.Popen(["xdg-open", url])
    except Exception:
        pass


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {__app_name__}")
        self.setFixedWidth(440)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(12)

        # ── Logo ─────────────────────────────────────────────────────────────
        logo_path = _resource_path(os.path.join("icons", "LongWeekendLabs.logo.jpg"))
        if os.path.exists(logo_path):
            logo_pm = QPixmap(logo_path).scaledToWidth(
                200, Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl = QLabel()
            logo_lbl.setPixmap(logo_pm)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(logo_lbl)

        # ── App name ─────────────────────────────────────────────────────────
        name_lbl = QLabel(__app_name__)
        f = QFont()
        f.setPointSize(18)
        f.setBold(True)
        name_lbl.setFont(f)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(name_lbl)

        # ── Version ───────────────────────────────────────────────────────────
        ver_lbl = QLabel(f"Version {__version__}")
        f2 = QFont()
        f2.setPointSize(11)
        ver_lbl.setFont(f2)
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        ver_lbl.setStyleSheet("color: #888;")
        layout.addWidget(ver_lbl)

        # ── Org / copyright ───────────────────────────────────────────────────
        org_lbl = QLabel(f"{__org_name__}\n{__copyright__}")
        org_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        org_lbl.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(org_lbl)

        # ── Divider ───────────────────────────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # ── Description ───────────────────────────────────────────────────────
        desc_lbl = QLabel(
            "AI-powered batch background removal — 100% offline.\n"
            "Drop your sprites and art; get clean transparent PNGs\n"
            "without cloud APIs, subscriptions, or watermarks.\n\n"
            "Built with: Python · PyQt6 · rembg · BiRefNet · ISNet · U²Net"
        )
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        desc_lbl.setStyleSheet("color: #999; font-size: 10px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_gh = QPushButton("GitHub")
        btn_gh.setToolTip(_GITHUB_URL)
        btn_gh.setFixedWidth(90)
        btn_gh.clicked.connect(lambda: _open_url(_GITHUB_URL))
        btn_row.addWidget(btn_gh)

        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(90)
        btn_close.setDefault(True)
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)

        btn_row.addStretch()
        layout.addLayout(btn_row)
