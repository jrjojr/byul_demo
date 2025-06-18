#include "internal/dstar_lite_pqueue.h"
#include "internal/core.h"
#include "internal/dstar_lite_key.h"

#include <string.h>

dstar_lite_pqueue dstar_lite_pqueue_new(void) {
    dstar_lite_pqueue q = g_new0(struct s_dstar_lite_pqueue, 1);
    q->pq = pqueue_new_full(
        dstar_lite_key_compare_raw, NULL,
        g_free, (GDestroyNotify)coord_free);

    q->coord_to_key = g_hash_table_new_full(
        (GHashFunc) coord_hash,
        (GEqualFunc) coord_equal, 
        (GDestroyNotify)coord_free, 
        g_free
    );
    return q;
}

void dstar_lite_pqueue_free(dstar_lite_pqueue q) {
    if (!q) return;
    pqueue_free(q->pq);
    g_hash_table_destroy(q->coord_to_key);
    g_free(q);
}

void dstar_lite_pqueue_push(
    dstar_lite_pqueue q, const dstar_lite_key key, const coord c) {

    // dstar_lite_key new_key = dstar_lite_key_copy(key);
    // coord new_coord = coord_copy(c);
    pqueue_push(q->pq, key, sizeof(dstar_lite_key_t), 
        c, sizeof(coord_t));

    dstar_lite_key key_for_hash = dstar_lite_key_copy(key);
    g_hash_table_replace(q->coord_to_key, coord_copy(c), key_for_hash);
}

coord dstar_lite_pqueue_peek(dstar_lite_pqueue q) {
    return (coord)pqueue_peek(q->pq);
}

coord dstar_lite_pqueue_pop(dstar_lite_pqueue q) {
    coord c = (coord)pqueue_pop(q->pq);
    if (c) {
        g_hash_table_remove(q->coord_to_key, c);
    }
    return c;
}

gboolean dstar_lite_pqueue_is_empty(dstar_lite_pqueue q) {
    return pqueue_is_empty(q->pq);
}

gboolean dstar_lite_pqueue_remove(
    dstar_lite_pqueue q, const coord u) {
    if (!q || !u) return FALSE;

    dstar_lite_key key = g_hash_table_lookup(q->coord_to_key, u);
    if (!key) return FALSE;

    gboolean removed = pqueue_remove_custom(
        q->pq, key, u, (GCompareFunc)coord_compare);
    // gboolean removed = pqueue_remove_custom(
    //     q->pq, key, u, (GCompareFunc) dstar_lite_key_compare);

    if (removed) {
        g_hash_table_remove(q->coord_to_key, u);
    }

    return removed;
}

gboolean dstar_lite_pqueue_remove_full(
    dstar_lite_pqueue q, const dstar_lite_key key, const coord c) {
    if (!q || !key || !c) return FALSE;

    gboolean removed = pqueue_remove_custom(
        q->pq, (gpointer)key, (gconstpointer)c, (GCompareFunc)coord_compare);
    // gboolean removed = pqueue_remove_custom(
    //     q->pq, (gpointer)key, (gconstpointer)c, 
    //     (GCompareFunc) dstar_lite_key_compare);

    if (removed) {
        g_hash_table_remove(q->coord_to_key, c);
    }

    return removed;
}

dstar_lite_key dstar_lite_pqueue_find_key_by_coord(
    dstar_lite_pqueue q, const coord c) {
    return (dstar_lite_key)g_hash_table_lookup(q->coord_to_key, c);
}

dstar_lite_key dstar_lite_pqueue_top_key(dstar_lite_pqueue q) {
    dstar_lite_key min_key = NULL;
    min_key = (dstar_lite_key) pqueue_top_key(q->pq);
    return min_key;
}

gboolean dstar_lite_pqueue_contains(
    dstar_lite_pqueue q, const coord u) {
    if (!q || !u) return FALSE;
    return g_hash_table_contains(q->coord_to_key, u);
}
