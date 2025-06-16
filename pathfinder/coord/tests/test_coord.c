#include <glib.h>
#include "internal/coord.h"

static void test_coord_create_free(void) {
    coord c = coord_new_full(10, 20);
    g_assert_nonnull(c);
    g_assert_cmpint(coord_get_x(c), ==, 10);
    g_assert_cmpint(coord_get_y(c), ==, 20);
    coord_free(c);
}

static void test_coord_hash_equal_copy(void) {
    coord c1 = coord_new_full(5, 5);
    coord c2 = coord_copy(c1);
    g_assert_true(coord_equal(c1, c2));
    g_assert_cmpuint(coord_hash(c1), ==, coord_hash(c2));
    coord_free(c1);
    coord_free(c2);
}

static void test_coord_pack_unpack(void) {
    coord c = coord_new_full(42, 84);
    guint64 packed = coord_pack(c);
    coord c2 = coord_unpack(packed);
    g_assert_true(coord_equal(c, c2));
    coord_free(c);
    coord_free(c2);
}

int main(int argc, char **argv) {
    g_test_init(&argc, &argv, NULL);
    g_test_add_func("/coord/create_free", test_coord_create_free);
    g_test_add_func("/coord/hash_equal_copy", test_coord_hash_equal_copy);
    g_test_add_func("/coord/pack_unpack", test_coord_pack_unpack);

    return g_test_run();
}