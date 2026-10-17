/*
 * fscrypt_policy_helpers.c
 *
 * Completes the OrangeFox-style fscrypt API that TeamWin's
 * android-14.1 bootable/recovery/libtar expects but that TeamWin's
 * system/vold/fscrypt_policy.h never provided (it only has the v1/v2
 * struct helpers).  The logic matches the OrangeFox implementation so
 * tar backups of FBE directories keep the same on-disk policy layout.
 *
 * Only the helpers that libvold does NOT provide live here.  The
 * functions libvold already defines (fscrypt_policy_get_struct/set_struct,
 * lookup_ref_key, lookup_ref_tar, bytes_to_hex) must not be duplicated
 * or the static link against libvold fails with multiple definitions.
 */
#include "fscrypt_policy.h"

#include <stdio.h>

uint8_t* get_policy_descriptor(fscrypt_policy* fep) {
    if (fep == NULL) {
        return NULL;
    }
    switch (fep->version) {
        case FSCRYPT_POLICY_V1:
            return fep->v1.master_key_descriptor;
        case FSCRYPT_POLICY_V2:
            return fep->v2.master_key_identifier;
        default:
            return NULL;
    }
}

uint8_t get_policy_size(fscrypt_policy* fep, bool hex) {
    if (fep == NULL) {
        return 0;
    }
    switch (fep->version) {
        case FSCRYPT_POLICY_V1:
            return (uint8_t)(hex ? FS_KEY_DESCRIPTOR_SIZE_HEX : FSCRYPT_KEY_DESCRIPTOR_SIZE);
        case FSCRYPT_POLICY_V2:
            return (uint8_t)(hex ? FSCRYPT_KEY_IDENTIFIER_SIZE_HEX : FSCRYPT_KEY_IDENTIFIER_SIZE);
        default:
            return 0;
    }
}

void* get_policy(const fscrypt_policy* fep) {
    if (fep == NULL) {
        return NULL;
    }
    switch (fep->version) {
        case FSCRYPT_POLICY_V1:
            return (void*)&fep->v1;
        case FSCRYPT_POLICY_V2:
            return (void*)&fep->v2;
        default:
            return NULL;
    }
}

int fscrypt_policy_size(const fscrypt_policy* fep) {
    if (fep == NULL) {
        return 0;
    }
    switch (fep->version) {
        case FSCRYPT_POLICY_V1:
            return (int)sizeof(fep->v1);
        case FSCRYPT_POLICY_V2:
            return (int)sizeof(fep->v2);
        default:
            return 0;
    }
}

/* Debug-only helper: formats the policy as text.  Same behaviour as the
 * OrangeFox implementation (block.c only calls it under #ifdef DEBUG). */
void get_policy_content(fscrypt_policy* fep, char* content) {
    if (fep == NULL || content == NULL) {
        return;
    }
    switch (fep->version) {
        case FSCRYPT_POLICY_V1:
            sprintf(content, "%i %i %i %i %s", (int)fep->v1.version,
                    (int)fep->v1.contents_encryption_mode,
                    (int)fep->v1.filenames_encryption_mode, (int)fep->v1.flags,
                    (char*)fep->v1.master_key_descriptor);
            break;
        case FSCRYPT_POLICY_V2:
            sprintf(content, "%i %i %i %i %s", (int)fep->v2.version,
                    (int)fep->v2.contents_encryption_mode,
                    (int)fep->v2.filenames_encryption_mode, (int)fep->v2.flags,
                    (char*)fep->v2.master_key_identifier);
            break;
        default:
            break;
    }
}
