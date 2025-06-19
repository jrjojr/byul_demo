// routefinder.h
//
// Copyright (c) 2025 별이아빠 (byuldev@outlook.kr)
// This file is part of the Byul World project.
// Licensed under the Byul World 공개 라이선스 v1.0
// See the LICENSE file for details.

#include "internal/dstar_lite.h"
#include "internal/map.h"
#include "internal/route.h"
#include "internal/dstar_lite_pqueue.h"
#include "internal/dstar_lite_key.h"

#include <float.h>
#include <math.h>
#include <stdlib.h>

static gint auto_max_range(const coord start, const coord goal) {
    gint dx = abs(goal->x - start->x);
    gint dy = abs(goal->y - start->y);
    return dx + dy;
}

static gint auto_compute_max_retry(const coord start, const coord goal) {
    gint dx = abs(goal->x - start->x);
    gint dy = abs(goal->y - start->y);
    gint r = dx * dy;
    return r ? r : 100;
}

static gint auto_reconstruct_max_retry(const coord start, const coord goal) {
    gint dx = abs(goal->x - start->x);
    gint dy = abs(goal->y - start->y);
    gint r = dx * 2 + dy * 2;
    return r ? r : 40;
}

gfloat dstar_lite_cost(
    const map m, const coord start, const coord goal, gpointer userdata) {

    if (!m || !start || !goal)
        return FLT_MAX;

    if (map_is_blocked(m, goal->x, goal->y))
        return FLT_MAX;

    gfloat dx = (gfloat)(start->x - goal->x);
    gfloat dy = (gfloat)(start->y - goal->y);
    return hypotf(dx, dy);  // ✅ 더 안전한 방식
}

dsl_cost_func dstar_lite_get_cost_func(const dstar_lite dsl) {
    return dsl->cost_fn;
}

void dstar_lite_set_cost_func(dstar_lite dsl, dsl_cost_func fn) {
    if (!dsl) return;
    dsl->cost_fn = fn;
}

gpointer dstar_lite_get_cost_func_userdata(const dstar_lite dsl) {
    return dsl->cost_fn_userdata;
}

void dstar_lite_set_cost_func_userdata(dstar_lite dsl, gpointer userdata) {
    if (!dsl) return;
    dsl->cost_fn_userdata = userdata;
}

gboolean dstar_lite_is_blocked(
    dstar_lite dsl, gint x, gint y, gpointer userdata) {
        
    if (!dsl || !dsl->is_blocked_fn) return FALSE;
    return map_is_blocked(dsl->m, x, y);
}

dsl_is_blocked_func dstar_lite_get_is_blocked_func(dstar_lite dsl) {
    if (!dsl) return NULL;
    return dsl->is_blocked_fn;
}

void dstar_lite_set_is_blocked_func(
    dstar_lite dsl, dsl_is_blocked_func fn) {
    if (!dsl) return;
    dsl->is_blocked_fn = fn;
}

gpointer dstar_lite_get_is_blocked_func_userdata(dstar_lite dsl) {
    if (!dsl) return NULL;
    return dsl->is_blocked_fn_userdata;
}

void dstar_lite_set_is_blocked_func_userdata(
    dstar_lite dsl, gpointer userdata) {
    if (!dsl) return;
    dsl->is_blocked_fn_userdata = userdata;
}

gfloat dstar_lite_heuristic(
    const coord start, const coord goal, gpointer userdata) {

    if (!start || !goal)
        return FLT_MAX;

    gfloat dx = (gfloat)(start->x - goal->x);
    gfloat dy = (gfloat)(start->y - goal->y);
    return hypotf(dx, dy);  // ✅ 더 정확하고 안정적
}

dsl_heuristic_func dstar_lite_get_heuristic_func(const dstar_lite dsl) {
    return dsl->heuristic_fn;
}

void dstar_lite_set_heuristic_func(dstar_lite dsl, dsl_heuristic_func func) {
    dsl->heuristic_fn = func;
}

gpointer dstar_lite_get_heuristic_func_userdata(const dstar_lite dsl) {
    return dsl->heuristic_fn_userdata;
}

void dstar_lite_set_heuristic_func_userdata(dstar_lite dsl, gpointer userdata) {
    dsl->heuristic_fn_userdata = userdata;
}

void move_to(const coord c, gpointer userdata) {
    g_print("move to (%d, %d) in finder.\n", c->x, c->y);
    // coord_free(c);
}

move_func dstar_lite_get_move_func(const dstar_lite dsl) {
    if (!dsl) return NULL;
    return dsl->move_fn;
}

void dstar_lite_set_move_func(dstar_lite dsl, move_func fn) {
    if (!dsl) return;
    dsl->move_fn = fn;    
}

gpointer dstar_lite_get_move_func_userdata(const dstar_lite dsl) {
    if (!dsl) return NULL;
    return dsl->move_fn_userdata;
}

void dstar_lite_set_move_func_userdata(
    dstar_lite dsl, gpointer userdata) {
    
    if (!dsl) return;
    dsl->move_fn_userdata = userdata;
}

GList* get_changed_coords(gpointer userdata) {
    if (!userdata) {
        // g_warning("changed_coords: userdata is NULL");
        g_print("changed_coords: userdata is NULL\n");
        return NULL;
    }

    GList* original = (GList*)userdata;
    GList* copy = NULL;

    for (GList* l = original; l != NULL; l = l->next) {
        coord original_c = (coord)l->data;
        coord copied_c = coord_copy(original_c);
        // coord copied_c = original_c;
        copy = g_list_append(copy, copied_c);
    }

    g_print("changed_coords: %d changed coords copied and returned.\n",
        g_list_length(copy));
    return copy;
}

changed_coords_func dstar_lite_get_changed_coords_func(
    const dstar_lite dsl) {

    if (!dsl) return NULL;
    return dsl->changed_coords_fn;
}

void dstar_lite_set_changed_coords_func(
    dstar_lite dsl, changed_coords_func fn) {

    if (!dsl) return;
    dsl->changed_coords_fn = fn;
}

gpointer dstar_lite_get_changed_coords_func_userdata(
    const dstar_lite dsl) {

    if (!dsl) return NULL;
    return dsl->changed_coords_fn_userdata;
}

void dstar_lite_set_changed_coords_func_userdata(
    dstar_lite dsl, gpointer userdata) {

    if (!dsl) return;
    dsl->changed_coords_fn_userdata = userdata;
}

dstar_lite dstar_lite_new(map m) {
    if (!m) return NULL;

    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic,        
        FALSE);

    return dsl;
}

dstar_lite dstar_lite_new_full(map m, 
    dsl_cost_func cost_fn, dsl_heuristic_func heuristic_fn,
    gboolean debug_mode_enabled) {

    if (!m) return NULL;

    dstar_lite dsl = g_new0(dstar_lite_t, 1);
    dsl->m = m;
    dsl->start = coord_new_full(0, 0);
    dsl->goal = coord_new_full(0, 0);
    
    dsl->km = 0.0f;
    dsl->max_range = auto_max_range(dsl->start, dsl->goal);
    
    dsl->real_loop_max_retry = auto_compute_max_retry(dsl->start, dsl->goal);

    dsl->compute_max_retry = auto_compute_max_retry(dsl->start, dsl->goal);
    dsl->reconstruct_max_retry = auto_reconstruct_max_retry(dsl->start, dsl->goal);

    dsl->cost_fn = cost_fn ? cost_fn : dstar_lite_cost;
    dsl->heuristic_fn = heuristic_fn ? heuristic_fn : dstar_lite_heuristic;

    dsl->debug_mode_enabled = debug_mode_enabled;

    dsl->g_table = g_hash_table_new_full(
        (GHashFunc) coord_hash, 
        (GEqualFunc) coord_equal, 
        (GDestroyNotify) coord_free, 
        g_free
    );
    dsl->rhs_table = g_hash_table_new_full(
        (GHashFunc) coord_hash, 
        (GEqualFunc) coord_equal, 
        (GDestroyNotify) coord_free, 
        g_free
    );
    dsl->update_count_table = g_hash_table_new_full(
        (GHashFunc) coord_hash, 
        (GEqualFunc) coord_equal, 
        (GDestroyNotify) coord_free, 
        g_free
    );
    dsl->frontier = dstar_lite_pqueue_new();

    dsl->interval_msec = 0;
    dsl->proto_route = NULL;
    dsl->real_route = NULL;

    dsl->move_fn = NULL;
    dsl->move_fn_userdata = NULL;

    dsl->changed_coords_fn = NULL;
    dsl->changed_coords_fn_userdata = NULL;

    dsl->force_quit = FALSE;

    dsl->proto_compute_retry_count = 0;
    dsl->real_compute_retry_count = 0;

    dsl->reconstruct_retry_count = 0;

    dsl->real_loop_retry_count = 0;

    return dsl;
}

void dstar_lite_free(dstar_lite dsl) {
    if (!dsl) return;
    coord_free(dsl->start);
    coord_free(dsl->goal);
    g_hash_table_destroy(dsl->g_table);
    g_hash_table_destroy(dsl->rhs_table);
    g_hash_table_destroy(dsl->update_count_table);
    dstar_lite_pqueue_free(dsl->frontier);
    if (dsl->proto_route) route_free(dsl->proto_route);
    if (dsl->real_route) route_free(dsl->real_route);
    g_free(dsl);
}

coord dstar_lite_get_start(const dstar_lite dsl) {
    return dsl->start;
}

void dstar_lite_set_start(dstar_lite dsl, const coord c) {
    // dsl->start = c;
    coord_set(dsl->start, c->x, c->y);
}

coord dstar_lite_get_goal(const dstar_lite dsl) {
    return dsl->goal;
}

void dstar_lite_set_goal(dstar_lite dsl, const coord c) {
    // dsl->goal = c;
    coord_set(dsl->goal, c->x, c->y);
}

GHashTable* dstar_lite_get_g_table(const dstar_lite dsl) {
    return dsl->g_table;
}

GHashTable* dstar_lite_get_rhs_table(const dstar_lite dsl) {
    return dsl->rhs_table;
}

dstar_lite_pqueue dstar_lite_get_frontier(const dstar_lite dsl) {
    return dsl->frontier;
}

void dstar_lite_set_frontier(dstar_lite dsl, dstar_lite_pqueue frontier) {
    if (dsl->frontier) dstar_lite_pqueue_free(dsl->frontier);
    dsl->frontier = frontier;
}

gfloat dstar_lite_get_km(const dstar_lite dsl) {
    return dsl->km;
}

void dstar_lite_set_km(dstar_lite dsl, gfloat km) {
    dsl->km = km;
}

gint dstar_lite_get_max_range(const dstar_lite dsl) {
    return dsl->max_range;
}

void dstar_lite_set_max_range(dstar_lite dsl, gint value) {
    dsl->max_range = value;
}


gint dstar_lite_get_real_loop_max_retry(const dstar_lite dsl) {
    return dsl->real_loop_max_retry;
}
void dstar_lite_set_real_loop_max_retry(dstar_lite dsl, gint value) {
    dsl->real_loop_max_retry = value;
}
gint dstar_lite_real_loop_retry_count(dstar_lite dsl) {
    return dsl->real_loop_retry_count;
}

gint dstar_lite_get_compute_max_retry(const dstar_lite dsl) {
    return dsl->compute_max_retry;
}
void dstar_lite_set_compute_max_retry(
    const dstar_lite dsl, gint v) {
        
    dsl->compute_max_retry = v;
}

gint dstar_lite_proto_compute_retry_count(dstar_lite dsl) {
    return dsl->proto_compute_retry_count;
}
gint dstar_lite_real_compute_retry_count(dstar_lite dsl) {
    return dsl->real_compute_retry_count;
}

gint dstar_lite_get_reconstruct_max_retry(const dstar_lite dsl) {
    return dsl->reconstruct_max_retry;
}

void dstar_lite_set_reconstruct_max_retry(
    const dstar_lite dsl, gint v) {
    dsl->reconstruct_max_retry = v;
}

gint dstar_lite_reconstruct_retry_count(dstar_lite dsl) {
    return dsl->reconstruct_retry_count;
}

gboolean dstar_lite_get_debug_mode_enabled(const dstar_lite dsl) {
    return dsl->debug_mode_enabled;
}

void dstar_lite_set_debug_mode_enabled(dstar_lite dsl, gboolean enabled) {
    dsl->debug_mode_enabled = enabled;
}

GHashTable* dstar_lite_get_update_count_table(const dstar_lite dsl) {
    return dsl->update_count_table;
}

void dstar_lite_add_update_count(dstar_lite dsl, const coord c) {
    gpointer val = g_hash_table_lookup(dsl->update_count_table, c);
    if (!val) {
        gint* count = g_new(gint, 1);
        *count = 1;
        g_hash_table_replace(dsl->update_count_table, coord_copy(c), count);
    } else {
        (*(gint*)val)++;
    }
}

void dstar_lite_clear_update_count(dstar_lite dsl) {
    g_hash_table_remove_all(dsl->update_count_table);
}

gint dstar_lite_get_update_count(dstar_lite dsl, const coord c) {
    gpointer val = g_hash_table_lookup(dsl->update_count_table, c);
    return val ? *((gint*)val) : 0;
}

const map dstar_lite_get_map(const dstar_lite dsl) {
    return dsl->m;
}

const route dstar_lite_get_proto_route(const dstar_lite dsl) {
    return dsl->proto_route;
}

const route dstar_lite_get_real_route(const dstar_lite dsl) {
    return dsl->real_route;
}

void dstar_lite_reset(dstar_lite dsl) {
    // 🔥 해시테이블 완전 삭제 및 재생성
    g_hash_table_destroy(dsl->g_table);
    g_hash_table_destroy(dsl->rhs_table);
    g_hash_table_destroy(dsl->update_count_table);

    dsl->g_table = g_hash_table_new_full(
        (GHashFunc) coord_hash, 
        (GEqualFunc) coord_equal, 
        (GDestroyNotify) coord_free, 
        g_free
    );
    dsl->rhs_table = g_hash_table_new_full(
        (GHashFunc) coord_hash, 
        (GEqualFunc) coord_equal, 
        (GDestroyNotify) coord_free, 
        g_free
    );
    dsl->update_count_table = g_hash_table_new_full(
        (GHashFunc) coord_hash, 
        (GEqualFunc) coord_equal, 
        (GDestroyNotify) coord_free, 
        g_free
    );

    if (dsl->proto_route) {
        route_free(dsl->proto_route);
        dsl->proto_route = NULL;
    }

    if (dsl->real_route) {
        route_free(dsl->real_route);
        dsl->real_route = NULL;
    }    
        
    // ♻️ 우선순위 큐도 완전 교체
    dstar_lite_pqueue_free(dsl->frontier);
    dsl->frontier = dstar_lite_pqueue_new();

    // 🎯 시작 / 목표 좌표 초기화
    // coord_set(dsl->start, 0, 0);
    // coord_set(dsl->goal, 0, 0);

    // ⚙️ 설정 값 초기화
    // dsl->km = 0.0f;
    // dsl->max_range = 0;
    // dsl->real_loop_max_retry = 0;
    // dsl->interval_msec = 0;

    dsl->proto_compute_retry_count = 0;
    dsl->real_compute_retry_count = 0;
    dsl->reconstruct_retry_count = 0;
    dsl->real_loop_retry_count = 0;    

    dstar_lite_init(dsl);
}

void dstar_lite_set_interval_msec(dstar_lite dsl, gint msec) {
    if (!dsl) return;
    dsl->interval_msec = msec;
}

gint dstar_lite_get_interval_msec(const dstar_lite dsl) {
    return dsl ? dsl->interval_msec : 0;
}

dstar_lite_key dstar_lite_calculate_key(dstar_lite dsl, const coord s) {
    gfloat g_val = FLT_MAX;
    gfloat rhs_val = FLT_MAX;

    gpointer g_val_ptr = g_hash_table_lookup(dsl->g_table, s);
    if (g_val_ptr != NULL) {
        g_val = *((gfloat*)g_val_ptr);
    }

    gpointer rhs_val_ptr = g_hash_table_lookup(dsl->rhs_table, s);
    if (rhs_val_ptr != NULL) {
        rhs_val = *((gfloat*)rhs_val_ptr);
    }

    gfloat k2 = fminf(g_val, rhs_val);
    gfloat h = dsl->heuristic_fn(dsl->start, s, NULL);
    gfloat k1 = k2 + h + dsl->km;

    dstar_lite_key key = dstar_lite_key_new_full( k1, k2 );
    return key;
}

void dstar_lite_init(dstar_lite dsl) {
    dsl->km = 0.0f;

    // for s in all_states:
    //     g[s] = float('inf')
    //     rhs[s] = float('inf')    
    // dstar_lite_cost()함수가 기본적으로 무한대를 할당하고 있다.

    // rhs[goal] = 0    
    gfloat* rhs_goal_ptr = g_malloc(sizeof(gfloat));
    *rhs_goal_ptr = 0.0f;
    g_hash_table_replace(dsl->rhs_table, coord_copy(dsl->goal), rhs_goal_ptr);
    
    // U.insert(goal, calculate_key(goal))
    dstar_lite_key calc_key_goal = dstar_lite_calculate_key(dsl, dsl->start);
    dstar_lite_pqueue_push(dsl->frontier, calc_key_goal, dsl->goal);
    dstar_lite_key_free(calc_key_goal);
}

void dstar_lite_update_vertex(const dstar_lite dsl, const coord u) {
    if (!dsl || !u) return;

    // ✅ 디버그용: update 횟수 기록
    if (dsl->debug_mode_enabled)
        dstar_lite_add_update_count(dsl, u);

    gfloat min_rhs = FLT_MAX;
    GList* successors_s = NULL;
    coord s = NULL;
    
    gfloat* g_s_ptr = NULL;
    gfloat g_s = FLT_MAX;

    gfloat cost =  FLT_MAX;

    gfloat* g_u_ptr = NULL;
    gfloat g_u = FLT_MAX;

    gfloat* rhs_u_ptr = NULL;
    gfloat rhs_u = FLT_MAX;

    if (!coord_equal(u, dsl->goal)) {
        successors_s = map_clone_neighbors_all(dsl->m, u->x, u->y);
        for (GList* l = successors_s; l; l = l->next) {
            s = l->data;

            g_s_ptr = (gfloat*)g_hash_table_lookup(dsl->g_table, s);
            if (g_s_ptr) {
                g_s = *g_s_ptr;
            } else {
                g_s = FLT_MAX;
            }

            cost = dsl->cost_fn(dsl->m, u, s, NULL) + g_s;

            if (cost < min_rhs)
                min_rhs = cost;
        }
        g_list_free_full(successors_s, (GDestroyNotify) coord_free);

        gfloat* new_rhs_ptr = g_new(gfloat, 1);        
        *new_rhs_ptr = min_rhs;
        g_hash_table_replace(dsl->rhs_table, coord_copy(u), new_rhs_ptr);
    }

    if (dstar_lite_pqueue_contains(dsl->frontier, u)) 
        dstar_lite_pqueue_remove(dsl->frontier, u);

    g_u_ptr = (gfloat*) g_hash_table_lookup(dsl->g_table, u);
    if (g_u_ptr) {
        g_u = *g_u_ptr;
    } else {
        g_u = FLT_MAX;
    }

    rhs_u_ptr = g_hash_table_lookup(dsl->rhs_table, u);
    if (rhs_u_ptr) {
        rhs_u = *(gfloat*)rhs_u_ptr;
    } else {
        rhs_u = FLT_MAX;
    }

    if (!float_equal(g_u, rhs_u)) {
        dstar_lite_key key = dstar_lite_calculate_key(dsl, u);
        dstar_lite_pqueue_push(dsl->frontier, key, u);
        dstar_lite_key_free(key);
    }
}        

void dstar_lite_update_vertex_range(const dstar_lite dsl, 
    const coord s, gint max_range) {

    if (!dsl) return;

    if (max_range < 1) {
        dstar_lite_update_vertex(dsl, s);
        return;
    }    

    GList* neighbors = map_clone_neighbors_all_range(dsl->m, 
        s->x, s->y, max_range);

    for (GList* l = neighbors; l; l = l->next) {
        coord c = l->data;
        dstar_lite_update_vertex(dsl, c);
    }

    g_list_free_full(neighbors, (GDestroyNotify)coord_free);
}

void dstar_lite_update_vertex_auto_range(
    const dstar_lite dsl, const coord s) {
    
    gint max_range = dsl->max_range;
    return dstar_lite_update_vertex_range(dsl, s, max_range);
}

void dstar_lite_update_vertex_by_route(const dstar_lite dsl, const route p) {
    if (!dsl || !p) return;

    GList* coords = route_get_coords(p);
    for (GList* l = coords; l; l = l->next) {
        
        coord c = (coord)l->data;
        dstar_lite_update_vertex(dsl, c);
    }
}

void dstar_lite_compute_shortest_route(dstar_lite dsl) {
    if (!dsl) return;

    coord u = NULL;

    gfloat* g_u_ptr = NULL;
    gfloat g_u = FLT_MAX;
    
    gfloat* rhs_u_ptr = NULL;
    gfloat rhs_u = FLT_MAX;

    dstar_lite_key calc_key = NULL;

    GList* predecessors_u = NULL;
    coord s = NULL;

    gfloat* g_old_ptr = NULL;
    gfloat g_old = FLT_MAX;

    gfloat cost_s_u = FLT_MAX;
    gfloat* rhs_s_ptr = NULL;
    gfloat rhs_s = FLT_MAX;

    gfloat min = FLT_MAX;   

    gfloat min_old = FLT_MAX;
    gfloat cost_s_s_prime = FLT_MAX;
    
    gfloat* g_s_prime_ptr = NULL;
    gfloat g_s_prime = FLT_MAX;    

    GList* successors_s = NULL;

    coord s_prime = NULL;
    
    gfloat g_start = FLT_MAX;
    gfloat rhs_start = FLT_MAX;
    gfloat* g_start_ptr = NULL;
    gfloat* rhs_start_ptr = NULL;

    gint loop = 0;

    dstar_lite_key calc_key_start = NULL;
    dstar_lite_key k_old = NULL;
    dstar_lite_key top_key = dstar_lite_pqueue_top_key(dsl->frontier);
    do {
        loop++;
        // g_print("dstar_lite_compute_shortest_route "
        //     "내부에서 루프 %d 시작.\n", loop);

        // print_all_dsl_internal(
        //     m, start, goal, km, g_table, rhs_table, frontier);

        if (k_old) {
            dstar_lite_key_free(k_old);
            k_old = NULL;
        }
        k_old = dstar_lite_key_copy(top_key);
        u = dstar_lite_pqueue_pop(dsl->frontier);
        if (!u) {
            // dstar_lite_key_free(k_old);
            break;
        }

        g_u_ptr = (gfloat*) g_hash_table_lookup(dsl->g_table, u);
        if (g_u_ptr) {
            g_u = *(gfloat*)g_u_ptr;
        } else {
            g_u = FLT_MAX;
        }

        rhs_u_ptr = (gfloat*) g_hash_table_lookup(dsl->rhs_table, u);
        if (rhs_u_ptr) {
            rhs_u = *rhs_u_ptr;
        } else {
            rhs_u = FLT_MAX;
        }

        if(calc_key) {
            dstar_lite_key_free(calc_key);
            calc_key = NULL;
        }
        calc_key = dstar_lite_calculate_key(dsl, u);
        if (dstar_lite_key_compare(k_old, calc_key) < 0) {
            dstar_lite_pqueue_push(dsl->frontier, calc_key, u);
        } else if ( g_u > rhs_u) {
            // g_u = rhs_u;
            
            gfloat* new_g = g_malloc(sizeof(gfloat));
            *new_g = rhs_u;
            g_hash_table_replace(dsl->g_table, coord_copy(u), new_g);

            // for s in predecessors(u):
            //     update_vertex(s)
            predecessors_u = map_clone_neighbors_all(
                dsl->m, u->x, u->y);

            for (GList* l = predecessors_u; l; l = l->next) {
                s = l->data;
                dstar_lite_update_vertex(dsl, s);
            }
            g_list_free_full(predecessors_u, (GDestroyNotify)coord_free);
        } else {
            g_old_ptr = g_hash_table_lookup(dsl->g_table, u);
            if (g_old_ptr) {
                g_old = *g_old_ptr;
            } else {
                g_old = FLT_MAX;
            }

            gfloat* new_g = g_malloc(sizeof(gfloat));
            *new_g = FLT_MAX;
            g_hash_table_replace(dsl->g_table, coord_copy(u), new_g);

            // for s in predecessors(u) | {u}:            
            predecessors_u = map_clone_neighbors_all(
                dsl->m, u->x, u->y);
            predecessors_u = g_list_append(predecessors_u, coord_copy(u));
            for (GList* l = predecessors_u; l; l = l->next) {
                s = l->data;
                cost_s_u = dsl->cost_fn(dsl->m, s, u, NULL);

                rhs_s_ptr = (gfloat*) g_hash_table_lookup(dsl->rhs_table, s);
                if (rhs_s_ptr) {
                    rhs_s = *rhs_s_ptr;
                } else {
                    rhs_s = FLT_MAX;
                }

                if (float_equal(rhs_s, cost_s_u + g_old)) {
                    if (!coord_equal(s, dsl->goal)) {

                        successors_s = map_clone_neighbors_all(
                            dsl->m, s->x, s->y);
                        for (GList* l = successors_s; l; l = l->next) {
                            s_prime = l->data;

                            cost_s_s_prime = dsl->cost_fn(dsl->m, s, s_prime, NULL);
                            g_s_prime_ptr = (gfloat*) g_hash_table_lookup(
                                dsl->g_table, s_prime);

                            if ( g_s_prime_ptr ) {
                                g_s_prime = *g_s_prime_ptr;
                            } else {
                                g_s_prime = FLT_MAX;
                            }

                            min = fminf(min, cost_s_s_prime + g_s_prime);

                            gfloat* min_ptr = g_new0(gfloat, 1);
                            *min_ptr = min;
                g_hash_table_replace(dsl->rhs_table, coord_copy(s), min_ptr);
                        }
                        g_list_free_full(successors_s, 
                                (GDestroyNotify)coord_free);
                    }
                    dstar_lite_update_vertex(dsl, s);
                }
            }
            g_list_free_full(predecessors_u, (GDestroyNotify)coord_free);
        }
        coord_free(u);

        top_key = dstar_lite_pqueue_top_key(dsl->frontier);
        if (!top_key) break;

        if (calc_key_start) {
            dstar_lite_key_free(calc_key_start);
            calc_key_start = NULL;
        }
        calc_key_start = dstar_lite_calculate_key(dsl, dsl->start);
                    
        g_start_ptr = (gfloat*)g_hash_table_lookup(dsl->g_table, dsl->start);
        if ( g_start_ptr ) {
            g_start = *g_start_ptr;
        } else {
            g_start = FLT_MAX;
        }

        rhs_start_ptr = (gfloat*)g_hash_table_lookup(
            dsl->rhs_table, dsl->start);

        if ( rhs_start_ptr ) {
            rhs_start = *rhs_start_ptr;
        } else {
            rhs_start = FLT_MAX;
        }

    } while ((loop < dsl->compute_max_retry) && 
        ( (dstar_lite_key_compare(top_key, calc_key_start) < 0) || 
            (!float_equal(rhs_start, g_start) ) ) );

    if (calc_key_start) {
        dstar_lite_key_free(calc_key_start);
        calc_key_start = NULL;
    }            
    if (k_old) {
        dstar_lite_key_free(k_old);
        k_old = NULL;
    }
    if(calc_key) {
        dstar_lite_key_free(calc_key);
        calc_key = NULL;
    }

    // if dsl->proto_route == NULL
    if (dsl->proto_route == NULL) {
        dsl->proto_compute_retry_count = loop;
    } else {
        dsl->real_compute_retry_count = loop;
    }
}

route dstar_lite_reconstruct_route(const dstar_lite dsl) {
    if (!dsl) return NULL;

    route p = route_new();
    route_add_coord(p, dsl->start);    

    gfloat* g_start_ptr = g_hash_table_lookup(dsl->g_table, dsl->start);
    if (!g_start_ptr || float_equal(*g_start_ptr, FLT_MAX))
        return p;

    coord current = coord_copy(dsl->start);
    // coord current = start;

    gint loop = 0;
    while (!coord_equal(current, dsl->goal) && 
        (loop < dsl->reconstruct_max_retry)) {

        loop++;
        // g_print("dstar_lite_reconstruct_route "
        //     "내부에서 루프 %d 시작.\n", loop);

        GList* neighbors = map_clone_neighbors_all(
            dsl->m, current->x, current->y);

        gfloat min_cost = FLT_MAX;
        coord next = NULL;

        for (GList* l = neighbors; l; l = l->next) {
            coord s = l->data;

            gfloat cost_current_s = dsl->cost_fn(dsl->m, current, s, NULL);
            gfloat* g_s_ptr = g_hash_table_lookup(dsl->g_table, s);
            gfloat g_s = (g_s_ptr) ? *g_s_ptr : FLT_MAX;

            gfloat total_cost = cost_current_s + g_s;
            if (total_cost < min_cost) {
                min_cost = total_cost;
                
                if (next) coord_free(next);  // 기존 next 해제
                next = coord_copy(s);
                // next = s;
            }
        }
        g_list_free_full(neighbors, (GDestroyNotify)coord_free);

        if (!next) {  // 더 이상 진행할 수 없음
            coord_free(current);
            // route_free(p);
            route_set_success(p, FALSE);
            return p;
        }

        gfloat* g_next_ptr = g_hash_table_lookup(dsl->g_table, next);
        if (!g_next_ptr || float_equal(*g_next_ptr, FLT_MAX)) {
            coord_free(current);
            coord_free(next);
            // route_free(p);
            route_set_success(p, FALSE);
            return p;
        }

        route_add_coord(p, next);
        coord_free(current);
        current = next;
    }

    dsl->reconstruct_retry_count = loop;

    coord_free(current);
    route_set_success(p, TRUE);    
    return p;
}

route dstar_lite_find(const dstar_lite dsl) {
    if (!dsl) return NULL;

    dstar_lite_reset(dsl);

    dstar_lite_compute_shortest_route(dsl);
    return dstar_lite_reconstruct_route(dsl);
}

void dstar_lite_find_full(const dstar_lite dsl) {
    if (!dsl) return;
    dstar_lite_find_proto(dsl);
    dstar_lite_find_loop(dsl);
}

void dstar_lite_find_proto(const dstar_lite dsl) {
    if (!dsl) return;
    // dstar_lite_reset(dsl);
    dsl->proto_route = dstar_lite_find(dsl);
}
 
void dstar_lite_find_loop(const dstar_lite dsl) {
    if (!dsl) return;

    // if (!dsl->proto_route) dstar_lite_find_proto(dsl);

    coord s_last = coord_copy(dsl->start);
    coord start = coord_copy(dsl->start);

    dsl->real_route = route_new();
    route_add_coord(dsl->real_route, start);

    gfloat* rhs_start_ptr = NULL;
    gfloat rhs_start = FLT_MAX;

    GList* successors_start = NULL;
    GList* l = NULL;

    gfloat min_cost = FLT_MAX;
    coord next = NULL;

    coord s = NULL;
    gfloat* g_s_ptr = NULL;
    gfloat g_s = FLT_MAX;
    gfloat cost_start_s = FLT_MAX;
    gfloat total_cost = FLT_MAX;

    GList* changed_coords = NULL;

    gint loop = 0;
    while (!coord_equal(start, dsl->goal) && 
        (loop < dsl->real_loop_max_retry) && !dsl->force_quit) {

        loop++;
        // g_print("dstar_lite_find_loop "
        //     "내부에서 루프 %d 시작.\n", loop);

        rhs_start_ptr = g_hash_table_lookup(dsl->rhs_table, dsl->start);
        if (rhs_start_ptr) {
            rhs_start = *rhs_start_ptr;
        } else {
            rhs_start = FLT_MAX;
        }

        if (float_equal(rhs_start, FLT_MAX)) {
            route_set_success(dsl->real_route, FALSE);
            dsl->real_loop_retry_count = loop;
            dsl->force_quit = FALSE;
            return;
        }
        
        // 다음 이동 위치 선택
        min_cost = FLT_MAX;
        successors_start = map_clone_neighbors_all(
            dsl->m, start->x, start->y);
        for (l = successors_start; l; l = l->next) {
            s = l->data;

            g_s_ptr = g_hash_table_lookup(dsl->g_table, s);
            g_s = (g_s_ptr) ? *g_s_ptr : FLT_MAX;
            cost_start_s = dsl->cost_fn(dsl->m, start, s, NULL);
            total_cost = cost_start_s + g_s;

            if (total_cost < min_cost) {
                min_cost = total_cost;

                // next = s;
                if (next) coord_free(next);  // 기존 next 해제
                next = coord_copy(s);
            }
        }
        g_list_free_full(successors_start, (GDestroyNotify)coord_free);

        if (!next) {
            route_set_success(dsl->real_route, FALSE);
            dsl->real_loop_retry_count = loop;
            dsl->force_quit = FALSE;
            return;
        }
        route_add_coord(dsl->real_route, next);

        if (dsl->force_quit) break;
        // move callback을 실행한다.
        // if (dsl->move_fn) dsl->move_fn(coord_copy(next),
        //     dsl->move_fn_userdata);

        if (dsl->move_fn) dsl->move_fn(next,
            dsl->move_fn_userdata);            

        // 이동 간 대기 시간 적용
        // time.sleep(dsl->interval_msec / 1000.0);
        // g_usleep(dsl->interval_msec * 1000);  // 밀리초 → 마이크로초
        if (dsl->interval_msec <= 0)
            //쓰레드에서도 안전하게
            g_thread_yield();   // 틱 양보
        else
            g_usleep(dsl->interval_msec * 1000);

        if (dsl->force_quit) break;


        if(start) coord_free(start);
        start = coord_copy(next);

        // 환경 변화 감지 및 반영
        if (dsl->changed_coords_fn) {
            changed_coords = dsl->changed_coords_fn(
                dsl->changed_coords_fn_userdata);

            if (changed_coords) {
                dsl->km += dsl->heuristic_fn(s_last, start, NULL);

                if (s_last) coord_free(s_last);
                s_last = coord_copy(start);

                // for u in changed_coords:
                    // update_vertex(u)
                for (l = changed_coords; l; l = l->next) {
                    s = l->data;
                    dstar_lite_update_vertex(dsl, s);
                }
            }
            if (changed_coords) {
                g_list_free_full(changed_coords, (GDestroyNotify)coord_free);
            }
            dstar_lite_compute_shortest_route(dsl);
        }
        loop++;
    }
    dsl->force_quit = FALSE;
    if (start) coord_free(start);
    if (next) coord_free(next);

    if (loop >= dsl->real_loop_max_retry) {
        // 길을 못찾고 루프가 한계에 도달했다.
        if (s_last) {
            if (!coord_equal(s_last, dsl->goal)) {
                route_set_success(dsl->real_route, FALSE);
                dsl->real_loop_retry_count = loop;
                coord_free(s_last);
                    dsl->force_quit = FALSE;
                return;
            }
        }
    }
    route_set_success(dsl->real_route, TRUE);
    dsl->real_loop_retry_count = loop;
    if (s_last) coord_free(s_last);    
        dsl->force_quit = FALSE;
    return;    
}

void dstar_lite_force_quit(dstar_lite dsl) {
    dsl->force_quit = TRUE;
}

gboolean dstar_lite_is_quit_forced(dstar_lite dsl) {
    return dsl->force_quit;
}

void dstar_lite_set_force_quit(dstar_lite dsl, gboolean v) {
    dsl->force_quit = v;
}

