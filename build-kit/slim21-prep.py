#!/usr/bin/env python3
# ==== slim21 一次性准备脚本(在 VM 上以 root 跑)====
# 1) partition.cpp 加 mifs 识别
# 2) twrp.flags 的 /data 改成 mifs
# 3) 更新 build-slim11.py:恢复 TA、新增删减项(keystore2/busybox/magiskboot/bash/nano)
import re, os

REC = '/root/twrp/bootable/recovery/partition.cpp'
src = open(REC).read()
if 'File_System == "mifs"' not in src:
    old = 'File_System == "f2fs" ||'
    assert old in src, 'Is_File_System 模式未命中'
    src = src.replace(old, old + '\n\t\tFile_System == "mifs" ||', 1)
    open(REC, 'w').write(src)
    print('[1] partition.cpp: mifs 已加入')
else:
    print('[1] partition.cpp: 已有 mifs')

FLAGS = '/root/twrp/device/xiaomi/corot/recovery/root/system/etc/twrp.flags'
f = open(FLAGS).read()
f2 = re.sub(r'(/data\s+)f2fs(\s+/dev/block/by-name/userdata)', r'\1mifs\2', f)
if f2 != f:
    open(FLAGS, 'w').write(f2)
    print('[2] twrp.flags: /data 类型 f2fs -> mifs')
else:
    print('[2] twrp.flags: /data 已是 mifs 或未匹配:', '/data' in f)

B = '/root/build-slim11.py'
b = open(B).read()
# 恢复 TA(从 DROP 里移除)
b = b.replace("    'vendor/mitee/ta/a734eed9-d6a1-4244-aa507c99719e7b7f.ta',\n", '')
# 新增瘦身项
add = """    'system/bin/keystore2',
    'system/bin/busybox',
    'system/bin/magiskboot',
    'system/bin/bash',
    'system/bin/nano',
"""
if "'system/bin/keystore2'" not in b:
    b = b.replace("DROP = {\n", "DROP = {\n" + add, 1)
open(B, 'w').write(b)
print('[3] build-slim11.py: TA 恢复 + 5 项新增删除')

# 校验
print('[check] DROP 现今 =')
m = re.search(r'DROP = \{(.*?)\}', b, re.S)
print(m.group(1).strip() if m else '???')

# ==== 4) 移除 twrp.cpp 的 2 秒循环日志线程(每 2 秒 fork+system() 的风扇式开销 + 无界写)====
T = '/root/twrp/bootable/recovery/twrp.cpp'
t = open(T).read()
removed = 0
while True:
    i = t.find('twrp_live_log.txt')
    if i < 0:
        break
    j = t.find('std::thread', max(0, i - 800))
    k = t.find('});', i)
    if j < 0 or k < 0:
        break
    t = t[:j] + t[k + 3:]
    removed += 1
    if removed > 3:
        break
if removed:
    open(T, 'w').write(t)
print('[4] twrp.cpp 直播日志线程移除:', removed, '处')

