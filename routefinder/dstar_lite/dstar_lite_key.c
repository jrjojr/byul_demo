#include "internal/dstar_lite_key.h"
#include <glib.h>
#include <stdlib.h>

gint dstar_lite_key_compare(
    const dstar_lite_key dsk0, const dstar_lite_key dsk1) {

    if (dsk0->k1 < dsk1->k1)
        return -1;
    else if (dsk0->k1 > dsk1->k1)
        return 1;
    else {
        if (dsk0->k2 < dsk1->k2)
            return -1;
        else if (dsk0->k2 > dsk1->k2)
            return 1;
        else
            return 0;
    }
}

gint dstar_lite_key_compare_raw(
    gconstpointer a, gconstpointer b, gpointer userdata) {
        
    const dstar_lite_key dsk0 = (const dstar_lite_key)a;
    const dstar_lite_key dsk1 = (const dstar_lite_key)b;
    return dstar_lite_key_compare(dsk0, dsk1);
}


dstar_lite_key dstar_lite_key_new(void) {
    return dstar_lite_key_new_full(0.0f, 0.0f);
}

dstar_lite_key dstar_lite_key_new_full(gfloat k1, gfloat k2) {
    dstar_lite_key key = g_new(dstar_lite_key_t, 1);
    key->k1 = k1;
    key->k2 = k2;
    return key;
}

dstar_lite_key dstar_lite_key_copy(dstar_lite_key key) {
    if (!key) return NULL;

    dstar_lite_key copy = g_new(dstar_lite_key_t, 1);
    copy->k1 = key->k1;
    copy->k2 = key->k2;
    return copy;
}

void dstar_lite_key_free(dstar_lite_key key) {
    g_free(key);
}
