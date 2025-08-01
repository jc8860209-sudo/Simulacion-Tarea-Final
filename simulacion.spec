# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['simulacion.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'simpy',
        'pandas',
        'matplotlib',
        'seaborn',
        'tkinter',
        'matplotlib.backends.backend_tkagg',
        'numpy'  # Requerido por pandas y matplotlib
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='simulacion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Cambiar a True si necesitas ver la consola para depuración
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Agrega la ruta a un archivo .ico si deseas un icono personalizado
)