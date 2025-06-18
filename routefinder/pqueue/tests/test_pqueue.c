#include "internal/pqueue.h"
#include "internal/coord.h"
#include "internal/core.h"

#include <glib.h>
#include <stdlib.h>
#include <string.h>

#define FLOAT(v) ({ float* _f = g_new(float, 1); *_f = (v); _f; })
#define STR(v) g_strdup(v)

static void value_destroy_func(gpointer data) {
    g_free(data);
}

static void coord_value_destroy(gpointer data) {
    coord_free((coord)data);
}

typedef struct {
    int offset;
} OffsetContext;

static gint offset_compare(gconstpointer a, gconstpointer b, gpointer userdata) {
    const OffsetContext* ctx = (const OffsetContext*)userdata;
    float af = *((float*)a) + ctx->offset;
    float bf = *((float*)b) + ctx->offset;
    return (af > bf) - (af < bf);
}

static void test_basic_push_peek_pop(void) {
    pqueue pq = pqueue_new_full(float_compare, NULL, g_free, g_free);

    float* k1 = FLOAT(2.0f);
    float* k2 = FLOAT(1.0f);
    float* k3 = FLOAT(3.0f);

    char* v1 = STR("middle");
    char* v2 = STR("low");
    char* v3 = STR("high");

    pqueue_push(pq, k1, sizeof(float), v1, strlen(v1) + 1);
    pqueue_push(pq, k2, sizeof(float), v2, strlen(v2) + 1);
    pqueue_push(pq, k3, sizeof(float), v3, strlen(v3) + 1);

    g_free(k1); g_free(k2); g_free(k3);
    g_free(v1); g_free(v2); g_free(v3);

    // 반환값 복사본 → 직접 해제 필요
    char* out1 = pqueue_peek(pq);
    g_assert_cmpstr(out1, ==, "low");

    char* out2 = pqueue_pop(pq);  // "low"
    // char* out3 = pqueue_pop(pq);  // "middle"
    // char* out4 = pqueue_pop(pq);  // "high"

    g_assert_cmpstr(out2, ==, "low");
    // g_assert_cmpstr(out3, ==, "middle");
    // g_assert_cmpstr(out4, ==, "high");

    g_free(out2);
    // g_free(out3);
    // g_free(out4);

    // g_assert_true(pqueue_is_empty(pq));
    pqueue_free(pq);
}

static void test_remove_entry(void) {
    pqueue pq = pqueue_new_full(float_compare, NULL, g_free, g_free);

    float* k1 = FLOAT(1.0f);
    float* k2 = FLOAT(2.0f);
    float* k3 = FLOAT(3.0f);

    char* v1 = STR("low");
    char* v2 = STR("middle");
    char* v3 = STR("high");

    pqueue_push(pq, k1, sizeof(float), v1, strlen(v1) + 1);
    pqueue_push(pq, k2, sizeof(float), v2, strlen(v2) + 1);
    pqueue_push(pq, k3, sizeof(float), v3, strlen(v3) + 1);

    g_free(k1); g_free(k2); g_free(k3);
    g_free(v1); g_free(v2); g_free(v3);

    // 중간 값 제거
    float key2 = 2.0f;
    char* target = "middle";

    // gboolean removed = pqueue_remove(pq, &key2, target);
    gboolean removed = pqueue_remove_custom(pq, &key2, target, (GCompareFunc)strcmp);

    g_assert_true(removed);

    // 나머지 확인
    char* out1 = pqueue_pop(pq);
    char* out2 = pqueue_pop(pq);

    g_assert_cmpstr(out1, ==, "low");
    g_assert_cmpstr(out2, ==, "high");

    g_free(out1);
    g_free(out2);

    g_assert_true(pqueue_is_empty(pq));
    pqueue_free(pq);
}


int main(int argc, char* argv[]) {
    g_test_init(&argc, &argv, NULL);

    g_test_add_func("/pqueue/basic_push_peek_pop", test_basic_push_peek_pop);
    g_test_add_func("/pqueue/remove_entry", test_remove_entry);


    return g_test_run();
}
