"""
preview_panel.py — Right panel: side-by-side before/after preview with per-model switching.
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QPushButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor
from PIL import Image


# ── PIL → QPixmap conversion ─────────────────────────────────────────────────

def pil_to_qpixmap(pil_img: Image.Image) -> QPixmap:
    if pil_img.mode not in ("RGB", "RGBA"):
        pil_img = pil_img.convert("RGBA")

    if pil_img.mode == "RGBA":
        data   = bytes(pil_img.tobytes("raw", "RGBA"))
        stride = pil_img.width * 4
        fmt    = QImage.Format.Format_RGBA8888
    else:
        data   = bytes(pil_img.tobytes("raw", "RGB"))
        stride = pil_img.width * 3
        fmt    = QImage.Format.Format_RGB888

    qimg = QImage(data, pil_img.width, pil_img.height, stride, fmt)
    return QPixmap.fromImage(qimg.copy())


# ── Checkerboard helper ──────────────────────────────────────────────────────

def _make_checkerboard(width: int, height: int, tile: int = 16) -> QPixmap:
    pixmap  = QPixmap(width, height)
    painter = QPainter(pixmap)
    light   = QColor(200, 200, 200)
    dark    = QColor(150, 150, 150)
    for y in range(0, height, tile):
        for x in range(0, width, tile):
            color = light if (x // tile + y // tile) % 2 == 0 else dark
            painter.fillRect(x, y, min(tile, width - x), min(tile, height - y), color)
    painter.end()
    return pixmap


def composite_on_checkerboard(pixmap: QPixmap, tile: int = 16) -> QPixmap:
    w, h    = pixmap.width(), pixmap.height()
    result  = _make_checkerboard(w, h, tile)
    painter = QPainter(result)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    return result


# ── Auto-scaling image label ─────────────────────────────────────────────────

class _ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._source: QPixmap | None = None
        self.setMinimumSize(80, 80)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: #111111;")

    def set_pixmap(self, pixmap: QPixmap):
        self._source = pixmap
        self._redraw()

    def clear_image(self):
        self._source = None
        self.clear()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._redraw()

    def _redraw(self):
        if self._source:
            scaled = self._source.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            super().setPixmap(scaled)


# ── Model switcher button style ───────────────────────────────────────────────

_MODEL_BTN = """
    QPushButton {{
        background: {bg}; color: {fg};
        border: 1px solid {border}; border-radius: 3px;
        padding: 1px 7px; font-size: 10px;
    }}
    QPushButton:hover {{ background: #4a6080; color: #fff; }}
"""
_MODEL_BTN_ACTIVE   = _MODEL_BTN.format(bg="#2d6a9f", fg="#fff",   border="#4a8abf")
_MODEL_BTN_INACTIVE = _MODEL_BTN.format(bg="#2a2a2a", fg="#888",   border="#3a3a3a")


# ── Preview panel ────────────────────────────────────────────────────────────

_COL_HDR = (
    "color: #777; font-size: 11px; background: #1a1a1a;"
    " padding: 4px; border-bottom: 1px solid #2a2a2a;"
)


class PreviewPanel(QWidget):
    """Right panel: side-by-side before / after preview with per-model caching."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # State
        self._original_path  = ""
        self._model_results: dict[str, str] = {}   # model_name → file_path
        self._active_model   = ""
        self._model_btns: dict[str, QPushButton] = {}

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(32)
        header.setStyleSheet("background: #252525; border-bottom: 1px solid #3a3a3a;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 0, 10, 0)
        title = QLabel("Preview")
        title.setStyleSheet("color: #aaa; font-size: 12px; font-weight: bold;")
        hl.addWidget(title)
        layout.addWidget(header)

        # Stack: page 0 = placeholder, page 1 = images
        self.stack = QStackedWidget()

        # ── Page 0: placeholder ──────────────────────────────────────────────
        ph_page = QWidget()
        ph_page.setStyleSheet("background: #111111;")
        pl = QVBoxLayout(ph_page)
        self._placeholder_lbl = QLabel(
            "Select a completed image\nto see the before / after preview"
        )
        self._placeholder_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder_lbl.setStyleSheet(
            "color: #3d3d3d; font-size: 14px; background: transparent;"
        )
        self._placeholder_lbl.setWordWrap(True)
        pl.addWidget(self._placeholder_lbl)
        self.stack.addWidget(ph_page)

        # ── Page 1: images ───────────────────────────────────────────────────
        img_page = QWidget()
        img_page.setStyleSheet("background: #111111;")
        il = QVBoxLayout(img_page)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(0)

        # Column headers row
        hdr_row = QHBoxLayout()
        hdr_row.setSpacing(2)
        hdr_row.setContentsMargins(0, 0, 0, 0)

        orig_hdr = QLabel("Original")
        orig_hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orig_hdr.setStyleSheet(_COL_HDR)
        orig_hdr.setFixedHeight(28)

        # Result header: "Result:" label + model switcher buttons side by side
        result_hdr = QWidget()
        result_hdr.setFixedHeight(28)
        result_hdr.setStyleSheet("background: #1a1a1a; border-bottom: 1px solid #2a2a2a;")
        rh_layout = QHBoxLayout(result_hdr)
        rh_layout.setContentsMargins(6, 2, 6, 2)
        rh_layout.setSpacing(5)

        self._result_lbl = QLabel("Result:")
        self._result_lbl.setStyleSheet("color: #555; font-size: 10px;")
        rh_layout.addWidget(self._result_lbl)

        # Model buttons go in this layout (rebuilt on each entry selection)
        self._model_btn_layout = QHBoxLayout()
        self._model_btn_layout.setSpacing(4)
        self._model_btn_layout.setContentsMargins(0, 0, 0, 0)
        rh_layout.addLayout(self._model_btn_layout)
        rh_layout.addStretch()

        hdr_row.addWidget(orig_hdr)
        hdr_row.addWidget(result_hdr)
        il.addLayout(hdr_row)

        # Image labels
        img_row = QHBoxLayout()
        img_row.setSpacing(2)
        img_row.setContentsMargins(0, 0, 0, 0)
        self._lbl_original = _ImageLabel()
        self._lbl_result   = _ImageLabel()
        img_row.addWidget(self._lbl_original)
        img_row.addWidget(self._lbl_result)
        il.addLayout(img_row, 1)

        self.stack.addWidget(img_page)
        layout.addWidget(self.stack, 1)
        self.stack.setCurrentIndex(0)

    # ── Public API ───────────────────────────────────────────────────────────

    def update_for_entry(self, original_path: str, model_results: dict[str, str]):
        """Show original + model-switcher buttons for a selected Done entry."""
        self._original_path = original_path
        self._model_results = dict(model_results)

        # Load original image
        try:
            self._lbl_original.set_pixmap(pil_to_qpixmap(Image.open(original_path)))
        except Exception:
            self._lbl_original.clear_image()

        # Rebuild model buttons
        self._rebuild_model_buttons()

        # Show the most recently processed model by default
        if model_results:
            latest = list(model_results.keys())[-1]
            self._show_model_result(latest)
        else:
            self._lbl_result.clear_image()

        self.stack.setCurrentIndex(1)

    def show_placeholder(self, text: str = ""):
        if text:
            self._placeholder_lbl.setText(text)
        self.stack.setCurrentIndex(0)

    def clear_preview(self):
        self._original_path = ""
        self._model_results  = {}
        self._active_model   = ""
        self._lbl_original.clear_image()
        self._lbl_result.clear_image()
        self._rebuild_model_buttons()
        self._placeholder_lbl.setText(
            "Select a completed image\nto see the before / after preview"
        )
        self.stack.setCurrentIndex(0)

    # ── Model switcher ────────────────────────────────────────────────────────

    def _rebuild_model_buttons(self):
        """Destroy and recreate the row of model result buttons."""
        # Remove existing buttons
        for btn in self._model_btns.values():
            self._model_btn_layout.removeWidget(btn)
            btn.deleteLater()
        self._model_btns.clear()

        for model_name in self._model_results:
            btn = QPushButton(model_name)
            btn.setFixedHeight(20)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(_MODEL_BTN_INACTIVE)
            btn.clicked.connect(
                lambda _checked, m=model_name: self._show_model_result(m)
            )
            self._model_btn_layout.addWidget(btn)
            self._model_btns[model_name] = btn

    def _show_model_result(self, model_name: str):
        """Switch the result pane to display a specific model's cached output."""
        self._active_model = model_name

        # Highlight active button
        for name, btn in self._model_btns.items():
            btn.setStyleSheet(
                _MODEL_BTN_ACTIVE if name == model_name else _MODEL_BTN_INACTIVE
            )

        path = self._model_results.get(model_name, "")
        if path and os.path.exists(path):
            try:
                result_pixmap = pil_to_qpixmap(Image.open(path))
                self._lbl_result.set_pixmap(composite_on_checkerboard(result_pixmap))
                return
            except Exception:
                pass
        self._lbl_result.clear_image()
