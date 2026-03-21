# -*- mode: python ; coding: utf-8 -*-
import os

BASE = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(BASE, 'main.py')],
    pathex=[BASE],
    binaries=[],
    datas=[
        (os.path.join(BASE, 'data'),   'data'),
        (os.path.join(BASE, 'assets'), 'assets'),
        # 捆绑系统中文字体，供 font_manager 在打包环境下使用
        ('/System/Library/Fonts/STHeiti Light.ttc', 'system_fonts'),
    ],
    hiddenimports=['pygame', 'pygame.font', 'pygame.mixer', 'numpy', 'numpy.core', 'numpy.core._multiarray_umath'],
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
    [],
    exclude_binaries=True,
    name='打字大挑战-乐乐',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,   # 不显示终端窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='打字大挑战-乐乐',
)

app = BUNDLE(
    coll,
    name='打字大挑战-乐乐.app',
    icon=None,
    bundle_identifier='com.lele.typing-game',
    info_plist={
        'CFBundleDisplayName': '打字大挑战-乐乐',
        'CFBundleName':        '打字大挑战-乐乐',
        'CFBundleVersion':     '1.1.0',
        'CFBundleShortVersionString': '1.1.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
