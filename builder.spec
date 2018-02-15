# myspecfile.spec
# -*- mode: python -*-
from os import path 
import sys
site_packages = next(p for p in sys.path if 'site-packages' in p)
block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[(path.join(site_packages,"docx","templates"), "docx/templates")],

             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          a.binaries + [('ikona.ico', 'ikona.ico', 'DATA')], 
          name='Dzielnik',
          icon="ikona.ico",
          debug=False,
          strip=False,
          upx=True,
          console=False )