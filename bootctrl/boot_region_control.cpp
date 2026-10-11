/*****************************************************************************
*  Copyright Statement:
*  --------------------
*  This software is protected by Copyright and the information contained
*  herein is confidential. The software may not be copied and the information
*  contained herein may not be used or disclosed except with the written
*  permission of MediaTek Inc. (C) 2020
*
*  BY OPENING THIS FILE, BUYER HEREBY UNEQUIVOCALLY ACKNOWLEDGES AND AGREES
*  THAT THE SOFTWARE/FIRMWARE AND ITS DOCUMENTATIONS ("MEDIATEK SOFTWARE")
*  RECEIVED FROM MEDIATEK AND/OR ITS REPRESENTATIVES ARE PROVIDED TO BUYER ON
*  AN "AS-IS" BASIS ONLY. MEDIATEK EXPRESSLY DISCLAIMS ANY AND ALL WARRANTIES,
*  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
*  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE OR NONINFRINGEMENT.
*  NEITHER DOES MEDIATEK PROVIDE ANY WARRANTY WHATSOEVER WITH RESPECT TO THE
*  SOFTWARE OF ANY THIRD PARTY WHICH MAY BE USED, INCORPORATED IN, OR
*  SUPPLIED WITH THE MEDIATEK SOFTWARE, AND BUYER AGREES TO LOOK ONLY TO SUCH
*  THIRD PARTY FOR ANY WARRANTY CLAIM RELATING THERETO. MEDIATEK SHALL ALSO
*  NOT BE RESPONSIBLE FOR ANY MEDIATEK SOFTWARE RELEASES MADE TO BUYER'S
*  SPECIFICATION OR TO CONFORM TO A PARTICULAR STANDARD OR OPEN FORUM.
*
*  BUYER'S SOLE AND EXCLUSIVE REMEDY AND MEDIATEK'S ENTIRE AND CUMULATIVE
*  LIABILITY WITH RESPECT TO THE MEDIATEK SOFTWARE RELEASED HEREUNDER WILL BE,
*  AT MEDIATEK'S OPTION, TO REVISE OR REPLACE THE MEDIATEK SOFTWARE AT ISSUE,
*  OR REFUND ANY SOFTWARE LICENSE FEES OR SERVICE CHARGE PAID BY BUYER TO
*  MEDIATEK FOR SUCH MEDIATEK SOFTWARE AT ISSUE.
*
*  THE TRANSACTION CONTEMPLATED HEREUNDER SHALL BE CONSTRUED IN ACCORDANCE
*  WITH THE LAWS OF THE STATE OF CALIFORNIA, USA, EXCLUDING ITS CONFLICT OF
*  LAWS PRINCIPLES.  ANY DISPUTES, CONTROVERSIES OR CLAIMS ARISING THEREOF AND
*  RELATED THERETO SHALL BE SETTLED BY ARBITRATION IN SAN FRANCISCO, CA, UNDER
*  THE RULES OF THE INTERNATIONAL CHAMBER OF COMMERCE (ICC).
*
*****************************************************************************/

#include <android-base/logging.h>

#include "boot_region_control_private.h"

namespace android {
namespace bootable {

/*
 * The MTK UFS "switch the boot LUN" ioctl is intentionally NOT implemented.
 *
 * The vendor struct ufs_ioctl_query_data used by the tree's ufs-mtk-ioctl.h is
 * 16 bytes (__u32 opcode; __u8 idn; __u8 idx; __u16 buf_byte; __u8 *buf_ptr)
 * and places the attribute value behind a user pointer. The kernel actually
 * running on corot uses an 8-byte layout (__u32 opcode; __u8 idn;
 * __u16 buf_size; __u8 buffer[0]) and reads the attribute value from
 * buffer + sizeof(struct ufs_ioctl_query_data) == offset 8, i.e. the kernel
 * would read the buf_ptr field itself as the attribute value. Its only check
 * is "if (!att) return -EINVAL", so any non-zero pointer would be programmed
 * straight into the UFS device's bBootLunEn attribute via ufshcd_query_attr.
 * That can corrupt the boot-LUN selection of the device's own boot path.
 *
 * The previous implementation also declared "int fd, ret = true" and returned
 * ret without ever inspecting errno, so ioctl failures were reported to the
 * framework as success.
 *
 * A/B slot switching is handled by the AOSP libboot_control through /misc,
 * which is what the bootloader reads. Doing nothing here is correct and safe.
 */
bool BootControlExt::SetBootRegionSlot(unsigned int slot) {
  LOG(INFO) << "SetBootRegionSlot(" << slot << ") ignored: UFS boot-LUN "
            << "switching is disabled (see boot_region_control.cpp)";
  return true;
}

}
}
