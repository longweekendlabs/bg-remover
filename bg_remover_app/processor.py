"""
processor.py — Background QThread that runs rembg to remove image backgrounds.
"""

import os

from PyQt6.QtCore import QThread, pyqtSignal
from PIL import Image


class ProcessorThread(QThread):
    """Background thread that removes image backgrounds using rembg.

    Signals are emitted from this thread and automatically queued to the
    main thread via Qt's cross-thread signal mechanism.
    """

    model_loading = pyqtSignal(str, int)   # model_name, size_mb (download starting)
    model_ready   = pyqtSignal(str)        # model_name (session created, ready to process)
    item_started  = pyqtSignal(int)        # queue_index
    item_done     = pyqtSignal(int, str)   # queue_index, output_path
    item_failed   = pyqtSignal(int, str)   # queue_index, error_message
    all_done      = pyqtSignal(int, int)   # succeeded_count, failed_count

    def __init__(self, items, model_name, output_folder, overwrite, parent=None):
        """
        Args:
            items: list of (queue_index, file_path) tuples
            model_name: rembg model id string
            output_folder: explicit output directory, or "" for auto (input/output/)
            overwrite: if False, skip files that already exist at destination
        """
        super().__init__(parent)
        self.items = items
        self.model_name = model_name
        self.output_folder = output_folder
        self.overwrite = overwrite
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        from rembg import remove, new_session
        from settings import MODEL_SIZES_MB

        # Signal that we're about to load/download the model.
        # The UI will show an indeterminate progress bar during this phase.
        size_mb = MODEL_SIZES_MB.get(self.model_name, 150)
        self.model_loading.emit(self.model_name, size_mb)

        # Create session once and reuse across the batch for performance.
        # On first run, this triggers the model download (~170 MB).
        try:
            session = new_session(self.model_name)
        except Exception as exc:
            for queue_idx, _ in self.items:
                self.item_failed.emit(queue_idx, f"Failed to load model: {exc}")
            self.all_done.emit(0, len(self.items))
            return

        self.model_ready.emit(self.model_name)

        succeeded = 0
        failed = 0

        for queue_idx, file_path in self.items:
            if self._stop_flag:
                break

            self.item_started.emit(queue_idx)

            try:
                img = Image.open(file_path)

                # Determine output directory — each model gets its own subfolder
                if self.output_folder:
                    out_dir = self.output_folder
                else:
                    out_dir = os.path.join(os.path.dirname(file_path), "output")

                model_dir = os.path.join(out_dir, self.model_name)
                os.makedirs(model_dir, exist_ok=True)

                stem = os.path.splitext(os.path.basename(file_path))[0]
                out_path = os.path.join(model_dir, stem + ".png")

                if not self.overwrite and os.path.exists(out_path):
                    self.item_done.emit(queue_idx, out_path)
                    succeeded += 1
                    continue

                result = remove(img, session=session)
                result.save(out_path)

                self.item_done.emit(queue_idx, out_path)
                succeeded += 1

            except Exception as exc:
                self.item_failed.emit(queue_idx, str(exc))
                failed += 1

        self.all_done.emit(succeeded, failed)
