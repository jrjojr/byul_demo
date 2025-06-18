#include "coord.h"
#include <glib.h>

coord coord_new_full(gint x, gint y) {
    coord c = g_malloc0(sizeof(coord_t));
    if (!c) return NULL;
    c->x = x;
    c->y = y;

    return c;
}

coord coord_new() {
    return coord_new_full(0, 0);
}

void coord_free(coord c) {
    if (!c) return;
    g_free(c);
}

guint coord_hash(const coord c) {
    if (!c) return 0;
    return ((guint)c->x << 16) ^ (guint)c->y;
}

gboolean coord_equal(const coord c1, const coord c2) {
    if (!c1 || !c2) return FALSE;    
    return c1->x == c2->x && c1->y == c2->y;
}

gint coord_compare(const coord c1, const coord c2) {
    if (c1 == c2) return 0;
    if (!c1) return -1;
    if (!c2) return 1;

    int d1 = abs(c1->x) + abs(c1->y);
    int d2 = abs(c2->x) + abs(c2->y);

    return (d1 > d2) - (d1 < d2);  // 빠른 비교
}

coord coord_copy(const coord c) {
    if (!c) return NULL;
    coord copy = coord_new_full(c->x, c->y);
    
    return copy;
}

// coord 관련 함수
// start----------------------------------------------------------------------
gint coord_get_x(const coord c) {
    return c ? c->x : 0;
}

void coord_set_x(coord c, gint x) {
    if (c) c->x = x;
}

gint coord_get_y(const coord c) {
    return c ? c->y : 0;
}

void coord_set_y(coord c, gint y) {
    if (c) c->y = y;
}

guint64 coord_pack(const coord c) {
    if (!c) return 0;
    return (((guint64)c->x) << 32) | (guint)(c->y & 0xffffffffU);
}

coord coord_unpack(guint64 packed) {
    gint x = (gint)(packed >> 32);
    gint y = (gint)(packed & 0xffffffffU);
    return coord_new_full(x, y);
}

void     coord_set(coord c, gint x, gint y) {
    if (c) {
        c->x = x;
        c->y = y;
    }
}

void     coord_fetch(coord c, gint* out_x, gint* out_y) {
    if (c) {
        *out_x = c->x;
        *out_y = c->y;
    } else {
        *out_x = 0;
        *out_y = 0;
    }
}
// ------------------------------------------------------------------------end
