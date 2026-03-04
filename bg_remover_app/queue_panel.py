"""
queue_panel.py — Left panel: scrollable file queue with drag-and-drop support.
"""

import os
from dataclasses import dataclass, field

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QSizePolicy, QMenu, QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage, QColor, QAction
from PIL import Image

from settings import SUPPORTED_EXTENSIONS


# ── Status display helpers ──────────────────────────────────────────────────

STATUS_COLORS = {
    "Pending":    "#888888",
    "Processing": "#f0a500",
    "Done":       "#4caf50",
    "Failed":     "#f44336",
}

STATUS_ICONS = {
    "Pending":    "○",
    "Processing": "⟳",
    "Done":       "✓",
    "Failed":     "✗",
}


# ── Data model ──────────────────────────────────────────────────────────────

@dataclass
class QueueEntry:
    file_path: str
    status: str = "Pending"
    output_path: str = ""
    error_msg: str = ""
    thumbnail: object = None                         # QPixmap, set at add time
    model_results: dict = field(default_factory=dict)  # model_name → output_path


# ── Helpers ─────────────────────────────────────────────────────────────────

def _format_size(path: str) -> str:
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / 1024 / 1024:.1f} MB"
    except OSError:
        return "?"


def _load_thumbnail(file_path: str, size: int = 64) -> QPixmap | None:
    try:
        img = Image.open(file_path)
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        img = img.convert("RGBA")
        data = bytes(img.tobytes("raw", "RGBA"))
        stride = img.width * 4
        qimg = QImage(data, img.width, img.height, stride,
                      QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimg.copy())
    except Exception:
        return None


# ── Per-item widget ──────────────────────────────────────────────────────────

ITEM_HEIGHT = 72

_ITEM_STYLE = """
    QWidget { background: transparent; }
    QLabel  { background: transparent; }
"""

_STATUS_BTN_STYLE = (
    "color: {color}; font-size: 11px; font-weight: bold;"
    " min-width: 88px; background: transparent;"
)


class QueueItemWidget(QWidget):
    def __init__(self, entry: QueueEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setFixedHeight(ITEM_HEIGHT)
        self.setStyleSheet(_ITEM_STYLE)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Thumbnail
        self.thumb = QLabel()
        self.thumb.setFixedSize(60, 60)
        self.thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb.setStyleSheet(
            "background: #1e1e1e; border-radius: 4px; color: #555;"
        )
        layout.addWidget(self.thumb)

        # Info column
        info = QVBoxLayout()
        info.setSpacing(1)
        self.lbl_name = QLabel()
        self.lbl_name.setStyleSheet("color: #ddd; font-size: 13px;")
        self.lbl_name.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.lbl_name.setMaximumWidth(9999)

        self.lbl_size = QLabel()
        self.lbl_size.setStyleSheet("color: #777; font-size: 11px;")

        self.lbl_error = QLabel()
        self.lbl_error.setStyleSheet("color: #f44336; font-size: 10px;")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()

        info.addWidget(self.lbl_name)
        info.addWidget(self.lbl_size)
        info.addWidget(self.lbl_error)
        info.addStretch()
        layout.addLayout(info, 1)

        # Status label
        self.lbl_status = QLabel()
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.lbl_status)

    def refresh(self):
        e = self.entry
        self.setToolTip(e.file_path)

        # Thumbnail
        if e.thumbnail:
            scaled = e.thumbnail.scaled(
                58, 58,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.thumb.setPixmap(scaled)
        else:
            self.thumb.setText("?")

        # Name & size
        self.lbl_name.setText(os.path.basename(e.file_path))
        self.lbl_size.setText(_format_size(e.file_path))

        # Error
        if e.error_msg:
            self.lbl_error.setText(e.error_msg)
            self.lbl_error.show()
        else:
            self.lbl_error.hide()

        # Status
        icon  = STATUS_ICONS.get(e.status, "?")
        color = STATUS_COLORS.get(e.status, "#888")
        self.lbl_status.setText(f"{icon}  {e.status}")
        self.lbl_status.setStyleSheet(_STATUS_BTN_STYLE.format(color=color))


# ── Queue panel ──────────────────────────────────────────────────────────────

_PANEL_STYLE = """
    QListWidget {
        background: #1a1a1a;
        border: none;
        outline: none;
    }
    QListWidget::item {
        border-bottom: 1px solid #242424;
    }
    QListWidget::item:selected {
        background: #2d4a7a;
    }
    QListWidget::item:hover:!selected {
        background: #222222;
    }
"""

_BTN_STYLE = """
    QPushButton {
        background: #3c3f41; color: #ccc; border: 1px solid #555;
        padding: 2px 10px; border-radius: 3px; font-size: 11px;
    }
    QPushButton:hover  { background: #4c5052; }
    QPushButton:disabled { color: #555; background: #2c2c2c; border-color: #3a3a3a; }
"""


class QueuePanel(QWidget):
    """Left panel: scrollable file queue with drag-and-drop support."""

    selection_changed = pyqtSignal(object)   # QueueEntry | None
    files_added       = pyqtSignal(int)      # number of newly added files

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries: list[QueueEntry] = []
        self._build_ui()
        self.setAcceptDrops(True)

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QWidget()
        header.setFixedHeight(32)
        header.setStyleSheet("background: #252525; border-bottom: 1px solid #3a3a3a;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 0, 10, 0)
        lbl = QLabel("File Queue")
        lbl.setStyleSheet("color: #aaa; font-size: 12px; font-weight: bold;")
        self.lbl_count = QLabel("0 files")
        self.lbl_count.setStyleSheet("color: #666; font-size: 11px;")
        hl.addWidget(lbl)
        hl.addStretch()
        hl.addWidget(self.lbl_count)
        layout.addWidget(header)

        # Drop hint (shown when queue is empty)
        self.drop_hint = QLabel(
            "Drag && drop images or folders here\n"
            "or use  Add Files / Add Folder  above"
        )
        self.drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_hint.setStyleSheet(
            "color: #484848; font-size: 13px; background: #1a1a1a; padding: 40px;"
        )
        self.drop_hint.setWordWrap(True)
        layout.addWidget(self.drop_hint)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(_PANEL_STYLE)
        self.list_widget.setSpacing(0)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.currentItemChanged.connect(self._on_current_changed)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.hide()
        layout.addWidget(self.list_widget, 1)

        # Bottom button bar
        btn_bar = QWidget()
        btn_bar.setFixedHeight(36)
        btn_bar.setStyleSheet("background: #252525; border-top: 1px solid #3a3a3a;")
        bl = QHBoxLayout(btn_bar)
        bl.setContentsMargins(8, 4, 8, 4)
        bl.setSpacing(6)

        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.setEnabled(False)
        self.btn_remove.setStyleSheet(_BTN_STYLE)
        self.btn_remove.setToolTip(
            "Remove the highlighted image from the queue.\n"
            "This does NOT delete the file from disk."
        )
        self.btn_remove.clicked.connect(self._remove_selected)

        self.btn_retry = QPushButton("Retry Failed")
        self.btn_retry.setEnabled(False)
        self.btn_retry.setStyleSheet(_BTN_STYLE)
        self.btn_retry.setToolTip(
            "Reset all Failed items back to Pending\n"
            "so they are included in the next batch run."
        )
        self.btn_retry.clicked.connect(self._retry_failed)

        bl.addWidget(self.btn_remove)
        bl.addWidget(self.btn_retry)
        bl.addStretch()
        layout.addWidget(btn_bar)

    # ── Public API ───────────────────────────────────────────────────────────

    def add_file_paths(self, paths: list[str]) -> int:
        """Add files/folders to queue, skip duplicates and unsupported formats."""
        existing = {e.file_path for e in self.entries}
        added = 0

        for path in paths:
            if os.path.isfile(path):
                if self._maybe_add(path, existing):
                    existing.add(path)
                    added += 1
            elif os.path.isdir(path):
                for root, _dirs, files in os.walk(path):
                    for fname in files:
                        fp = os.path.join(root, fname)
                        if fp not in existing:
                            if self._maybe_add(fp, existing):
                                existing.add(fp)
                                added += 1

        self._refresh_ui()
        if added:
            self.files_added.emit(added)
        return added

    def clear_all(self):
        self.entries.clear()
        self.list_widget.clear()
        self._refresh_ui()
        self.selection_changed.emit(None)

    def update_item_status(self, index: int, status: str,
                           output_path: str = "", error_msg: str = ""):
        if not (0 <= index < len(self.entries)):
            return
        entry = self.entries[index]
        entry.status = status
        entry.output_path = output_path
        entry.error_msg = error_msg

        item = self.list_widget.item(index)
        if item:
            widget = self.list_widget.itemWidget(item)
            if isinstance(widget, QueueItemWidget):
                widget.refresh()

        # Enable Retry Failed button if any failures exist
        has_failed = any(e.status == "Failed" for e in self.entries)
        self.btn_retry.setEnabled(has_failed)

    def get_items_to_process(self, model_name: str,
                             overwrite: bool) -> list[tuple[int, str]]:
        """Return (index, path) for every item that should be processed.

        Logic per item:
          - Failed            → always include (retry)
          - No result yet for this model → always include
          - Has result + overwrite=True  → include (re-run)
          - Has result + overwrite=False → skip
        """
        result = []
        for i, e in enumerate(self.entries):
            if e.status == "Failed":
                result.append((i, e.file_path))
            elif model_name not in e.model_results:
                result.append((i, e.file_path))
            elif overwrite:
                result.append((i, e.file_path))
        return result

    def add_model_result(self, index: int, model_name: str, output_path: str):
        """Register a completed result for a specific model."""
        if 0 <= index < len(self.entries):
            self.entries[index].model_results[model_name] = output_path

    def current_entry(self) -> QueueEntry | None:
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.entries):
            return self.entries[row]
        return None

    # ── Private helpers ──────────────────────────────────────────────────────

    def _maybe_add(self, file_path: str, existing: set) -> bool:
        if file_path in existing:
            return False
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return False
        thumb = _load_thumbnail(file_path)
        entry = QueueEntry(file_path=file_path, thumbnail=thumb)
        self.entries.append(entry)
        self._append_list_item(entry)
        return True

    def _append_list_item(self, entry: QueueEntry):
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(QSize(200, ITEM_HEIGHT))
        widget = QueueItemWidget(entry)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def _refresh_ui(self):
        n = len(self.entries)
        self.lbl_count.setText(f"{n} file{'s' if n != 1 else ''}")
        if n:
            self.drop_hint.hide()
            self.list_widget.show()
        else:
            self.list_widget.hide()
            self.drop_hint.show()

    def _remove_selected(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        self.list_widget.takeItem(row)
        self.entries.pop(row)
        self._refresh_ui()
        if not self.list_widget.currentItem():
            self.btn_remove.setEnabled(False)
            self.selection_changed.emit(None)

    def _retry_failed(self):
        """Reset all Failed items back to Pending."""
        for i, entry in enumerate(self.entries):
            if entry.status == "Failed":
                self.update_item_status(i, "Pending")
        self.btn_retry.setEnabled(False)

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        row = self.list_widget.row(item)
        entry = self.entries[row]

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: #2b2b2b; color: #ccc; border: 1px solid #555; }
            QMenu::item:selected { background: #3a5a8a; }
        """)

        act_remove = menu.addAction("Remove from Queue")
        act_retry = None
        if entry.status == "Failed":
            menu.addSeparator()
            act_retry = menu.addAction("Retry This File")

        chosen = menu.exec(self.list_widget.mapToGlobal(pos))
        if chosen == act_remove:
            self.list_widget.setCurrentRow(row)
            self._remove_selected()
        elif act_retry and chosen == act_retry:
            self.update_item_status(row, "Pending")

    # ── Selection signal ─────────────────────────────────────────────────────

    def _on_current_changed(self, current, _previous):
        if current:
            row = self.list_widget.row(current)
            if 0 <= row < len(self.entries):
                self.btn_remove.setEnabled(True)
                self.selection_changed.emit(self.entries[row])
                return
        self.btn_remove.setEnabled(False)
        self.selection_changed.emit(None)

    # ── Drag and drop ────────────────────────────────────────────────────────

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.add_file_paths(paths)
            event.acceptProposedAction()
        else:
            event.ignore()
