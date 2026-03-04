"""
about_dialog.py — About dialog with Long Weekend Labs branding.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPixmap, QFont

from version import __version__, __app_name__


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {__app_name__}")
        self.setFixedSize(460, 340)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #1e1e1e;
            }
            QLabel {
                color: #ccc;
                background: transparent;
            }
            QPushButton {
                background: #3c3f41; color: #ccc;
                border: 1px solid #555; padding: 5px 16px;
                border-radius: 4px; font-size: 12px;
            }
            QPushButton:hover { background: #4c5052; }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(0)

        # ── Logo / branding row ──────────────────────────────────────────────
        brand_row = QHBoxLayout()
        brand_row.setSpacing(14)

        # Coloured square stand-in for logo
        logo_lbl = QLabel()
        logo_lbl.setFixedSize(52, 52)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #1e4a6b, stop:1 #2d6a9f);"
            "border-radius: 10px; color: #fff; font-size: 22px;"
        )
        logo_lbl.setText("✂")

        brand_col = QVBoxLayout()
        brand_col.setSpacing(2)

        app_name_lbl = QLabel(__app_name__)
        app_name_lbl.setFont(QFont("", 18, QFont.Weight.Bold))
        app_name_lbl.setStyleSheet("color: #e0e0e0;")

        ver_lbl = QLabel(f"Version {__version__}")
        ver_lbl.setStyleSheet("color: #666; font-size: 12px;")

        brand_col.addWidget(app_name_lbl)
        brand_col.addWidget(ver_lbl)
        brand_col.addStretch()

        brand_row.addWidget(logo_lbl)
        brand_row.addLayout(brand_col)
        brand_row.addStretch()
        layout.addLayout(brand_row)

        layout.addSpacing(18)

        # ── Description ──────────────────────────────────────────────────────
        desc = QLabel(
            "AI-powered batch background removal — <b>100% offline</b>.<br>"
            "Drop your sprites and character art; get clean transparent PNGs<br>"
            "without cloud APIs, subscriptions, or watermarks."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #aaa; font-size: 12px; line-height: 1.5;")
        desc.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(desc)

        layout.addSpacing(16)

        # ── Powered-by row ───────────────────────────────────────────────────
        powered = QLabel(
            "Powered by <b>rembg</b> · BiRefNet · ISNet · U²Net"
        )
        powered.setStyleSheet("color: #666; font-size: 11px;")
        powered.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(powered)

        layout.addSpacing(20)

        # ── Divider ──────────────────────────────────────────────────────────
        div = QLabel()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #333;")
        layout.addWidget(div)

        layout.addSpacing(14)

        # ── Bottom row: org + buttons ─────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        org_lbl = QLabel("© 2025 Long Weekend Labs")
        org_lbl.setStyleSheet("color: #555; font-size: 11px;")
        bottom.addWidget(org_lbl)
        bottom.addStretch()

        btn_gh = QPushButton("GitHub")
        btn_gh.setToolTip("Open the project page on GitHub")
        btn_gh.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/longweekendlabs/bg-remover")
            )
        )

        btn_ok = QPushButton("Close")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setStyleSheet("""
            QPushButton {
                background: #2d5a9f; color: #fff;
                border: 1px solid #4a7abf; padding: 5px 16px;
                border-radius: 4px; font-size: 12px;
            }
            QPushButton:hover { background: #3a6ab0; }
        """)

        bottom.addWidget(btn_gh)
        bottom.addWidget(btn_ok)
        layout.addLayout(bottom)
