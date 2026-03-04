# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for BG Remover — single-file binary for Linux and Windows."""

import sys, os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# rembg ships ONNX runtime and model data that must be bundled
rembg_datas   = collect_data_files("rembg")
onnx_datas    = collect_data_files("onnxruntime")
hiddenimports = collect_submodules("rembg") + collect_submodules("onnxruntime")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("icons/icon.png",  "icons"),
        ("icons/icon.ico",  "icons"),
    ] + rembg_datas + onnx_datas,
    hiddenimports=hiddenimports + [
        "PIL._tkinter_finder",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "notebook"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="BGRemover",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icons/icon.ico" if sys.platform == "win32" else "icons/icon.png",
)
