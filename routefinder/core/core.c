#include "internal/core.h"

#include <stdlib.h>
#include <math.h>

gboolean float_equal(gfloat a, gfloat b) {
    if (a == b) return TRUE;
    gfloat diff = fabsf(a - b);
    gfloat largest = fmaxf(fabsf(a), fabsf(b));
    return diff <= FLOAT_EPSILON * largest;
}

gint float_compare(
    gconstpointer a, gconstpointer b, gpointer userdata) {
        
    float fa = *(float*)a;
    float fb = *(float*)b;

    if (float_equal(fa, fb)) return 0;
    return (fa < fb) ? -1 : 1;
}

gint int_compare(
    gconstpointer a, gconstpointer b, gpointer userdata) {

    int ia = *(int*)a;
    int ib = *(int*)b;
    return (ia > ib) - (ia < ib);
}

GHashTable* g_hash_table_copy_deep(
    const GHashTable *src,
    GHashFunc hash_func,
    GEqualFunc equal_func,

    GCopyFunc key_copy_func,
    GDestroyNotify key_destroy_func,

    GCopyFunc value_copy_func,
    GDestroyNotify value_destroy_func
    ) {
        
    GHashTable* dst = g_hash_table_new_full(
        hash_func,
        equal_func,
        key_destroy_func,
        value_destroy_func
    );

    GHashTableIter iter;
    gpointer key, value;

    g_hash_table_iter_init(&iter, (GHashTable*)src);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        gpointer new_key = key_copy_func ? key_copy_func(key, NULL) : key;
        gpointer new_value = \
            value_copy_func ? value_copy_func(value, NULL) : value;

        g_hash_table_replace(dst, new_key, new_value);
    }

    return dst;
}

/// 새로운 hashset 생성 (기본 g_direct 기반)
GHashTable* hashset_new(void) {
    return g_hash_table_new(g_direct_hash, g_direct_equal);
}

/// 메모리 해제
void hashset_free(GHashTable* set) {
    if (set) g_hash_table_destroy(set);
}

/// 원소 추가
gboolean hashset_add(GHashTable* set, gpointer item) {
    return g_hash_table_add(set, item);
}

/// 원소 포함 여부
gboolean hashset_contains(GHashTable* set, gconstpointer item) {
    return g_hash_table_contains(set, item);
}

/// 원소 제거
gboolean hashset_remove(GHashTable* set, gconstpointer item) {
    return g_hash_table_remove(set, item);
}

/// 집합 크기
guint hashset_size(GHashTable* set) {
    return g_hash_table_size(set);
}

/// 모든 원소 제거
void hashset_clear(GHashTable* set) {
    if (set) g_hash_table_remove_all(set);
}

/// 하나 꺼내기 (peek)
gpointer hashset_peek(GHashTable* set) {
    if (!set || g_hash_table_size(set) == 0) return NULL;
    GHashTableIter iter;
    gpointer key = NULL;
    g_hash_table_iter_init(&iter, set);
    if (g_hash_table_iter_next(&iter, &key, NULL)) {
        return key;
    }
    return NULL;
}

/// 하나 꺼내서 제거 (pop)
gpointer hashset_pop(GHashTable* set) {
    if (!set || g_hash_table_size(set) == 0) return NULL;
    GHashTableIter iter;
    gpointer key = NULL;
    g_hash_table_iter_init(&iter, set);
    if (g_hash_table_iter_next(&iter, &key, NULL)) {
        g_hash_table_remove(set, key);
        return key;
    }
    return NULL;
}

/// foreach 순회
void hashset_foreach(GHashTable* set, GHFunc func, gpointer userdata) {
    if (set && func) g_hash_table_foreach(set, func, userdata);
}

static GHashTable* hashset_copy_with_func(GHashTable* original,
                                   GHashFunc hash_func,
                                   GEqualFunc equal_func) {
    if (!original || !hash_func || !equal_func) return NULL;

    GHashTable* copy = g_hash_table_new(hash_func, equal_func);

    GHashTableIter iter;
    gpointer key;
    g_hash_table_iter_init(&iter, original);
    while (g_hash_table_iter_next(&iter, &key, NULL)) {
        g_hash_table_add(copy, key);
    }

    return copy;
}

GHashTable* hashset_copy(GHashTable* original) {
    // 기본 문자열 해시셋인 경우
    return hashset_copy_with_func(original, g_str_hash, g_str_equal);
}

gboolean hashset_equal(gconstpointer a, gconstpointer b) {
    const GHashTable* set_a = (const GHashTable*)a;
    const GHashTable* set_b = (const GHashTable*)b;

    if (g_hash_table_size((GHashTable*)set_a) !=
        g_hash_table_size((GHashTable*)set_b)) {
        return FALSE;
    }

    GHashTableIter iter;
    gpointer key;
    g_hash_table_iter_init(&iter, (GHashTable*)set_a);
    while (g_hash_table_iter_next(&iter, &key, NULL)) {
        if (!g_hash_table_contains((GHashTable*)set_b, key)) {
            return FALSE;
        }
    }

    return TRUE;
}

/// GHashFunc 래퍼: g_direct_hash 사용
guint hashset_hash(gconstpointer key) {
    return g_direct_hash(key);
}

/// 합집합 생성
GHashTable* hashset_union(GHashTable* a, GHashTable* b) {
    GHashTable* result = hashset_new();
    GHashTableIter iter;
    gpointer key;

    g_hash_table_iter_init(&iter, a);
    while (g_hash_table_iter_next(&iter, &key, NULL)) {
        g_hash_table_add(result, key);
    }

    g_hash_table_iter_init(&iter, b);
    while (g_hash_table_iter_next(&iter, &key, NULL)) {
        g_hash_table_add(result, key);
    }

    return result;
}

/// 교집합 생성
GHashTable* hashset_intersect(GHashTable* a, GHashTable* b) {
    GHashTable* result = hashset_new();
    GHashTableIter iter;
    gpointer key;

    g_hash_table_iter_init(&iter, a);
    while (g_hash_table_iter_next(&iter, &key, NULL)) {
        if (g_hash_table_contains(b, key)) {
            g_hash_table_add(result, key);
        }
    }

    return result;
}

/// 차집합 (a - b)
GHashTable* hashset_difference(GHashTable* a, GHashTable* b) {
    GHashTable* result = hashset_new();
    GHashTableIter iter;
    gpointer key;

    g_hash_table_iter_init(&iter, a);
    while (g_hash_table_iter_next(&iter, &key, NULL)) {
        if (!g_hash_table_contains(b, key)) {
            g_hash_table_add(result, key);
        }
    }

    return result;
}    
