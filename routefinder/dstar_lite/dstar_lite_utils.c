#include <stdio.h>
#include "internal/core.h"

#include "internal/dstar_lite_utils.h"

#include "internal/coord.h"

static char get_map_char(
    const map m, gint x, gint y,
    const coord start, const coord goal,
    GHashTable* route_coords,
    GHashTable* visited_count
) {
    // 시작점과 도착점 우선 표시
    if (start && coord_get_x(start) == x && coord_get_y(start) == y) 
        return 'S';

    if (goal   && coord_get_x(goal)   == x && coord_get_y(goal)   == y) 
        return 'E';

    if (map_is_blocked(m, x, y)) return '#';

    // 비교용 좌표 생성
    coord tmp = coord_new_full(x, y);

    gboolean is_route    = route_coords && g_hash_table_contains(
        route_coords, tmp);

    gboolean is_visited = visited_count && g_hash_table_contains(
        visited_count, tmp);

    coord_free(tmp);

    if (is_route)    return '*';  // 실제 경로
    if (is_visited) return '+';  // 방문만 한 곳
    return '.';                  // 미방문 평지
}

static const char* get_map_string(
    const map m,
    gint x, gint y,
    const coord start,
    const coord goal,
    GHashTable* route_coords,    
    GHashTable* visited_count
) {
    static char buf[5]; // 충분한 버퍼 (3글자 + null)

    if (start && coord_get_x(start) == x && coord_get_y(start) == y)
        return "  S";
    if (goal && coord_get_x(goal) == x && coord_get_y(goal) == y)
        return "  E";
    if (map_is_blocked(m, x, y))
        return "  #";

    coord tmp = coord_new_full(x, y);

    gboolean is_route    = route_coords && g_hash_table_contains(
        route_coords, tmp);

    gpointer val = visited_count ? 
        g_hash_table_lookup(visited_count, tmp) : NULL;

    coord_free(tmp);

    if (is_route) {
        return "  *";  // 실제 경로
    } 
    else if (val) {
        gint count = GPOINTER_TO_INT(val);
        if (count > 99) count = 99;
        // snprintf(buf, sizeof(buf), "%2d", count);
        snprintf(buf, sizeof(buf), "%3d", count % 1000);
        // snprintf(buf, 4, "%2d", MIN(count, 99));

        return buf;
    }
    return "  .";
}

void print_all_g_table_internal(const map m, GHashTable* g_table) {
    if (!g_table) return;

    g_print("\n📊 g_table (g-values):\n");

    GHashTableIter iter;
    gpointer key, value;
    g_hash_table_iter_init(&iter, g_table);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        coord c = (coord)key;
        gfloat* gval = (gfloat*)value;
        g_print("  (%d, %d) → g = %.3f\n", c->x, c->y, *gval);
    }
}

void print_all_rhs_table_internal(const map m, GHashTable* rhs_table) {
    if (!rhs_table) return;

    g_print("\n📊 rhs_table:\n");

    GHashTableIter iter;
    gpointer key, value;
    g_hash_table_iter_init(&iter, rhs_table);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        coord c = (coord)key;
        gfloat* rhs = (gfloat*)value;
        g_print("  (%d, %d) → rhs = %.3f\n", c->x, c->y, *rhs);
    }
}

void print_all_dsl_internal_full(
    const map m,
    const coord start,
    const coord goal,
    gfloat km,
    GHashTable* g_table,
    GHashTable* rhs_table,
    dstar_lite_pqueue frontier,
    gint max_range,
    gint real_loop_max_retry,
    gboolean debug_mode_enabled,
    GHashTable* update_count_table)
{
    const char* mode_str = "UNKNOWN";
    if (m) {
        mode_str = (m->mode == MAP_NEIGHBOR_4) ? "MAP_NEIGHBOR_4" :
                   (m->mode == MAP_NEIGHBOR_8) ? "MAP_NEIGHBOR_8" :
                   "UNKNOWN";
        g_print("🗺️ Map Size: %d x %d, Mode: %s\n", 
            m->width, m->height, mode_str);
    }

    if (start && goal) {
        g_print("🚩 Start: (%d, %d), 🏁 Goal: (%d, %d)\n", 
            start->x, start->y, goal->x, goal->y);
    }

    g_print("📈 km         = %.3f\n", km);
    g_print("📏 max_range  = %d\n", max_range);
    g_print("🔁 real_loop_max_retry  = %d\n", real_loop_max_retry);
    g_print("🐞 debug_mode = %s\n", debug_mode_enabled ? "ON" : "OFF");

    // g_table
    if (g_table) {
        g_print("\n📊 g_table (g-values):\n");
        GHashTableIter iter;
        gpointer key, value;
        g_hash_table_iter_init(&iter, g_table);
        while (g_hash_table_iter_next(&iter, &key, &value)) {
            coord c = key;
            gfloat* gval = value;
            g_print("  (%d, %d) → g = %.3f\n", c->x, c->y, *gval);
        }
    }

    // rhs_table
    if (rhs_table) {
        g_print("\n📊 rhs_table:\n");
        GHashTableIter iter;
        gpointer key, value;
        g_hash_table_iter_init(&iter, rhs_table);
        while (g_hash_table_iter_next(&iter, &key, &value)) {
            coord c = key;
            gfloat* rhs = value;
            g_print("  (%d, %d) → rhs = %.3f\n", c->x, c->y, *rhs);
        }
    }

    // frontier
    if (frontier && frontier->pq) {
        // 전체 key 개수 가져오기
        GList* keys = pqueue_get_all_keys((pqueue)frontier->pq);
        int total = g_list_length(keys);
        g_list_free(keys);

        // 상단 출력
        g_print("\n📦 Frontier Queue (top 10 of %d keys):\n", total);

        // top 10 출력
        pqueue_iter pq_iter = pqueue_iter_new((pqueue)frontier->pq);
        gpointer key, value;
        int count = 0;

        while (pqueue_iter_next(pq_iter, &key, &value) && count++ < 10) {
            dstar_lite_key dk = key;
            GQueue* coords = value;
            g_print("  (k1=%.3f, k2=%.3f) →", dk->k1, dk->k2);

            int len = g_queue_get_length(coords);
            for (int i = 0; i < len && i < 3; ++i) {
                coord c = g_queue_peek_nth(coords, i);
                g_print(" (%d, %d)", c->x, c->y);
            }
            if (len > 3)
                g_print(" ...");

            g_print("\n");
        }

        pqueue_iter_free(pq_iter);
    }

    // update_count_table
    if (update_count_table) {
        g_print("\n🧮 update_count_table:\n");
        GHashTableIter iter;
        gpointer key, value;
        g_hash_table_iter_init(&iter, update_count_table);
        while (g_hash_table_iter_next(&iter, &key, &value)) {
            coord c = key;
            gint* cnt = value;
            g_print("  (%d, %d) → update count = %d\n", c->x, c->y, *cnt);
        }
    }
    g_print("\n\n");
}

void print_all_dsl(const dstar_lite dsl) {
    if (!dsl) return;
    print_all_dsl_internal_full(dsl->m, dsl->start, dsl->goal,
    dsl->km, dsl->g_table, dsl->rhs_table, dsl->frontier,
    dsl->max_range, dsl->real_loop_max_retry, 
    dsl->debug_mode_enabled, dsl->update_count_table);
}

void print_all_dsl_internal(const map m, const coord start, const coord goal,
    gfloat km, GHashTable* g_table, GHashTable* rhs_table,
    dstar_lite_pqueue frontier) 
{
    print_all_dsl_internal_full(m, start, goal, km, g_table,
    rhs_table, frontier, 0, 0, FALSE, NULL);
}

void dsl_print_ascii_only_map(const dstar_lite dsl) {
    if (!dsl) return;

    printf("[MAP %dx%d ASCII]\n", dsl->m->width, dsl->m->height);

    for (gint y = 0; y < dsl->m->height; y++) {
        for (gint x = 0; x < dsl->m->width; x++) {
            printf("%s", get_map_string(
                dsl->m, x, y, dsl->start, dsl->goal, NULL, NULL));
        }
        putchar('\n');
    }
}

// void dsl_print_ascii(const dstar_lite dsl, const route p) {
//     if (!dsl->m) return;

//     // hashset route_coords = NULL;
//     GHashTable* route_coords = g_hash_table_new_full(
//         (GHashFunc) coord_hash,
//         (GEqualFunc) coord_equal,
//         (GDestroyNotify) coord_free,
//         NULL);

//     if (p && route_get_success(p)) {
//         for (const GList* l = route_get_coords(p); l != NULL; l = l->next)
//             g_hash_table_add(route_coords, coord_copy((coord)l->data));
//     }

//     printf("[MAP %dx%d with ROUTE]\n", dsl->m->width, dsl->m->height);
//     for (gint y = 0; y < dsl->m->height; y++) {
//         for (gint x = 0; x < dsl->m->width; x++) {
//             printf("%s", get_map_string(
//                 dsl->m, x, y, dsl->start, dsl->goal, route_coords, NULL));
//         }
//         putchar('\n');
//     }

//     // if (route_coords) hashset_free(route_coords);
//     if (route_coords) g_hash_table_destroy(route_coords);
// }

void dsl_print_ascii(const dstar_lite dsl, const route p) {
    if (!dsl || !dsl->m) return;

    GHashTable* route_coords = g_hash_table_new_full(
        (GHashFunc) coord_hash,
        (GEqualFunc) coord_equal,
        (GDestroyNotify) coord_free,
        NULL);

    gint min_x = dsl->start->x, max_x = dsl->start->x;
    gint min_y = dsl->start->y, max_y = dsl->start->y;

    if (dsl->goal) {
        min_x = MIN(min_x, dsl->goal->x);
        max_x = MAX(max_x, dsl->goal->x);
        min_y = MIN(min_y, dsl->goal->y);
        max_y = MAX(max_y, dsl->goal->y);
    }

    if (p && route_get_success(p)) {
        for (const GList* l = route_get_coords(p); l != NULL; l = l->next) {
            coord c = (coord)l->data;
            g_hash_table_add(route_coords, coord_copy(c));
            min_x = MIN(min_x, c->x);
            max_x = MAX(max_x, c->x);
            min_y = MIN(min_y, c->y);
            max_y = MAX(max_y, c->y);
        }
    }

    const gint margin = 2;

    if (dsl->m->width == 0) {
        min_x -= margin;
        max_x += margin;
    } else {
        min_x = 0;
        max_x = dsl->m->width - 1;
    }

    if (dsl->m->height == 0) {
        min_y -= margin;
        max_y += margin;
    } else {
        min_y = 0;
        max_y = dsl->m->height - 1;
    }

    printf("[MAP %d,%d to %d,%d with ROUTE]\n", min_x, min_y, max_x, max_y);
    for (gint y = min_y; y <= max_y; y++) {
        for (gint x = min_x; x <= max_x; x++) {
            printf("%s", get_map_string(
                dsl->m, x, y, dsl->start, dsl->goal, route_coords, NULL));
        }
        putchar('\n');
    }

    g_hash_table_destroy(route_coords);
}


void dsl_print_ascii_uv(const dstar_lite dsl, const route p) {
    if (!dsl || !p) return;

    GHashTable* route_coords = g_hash_table_new_full(
        (GHashFunc) coord_hash,
        (GEqualFunc) coord_equal,
        (GDestroyNotify) coord_free,
        NULL);

    gint min_x = dsl->start->x, max_x = dsl->start->x;
    gint min_y = dsl->start->y, max_y = dsl->start->y;

    min_x = MIN(min_x, dsl->goal->x); max_x = MAX(max_x, dsl->goal->x);
    min_y = MIN(min_y, dsl->goal->y); max_y = MAX(max_y, dsl->goal->y);

    if (p && route_get_success(p)) {
        for (const GList* l = route_get_coords(p); l != NULL; l = l->next) {
            coord c = (coord)l->data;
            coord c_copy = coord_copy(c);
            g_hash_table_add(route_coords, c_copy);

            min_x = MIN(min_x, c->x); max_x = MAX(max_x, c->x);
            min_y = MIN(min_y, c->y); max_y = MAX(max_y, c->y);
        }
    }

    const gint margin = 2;
    if (dsl->m->width == 0) {
        min_x -= margin; max_x += margin;
    } else {
        min_x = 0;
        max_x = dsl->m->width - 1;
    }

    if (dsl->m->height == 0) {
        min_y -= margin; max_y += margin;
    } else {
        min_y = 0;
        max_y = dsl->m->height - 1;
    }

    printf("[MAP %d,%d to %d,%d - D* Lite Vertex Update Count]\n",
           min_x, min_y, max_x, max_y);

    for (gint y = min_y; y <= max_y; y++) {
        for (gint x = min_x; x <= max_x; x++) {
            coord c = coord_new_full(x, y);

            if (coord_equal(c, dsl->start)) {
                printf("  S");
            } else if (coord_equal(c, dsl->goal)) {
                printf("  E");
            } else if (g_hash_table_contains(route_coords, c)) {
                printf("  *");
            } else if (map_is_blocked(dsl->m, x, y)) {
                printf("  #");
            } else {
                if (dsl->debug_mode_enabled) {
                    gpointer val = g_hash_table_lookup(
                        dsl->update_count_table, c);
                    if (val) {
                        gint count = *(gint*)val;
                        printf("%3d", count > 99 ? 99 : count);
                    } else {
                        printf("  .");
                    }
                } else {
                    printf("  .");
                }
            }

            coord_free(c);
        }
        printf("\n");
    }

    g_hash_table_destroy(route_coords);
}

