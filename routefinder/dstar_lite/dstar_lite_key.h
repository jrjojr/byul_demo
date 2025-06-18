#ifndef DSTAR_LITE_KEY_H
#define DSTAR_LITE_KEY_H

#include "byul_config.h"
#include "internal/coord.h"
#include "internal/dstar_lite_key.h"
#include "internal/pqueue.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct s_dstar_lite_key{
    gfloat k1;
    gfloat k2;
} dstar_lite_key_t;

typedef dstar_lite_key_t* dstar_lite_key;

BYUL_API dstar_lite_key dstar_lite_key_new(void);

BYUL_API dstar_lite_key dstar_lite_key_new_full(gfloat k1, gfloat k2);

BYUL_API dstar_lite_key dstar_lite_key_copy(dstar_lite_key key);

BYUL_API void dstar_lite_key_free(dstar_lite_key key);

BYUL_API gint dstar_lite_key_compare(
    const dstar_lite_key dsk0, const dstar_lite_key dsk1);

BYUL_API gint dstar_lite_key_compare_raw(
    gconstpointer a, gconstpointer b, gpointer userdata);

#ifdef __cplusplus
}
#endif

#endif // DSTAR_LITE_KEY_H
