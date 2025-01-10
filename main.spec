# -*- mode: python ; coding: utf-8 -*-
import os

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ting.wav', '.'),
        ('saved_words.txt', '.'),
        ('icon.ico', '.'),
        ('settings.json', '.')
    ],
    hiddenimports=['win32com.client'],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=os.path.abspath('icon.ico'),
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
