/*
 * Local fscrypt_policy.h for TWRP's libtar.
 *
 * TeamWin's android-14.1 bootable/recovery/libtar was written against the
 * OrangeFox-style fscrypt API: a fscrypt_policy union plus the helpers
 * get_policy_size(), get_policy_descriptor(), get_policy(),
 * fscrypt_policy_size() and get_policy_content().  TeamWin's
 * system/vold/fscrypt_policy.h only declares the v1/v2 helpers, and
 * <linux/fs.h> keeps the legacy "fscrypt_policy" alias to
 * "fscrypt_policy_v1" (which is not a type name), so the libtar FBE code
 * stops compiling as soon as TW_INCLUDE_CRYPTO_FBE is enabled.
 *
 * This header restores the missing type and declarations.  The five
 * OrangeFox helpers live in fscrypt_policy_helpers.c; the functions that
 * libvold already provides (fscrypt_policy_get_struct/set_struct,
 * lookup_ref_key, lookup_ref_tar, bytes_to_hex) are declared here with the
 * libtar-side types and resolve to libvold at link time.
 *
 * Kept intentionally small: only what bootable/recovery/libtar/ uses.
 */
#ifndef TWRP_LIBTAR_FSCRYPT_POLICY_H
#define TWRP_LIBTAR_FSCRYPT_POLICY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Pulls in struct fscrypt_policy_v1/v2 and the FSCRYPT_* constants. */
#include <linux/fs.h>

/* linux/fscrypt.h keeps a legacy alias to the v1 struct; libtar needs the
 * version-dispatching union below instead. */
#undef fscrypt_policy

typedef union fscrypt_policy {
    uint8_t version;
    struct fscrypt_policy_v1 v1;
    struct fscrypt_policy_v2 v2;
} fscrypt_policy;

#define FS_KEY_DESCRIPTOR_SIZE_HEX (2 * FSCRYPT_KEY_DESCRIPTOR_SIZE + 1)
#define FSCRYPT_KEY_IDENTIFIER_SIZE_HEX ((2 * FSCRYPT_KEY_IDENTIFIER_SIZE) + 1)

/* Policy payload prefixes.  append.c concatenates the numeric policy
 * version with these: "%u" + "CE" -> "2CE" for a v2 user CE policy. */
#define USER_CE_FSCRYPT_POLICY "CE"
#define USER_DE_FSCRYPT_POLICY "DE"
#define SYSTEM_DE_FSCRYPT_POLICY "DK"

/* Implemented by system/vold (fscrypt_policy.cpp / Decrypt.cpp) with C
 * linkage.  Declared with the libtar types because those translation units
 * pass fscrypt_policy pointers straight through. */
bool fscrypt_policy_get_struct(const char* directory, fscrypt_policy* fep);
bool fscrypt_policy_set_struct(const char* directory, const fscrypt_policy* fep);
bool lookup_ref_key(fscrypt_policy* fep, uint8_t* policy_type);
bool lookup_ref_tar(fscrypt_policy* fep, uint8_t* policy);
void bytes_to_hex(const uint8_t* bytes, size_t num_bytes, char* hex);

/* Provided by fscrypt_policy_helpers.c. */
uint8_t* get_policy_descriptor(fscrypt_policy* fep);
void* get_policy(const fscrypt_policy* fep);
uint8_t get_policy_size(fscrypt_policy* fep, bool hex);
int fscrypt_policy_size(const fscrypt_policy* fep);
void get_policy_content(fscrypt_policy* fep, char* content);

#endif /* TWRP_LIBTAR_FSCRYPT_POLICY_H */
