#ifndef PQUEUE_H
#define PQUEUE_H

#include <glib.h>
#include <math.h>
#include "byul_config.h"

#ifdef __cplusplus
extern "C" {
#endif

struct s_pqueue {
    GTree* tree;  // key: gpointer, value: GQueue*
    GCompareDataFunc compare;
    gpointer userdata;
    GDestroyNotify value_destroy;
};

typedef struct s_pqueue pqueue_t;
typedef pqueue_t* pqueue;

struct s_pqueue_iter {
    GList* keys;
    GList* current;
    pqueue pq;
};

typedef struct s_pqueue_iter pqueue_iter_t;
typedef pqueue_iter_t* pqueue_iter;

/// @brief float 우선순위 큐 기본 생성자 (float 비교 사용)
BYUL_API pqueue pqueue_new(void);

BYUL_API pqueue pqueue_new_full(
    GCompareDataFunc cmp, gpointer userdata, 
    GDestroyNotify  key_destroy, GDestroyNotify value_destroy);

/// @brief 큐 해제
BYUL_API void pqueue_free(pqueue pq);

BYUL_API gboolean pqueue_find_min_key(pqueue pq, gpointer* out_key);

/// @brief key에 해당하는 우선순위로 value 삽입
// BYUL_API void pqueue_push(pqueue pq, gpointer key, gpointer value);

BYUL_API void pqueue_push(pqueue pq, gpointer key, gsize key_size, 
    gpointer value, gsize value_size);

/// @brief 현재 최소 우선순위의 값 조회 (삭제하지 않음)
BYUL_API gpointer pqueue_peek(pqueue pq);

/// @brief 현재 최소 우선순위의 값 pop (삭제함)
BYUL_API gpointer pqueue_pop(pqueue pq);

/// @brief 큐가 비었는지 확인
BYUL_API gboolean pqueue_is_empty(pqueue pq);

/// @brief 주어진 key, value 쌍을 큐에서 제거
BYUL_API gboolean pqueue_remove(pqueue pq, gpointer key, gpointer value);

BYUL_API gboolean pqueue_remove_custom(
    pqueue pq, gpointer key, gconstpointer target_value, GCompareFunc cmp);

/// @brief 기존 key를 제거하고 새로운 key로 다시 삽입
// BYUL_API void pqueue_update(
//     pqueue pq, gpointer old_key, gpointer new_key, gpointer value);

BYUL_API void pqueue_update(
    pqueue pq, gpointer old_key, gpointer new_key, gsize key_size, 
    gpointer value, gsize value_size);    

/// @brief 주어진 key에 해당하는 항목이 큐에 존재하는지 확인
BYUL_API gboolean pqueue_contains(pqueue pq, gconstpointer key);

/// @brief 주어진 key에 해당하는 값 리스트(GQueue*)를 반환
BYUL_API GQueue* pqueue_get_values(pqueue pq, gconstpointer key);

/// @brief 현재 큐에 존재하는 모든 key를 GList* 형태로 반환
BYUL_API GList* pqueue_get_all_keys(pqueue pq);

/// @brief 큐의 모든 항목을 제거하고 비웁니다.
BYUL_API void pqueue_clear(pqueue pq);

/// @brief 해당 value를 포함하고 있는 key를 찾아 반환 (없으면 NULL)
BYUL_API gpointer pqueue_find_key_by_value(pqueue pq, gconstpointer value);

/// @brief 반복자 생성
BYUL_API pqueue_iter pqueue_iter_new(pqueue pq);

/// @brief 반복자의 다음 key/value 쌍을 반환 (value는 GQueue*)
BYUL_API gboolean pqueue_iter_next(
    pqueue_iter iter, gpointer* out_key, gpointer* out_value);

/// @brief 반복자 해제
BYUL_API void pqueue_iter_free(pqueue_iter iter);

BYUL_API gpointer pqueue_top_key(pqueue pq);

#ifdef __cplusplus
}
#endif

#endif // PQUEUE_H
