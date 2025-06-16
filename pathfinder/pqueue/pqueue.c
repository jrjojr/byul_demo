#include "internal/pqueue.h"
#include "internal/core.h"

#include <stdlib.h>
#include <string.h>

static gint _collect_keys(gpointer key, gpointer value, gpointer userdata) {
    GList** list = (GList**)userdata;
    *list = g_list_prepend(*list, key);
    return FALSE;
}

static gint _free_queue_values(gpointer key, gpointer val, gpointer userdata) {
    GQueue* queue = (GQueue*)val;
    GDestroyNotify destroy_func = (GDestroyNotify)userdata;
    g_queue_free_full(queue, destroy_func);  // 내부 값 + 구조체 모두 free
    // g_queue_clear_full(queue, destroy_func);
    g_free(key);  // key는 g_memdup2()된 것이므로 반드시 free 필요
    return FALSE;
}

static gint _clear_queue_values(
    gpointer key, gpointer val, gpointer userdata) {

    GQueue* queue = (GQueue*)val;
    GDestroyNotify destroy_func = (GDestroyNotify)userdata;
    g_queue_clear_full(queue, destroy_func);
    return FALSE;
}

static gint find_min_key(gpointer key, gpointer val, gpointer data) {
    GQueue* q = val;
    if (!g_queue_is_empty(q)) {
        *(gpointer*)data = key;
        return TRUE;
    }
    return FALSE;
}

static gboolean callback(gpointer key, gpointer val, gpointer data) {
    GQueue* q = val;
    if (!g_queue_is_empty(q)) {
        *(gpointer*)data = key;
        return TRUE;  // stop iteration
    }
    return FALSE;
}

gboolean pqueue_find_min_key(pqueue pq, gpointer* out_key) {
    if (!pq || !pq->tree || !out_key) return FALSE;

    *out_key = NULL;

    g_tree_foreach(pq->tree, callback, out_key);
    return *out_key != NULL;
}

pqueue pqueue_new(void) {
    return pqueue_new_full(float_compare, NULL, g_free, g_free);
}

pqueue pqueue_new_full(
    GCompareDataFunc cmp, gpointer userdata, 
    GDestroyNotify key_destroy, GDestroyNotify value_destroy) {

    pqueue pq = g_new0(pqueue_t, 1);
    pq->compare = cmp;
    pq->userdata = userdata;
    pq->value_destroy = value_destroy;
    pq->tree = g_tree_new_full(
        cmp, userdata, key_destroy, (GDestroyNotify)g_queue_free);
    return pq;
}

void pqueue_free(pqueue pq) {
    if (!pq) return;
    if (pq->tree) {
        // g_tree_foreach(pq->tree, _free_queue_values, pq->value_destroy);        
        g_tree_foreach(pq->tree, _clear_queue_values, pq->value_destroy);
        g_tree_destroy(pq->tree);
    }
    g_free(pq);
}

void pqueue_push(pqueue pq, gpointer key, gsize key_size,
                 gpointer value, gsize value_size) {
    if (!pq || !key || !value || key_size == 0 || value_size == 0)
        return;

    GQueue* q = g_tree_lookup(pq->tree, key);
    if (!q) {
        gpointer new_key = g_memdup2(key, key_size);
        q = g_queue_new();
        // g_tree_insert(pq->tree, new_key, q);
        g_tree_replace(pq->tree, new_key, q);
    }

    gpointer new_value = g_memdup2(value, value_size);
    g_queue_push_tail(q, new_value);
}


gpointer pqueue_peek(pqueue pq) {
    gpointer min_key = NULL;
    g_tree_foreach(pq->tree, find_min_key, &min_key);
    if (min_key) {
        GQueue* q = g_tree_lookup(pq->tree, min_key);
        return g_queue_peek_head(q);
    }
    return NULL;
}

gpointer pqueue_pop(pqueue pq) {
    if (!pq || !pq->tree)
        return NULL;

    gpointer min_key = NULL;
    g_tree_foreach(pq->tree, find_min_key, &min_key);
    if (!min_key)
        return NULL;

    GQueue* q = g_tree_lookup(pq->tree, min_key);
    if (!q || g_queue_is_empty(q))
        return NULL;

    gpointer result = g_queue_pop_head(q);

    if (g_queue_is_empty(q)) {
        g_tree_remove(pq->tree, min_key);
    }

    return result;  // 💡 호출자 책임: g_free(result)
}


gboolean pqueue_is_empty(pqueue pq) {
    return g_tree_nnodes(pq->tree) == 0;
}

gboolean pqueue_remove(pqueue pq, gpointer key, gpointer value) {
    GQueue* q = g_tree_lookup(pq->tree, key);
    if (!q) return FALSE;
    GList* node = g_queue_find(q, value);
    if (!node) return FALSE;

    if (pq->value_destroy) {
        pq->value_destroy(node->data);  // 🔥 직접 해제!
    }
    
    g_queue_delete_link(q, node);
    if (g_queue_is_empty(q)) {
        g_tree_remove(pq->tree, key);
    }
    return TRUE;
}

gboolean pqueue_remove_custom(
    pqueue pq, gpointer key, gconstpointer target_value, GCompareFunc cmp) {

    GQueue* q = g_tree_lookup(pq->tree, key);
    if (!q) return FALSE;

    GList* node = g_queue_find_custom(q, target_value, cmp);
    if (!node) return FALSE;

    if (pq->value_destroy) {
        pq->value_destroy(node->data);  // 🔥 직접 해제!
    }

    g_queue_delete_link(q, node);

    if (g_queue_is_empty(q)) {
        g_tree_remove(pq->tree, key);
    }

    return TRUE;
}


void pqueue_update(pqueue pq, gpointer old_key, gpointer new_key, 
    gsize key_size, gpointer value, gsize value_size) {

    if (pqueue_remove(pq, old_key, value)) {
        pqueue_push(pq, new_key, key_size, value, value_size);
    }
}

gboolean pqueue_contains(pqueue pq, gconstpointer key) {
    return g_tree_lookup(pq->tree, key) != NULL;
}

GList* pqueue_get_all_keys(pqueue pq) {
    if (!pq || !pq->tree) return NULL;
    GList* keys = NULL;
    g_tree_foreach(pq->tree, _collect_keys, &keys);
    return g_list_reverse(keys);
}

GQueue* pqueue_get_values(pqueue pq, gconstpointer key) {
    if (!pq || !pq->tree || !key) return NULL;
    return g_tree_lookup(pq->tree, key);
}

void pqueue_clear(pqueue pq) {
    if (!pq || !pq->tree) return;
    g_tree_foreach(pq->tree, _clear_queue_values, pq->value_destroy);
    g_tree_remove_all(pq->tree);
}

// gpointer pqueue_find_key_by_value(pqueue pq, gconstpointer value) {
//     if (!pq || !pq->tree || !value) return NULL;

//     struct {
//         gconstpointer target_value;
//         gpointer found_key;
//     } search = { value, NULL };

//     gboolean finder(gpointer key, gpointer val, gpointer userdata) {
//         GQueue* q = (GQueue*)val;
//         if (g_queue_find(q, ((typeof(search)*)userdata)->target_value)) {
//             ((typeof(search)*)userdata)->found_key = key;
//             return TRUE;
//         }
//         return FALSE;
//     }

//     g_tree_foreach(pq->tree, (GTraverseFunc)finder, &search);
//     return search.found_key;
// }

static gboolean _pqueue_find_key_by_value_callback(
    gpointer key, gpointer val, gpointer userdata) {

    struct {
        gconstpointer target_value;
        gpointer found_key;
    } *search = userdata;

    if (g_queue_find((GQueue*)val, search->target_value)) {
        search->found_key = key;
        return TRUE;
    }
    return FALSE;
}

gpointer pqueue_find_key_by_value(pqueue pq, gconstpointer value) {
    if (!pq || !pq->tree || !value) return NULL;

    struct {
        gconstpointer target_value;
        gpointer found_key;
    } search = { value, NULL };

    g_tree_foreach(pq->tree, _pqueue_find_key_by_value_callback, &search);
    return search.found_key;
}

pqueue_iter pqueue_iter_new(pqueue pq) {
    pqueue_iter iter = g_new0(pqueue_iter_t, 1);
    iter->keys = pqueue_get_all_keys(pq);
    iter->current = iter->keys;
    iter->pq = pq;
    return iter;
}

gboolean pqueue_iter_next(
    pqueue_iter iter, gpointer* out_key, gpointer* out_value) {

    if (!iter || !iter->current) return FALSE;
    *out_key = iter->current->data;
    *out_value = pqueue_get_values(iter->pq, *out_key);
    iter->current = iter->current->next;
    return TRUE;
}

void pqueue_iter_free(pqueue_iter iter) {
    if (!iter) return;
    g_list_free(iter->keys);
    g_free(iter);
}

BYUL_API gpointer pqueue_top_key(pqueue pq) {
    gpointer key = NULL;
    if (pqueue_find_min_key(pq, &key))
        return key;
    return NULL;
}
