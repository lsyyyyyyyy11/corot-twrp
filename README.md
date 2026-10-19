# corot-twrp · Redmi K60 Ultra TWRP 设备树(增强 fork)

[corot](https://github.com/qiyuan2403/corot-twrp-device-tree)(Redmi K60 Ultra / Redmi 13T Pro,MT6985)的 TWRP 设备树增强分支,基于 twrp-14.1 基线,已在本机(HyperOS 3.0.305.0 / Android 16)完整实测。

## 相对上游的增强

| 补丁 | 内容 |
|---|---|
| twrp-patches/0008 | `partition.cpp` 识别 **mifs** 文件系统(HyperOS 2+ 的 /data = 小米魔改 f2fs,不识别则无法挂载) |
| twrp-patches/0009 | 修复 split archive **99 分卷上限**(TeamWin [#417](https://github.com/TeamWin/android_bootable_recovery/issues/417),大备份必踩) |
| BoardConfig | `TW_NO_HAPTICS := true` —— **MTK 下按下触感会挂死 GUI 线程**(表现为"触摸没反应"),禁用后触摸全链路正常 |
| twrp.flags | /data 类型 f2fs → mifs |

## 实测功能

- 触摸 / 中文界面 / 全屏主题
- 安卓 + TWRP 单 vendor_boot 共存(安卓侧触摸/指纹/信号正常,SELinux Enforcing)
- fastbootd / OTG / exFAT / NTFS / 分区挂载与备份(见下方限制)
- 版本标识:`Redmi K60 Ultra | mominqimiang | lsyyyyyyy`

## 已知限制(诚实声明)

1. **/data 解密不可用**:本机只有 keymint 2.0(AIDL)服务,TWRP 3.7.1 的解密链路只认 keymaster(HIDL),且 /data 之上还有 dm("userdata")层——两者叠加,当前无解。等 twrp-16 生态跟进 keymint。
2. **USB 插拔可能触发内核崩溃**(mtk_charger_framework 的 rust_det 定时器 BUG):避开方式 = 开机时不要插线,进系统后再插。
3. TWRP 备份建议走 USB-OTG(内部存储因 /data 加密不可写)。

## 构建

```bash
# 1) repo init 到 twrp-14.1 并 sync;设备树放入 device/xiaomi/corot
# 2) 应用 twrp-patches/0001-0009
# 3) make vendorbootimage
# 4) 产物 ramdisk 过 build-kit/build-slim11.py(需原厂模块集,见 build-kit/stock-modules-manifest.json)
# 5) lz4 + 组装 v4 vendor_boot(方法见上游 README)
```

`build-kit/` 含打包脚本与固化套件;完整构建记录与镜像见 Releases。

## 致谢

- [TeamWin Recovery Project](https://github.com/TeamWin/android_bootable_recovery)(GPL)
- 上游设备树:[qiyuan2403/corot-twrp-device-tree](https://github.com/qiyuan2403/corot-twrp-device-tree)
- 原始版本作者:mominqimiang
- mifs 识别思路:laomadaemon/fuxi OFRP 设备树

## License

沿上游(GPL-3.0 / TeamWin)。
