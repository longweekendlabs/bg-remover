# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for BG Remover — single-file binary for Linux and Windows."""

import sys, os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

block_cipher = None

# rembg → pymatting calls importlib.metadata.version() — must bundle dist-info.
# Do NOT use collect_submodules("onnxruntime") — crashes Windows PyInstaller analysis.
# The pyinstaller-hooks-contrib hook handles onnxruntime correctly.
rembg_datas   = collect_data_files("rembg")
rembg_hidden  = collect_submodules("rembg")
scipy_datas   = collect_data_files("scipy")
scipy_hidden  = collect_submodules("scipy")
meta_datas    = (
    copy_metadata("pymatting") +
    copy_metadata("rembg")
)

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("icons/icon.png",                 "icons"),
        ("icons/icon.ico",                 "icons"),
        ("icons/LongWeekendLabs.logo.jpg", "icons"),
    ] + rembg_datas + scipy_datas + meta_datas,
    hiddenimports=rembg_hidden + scipy_hidden + [
        "PIL._tkinter_finder",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "notebook"],
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
