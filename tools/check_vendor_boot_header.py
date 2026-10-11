#!/usr/bin/env python3
"""Check that the tree's mkbootimg config reproduces a real vendor_boot image header.
Usage: check_vendor_boot_header.py <vendor_boot.img> [TREE_DIR]"""
import os, re, struct, sys
IMG = sys.argv[1]
TREE = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else ".")
bc = open(os.path.join(TREE, "BoardConfig.mk")).read()
def val(k):
    m = re.search(r"^%s\s*:?=\s*(.+)$" % re.escape(k), bc, re.M)
    if not m: return None
    v = m.group(1).split("#")[0].strip()
    return int(v, 16) if v.startswith("0x") else (int(v) if v.isdigit() else v)
BASE = val("BOARD_KERNEL_BASE")
d = open(IMG, "rb").read()
assert d[:8] == b"VNDRBOOT", d[:8]
(hdrver, psz, kaddr, raddr, vrsize) = struct.unpack_from("<5I", d, 8)
cmdline = d[28:28+2048].split(b"\0")[0]
tags, = struct.unpack_from("<I", d, 28+2048)
hsize, dtbsize = struct.unpack_from("<2I", d, 2096)
dtbaddr, = struct.unpack_from("<Q", d, 2104)
checks = [
    ("BOARD_BOOT_HEADER_VERSION", hdrver, val("BOARD_BOOT_HEADER_VERSION")),
    ("BOARD_PAGE_SIZE", psz, val("BOARD_PAGE_SIZE")),
    ("BOARD_KERNEL_BASE+BOARD_KERNEL_OFFSET", kaddr, BASE+val("BOARD_KERNEL_OFFSET")),
    ("BOARD_KERNEL_BASE+BOARD_RAMDISK_OFFSET", raddr, BASE+val("BOARD_RAMDISK_OFFSET")),
    ("BOARD_KERNEL_BASE+BOARD_TAGS_OFFSET", tags, BASE+val("BOARD_TAGS_OFFSET")),
    ("BOARD_KERNEL_BASE+BOARD_DTB_OFFSET", dtbaddr, BASE+val("BOARD_DTB_OFFSET")),
    ("BOARD_HEADER_SIZE", hsize, val("BOARD_HEADER_SIZE")),
    ("BOARD_DTB_SIZE", dtbsize, val("BOARD_DTB_SIZE")),
    ("BOARD_VENDOR_CMDLINE", cmdline, str(val("BOARD_VENDOR_CMDLINE")).encode()),
    ("BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE", len(d), val("BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE")),
]
f = 0
for n, real, cfg in checks:
    ok = real == cfg
    print("%s %-42s image=%-12s config=%s" % ("ok  " if ok else "FAIL", n, real, cfg))
    f += 0 if ok else 1
print("\nRESULT:", "OK" if not f else "FAIL (%d)" % f)
sys.exit(1 if f else 0)
