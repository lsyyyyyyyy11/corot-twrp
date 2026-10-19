#!/usr/bin/env python3
import os

BASE = '/root/build_rd.cpio'
OUT  = '/root/slim11.cpio'
FRESH_LIBMINUI = '/root/fresh_libminuitwrp.so'
DROP = {
    'system/bin/keystore2',
    'system/bin/busybox',
    'system/bin/magiskboot',
    'system/bin/bash',
    'system/bin/nano',
    'system/bin/update_engine_sideload',
}
ADD_LIB_DIRS = ['/root/libs64', '/root/libs64/chain']
RC_NAME = 'init.recovery.mt6985.rc'
RC_ADD = b"\non init\n    write /sys/fs/selinux/enforce 0\n"
UIXML_OLD = b'<resolution width="1080" height="1920"/>'
UIXML_NEW = b'<resolution width="1220" height="2712"/>'
assert len(UIXML_OLD) == len(UIXML_NEW)

raw = open(BASE, 'rb').read()
entries = []
pos = 0
while pos < len(raw) - 110:
    if raw[pos:pos+6] not in (b'070701', b'070702'):
        break
    def f(o, n=8): return int(raw[pos+o:pos+o+n], 16)
    ns, fs = f(94), f(54)
    mode = f(14)
    name = raw[pos+110:pos+110+ns-1].decode('utf-8', 'replace')
    ds = pos + ((110+ns+3) & ~3)
    data = raw[ds:ds+fs]
    pos = ds + ((fs+3) & ~3)
    if name == 'TRAILER!!!':
        continue
    if name in DROP:
        continue
    if name == RC_NAME:
        data = data + RC_ADD
    if name == 'system/lib64/libminuitwrp.so':
        data = open(FRESH_LIBMINUI, 'rb').read()
        mode = 0o100755
    if False and UIXML_OLD in data:
        data = data.replace(UIXML_OLD, UIXML_NEW)
    entries.append([name, mode, bytearray(data)])

existing = {e[0] for e in entries}
added = 0
for d in ADD_LIB_DIRS:
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.so'):
            continue
        path = 'system/lib64/' + fn
        if path in existing:
            continue
        entries.append([path, 0o100644, bytearray(open(os.path.join(d, fn), 'rb').read())])
        added += 1
if 'system/etc/additional.fstab' not in existing:
    entries.append(['system/etc/additional.fstab', 0o100644, bytearray()])

# ==== 原厂模块宗替换(slim22 固化,2026-10-19)====
import json as _json
_manifest = _json.load(open('/root/stock_modules/MANIFEST.json'))
entries = [e for e in entries if not e[0].startswith('lib/modules/')]
for _fn, _mode in sorted(_manifest.items()):
    _data = open('/root/stock_modules/' + _fn, 'rb').read()
    entries.append(['lib/modules/' + _fn, _mode, bytearray(_data)])

out = bytearray()
ino = 100
for name, mode, data in entries:
    nm = name.encode() + b'\0'
    hdr = bytearray(110)
    hdr[0:6] = b'070701'
    vals = [ino, mode, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(nm), 0]
    for i, v in enumerate(vals):
        hdr[6+8*i:6+8*(i+1)] = b'%08X' % v
    ino += 1
    out += hdr + nm
    out += b'\0' * ((4 - len(out) % 4) % 4)
    out += data
    out += b'\0' * ((4 - len(out) % 4) % 4)
tr = bytearray(110); tr[0:6] = b'070701'
nm = b'TRAILER!!!\0'
vals = [999999, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, len(nm), 0]
for i, v in enumerate(vals):
    tr[6+8*i:6+8*(i+1)] = b'%08X' % v
out += tr + nm
out += b'\0' * ((4 - len(out) % 4) % 4)
open(OUT, 'wb').write(out)

byname = {e[0]: e[2] for e in entries}
print('libminuitwrp 大小:', len(byname['system/lib64/libminuitwrp.so']))
print('libminuitwrp TWRPDBG:', b'TWRPDBG ev_init' in byname['system/lib64/libminuitwrp.so'], b'TWRPDBG ev_get' in byname['system/lib64/libminuitwrp.so'])
print('recovery 含 selinux 补丁:', b'/sys/fs/selinux/enforce' in byname['system/bin/recovery'])
print('additional.fstab:', 'system/etc/additional.fstab' in byname)
print('rc write line:', RC_ADD in byname[RC_NAME])
print('entries:', len(entries), '| cpio:', len(out))
