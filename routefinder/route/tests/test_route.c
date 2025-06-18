#include <glib.h>
#include "internal/route.h"
#include "internal/coord.h"

static void test_route_creation_and_basic_ops() {
    route p = route_new();
    g_assert_nonnull(p);
    g_assert_cmpint(route_get_cost(p), ==, 0.0f);
    g_assert_false(route_get_success(p));

    coord a = coord_new_full(1, 2);
    coord b = coord_new_full(2, 2);
    coord c = coord_new_full(3, 2);

    route_add_coord(p, a);
    route_add_coord(p, b);
    route_add_coord(p, c);

    GList* coords = route_get_coords(p);
    g_assert_cmpint(g_list_length(coords), ==, 3);
    g_assert_true(coord_equal(coords->data, a));
    g_assert_true(coord_equal(g_list_last(coords)->data, c));

    coord_free(a);
    coord_free(b);
    coord_free(c);

    route_free(p);
}

static void test_route_visited_logging() {
    route p = route_new();

    coord a = coord_new_full(5, 5);
    coord b = coord_new_full(6, 5);
    coord c = coord_new_full(7, 5);

    route_add_visited(p, a);
    route_add_visited(p, b);
    route_add_visited(p, a);  // visit a again

    GHashTable* visited_count = route_get_visited_count(p);
    g_assert_cmpint(GPOINTER_TO_INT(g_hash_table_lookup(visited_count, a)), ==, 2);
    g_assert_cmpint(GPOINTER_TO_INT(g_hash_table_lookup(visited_count, b)), ==, 1);

    GList* order = route_get_visited_order(p);
    g_assert_cmpint(g_list_length(order), ==, 3);
    g_assert_true(coord_equal(order->data, a));
    g_assert_true(coord_equal(g_list_last(order)->data, a));

    coord_free(a);
    coord_free(b);
    coord_free(c);
    route_free(p);
}

static void test_route_get_coord_at() {
    route p = route_new();
    coord a = coord_new_full(0, 0);
    coord b = coord_new_full(1, 0);
    coord c = coord_new_full(2, 0);
    route_add_coord(p, a);
    route_add_coord(p, b);
    route_add_coord(p, c);

    coord r1 = route_get_coord_at(p, 0);
    coord r2 = route_get_coord_at(p, 1);
    coord r3 = route_get_coord_at(p, 2);
    g_assert_true(coord_equal(r1, a));
    g_assert_true(coord_equal(r2, b));
    g_assert_true(coord_equal(r3, c));

    coord r_invalid = route_get_coord_at(p, 10);
    g_assert_null(r_invalid);

    coord_free(a);
    coord_free(b);
    coord_free(c);
    route_free(p);
}

void test_route_direction_and_angle() {
    route p = route_new();
    coord a = coord_new_full(1, 1);
    coord b = coord_new_full(2, 1);
    coord c = coord_new_full(3, 2);
    route_add_coord(p, a);
    route_add_coord(p, b);
    route_add_coord(p, c);

    coord vec1 = route_look_at(p, 0);
    g_assert_cmpint(vec1->x, ==, 1);
    g_assert_cmpint(vec1->y, ==, 0);

    route_dir_t dir1 = route_get_direction_enum(vec1);
    g_assert_cmpint(dir1, ==, ROUTE_DIR_RIGHT);

    route_dir_t dir2 = route_get_direction(p, 0);
    g_assert_cmpint(dir2, ==, ROUTE_DIR_RIGHT);

    coord from = coord_new_full(2, 2);
    coord to1 = coord_new_full(3, 2);  // → RIGHT
    coord to2 = coord_new_full(2, 3);  // ↓ DOWN → 다른 방향

    route_update_average_vector(p, from, to1);

    gfloat angle;
    gboolean changed = route_has_changed_with_angle(
        p, from, to2, 10.0f, &angle);

    g_assert_true(changed);
    g_assert_cmpfloat(angle, >=, 89.0f);

    coord_free(vec1);
    coord_free(from);
    coord_free(to1);
    coord_free(to2);
    coord_free(a);
    coord_free(b);
    coord_free(c);
    route_free(p);
}

static void test_route_index_based_angle_analysis() {
    route p = route_new();

    coord c1 = coord_new_full(1, 1);
    coord c2 = coord_new_full(2, 1);
    coord c3 = coord_new_full(3, 2);

    // 예시 경로: (1,1) -> (2,1) -> (3,2)
    route_add_coord(p, c1); // index 0
    route_add_coord(p, c2); // index 1
    route_add_coord(p, c3); // index 2

    // 평균 벡터 갱신
    route_update_average_vector_by_index(p, 0, 1);  // (1,0)

    gfloat angle;
    gboolean changed = route_has_changed_with_angle_by_index(
        p, 1, 2, 5.0f, &angle);

    g_assert_true(changed);
    g_assert_cmpfloat(angle, >, 0.0f);

    // 예외 처리 테스트: 인덱스 오류
    g_assert_false(route_has_changed_by_index(p, 10, 11, 5.0f));
    g_assert_false(route_has_changed_with_angle_by_index(
        p, 10, 11, 5.0f, &angle));

    coord_free(c1);
    coord_free(c2);
    coord_free(c3);
    route_free(p);
}


int main(int argc, char** argv) {
    g_test_init(&argc, &argv, NULL);

    g_test_add_func("/route/basic_ops", test_route_creation_and_basic_ops);
    g_test_add_func("/route/visited_tracking", test_route_visited_logging);
    g_test_add_func("/route/get_coord_at", test_route_get_coord_at);
    g_test_add_func("/route/direction_and_angle", test_route_direction_and_angle);    
    g_test_add_func("/route/index_angle_analysis", 
        test_route_index_based_angle_analysis);    

    return g_test_run();
}
