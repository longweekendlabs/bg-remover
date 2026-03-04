"""
main_window.py — MainWindow: assembles toolbar, queue panel, and preview panel.
"""

import os
import shutil

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar,
    QSplitter, QFileDialog, QMessageBox, QLineEdit, QCheckBox,
    QMenuBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from queue_panel import QueuePanel
from preview_panel import PreviewPanel
from processor import ProcessorThread
from version import __version__, __app_name__
from settings import MODELS, MODEL_LABELS, MODEL_SIZES_MB, DEFAULT_MODEL, SUPPORTED_EXTENSIONS
from about_dialog import AboutDialog


# ── App-local cache (deleted on exit) ────────────────────────────────────────

_APP_DIR   = os.path.dirname(os.path.abspath(__file__))
_CACHE_DIR = os.path.join(_APP_DIR, ".cache")


# ── Shared style snippets ────────────────────────────────────────────────────

_TOOLBAR_BTN = """
    QPushButton {{
        background: #3c3f41; color: #ccc;
        border: 1px solid #555; padding: 4px 12px;
        border-radius: 4px; font-size: 12px;
    }}
    QPushButton:hover {{ background: #4c5052; }}
    QPushButton:disabled {{ color: #555; background: #2c2c2c; border-color: #3a3a3a; }}
"""

_MODEL_BTN_ON = """
    QPushButton {
        background: #2d5a9f; color: #fff;
        border: 1px solid #4a7abf; padding: 3px 10px;
        border-radius: 4px; font-size: 11px; font-weight: bold;
    }
"""
_MODEL_BTN_OFF = """
    QPushButton {
        background: #3c3f41; color: #999;
        border: 1px solid #555; padding: 3px 10px;
        border-radius: 4px; font-size: 11px;
    }
    QPushButton:hover { background: #4c5052; color: #ddd; }
"""

_START_BTN = """
    QPushButton {
        background: #1e6b35; color: #eee;
        border: 1px solid #2d9448; padding: 5px 18px;
        border-radius: 4px; font-size: 13px;
    }
    QPushButton:hover    { background: #28873f; }
    QPushButton:disabled { background: #182d1f; color: #555; border-color: #2a3a2e; }
"""

_STOP_BTN = """
    QPushButton {
        background: #6b1e1e; color: #eee;
        border: 1px solid #944; padding: 5px 18px;
        border-radius: 4px; font-size: 13px;
    }
    QPushButton:hover    { background: #872828; }
    QPushButton:disabled { background: #2d1a1a; color: #555; border-color: #3a2424; }
"""

_PREVIEW_BTN = """
    QPushButton {
        background: #1e4a6b; color: #eee;
        border: 1px solid #2d6a9f; padding: 5px 14px;
        border-radius: 4px; font-size: 13px;
    }
    QPushButton:hover    { background: #285a82; }
    QPushButton:disabled { background: #182030; color: #555; border-color: #223040; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{__app_name__} v{__version__}")
        self.setMinimumSize(900, 600)
        self.resize(1280, 760)

        self._output_folder    = ""
        self._processor_thread = None
        self._preview_thread   = None
        self._processing       = False
        self._previewing       = False
        self._total            = 0
        self._completed        = 0
        self._current_model_id = DEFAULT_MODEL
        self._active_model_id  = DEFAULT_MODEL
        self._model_btns: dict[str, QPushButton] = {}

        self._apply_dark_theme()
        self._build_ui()
        self._build_menubar()

    # ── Menu bar ─────────────────────────────────────────────────────────────

    def _build_menubar(self):
        mb = self.menuBar()
        mb.setStyleSheet("""
            QMenuBar {
                background: #1e1e1e; color: #ccc; font-size: 12px;
                border-bottom: 1px solid #333;
            }
            QMenuBar::item:selected { background: #2d5a9f; color: #fff; }
            QMenu {
                background: #2b2b2b; color: #ccc;
                border: 1px solid #555;
            }
            QMenu::item:selected { background: #3a5a8a; }
            QMenu::separator { height: 1px; background: #444; margin: 3px 8px; }
        """)

        # Help menu
        help_menu = mb.addMenu("Help")

        act_about = QAction(f"About {__app_name__}", self)
        act_about.setStatusTip("Show application information")
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    # ── Theme ────────────────────────────────────────────────────────────────

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #1a1a1a; color: #ccc; }
            QToolTip { background: #2b2b2b; color: #ddd; border: 1px solid #555; }
            QScrollBar:vertical {
                background: #1a1a1a; width: 10px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #444; border-radius: 5px; min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        main.addWidget(self._create_toolbar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #333333; width: 2px; }")

        self.queue_panel   = QueuePanel()
        self.preview_panel = PreviewPanel()
        self.queue_panel.selection_changed.connect(self._on_selection_changed)

        splitter.addWidget(self.queue_panel)
        splitter.addWidget(self.preview_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([420, 660])

        main.addWidget(splitter, 1)
        main.addWidget(self._create_bottom_bar())

    def _create_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(108)
        bar.setStyleSheet("""
            QWidget   { background: #252525; border-bottom: 1px solid #3a3a3a; }
            QLabel    { color: #aaa; font-size: 12px; background: transparent; }
            QLineEdit {
                background: #3c3f41; color: #ccc; border: 1px solid #555;
                padding: 3px 6px; border-radius: 4px;
            }
            QCheckBox { color: #aaa; spacing: 5px; }
            QCheckBox::indicator {
                width: 14px; height: 14px;
                border: 1px solid #666; border-radius: 3px; background: #3c3f41;
            }
            QCheckBox::indicator:checked { background: #2d6a9f; border-color: #4a8abf; }
        """)

        vl = QVBoxLayout(bar)
        vl.setContentsMargins(10, 6, 10, 6)
        vl.setSpacing(5)

        # ── Row 1: action buttons ────────────────────────────────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(6)

        btn_add_files  = QPushButton("＋  Add Files")
        btn_add_folder = QPushButton("＋  Add Folder")
        btn_clear_all  = QPushButton("✕  Clear All")

        btn_add_files.setToolTip(
            "Open a file picker to select one or more images.\n"
            "Supported formats: PNG, JPG, JPEG, WEBP"
        )
        btn_add_folder.setToolTip(
            "Add all supported images from a folder and its subfolders.\n"
            "Duplicates are automatically skipped."
        )
        btn_clear_all.setToolTip(
            "Remove every image from the queue.\n"
            "This does NOT delete any files from disk."
        )

        for btn in (btn_add_files, btn_add_folder, btn_clear_all):
            btn.setStyleSheet(_TOOLBAR_BTN)

        btn_add_files .clicked.connect(self._add_files)
        btn_add_folder.clicked.connect(self._add_folder)
        btn_clear_all .clicked.connect(self._clear_all)

        row1.addWidget(btn_add_files)
        row1.addWidget(btn_add_folder)
        row1.addWidget(btn_clear_all)
        row1.addStretch()
        vl.addLayout(row1)

        # ── Row 2: model toggle buttons ──────────────────────────────────────
        row2 = QHBoxLayout()
        row2.setSpacing(4)

        lbl_model = QLabel("Model:")
        lbl_model.setStyleSheet("color: #777; font-size: 11px;")
        row2.addWidget(lbl_model)

        for model_id, desc in MODELS.items():
            label = MODEL_LABELS[model_id]
            btn   = QPushButton(label)
            btn.setFixedHeight(26)
            size_mb = MODEL_SIZES_MB.get(model_id, 150)
            btn.setToolTip(f"{desc}\n~{size_mb} MB download (one-time, stored in ~/.u2net/)")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            is_default = (model_id == DEFAULT_MODEL)
            btn.setStyleSheet(_MODEL_BTN_ON if is_default else _MODEL_BTN_OFF)
            btn.clicked.connect(
                lambda _checked, mid=model_id: self._on_model_selected(mid)
            )
            self._model_btns[model_id] = btn
            row2.addWidget(btn)

        row2.addStretch()
        vl.addLayout(row2)

        # ── Row 3: output controls ───────────────────────────────────────────
        row3 = QHBoxLayout()
        row3.setSpacing(8)

        row3.addWidget(QLabel("Output:"))

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText(
            "Default: same folder as input images  /  output/{model}/  subfolder"
        )
        self.output_edit.setReadOnly(True)
        row3.addWidget(self.output_edit, 1)

        btn_browse = QPushButton("Browse…")
        btn_browse.setStyleSheet(_TOOLBAR_BTN)
        btn_browse.setFixedWidth(80)
        btn_browse.setToolTip(
            "Choose a custom output folder.\n"
            "Default: a subfolder called output/{model}/ next to each input image."
        )
        btn_browse.clicked.connect(self._browse_output)
        row3.addWidget(btn_browse)

        row3.addSpacing(10)
        self.overwrite_check = QCheckBox("Overwrite existing")
        self.overwrite_check.setChecked(True)
        self.overwrite_check.setToolTip(
            "If checked, images are re-processed even if an output file\n"
            "already exists for the selected model.\n"
            "If unchecked, existing outputs are skipped."
        )
        row3.addWidget(self.overwrite_check)

        row3.addStretch()
        vl.addLayout(row3)

        return bar

    def _create_bottom_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(50)
        bar.setStyleSheet("""
            QWidget      { background: #222222; border-top: 1px solid #3a3a3a; }
            QLabel        { color: #aaa; font-size: 12px; background: transparent; }
            QProgressBar  {
                background: #1a1a1a; border: 1px solid #444;
                border-radius: 4px; text-align: center; color: #ccc;
                min-height: 18px;
            }
            QProgressBar::chunk { background: #2d6a9f; border-radius: 3px; }
        """)

        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10, 7, 10, 7)
        bl.setSpacing(10)

        self.btn_preview = QPushButton("⬛  Preview Selected")
        self.btn_preview.setStyleSheet(_PREVIEW_BTN)
        self.btn_preview.setMinimumWidth(150)
        self.btn_preview.setEnabled(False)
        self.btn_preview.setToolTip(
            "Process only the selected image with the active AI model\n"
            "and show the before/after result instantly.\n"
            "The file is NOT saved to the output folder — use Start Processing for that."
        )
        self.btn_preview.clicked.connect(self._run_preview_for_selected)

        self.btn_start = QPushButton("▶   Start Processing")
        self.btn_start.setStyleSheet(_START_BTN)
        self.btn_start.setMinimumWidth(160)
        self.btn_start.setToolTip(
            "Begin removing backgrounds from all queued images\n"
            "using the currently selected AI model.\n"
            "Output PNGs are saved to the configured output folder."
        )
        self.btn_start.clicked.connect(self._start_processing)

        self.btn_stop = QPushButton("■   Stop")
        self.btn_stop.setStyleSheet(_STOP_BTN)
        self.btn_stop.setMinimumWidth(100)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setToolTip(
            "Stop the current batch after the image currently being\n"
            "processed finishes. Already-completed images are kept."
        )
        self.btn_stop.clicked.connect(self._stop_processing)

        self.progress_label = QLabel("Ready")
        self.progress_label.setMinimumWidth(140)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")

        bl.addWidget(self.btn_preview)
        bl.addSpacing(6)
        bl.addWidget(self.btn_start)
        bl.addWidget(self.btn_stop)
        bl.addSpacing(8)
        bl.addWidget(self.progress_label)
        bl.addWidget(self.progress_bar, 1)

        return bar

    # ── Model download helpers ────────────────────────────────────────────────

    def _is_model_cached(self, model_id: str) -> bool:
        u2net_home = os.environ.get(
            "U2NET_HOME", os.path.join(os.path.expanduser("~"), ".u2net")
        )
        return os.path.exists(os.path.join(u2net_home, f"{model_id}.onnx"))

    def _confirm_model_download(self, model_id: str) -> bool:
        """Return True if the model is already cached or the user confirms the download."""
        if self._is_model_cached(model_id):
            return True
        size_mb = MODEL_SIZES_MB.get(model_id, 150)
        label   = MODEL_LABELS.get(model_id, model_id)
        reply   = QMessageBox.question(
            self,
            "Model Download Required",
            f"<b>{label}</b> has not been downloaded yet.<br><br>"
            f"&nbsp;&nbsp;Download size : <b>~{size_mb} MB</b><br>"
            f"&nbsp;&nbsp;Saved to&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <tt>~/.u2net/{model_id}.onnx</tt><br><br>"
            "This is a one-time download per model — the app works fully offline afterwards.<br>"
            "An internet connection is required. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        return reply == QMessageBox.StandardButton.Yes

    # ── Model toggle ─────────────────────────────────────────────────────────

    def _on_model_selected(self, model_id: str):
        """Called when a model button is clicked. Updates selection state only."""
        self._active_model_id = model_id

        for mid, btn in self._model_btns.items():
            btn.setStyleSheet(_MODEL_BTN_ON if mid == model_id else _MODEL_BTN_OFF)

    # ── Toolbar actions ──────────────────────────────────────────────────────

    def _add_files(self):
        exts = " ".join(f"*{e}" for e in sorted(SUPPORTED_EXTENSIONS))
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            f"Images ({exts});;All Files (*)",
        )
        if paths:
            self.queue_panel.add_file_paths(paths)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.queue_panel.add_file_paths([folder])

    def _clear_all(self):
        if self._processing:
            return
        self.queue_panel.clear_all()
        self.preview_panel.clear_preview()
        self.progress_label.setText("Ready")
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 100)

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self._output_folder = folder
            self.output_edit.setText(folder)

    # ── Batch processing ─────────────────────────────────────────────────────

    def _start_processing(self):
        if self._processing:
            return

        # Cancel any running preview so batch can start immediately
        if self._previewing:
            if self._preview_thread and self._preview_thread.isRunning():
                self._preview_thread.stop()
                self._preview_thread.wait(2000)
            self._previewing = False
            self.btn_stop.setEnabled(False)

        model_id  = self._active_model_id
        overwrite = self.overwrite_check.isChecked()

        items = self.queue_panel.get_items_to_process(model_id, overwrite)
        if not items:
            QMessageBox.information(
                self, "Nothing to Process",
                f"All images already have a cached result for  '{model_id}'.\n\n"
                "Enable  Overwrite existing,  switch to a different model,\n"
                "or add new images.",
            )
            return

        if not self._confirm_model_download(model_id):
            return

        for idx, _ in items:
            self.queue_panel.update_item_status(idx, "Pending")

        self._current_model_id = model_id
        self._total     = len(items)
        self._completed = 0
        self._succeeded = 0
        self._failed    = 0

        self.progress_bar.setRange(0, self._total)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"0 / {self._total}")

        self._processing = True
        self.btn_start.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self._processor_thread = ProcessorThread(
            items         = items,
            model_name    = model_id,
            output_folder = self._output_folder,
            overwrite     = overwrite,
        )
        self._processor_thread.item_started.connect(self._on_item_started)
        self._processor_thread.item_done   .connect(self._on_item_done)
        self._processor_thread.item_failed .connect(self._on_item_failed)
        self._processor_thread.all_done    .connect(self._on_all_done)
        self._processor_thread.start()

    def _stop_processing(self):
        for thread in (self._processor_thread, self._preview_thread):
            if thread and thread.isRunning():
                thread.stop()
        self.btn_stop.setEnabled(False)
        self.progress_label.setText("Stopping…")

    # ── Batch signal handlers ────────────────────────────────────────────────

    def _on_item_started(self, queue_idx: int):
        self.queue_panel.update_item_status(queue_idx, "Processing")

    def _on_item_done(self, queue_idx: int, output_path: str):
        self.queue_panel.add_model_result(queue_idx, self._current_model_id, output_path)
        self.queue_panel.update_item_status(queue_idx, "Done", output_path=output_path)
        self._completed += 1
        self._succeeded += 1
        self.progress_bar.setValue(self._completed)
        self.progress_label.setText(f"{self._completed} / {self._total}")

        entry = self.queue_panel.current_entry()
        if entry and entry.output_path == output_path:
            self.preview_panel.update_for_entry(entry.file_path, entry.model_results)

    def _on_item_failed(self, queue_idx: int, error_msg: str):
        self.queue_panel.update_item_status(queue_idx, "Failed", error_msg=error_msg)
        self._completed += 1
        self._failed    += 1
        self.progress_bar.setValue(self._completed)
        self.progress_label.setText(f"{self._completed} / {self._total}")

    def _on_all_done(self, succeeded: int, failed: int):
        self._processing = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_preview.setEnabled(self.queue_panel.current_entry() is not None)

        if failed == 0:
            self.progress_label.setText(f"Done — {succeeded} processed")
        else:
            self.progress_label.setText(f"Done — {succeeded} ✓   {failed} ✗")

        symbol = "✓" if failed == 0 else "⚠"
        QMessageBox.information(
            self,
            f"{symbol}  Batch Complete",
            f"Processing finished.\n\n"
            f"  ✓  Succeeded : {succeeded}\n"
            f"  ✗  Failed    : {failed}",
        )

    # ── Single-image preview ─────────────────────────────────────────────────

    def _run_preview_for_selected(self):
        """Process just the selected image with the active model.

        Uses the app-local .cache/ folder (deleted on exit).
        If a cached result already exists for this model, shows it instantly.
        """
        if self._processing or self._previewing:
            return

        entry = self.queue_panel.current_entry()
        if not entry:
            return

        model_id  = self._active_model_id
        overwrite = self.overwrite_check.isChecked()

        # Cache hit — show instantly without re-processing
        if not overwrite and model_id in entry.model_results:
            self.preview_panel.update_for_entry(entry.file_path, entry.model_results)
            self.progress_label.setText(f"Cached  ·  {model_id}")
            return

        if not self._confirm_model_download(model_id):
            return

        entry_idx = self.queue_panel.entries.index(entry)

        self._previewing       = True
        self._current_model_id = model_id
        self.btn_start.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_label.setText(f"Previewing  ·  {model_id}…")
        self.preview_panel.show_placeholder(f"Running {model_id}…\nThis may take a moment on first use.")

        self._preview_thread = ProcessorThread(
            items         = [(entry_idx, entry.file_path)],
            model_name    = model_id,
            output_folder = _CACHE_DIR,   # preview results go to local cache
            overwrite     = True,
        )
        self._preview_thread.item_done  .connect(self._on_preview_done)
        self._preview_thread.item_failed.connect(self._on_preview_failed)
        self._preview_thread.all_done   .connect(self._on_preview_all_done)
        self._preview_thread.start()

    def _on_preview_done(self, queue_idx: int, output_path: str):
        self.queue_panel.add_model_result(queue_idx, self._current_model_id, output_path)
        # Don't mark status as Done for a preview — item stays Pending for batch
        entry = self.queue_panel.entries[queue_idx]
        self.preview_panel.update_for_entry(entry.file_path, entry.model_results)

    def _on_preview_failed(self, queue_idx: int, error_msg: str):
        self.preview_panel.show_placeholder(f"Preview failed:\n{error_msg}")

    def _on_preview_all_done(self, _succeeded: int, failed: int):
        self._previewing = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_preview.setEnabled(self.queue_panel.current_entry() is not None)
        if failed == 0:
            self.progress_label.setText(f"Preview ready  ·  {self._current_model_id}")
        else:
            self.progress_label.setText("Preview failed")

    # ── Queue selection → preview ────────────────────────────────────────────

    def _on_selection_changed(self, entry):
        if entry is None:
            self.preview_panel.clear_preview()
            self.btn_preview.setEnabled(False)
            return

        self.btn_preview.setEnabled(not self._processing and not self._previewing)

        if entry.model_results:
            self.preview_panel.update_for_entry(entry.file_path, entry.model_results)
        elif entry.status == "Failed":
            self.preview_panel.show_placeholder(
                f"Processing failed\n\n{entry.error_msg or 'Unknown error'}"
            )
        elif entry.status == "Processing":
            self.preview_panel.show_placeholder("Processing…")
        else:
            self.preview_panel.show_placeholder(
                "Click  Preview Selected  to test the active model\n"
                "or  Start Processing  to run the full batch."
            )

    # ── App lifecycle ────────────────────────────────────────────────────────

    def closeEvent(self, event):
        # Stop any running threads cleanly
        for thread in (self._processor_thread, self._preview_thread):
            if thread and thread.isRunning():
                thread.stop()
                thread.wait(3000)

        # Delete the local preview cache
        if os.path.exists(_CACHE_DIR):
            shutil.rmtree(_CACHE_DIR, ignore_errors=True)

        event.accept()
