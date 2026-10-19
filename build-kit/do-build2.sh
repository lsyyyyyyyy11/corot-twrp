#!/bin/bash
export HOME=/root
if [ -f /root/twrp-build.log ] && [ "$(stat -c%s /root/twrp-build.log)" -gt 209715200 ]; then mv /root/twrp-build.log /root/twrp-build.log.old; fi
exec >>/root/twrp-build.log 2>&1
[ -f /root/build-done ] && exit 0
echo "BUILD_START=$(date -Is)"
cd /root/twrp
if [ ! -d device/xiaomi/corot ]; then
  mkdir -p device/xiaomi; cp -r /root/corot-trees/qiyuan2403_corot-twrp-device-tree device/xiaomi/corot
  rm -rf device/xiaomi/corot/.git
fi
source build/envsetup.sh
export ALLOW_MISSING_DEPENDENCIES=true
lunch twrp_corot-ap2a-eng
make vendorbootimage -j16
rc=$?
if [ $rc -ne 0 ]; then tail -300 /root/twrp-build.log > /root/twrp-build-fail-snapshot.txt; fi
echo "BUILD_RC=$rc"
if [ $rc -eq 0 ]; then
  ls -la out/target/product/corot/vendor_boot.img
  touch /root/build-done
  systemctl disable twrpbuild.service 2>/dev/null
else
  touch /root/build-failed
fi
exit $rc
