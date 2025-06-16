#include "internal/map.h"
#include "internal/core.h"
#include "internal/coord.h"

tile tile_new(void) {
    return tile_new_full(0, 0, 0, 0);
}

tile tile_new_full(guint8 type, gint8 height, guint8 flags, guint8 extra) {
    tile t = g_new0(tile_t, 1);
    t->type = type;
    t->height = height;
    t->flags = flags;
    t->extra = extra;
    return t;
}

void tile_free(tile t) {
    if (t) g_free(t);
}

map map_new(void) {
    return map_new_full(0, 0, MAP_NEIGHBOR_4);
}

map map_new_full(gint width, gint height, map_neighbor_mode_t mode) {
    map m = g_malloc0(sizeof(map_t));
    if (!m) return NULL;

    m->width = width;
    m->height = height;
    m->mode = mode;

    m->blocked_coords = g_hash_table_new_full(
        (GHashFunc) coord_hash,
        (GEqualFunc) coord_equal,
        (GDestroyNotify) coord_free,
        NULL
    );

    // 타일 해시테이블: key = coord*, value = tile_t*
    m->tiles = g_hash_table_new_full(
        (GHashFunc) coord_hash,
        (GEqualFunc) coord_equal,
        (GDestroyNotify) coord_free,
        (GDestroyNotify) tile_free   // 정확한 타입
    );

    // 기본 타일 값 지정
    m->default_tile.type = 0;
    m->default_tile.height = 0;
    m->default_tile.flags = 0;
    m->default_tile.extra = 0;

    return m;
}

void map_free(const map s) {
    if (!s) return;
    if (s->blocked_coords) g_hash_table_destroy(s->blocked_coords);
    if (s->tiles) g_hash_table_destroy(s->tiles);
    g_free(s);
}

guint map_hash(const map m) {
    if (!m) return 0;
    return (guint)(guintptr)m;    
}

gboolean map_equal(const map ma, const map mb) {
    if (!ma || !mb) return FALSE;
    return g_direct_equal(ma, mb);    
}

map map_copy(const map m) {
    if (!m) return NULL;

    map c = map_new();
    c->width = m->width;
    c->height = m->height;
    c->mode = m->mode;

    c->blocked_coords = g_hash_table_copy_deep(
        m->blocked_coords,
        (GHashFunc) coord_hash, 
        (GEqualFunc) coord_equal, 
        (GCopyFunc) coord_copy,
        (GDestroyNotify) coord_free, 
         NULL, NULL);
    return c;
}

// 전용 함수들

gint map_get_width(const map m) {
    return m ? m->width : 0;
}

void map_set_width(map m, gint width) {
    if (m) m->width = width;
}

gint map_get_height(const map m) {
    return m ? m->height : 0;
}

void map_set_height(map m, gint height) {
    if (m) m->height = height;
}

map_neighbor_mode_t map_get_neighbor_mode(const map m) {
    return m ? m->mode : MAP_NEIGHBOR_4;
}

void map_set_neighbor_mode(map m, map_neighbor_mode_t mode) {
    if (m) m->mode = mode;
}

const GHashTable* map_get_blocked_coords(const map s) {
    return s ? s->blocked_coords : NULL;
}

gboolean map_block_coord(map s, gint x, gint y) {
    if (!s) return FALSE;
    coord c = coord_new_full(x, y);
    return g_hash_table_add(s->blocked_coords, c);
}

gboolean map_unblock_coord(map s, gint x, gint y) {
    if (!s) return FALSE;
    coord c = coord_new_full(x, y);    
    gboolean result = g_hash_table_remove(s->blocked_coords, c);
    coord_free(c); // 생성한 임시 coord는 제거 필요    
    return result;
}

// gboolean map_is_inside(const map s, gint x, gint y) {
//     if (!s) return FALSE;
//     return (x >= 0 && x < s->width && y >= 0 && y < s->height);
// }

gboolean map_is_inside(const map s, gint x, gint y) {
    if (!s) return FALSE;

    gboolean x_ok = (s->width == 0 || (x >= 0 && x < s->width));
    gboolean y_ok = (s->height == 0 || (y >= 0 && y < s->height));

    return x_ok && y_ok;
}

GList* map_clone_neighbors(const map m, gint x, gint y) {
    if (!m) return NULL;

    GList* neighbors = NULL;

    static const gint dx4[] = { 0, -1, 1, 0 };
    static const gint dy4[] = { -1, 0, 0, 1 };

    static const gint dx8[] = { 0, -1, 1, 0, -1, -1, 1, 1 };
    static const gint dy8[] = { -1, 0, 0, 1, -1, 1, -1, 1 };

    const gint* dx = (m->mode == MAP_NEIGHBOR_8) ? dx8 : dx4;
    const gint* dy = (m->mode == MAP_NEIGHBOR_8) ? dy8 : dy4;
    gint count = (m->mode == MAP_NEIGHBOR_8) ? 8 : 4;

    for (gint i = 0; i < count; ++i) {
        gint nx = x + dx[i];
        gint ny = y + dy[i];

        if (!map_is_inside(m, nx, ny)) continue;
        if (map_is_blocked(m, nx, ny)) continue;

        coord neighbor = coord_new_full(nx, ny);
        neighbors = g_list_append(neighbors, neighbor);
    }

    return neighbors;
}

void map_clear(map s) {
    if (!s || !s->blocked_coords) return;
    g_hash_table_remove_all(s->blocked_coords);
}

/** 내부 유틸: 좌표에 해당하는 tile 가져오기 */
static const tile_t* map_lookup_tile(const map m, const coord c) {
    if (!m || !c) return NULL;
    tile_t* t = g_hash_table_lookup(m->tiles, c);
    return t ? t : &m->default_tile;
}

gboolean map_set_tile(map m, coord c, const tile_t* tile) {
    if (!m || !c || !tile) return FALSE;

    tile_t* copied = g_malloc(sizeof(tile_t));
    *copied = *tile;

    g_hash_table_replace(m->tiles, coord_copy(c), copied);
    return TRUE;
}

guint8 map_get_tile_type(const map m, gint x, gint y) {
    if (!m) return 0;
    coord c = coord_new_full(x, y);
    const tile_t* t = map_lookup_tile(m, c);
    guint8 type = t->type;
    coord_free(c);
    return type;
}

gint8 map_get_tile_height(const map m, gint x, gint y) {
    if (!m) return 0;
    coord c = coord_new_full(x, y);
    const tile_t* t = map_lookup_tile(m, c);
    gint8 height = t->height;
    coord_free(c);
    return height;
}

guint8 map_get_tile_flags(const map m, gint x, gint y) {
    if (!m) return 0;
    coord c = coord_new_full(x, y);
    const tile_t* t = map_lookup_tile(m, c);
    guint8 flags = t->flags;
    coord_free(c);
    return flags;
}

guint8 map_get_tile_extra(const map m, gint x, gint y) {
    if (!m) return 0;
    coord c = coord_new_full(x, y);
    const tile_t* t = map_lookup_tile(m, c);
    guint8 extra = t->extra;
    coord_free(c);
    return extra;
}

gboolean map_is_blocked(const map m, gint x, gint y) {
    if (!m) return FALSE;
    coord c = coord_new_full(x, y);
    gboolean result = g_hash_table_contains(m->blocked_coords, c);
    coord_free(c); // 임시 coord 해제
    return result;
}

GList* map_clone_neighbors_all(const map m, gint x, gint y) {
    if (!m) return NULL;

    GList* neighbors = NULL;

    static const gint dx4[] = { 0, -1, 1, 0 };
    static const gint dy4[] = { -1, 0, 0, 1 };

    static const gint dx8[] = { 0, -1, 1, 0, -1, -1, 1, 1 };
    static const gint dy8[] = { -1, 0, 0, 1, -1, 1, -1, 1 };

    const gint* dx = (m->mode == MAP_NEIGHBOR_8) ? dx8 : dx4;
    const gint* dy = (m->mode == MAP_NEIGHBOR_8) ? dy8 : dy4;
    gint count = (m->mode == MAP_NEIGHBOR_8) ? 8 : 4;

    for (gint i = 0; i < count; ++i) {
        gint nx = x + dx[i];
        gint ny = y + dy[i];

        if (!map_is_inside(m, nx, ny)) continue;

        coord neighbor = coord_new_full(nx, ny);
        neighbors = g_list_append(neighbors, neighbor);
    }

    return neighbors;
}

GList* map_clone_neighbors_all_range(const map m, 
    gint x, gint y, gint range) {
        
    if (!m || range < 0) return NULL;

    if (range == 0) return map_clone_neighbors_all(m, x, y);

    GHashTable* seen = g_hash_table_new_full(
        (GHashFunc)coord_hash,
        (GEqualFunc)coord_equal,
        (GDestroyNotify)coord_free,
        NULL
    );

    for (gint dx = -range; dx <= range; dx++) {
        for (gint dy = -range; dy <= range; dy++) {
            gint cx = x + dx;
            gint cy = y + dy;

            if (!map_is_inside(m, cx, cy)) continue;

            GList* partial = map_clone_neighbors_all(m, cx, cy);

            for (GList* l = partial; l; l = l->next) {
                coord c = (coord)l->data;
                if (!g_hash_table_contains(seen, c)) {
                    g_hash_table_add(seen, coord_copy(c));
                }
            }

            g_list_free_full(partial, (GDestroyNotify)coord_free);
        }
    }

    // GHashTable → GList 변환
    GList* result = NULL;
    GHashTableIter iter;
    gpointer value;
    g_hash_table_iter_init(&iter, seen);
    while (g_hash_table_iter_next(&iter, &value, NULL)) {
        result = g_list_prepend(result, coord_copy((coord)value));
    }

    g_hash_table_destroy(seen);
    return result;
}
