"""
model_download_dialog.py — Custom permission dialog shown before a model download.
"""

import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class ModelDownloadDialog(QDialog):
    """
    Shown when the user triggers an action that requires a model that hasn't
    been downloaded yet.  Displays the model name, what it's best for,
    download size, and save location, then asks for confirmation.
    """

    def __init__(self, model_id: str, label: str, description: str,
                 size_mb: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model Download Required")
        self.setFixedWidth(420)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog  { background: #1e1e1e; }
            QLabel   { background: transparent; color: #ccc; }
            QFrame   { color: #333; }
        """)
        self._build(model_id, label, description, size_mb)

    def _build(self, model_id: str, label: str, description: str, size_mb: int):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 18)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = QLabel("⬇   AI Model Download Required")
        f = QFont()
        f.setPointSize(13)
        f.setBold(True)
        hdr.setFont(f)
        hdr.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(hdr)
        layout.addSpacing(16)

        # ── Model card ────────────────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #252525; border: 1px solid #3a3a3a;"
            " border-radius: 8px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(6)

        model_lbl = QLabel(label)
        mf = QFont()
        mf.setPointSize(13)
        mf.setBold(True)
        model_lbl.setFont(mf)
        model_lbl.setStyleSheet("color: #6ea3ff; background: transparent;")
        card_layout.addWidget(model_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("color: #999; font-size: 11px; background: transparent;")
        card_layout.addWidget(desc_lbl)

        card_layout.addSpacing(8)

        # Size row
        size_row = QHBoxLayout()
        size_key = QLabel("Download size:")
        size_key.setStyleSheet("color: #666; font-size: 11px; background: transparent;")
        size_val = QLabel(f"~{size_mb} MB")
        size_val.setStyleSheet(
            "color: #fff; font-size: 11px; font-weight: bold; background: transparent;"
        )
        size_row.addWidget(size_key)
        size_row.addWidget(size_val)
        size_row.addStretch()
        card_layout.addLayout(size_row)

        # Location row
        u2net_home = os.environ.get(
            "U2NET_HOME", os.path.join(os.path.expanduser("~"), ".u2net")
        )
        loc_row = QHBoxLayout()
        loc_key = QLabel("Saved to:")
        loc_key.setStyleSheet("color: #666; font-size: 11px; background: transparent;")
        loc_val = QLabel(os.path.join(u2net_home, f"{model_id}.onnx"))
        loc_val.setStyleSheet(
            "color: #aaa; font-size: 10px; font-family: monospace; background: transparent;"
        )
        loc_val.setWordWrap(True)
        loc_row.addWidget(loc_key)
        loc_row.addWidget(loc_val, 1)
        card_layout.addLayout(loc_row)

        layout.addWidget(card)
        layout.addSpacing(14)

        # ── Info text ─────────────────────────────────────────────────────────
        info = QLabel(
            "This is a <b>one-time download</b> per model — after that the app "
            "works fully offline with no internet connection needed."
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        info.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(info)

        layout.addSpacing(6)

        warn = QLabel("⚠  An internet connection is required for this download.")
        warn.setStyleSheet("color: #f0a500; font-size: 11px;")
        layout.addWidget(warn)

        layout.addSpacing(18)

        # ── Divider ───────────────────────────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("QFrame { border: none; border-top: 1px solid #333; }")
        layout.addWidget(line)
        layout.addSpacing(12)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedWidth(90)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #3c3f41; color: #ccc;
                border: 1px solid #555; padding: 6px 16px;
                border-radius: 4px; font-size: 12px;
            }
            QPushButton:hover { background: #4c5052; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_dl = QPushButton("Download Now")
        btn_dl.setFixedWidth(120)
        btn_dl.setDefault(True)
        btn_dl.setStyleSheet("""
            QPushButton {
                background: #1e6b35; color: #eee;
                border: 1px solid #2d9448; padding: 6px 16px;
                border-radius: 4px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background: #28873f; }
        """)
        btn_dl.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(8)
        btn_row.addWidget(btn_dl)
        layout.addLayout(btn_row)
