#
# Copyright (C) 2022 The TWRP Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

PRODUCT_MAKEFILES := $(LOCAL_DIR)/twrp_corot.mk

# Android 14's lunch requires <product>-<release>-<variant>. The manifest's
# default revision is android-14.0.0_r67 (24Q2), whose only declared release
# config is "ap2a" (build/release/release_config_map.mk).
COMMON_LUNCH_CHOICES := \
    twrp_corot-ap2a-eng \
    twrp_corot-ap2a-userdebug \
    twrp_corot-ap2a-user
