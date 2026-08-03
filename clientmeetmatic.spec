# -*- mode: python ; coding: utf-8 -*-
#
# Builds a one-file, windowed ClientMeetMatic.exe from the GUI entry point (run_gui.py).
#
# pywin32/PyInstaller footgun: COM automation via win32com.client.Dispatch (used in
# src/scheduler.py) needs win32timezone, pythoncom, and pywintypes bundled explicitly —
# PyInstaller's static import analysis doesn't see them since pywin32 loads them
# dynamically. Omitting them produces a working build that fails at runtime the first
# time an Outlook call is made, with "No module named 'win32timezone'".

block_cipher = None

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'win32timezone',
        'win32com.client',
        'pythoncom',
        'pywintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # sentry_sdk isn't a project dependency, but if it's present in the build environment
    # (e.g. pulled in globally by an unrelated package) a pyinstaller-hooks-contrib bug
    # crashes the build while analyzing it. Excluding it avoids that entirely; building
    # from a clean virtualenv with only requirements.txt installed avoids the problem too.
    excludes=['sentry_sdk'],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClientMeetMatic',
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
