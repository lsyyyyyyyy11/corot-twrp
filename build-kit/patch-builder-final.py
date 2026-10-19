#!/usr/bin/env python3
# 固化 build-slim11.py:注入"原厂模块宗替换"(slim22 验证过的做法)
B = '/root/build-slim11.py'
src = open(B).read()

# 1) 清掉之前临时的 DO_MIEV / DO_MODLOAD 钩子
import re
src = re.sub(r'import os as _os\nif _os\.path\.exists\("/root/DO_MIEV"\):.*?entries\.append\(\["lib/modules/modules\.load"[^\n]*\)\n', '', src, flags=re.S)

# 2) 在 out = bytearray() 之前注入模块宗替换
anchor = 'out = bytearray()'
inject = '''# ==== 原厂模块宗替换(slim22 固化,2026-10-19)====
import json as _json
_manifest = _json.load(open('/root/stock_modules/MANIFEST.json'))
entries = [e for e in entries if not e[0].startswith('lib/modules/')]
for _fn, _mode in sorted(_manifest.items()):
    _data = open('/root/stock_modules/' + _fn, 'rb').read()
    entries.append(['lib/modules/' + _fn, _mode, bytearray(_data)])

out = bytearray()'''
assert anchor in src
src = src.replace(anchor, inject, 1)
open(B, 'w').write(src)
print('builder 固化完成')
print('DO_MIEV 残留:', src.count('DO_MIEV'), '| 模块替换注入了:', 'stock_modules' in src)
