# corot-twrp · 红米 K60 至尊版 TWRP(增强版)

本项目是红米 K60 至尊版(代号 corot)的 TWRP 设备树,在上游基础上补充了几处修复,基于 twrp-14.1,已在 HyperOS 3.0.305.0(Android 16)设备上测试可用。

## 相比上游的改动

| 补丁 | 内容 |
|---|---|
| 0008 | **识别 mifs 文件系统**:HyperOS 2+ 将 /data 的文件系统改名为 mifs(小米魔改版 f2fs),TWRP 不识别该名称时无法挂载 /data |
| 0009 | **解除备份 99 分卷上限**:备份超过 99 个分卷时会失败、校验错位;现支持至 9999 卷,读写两侧命名保持一致 |
| BoardConfig | **关闭触感反馈**(`TW_NO_HAPTICS`):该机型上按键震动会导致 GUI 线程死锁,表现为触摸无响应;关闭后触摸操作全部正常 |
| twrp.flags | /data 文件系统类型由 f2fs 调整为 mifs |

## 已知限制

1. **/data 解密不可用**:设备仅提供 keymint 2.0(AIDL)服务,而 TWRP 3.7.1 的解密链路只支持 keymaster(HIDL);同时 /data 之上还有一层 dm 设备,两者叠加导致当前无法解密,需等待 TWRP 支持 Android 16。
2. **备份请使用 USB-OTG**:内部存储因 /data 加密不可写。

## 构建方法

```bash
# 1) repo init 到 twrp-14.1 并 sync;设备树放入 device/xiaomi/corot
# 2) 依次应用 twrp-patches/0001-0009
# 3) make vendorbootimage
# 4) 产物 ramdisk 用 build-kit/build-slim11.py 处理(需要原厂内核模块,清单见 build-kit/stock-modules-manifest.json)
# 5) lz4 压缩后组装为 v4 vendor_boot(步骤见上游 README)
```

`build-kit/` 内为打包脚本与固化套件;成品镜像见 Releases。

## 引用、参考与致谢

**(1) 引用的项目:**

1. **[TeamWin Recovery Project](https://github.com/TeamWin/android_bootable_recovery)**(GPL-3.0):恢复环境主体源码(`bootable/recovery`,twrp-14.1 分支);另引用了其 Gerrit 变更 **8744、8745** 的构建修复,并参考 Issue **#417** 对分卷上限问题的分析。
2. **[qiyuan2403/corot-twrp-device-tree](https://github.com/qiyuan2403/corot-twrp-device-tree)**:corot 设备树本体、预编译资源(keymint 服务、TA 等)及 0001-0007 补丁体系;本项目 0008/0009 按同一体系提交上游。
3. **mominqimiang**:corot 原始 TWRP 移植作者,固件版本标识中的署名保留。
4. **[lamadaemon/device_xiaomi_fuxi_OFRP](https://github.com/lamadaemon/device_xiaomi_fuxi_OFRP)**:mifs 识别方案的先例;该设备树基于 **OrangeFox Recovery Project** 框架,一并致谢。
5. **[Android Open Source Project (AOSP)](https://source.android.com/)**:repo/manifest、编译工具链、mkbootimg、fastboot 等基础设施。
6. **小米 HyperOS 原厂固件(HyperOS 3.0.305.0)**:内核模块(如 miev.ko)、TA、预编译数据均提取自本机固件,版权归小米,仅用于本机设备维护。

**(2) 参考的思路:**

- mifs 为小米魔改版 f2fs(内核 `fs/mifs/*`):小米社区与酷安的讨论结论,并由 lamadaemon 设备树的做法印证;
- MTK 引导程序对 ramdisk 的 64MiB 大小限制:依据本机 expdb 引导日志分析及 MTK 社区资料;
- TWRP 3.7.1 不支持 keymint:社区讨论结合本机测试结论;
- 无独立 recovery 分区的机型依靠 misc/para 标志与 `fastboot reboot recovery` 进入 TWRP:来自 qiyuan2403 的文档与 MTK 社区资料;
- MTK 平台上按键触感触发 GUI 线程死锁:由本机日志定位,并已提交上游。

**(3) 发布:** lsyyyyyyyy11 —— 适配、测试与发布。

## License

GPL-3.0(沿 TeamWin 与上游设备树)。
