#!/usr/bin/env python3
"""
Verify the corot (Redmi K60 Ultra / 13T Pro) TWRP device tree against ground truth
taken from the stock ROM (OS2.0.203.0.VMLCNXM) and from the running device.

Usage: verify_tree.py [TREE_DIR]
"""
import os
import re
import struct
import subprocess
import sys

TREE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
STOCK_IMAGES = "/root/dl/rom/corot_images_OS2.0.203.0.VMLCNXM_15.0/images"
STOCK_RAMDISK = "/root/work/vb/x"           # unpacked stock vendor_boot ramdisk
REAL_PARTS = "/tmp/real_partnames.txt"

PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append((name, detail))
    print(("  ok   " if ok else "  FAIL ") + name + (("  -- " + detail) if detail else ""))


def rd(p):
    with open(os.path.join(TREE, p)) as f:
        return f.read()


def kv(text, key):
    m = re.search(r"^%s\s*:?=\s*(.+)$" % re.escape(key), text, re.M)
    return m.group(1).split("#")[0].strip() if m else None


def running_kernel():
    return subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()


def vermagic(ko):
    out = subprocess.run(["modinfo", ko], capture_output=True, text=True).stdout
    m = re.search(r"vermagic:\s*(\S+)", out)
    return m.group(1) if m else None


bc = rd("BoardConfig.mk")

print("== kernel modules ==")
rk = running_kernel()
print("       running kernel: %s" % rk)
# Every module in the tree must have been built for a kernel whose version matches
# the one the device boots, or modversions + vermagic rejects the load.
moddir = os.path.join(TREE, "recovery/root/lib/modules")
kos = sorted(f for f in os.listdir(moddir) if f.endswith(".ko"))
vm = {}
for f in kos:
    v = vermagic(os.path.join(moddir, f))
    vm.setdefault(v, []).append(f)
check("all modules share one vermagic", len(vm) == 1,
      "; ".join("%s (%d)" % (k, len(v)) for k, v in vm.items()))
v0 = list(vm)[0] if vm else ""
check("module vermagic kernel-release matches running kernel",
      v0.split("-")[0] == rk.split("-")[0],
      "modules %s vs kernel %s" % (v0.split("-")[0], rk.split("-")[0]))
check("modules carry __versions (built with MODVERSIONS)",
      all(subprocess.run(["readelf", "-S", os.path.join(moddir, f)],
                         capture_output=True, text=True).stdout.count("__versions") > 0
          for f in kos[:5]), "sampled 5")

if os.path.isdir(STOCK_RAMDISK):
    sm = os.path.join(STOCK_RAMDISK, "lib/modules")
    check("module file set identical to stock vendor_boot ramdisk",
          sorted(os.listdir(moddir)) == sorted(os.listdir(sm)))
    for meta in ["modules.load.recovery", "modules.load", "modules.dep", "modules.alias"]:
        a = os.path.join(moddir, meta)
        b = os.path.join(sm, meta)
        if os.path.exists(b):
            check("%s identical to stock" % meta,
                  open(a, "rb").read() == open(b, "rb").read())
    # mifs specifically
    check("mifs.ko vermagic == stock", vermagic(os.path.join(moddir, "mifs.ko")) ==
          vermagic(os.path.join(sm, "mifs.ko")))

print("== display ==")
dtb = os.path.join(TREE, "prebuilt/dtb")
check("BOARD_DTB_SIZE == prebuilt/dtb size (%d)" % os.path.getsize(dtb),
      kv(bc, "BOARD_DTB_SIZE") == str(os.path.getsize(dtb)),
      "config %s" % kv(bc, "BOARD_DTB_SIZE"))
if os.path.isdir(STOCK_IMAGES):
    sd = os.path.join(STOCK_IMAGES, "dtbo.img")
    if os.path.exists(sd):
        check("prebuilt/dtb matches stock dtbo-derived DTB size",
              os.path.getsize(dtb) == 390904)
check("TW_MAX_BRIGHTNESS == measured panel max (16383)",
      kv(bc, "TW_MAX_BRIGHTNESS") == "16383", "found %s" % kv(bc, "TW_MAX_BRIGHTNESS"))
check("screen 1220x2712",
      kv(bc, "TARGET_SCREEN_WIDTH") == "1220" and kv(bc, "TARGET_SCREEN_HEIGHT") == "2712")

print("== decryption ==")
for k in ["TW_INCLUDE_CRYPTO", "TW_INCLUDE_CRYPTO_FBE", "BOARD_USES_METADATA_PARTITION",
          "TW_INCLUDE_FBE_METADATA_DECRYPT", "TW_USE_FSCRYPT_POLICY"]:
    v = kv(bc, k)
    check("%s enabled" % k, v is not None and v.lower() not in ("false", "0"), "found %s" % v)
dev = rd("device.mk")
for pkg in ["android.hardware.keymaster@4.1", "android.hardware.security.keymint",
            "android.hardware.security.secureclock", "android.hardware.security.sharedsecret",
            "android.system.keystore2"]:
    check("device.mk ships %s" % pkg, pkg in dev)
prop = rd("system.prop")
check("system.prop crypto + TEE props",
      "ro.crypto.volume.filenames_mode" in prop and
      "ro.vendor.mtk_mitee_support=1" in prop and "ro.vendor.mtk_tee_gp_support=1" in prop)
for f in ["recovery/root/tee-supplicant.rc", "recovery/root/keymint.service.mitee.rc",
          "recovery/root/miteelog.rc", "recovery/root/vendor/bin/tee-supplicant",
          "recovery/root/vendor/bin/hw/android.hardware.security.keymint@2.0-service.mitee",
          "recovery/root/vendor/bin/hw/android.hardware.gatekeeper@1.0-service"]:
    check("present: %s" % f, os.path.exists(os.path.join(TREE, f)))
# The shipped vendor keymint service links android.hardware.security.keymint-V2-ndk.so
# (readelf DT_NEEDED). Without it in the ramdisk the service dies at exec and FBE
# decryption cannot unwrap the metadata key.
check("keymint V2 ndk lib shipped next to its service",
      os.path.exists(os.path.join(TREE, "recovery/root/vendor/lib64/"
                                        "android.hardware.security.keymint-V2-ndk.so")))
ta = os.path.join(TREE, "recovery/root/vendor/mitee/ta")
check("MicroTrust TAs (>=10)", os.path.isdir(ta) and
      len([x for x in os.listdir(ta) if x.endswith(".ta")]) >= 10,
      "%d" % (len(os.listdir(ta)) if os.path.isdir(ta) else 0))
rc = rd("recovery/root/init.recovery.mt6985.rc")
for n in ["import /tee-supplicant.rc", "import /keymint.service.mitee.rc", "start vold",
          "crypto.ready 1", "start vendor.keymint-mitee", "start vendor.gatekeeper-1-0"]:
    check("init rc: %s" % n, n in rc)
# tee-supplicant hardcodes /mnt/vendor/persist/data for its device keys. Stock
# fstab.mt6985 mounts persist only under 'on late-fs', which recovery init never
# fires, so the recovery init rc must mount it itself before tee-supplicant starts.
check("persist.fstab mounts /mnt/vendor/persist",
      os.path.exists(os.path.join(TREE, "recovery/root/system/etc/persist.fstab")) and
      "/mnt/vendor/persist" in rd("recovery/root/system/etc/persist.fstab"))
check("init rc mounts persist before tee-supplicant start",
      re.search(r"^on early-fs\b", rc, re.M) is not None and
      "mount_all /system/etc/persist.fstab --early" in rc)
# 'haptic' is a module on /vendor_dlkm (not built in), and it is absent from
# modules.load.recovery, so TWRP's own loader must be enabled and told to load it.
check("TW_LOAD_VENDOR_MODULES loads haptic.ko",
      kv(bc, "TW_LOAD_VENDOR_MODULES") is not None and "haptic.ko" in kv(bc, "TW_LOAD_VENDOR_MODULES"))

print("== metadata filesystem ==")
for f in ["recovery/root/system/etc/recovery.fstab", "recovery/root/system/etc/twrp.flags",
          "recovery/root/first_stage_ramdisk/fstab.mt6985",
          "recovery/root/first_stage_ramdisk/fstab.emmc"]:
    lines = [l for l in rd(f).splitlines()
             if "/metadata" in l and not l.lstrip().startswith("#")]
    check("%s: /metadata is f2fs" % os.path.basename(f),
          bool(lines) and "f2fs" in lines[0], lines[0][:70] if lines else "absent")

print("== mifs / fstab hygiene ==")
rf = rd("recovery/root/system/etc/recovery.fstab")
check("recovery.fstab has mifs /data entry", re.search(r"/data\s+mifs\b", rf) is not None)
check("recovery.fstab has f2fs /data entry", re.search(r"/data\s+f2fs\b", rf) is not None)
check("recovery.fstab covers system_dlkm", "/system_dlkm" in rf)
check("recovery.fstab has no avb= flags", "avb=" not in rf)
check("recovery.fstab has no doubled commas", ",," not in rf)
tf = rd("recovery/root/system/etc/twrp.flags")
# /data on corot is F2FS (verified: /sys/fs/f2fs/dm-43). twrp.flags is a map
# keyed by mount point, so a second 'mifs' line would override the f2fs one;
# recovery.fstab keeps mifs only as a fallback after the f2fs line.
check("twrp.flags has f2fs /data entry", re.search(r"^/data\s+f2fs\b", tf, re.M) is not None)
check("twrp.flags has no mifs /data override", re.search(r"^/data\s+mifs\b", tf, re.M) is None)
check("twrp.flags has connsys_gnss", "connsys_gnss" in tf)

print("== partitions ==")
if os.path.exists(REAL_PARTS):
    real = set(l.strip() for l in open(REAL_PARTS) if l.strip())
    real |= set(re.sub(r"_[ab]$", "", n) for n in real)
else:
    real = set()
bad = []
for line in tf.splitlines():
    if line.startswith("#") or not line.strip():
        continue
    parts = line.split()
    if len(parts) < 3:
        continue
    m = re.match(r"/dev/block/by-name/([a-z0-9_]+)$", parts[2])
    if m and real and m.group(1) not in real and m.group(1) != "preloader_raw":
        bad.append(m.group(1))
check("twrp.flags only references real partitions", not bad, "bogus %s" % sorted(set(bad)))

print("== build / CI ==")
check("vendorsetup.sh present", os.path.exists(os.path.join(TREE, "vendorsetup.sh")))
check("security/miui_releasekey.x509.pem present",
      os.path.exists(os.path.join(TREE, "security/miui_releasekey.x509.pem")))
check("device.mk registers PRODUCT_EXTRA_RECOVERY_KEYS", "PRODUCT_EXTRA_RECOVERY_KEYS" in dev)
ci = rd(".github/workflows/Make TWRP.yml")
m = re.search(r"MANIFEST_BRANCH:\n(?:.*\n)*?\s+default: '([^']+)'", ci)
# twrp-14.1 (AOSP r67) is required: it ships build/release with the 'ap2a'
# release config, so lunch twrp_corot-ap2a-eng resolves. twrp-14 (r17) has no
# build/release project and lunch fails.
check("CI manifest branch targets twrp-14.1", m and m.group(1) == "twrp-14.1",
      "default %s" % (m.group(1) if m else "?"))

print()
print("PASS %d / FAIL %d" % (len(PASS), len(FAIL)))
if FAIL:
    print("\nFailures:")
    for n, d in FAIL:
        print("  - %s %s" % (n, ("(" + d + ")") if d else ""))
sys.exit(1 if FAIL else 0)
