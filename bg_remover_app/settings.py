"""
settings.py — App-wide constants: models, labels, sizes, and supported file types.
"""

MODELS = {
    "birefnet-portrait":  "Portrait & character sprites — best quality",
    "birefnet-general":   "General purpose — best quality",
    "isnet-general-use":  "Detailed edges",
    "u2net_human_seg":    "Human figures — faster",
    "u2net":              "General purpose — faster",
    "silueta":            "Simple subjects — fastest",
}

# Short labels shown on the model toggle buttons in the toolbar
MODEL_LABELS = {
    "birefnet-portrait":  "BiRefNet Portrait ★",
    "birefnet-general":   "BiRefNet General",
    "isnet-general-use":  "ISNet",
    "u2net_human_seg":    "U2Net Human",
    "u2net":              "U2Net",
    "silueta":            "Silueta",
}

DEFAULT_MODEL = "birefnet-general"

# Approximate ONNX model download sizes in MB (one-time, stored in ~/.u2net/)
MODEL_SIZES_MB = {
    "birefnet-portrait":  175,
    "birefnet-general":   175,
    "isnet-general-use":  100,
    "u2net_human_seg":    176,
    "u2net":              176,
    "silueta":             43,
}

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
