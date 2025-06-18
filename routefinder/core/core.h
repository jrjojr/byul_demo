#ifndef CORE_H
#define CORE_H

#include <glib.h>
#include <math.h>
#include "byul_config.h"

#ifdef __cplusplus
extern "C" {
#endif

/// @brief float 비교를 위한 epsilon
#define FLOAT_EPSILON 1e-5f

/// @brief float 정확도 비교 함수
BYUL_API gboolean float_equal(gfloat a, gfloat b);

/// @brief float 비교 함수 (우선순위용)
// typedef gint (*GCompareDataFunc) (
//     gconstpointer a, gconstpointer b, gpointer userdata);
BYUL_API gint float_compare(
    gconstpointer a, gconstpointer b, gpointer userdata);

BYUL_API gint int_compare(
    gconstpointer a, gconstpointer b, gpointer userdata);

BYUL_API GHashTable* hashset_new(void);

BYUL_API void hashset_free(GHashTable* set);

/// 원소 추가
BYUL_API gboolean hashset_add(GHashTable* set, gpointer item);

/// 원소 포함 여부
BYUL_API gboolean hashset_contains(GHashTable* set, gconstpointer item);

/// 원소 제거
BYUL_API gboolean hashset_remove(GHashTable* set, gconstpointer item);

/// 집합 크기
BYUL_API guint hashset_size(GHashTable* set);

/// 모든 원소 제거
BYUL_API void hashset_clear(GHashTable* set);

/// 하나 꺼내기 (peek)
BYUL_API gpointer hashset_peek(GHashTable* set);

/// 하나 꺼내서 제거 (pop)
BYUL_API gpointer hashset_pop(GHashTable* set);

/// foreach 순회
BYUL_API void hashset_foreach(GHashTable* set, GHFunc func, gpointer userdata);

/// 해시셋 복제
BYUL_API GHashTable* hashset_copy(GHashTable* original);

BYUL_API gboolean hashset_equal(gconstpointer a, gconstpointer b);

BYUL_API guint hashset_hash(gconstpointer key);

/// 합집합 생성
BYUL_API GHashTable* hashset_union(GHashTable* a, GHashTable* b);

/// 교집합 생성
BYUL_API GHashTable* hashset_intersect(GHashTable* a, GHashTable* b);

/// 차집합 (a - b)
BYUL_API GHashTable* hashset_difference(GHashTable* a, GHashTable* b);

// 해시테이블의 깊은복사이다
BYUL_API GHashTable* g_hash_table_copy_deep(
    const GHashTable *src,
    GHashFunc hash_func,
    GEqualFunc equal_func,

    GCopyFunc key_copy_func,
    GDestroyNotify key_destroy_func,
    
    GCopyFunc value_copy_func,
    GDestroyNotify value_destroy_func
);

#ifdef __cplusplus
}
#endif

#endif // CORE_H
