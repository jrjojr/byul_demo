#include <glib.h>
#include "internal/core.h"

static void test_float_equal_func(void) {
    g_assert_true(float_equal(1.000001f, 1.000002f));
    g_assert_false(float_equal(1.0f, 1.1f));
}

static void test_float_compare_func(void) {
    gfloat a = 1.0f, b = 2.0f, c = 1.0f;
    g_assert_cmpint(float_compare(&a, &b, NULL), <, 0);
    g_assert_cmpint(float_compare(&b, &a, NULL), >, 0);
    g_assert_cmpint(float_compare(&a, &c, NULL), ==, 0);
}

static void test_hashset_basic_func(void) {
    GHashTable *set = hashset_new();

    g_assert_true(hashset_add(set, "apple"));
    g_assert_true(hashset_contains(set, "apple"));
    g_assert_false(hashset_add(set, "apple")); // 중복
    g_assert_cmpuint(hashset_size(set), ==, 1);
    g_assert_true(hashset_remove(set, "apple"));
    g_assert_cmpuint(hashset_size(set), ==, 0);

    hashset_free(set);
}

static void test_hashset_copy_and_equal_func(void) {
    GHashTable *a = hashset_new();
    hashset_add(a, "x");
    hashset_add(a, "y");

    GHashTable *b = hashset_copy(a);
    g_assert_true(hashset_equal(a, b));

    hashset_add(b, "z");
    g_assert_false(hashset_equal(a, b));

    hashset_free(a);
    hashset_free(b);
}

int main(int argc, char **argv) {
    g_test_init(&argc, &argv, NULL);

    g_test_add_func("/core/float_equal", test_float_equal_func);
    g_test_add_func("/core/float_compare", test_float_compare_func);
    g_test_add_func("/core/hashset_basic", test_hashset_basic_func);

    g_test_add_func("/core/hashset_copy_equal", 
        test_hashset_copy_and_equal_func);

    return g_test_run();
}
