#include <glib.h>
#include "internal/core.h"
#include "internal/map.h"
#include "internal/coord.h"

static void test_map_block_and_check(void) {
    // map m = map_new_full(10, 10, MAP_NEIGHBOR_4);
    map m = map_new();

    g_assert_true(map_block_coord(m, 6, 6));
    g_assert_true(map_is_blocked(m, 6, 6));

    g_assert_false(map_is_blocked(m, 5, 5));

    map_free(m);
}

static void test_map_unblock(void) {
    // map m = map_new_full(10, 10, MAP_NEIGHBOR_4);
    map m = map_new();

    g_assert_true(map_block_coord(m, 4, 4));
    g_assert_true(map_is_blocked(m, 4, 4));

    g_assert_true(map_unblock_coord(m, 4, 4));
    g_assert_false(map_is_blocked(m, 4, 4));

    map_free(m);
}

static void test_map_clear_all(void) {
    // map m = map_new_full(5, 5, MAP_NEIGHBOR_4);
    map m = map_new();

    for (int x = 0; x < 5; x++) {
        for (int y = 1; y < 10; y++) {
            map_block_coord(m, x, y);
        }
    }

    g_assert_true(map_is_blocked(m, 2, 2));
    map_clear(m);
    g_assert_false(map_is_blocked(m, 2, 2));

    map_free(m);
}

static void test_map_neighbors(void) {
    // map m = map_new_full(5, 5, MAP_NEIGHBOR_4);
    map m = map_new();

    // (2, 2)의 이웃은 (2,1), (1,2), (3,2), (2,3)
    // 이 중 (3,2), (2,3)은 차단
    map_block_coord(m, 3, 2);
    map_block_coord(m, 2, 3);

    GList* neighbors = map_clone_neighbors(m, 2, 2);
    g_assert_nonnull(neighbors);

    gint expected = 0;

    if (map_get_neighbor_mode(m) == MAP_NEIGHBOR_8) {
        // 8방향 중 (2,1), (1,2), (1,1), (1,3), (3,1), (3,3) 등 총 6개가 유효하다고 가정
        expected = 6;
    } else {
        // 4방향 중 (2,1), (1,2)만 유효
        expected = 2;
    }

    g_assert_cmpint(g_list_length(neighbors), ==, expected);


    // 좌표값 확인
    gboolean has_21 = FALSE, has_12 = FALSE;

    for (GList* l = neighbors; l != NULL; l = l->next) {
        coord c = (coord)(l->data);
        if (coord_get_x(c) == 2 && coord_get_y(c) == 1) has_21 = TRUE;
        if (coord_get_x(c) == 1 && coord_get_y(c) == 2) has_12 = TRUE;
    }

    g_assert_true(has_21);
    g_assert_true(has_12);

    g_list_free_full(neighbors, (GDestroyNotify)coord_free);
    map_free(m);
}


int main(int argc, char **argv) {
    g_test_init(&argc, &argv, NULL);

    g_test_add_func("/map/block_and_check", test_map_block_and_check);
    g_test_add_func("/map/unblock", test_map_unblock);
    g_test_add_func("/map/clear_all", test_map_clear_all);
    g_test_add_func("/map/neighbors", test_map_neighbors);

    return g_test_run();
}
