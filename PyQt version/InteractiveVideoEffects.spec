# InteractiveVideoEffects.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'mediapipe', 
        'cv2', 
        'PyQt5', 
        'numpy', 
        'pyarrow.compat', 
        'psycopg2', 
        'django.contrib.postgres.forms'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 
            'unittest', 
            'email', 
            'html', 
            'http', 
            'xml', 
            'logging', 
            'multiprocessing', 
            'distutils', 
            'pydoc'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='InteractiveVideoEffects',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='InteractiveVideoEffects',
)
