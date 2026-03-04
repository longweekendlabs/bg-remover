# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for BG Remover — single-file binary for Linux and Windows."""

import sys, os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# rembg ships model data that must be bundled.
# Do NOT use collect_submodules("onnxruntime") — it crashes on Windows during
# PyInstaller analysis. The pyinstaller-hooks-contrib hook handles it correctly.
rembg_datas   = collect_data_files("rembg")
rembg_hidden  = collect_submodules("rembg")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("icons/icon.png",  "icons"),
        ("icons/icon.ico",  "icons"),
    ] + rembg_datas,
    hiddenimports=rembg_hidden + [
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
