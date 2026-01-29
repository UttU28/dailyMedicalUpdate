# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Collect tkinterdnd2 data files and binaries
tkinterdnd2_datas = collect_data_files('tkinterdnd2')
tkinterdnd2_binaries = collect_dynamic_libs('tkinterdnd2')

# Include .env file if it exists
env_file = '.env'
env_datas = []
if os.path.exists(env_file):
    env_datas = [(env_file, '.')]  # Include .env in root of bundle

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=tkinterdnd2_binaries,
    datas=tkinterdnd2_datas + env_datas,
    hiddenimports=['tkinterdnd2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
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
)
