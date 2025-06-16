#include "internal/dstar_lite.h"
#include "internal/dstar_lite_utils.h"

#include <glib.h>
#include "internal/path.h"
#include <stdio.h>
#include <locale.h>
#include <unistd.h>

static void test_dstar_lite_basic(void) {
        coord start = coord_new_full(0, 0);
        coord goal = coord_new_full(9, 9);

        map m = map_new_full(0, 0, MAP_NEIGHBOR_8);
        dstar_lite dsl = dstar_lite_new_full(m,
            dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

        path p = dstar_lite_find(dsl);

        g_assert_true(path_get_success(p));
        g_print("[BASIC] path length = %d\n", path_length(p));

        path_print(p);
        dsl_print_ascii_uv(dsl, p);
        dsl_print_ascii(dsl, p);

        path_free(p);
        coord_free(start);
        coord_free(goal);
        dstar_lite_free(dsl);   
        map_free(m);
}

static void test_dstar_lite_blocked_path(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    for (int y = 1; y < 10; y++) map_block_coord(dsl->m, 5, y);    

    path p = dstar_lite_find(dsl);

    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);

    path_free(p);
    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
     
}

static void test_dstar_lite_blocked_path_refind_ub1(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

                dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    for (int y = 1; y < 10; y++) map_block_coord(dsl->m, 5, y);    

    path p = dstar_lite_find(dsl);

    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);

    coord c0 = coord_new_full(5,0);
    coord c1 = coord_new_full(5,1);

    map_block_coord(dsl->m, c0->x, c0->y);
    map_unblock_coord(dsl->m, c1->x, c1->y);

    dstar_lite_update_vertex_range(dsl, c0, 0);
    dstar_lite_update_vertex_range(dsl, c1, 0);    
    
    // dstar_lite_update_vertex_by_path(dsl, p);

    path p1 = dstar_lite_find(dsl);

    path_print(p);        
    dsl_print_ascii_uv(dsl, p1);

    coord_free(c0);
    coord_free(c1);

    path_free(p1);
    path_free(p);

    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
     
}

static void test_dstar_lite_blocked_path_refind_ub2(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    for (int y = 1; y < 10; y++) map_block_coord(dsl->m, 5, y);    

    path p = dstar_lite_find(dsl);

    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);

    coord c0 = coord_new_full(5,0);
    coord c2 = coord_new_full(5,2);

    map_block_coord(dsl->m, c0->x, c0->y);
    map_unblock_coord(dsl->m, c2->x, c2->y);

    dstar_lite_update_vertex_range(dsl, c0, 1);
    dstar_lite_update_vertex_range(dsl, c2, 1);    
    
    // 기존 경로 기반 update
    // dstar_lite_update_vertex_by_path(dsl, p);

    path p1 = dstar_lite_find(dsl);

    path_print(p);        
    dsl_print_ascii_uv(dsl, p1);

    coord_free(c0);
    coord_free(c2);

    path_free(p1);
    path_free(p);

    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
     
}

static void test_dstar_lite_blocked_path_refind_ub3(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    for (int y = 1; y < 10; y++) map_block_coord(dsl->m, 5, y);    

    path p = dstar_lite_find(dsl);

    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));

    path_print(p);    
    dsl_print_ascii_uv(dsl, p);

    coord c0 = coord_new_full(5,0);
    coord c3 = coord_new_full(5,3);

    map_block_coord(dsl->m, c0->x, c0->y);
    map_unblock_coord(dsl->m, c3->x, c3->y);

    dstar_lite_update_vertex_range(dsl, c0, 1);
    dstar_lite_update_vertex_range(dsl, c3, 1);    
    
    // 기존 경로 기반 update
    // dstar_lite_update_vertex_by_path(dsl, p);

    path p1 = dstar_lite_find(dsl);

    path_print(p);        
    dsl_print_ascii_uv(dsl, p1);

    coord_free(c0);
    coord_free(c3);

    path_free(p1);
    path_free(p);

    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
     
}

static void test_dstar_lite_blocked_path_refind_ub4(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    for (int y = 1; y < 10; y++) map_block_coord(dsl->m, 5, y);    

    path p = dstar_lite_find(dsl);

    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));

    dsl_print_ascii_uv(dsl, p);

    coord c0 = coord_new_full(5,0);
    coord c4 = coord_new_full(5,4);

    map_block_coord(dsl->m, c0->x, c0->y);
    map_unblock_coord(dsl->m, c4->x, c4->y);

    dstar_lite_update_vertex_range(dsl, c0, 1);
    dstar_lite_update_vertex_range(dsl, c4, 1);    
    
    path p1 = dstar_lite_find(dsl);

    path_print(p);        
    dsl_print_ascii_uv(dsl, p1);

    coord_free(c0);
    coord_free(c4);

    path_free(p1);
    path_free(p);

    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
     
}

static void test_dstar_lite_blocked_path_refind_ub5(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    for (int y = 1; y < 10; y++) map_block_coord(dsl->m, 5, y);    

    path p = dstar_lite_find(dsl);

    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));
        
    path_print(p);
    dsl_print_ascii_uv(dsl, p);

    coord c0 = coord_new_full(5,0);
    coord c5 = coord_new_full(5,5);

    map_block_coord(dsl->m, c0->x, c0->y);
    map_unblock_coord(dsl->m, c5->x, c5->y);

    dstar_lite_update_vertex_range(dsl, c0, 1);
    dstar_lite_update_vertex_range(dsl, c5, 1);
    
    path p1 = dstar_lite_find(dsl);

    path_print(p1);
    dsl_print_ascii_uv(dsl, p1);

    coord_free(c0);
    coord_free(c5);

    path_free(p1);
    path_free(p);

    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
     
}

static void test_dstar_lite_blocked_path_default(void) {
    coord start = coord_new_full(5, 5);
    coord goal = coord_new_full(5, 5);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new(m);
    dstar_lite_set_real_loop_max_retry(dsl, 20);

    g_print("기본 생성자로 길찾기\n");
    path p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    // g_assert_true(path_get_success(p));
    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;    

    g_print("목표는 (%d, %d)로 설정\n", goal->x, goal->y);
    dstar_lite_reset(dsl);
    dstar_lite_set_goal(dsl, goal);
    p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    // g_assert_true(path_get_success(p));
    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);

    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
}

static void test_dstar_lite_block_unblock_recover(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    // 🔹 1. 최초 경로
    path p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;

    coord c = coord_new_full(4, 4);
    coord c0 = coord_new_full(3, 3);
    coord c1 = coord_new_full(4, 3);

    // 🔹 2. 장애물 추가
    map_block_coord(dsl->m, c->x, c->y);
    map_block_coord(dsl->m, c0->x, c0->y);
    map_block_coord(dsl->m, c1->x, c1->y);

    p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    // g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;

    // 🔹 3. 장애물 제거
    map_unblock_coord(dsl->m, c->x, c->y);
    dstar_lite_update_vertex_range(dsl, c, 1);

    p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    // g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;

    coord_set(goal, 7, 6);
    dstar_lite_set_goal(dsl, goal);

    p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    // g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;

    coord_free(c);
    coord_free(c0);
    coord_free(c1);

    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
}    

static void test_dstar_lite_find_loop(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    // 🔹 1. 최초 경로
    g_print("최초 경로 dstar_lite_find()로 정적인 경로 생성\n");
    path p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;
    dstar_lite_reset(dsl);

    coord c = coord_new_full(4, 4);
    coord c0 = coord_new_full(3, 3);
    coord c1 = coord_new_full(4, 3);
    coord c2 = coord_new_full(5, 3);

    // 🔹 2. 장애물 추가
    g_print("장애물 추가 dstar_lite_find()로 정적인 경로 생성\n");    
    map_block_coord(dsl->m, c->x, c->y);
    map_block_coord(dsl->m, c0->x, c0->y);
    map_block_coord(dsl->m, c1->x, c1->y);

    p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    // g_assert_true(path_get_success(p));

    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;
    dstar_lite_reset(dsl);

    // 🔹 3. 장애물 제거
    g_print("장애물 제거 dstar_lite_find()로 정적인 경로 생성\n");    
    map_unblock_coord(dsl->m, c->x, c->y);
    dstar_lite_update_vertex_range(dsl, c, 1);

    dstar_lite_find_proto(dsl);
    g_assert_nonnull(dsl->proto_path);
    // g_assert_true(path_get_success(p));

    path_print(dsl->proto_path);
    dsl_print_ascii_uv(dsl, dsl->proto_path);

    dstar_lite_reset(dsl);

    g_print("목표 (7, 6)으로 변경 dstar_lite_find_proto()로 초기 경로 생성\n");        
    coord_set(goal, 7, 6);
    dstar_lite_set_goal(dsl, goal);

    dstar_lite_find_proto(dsl);
    
    g_assert_nonnull(dsl->proto_path);
    // g_assert_true(path_get_success(p));

    path_print(dsl->proto_path);
    dsl_print_ascii_uv(dsl, dsl->proto_path);
    // path_free(p);
    // p = NULL;


    // GList* path_list = NULL;
GList* changed_coords = NULL;
gint interval_msec = 100;

dstar_lite_set_interval_msec(dsl, interval_msec);

dstar_lite_find_loop(dsl);

for (guint i = 0; i < 5; i++) {
    g_print("인터벌 msec : %d, dstar_lite_find_loop()로 동적 경로 생성\n", interval_msec);

    coord coord_i = coord_new_full(i + 4, 5);
    g_print("블락했다 (%d, %d)\n", coord_get_x(coord_i), coord_get_y(coord_i));


    map_block_coord(dsl->m, coord_get_x(coord_i), coord_get_y(coord_i));

    // i == 2일 때 changed_coords_fn 등록 (복사본으로)
    if (i == 2) {
        changed_coords = g_list_append(changed_coords, coord_copy(coord_i));
        dsl->changed_coords_fn = get_changed_coords;
        dsl->changed_coords_fn_userdata = changed_coords;
    }

    g_assert_nonnull(dsl->real_path);

    // path_list = g_list_append(path_list, dsl->real_path);  // 나중에 일괄 해제

    path_print(p);
    dsl_print_ascii_uv(dsl, p);

    coord_free(coord_i);  // 원본 해제
}

// 정리
g_list_free_full((GList*)dsl->changed_coords_fn_userdata, (GDestroyNotify)coord_free);
// g_list_free_full(path_list, (GDestroyNotify)path_free);



    coord_free(c);
    coord_free(c0);
    coord_free(c1);
    coord_free(c2);

    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
}    

static void test_dstar_lite_find_static(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(9, 9);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    // 🔹 최초 경로
    g_print("최초 경로 dstar_lite_find()로 정적인 경로 생성\n");
    path p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));
    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    dstar_lite_reset(dsl);

    // 🔹 장애물 추가 후 경로 재계산
    coord c = coord_new_full(4, 4);
    coord c0 = coord_new_full(3, 3);
    coord c1 = coord_new_full(4, 3);
    coord c2 = coord_new_full(5, 3);

    g_print("장애물 추가 dstar_lite_find()로 경로 생성\n");
    map_block_coord(dsl->m, c->x, c->y);
    map_block_coord(dsl->m, c0->x, c0->y);
    map_block_coord(dsl->m, c1->x, c1->y);

    p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    dstar_lite_reset(dsl);

    // 🔹 장애물 제거 후 경로 재계산
    g_print("장애물 제거 dstar_lite_find_proto()로 경로 생성\n");
    map_unblock_coord(dsl->m, c->x, c->y);
    dstar_lite_update_vertex_range(dsl, c, 1);

    dstar_lite_find_proto(dsl);
    p = dsl->proto_path;
    g_assert_nonnull(p);
    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    dstar_lite_reset(dsl);

    // 목표 변경
    g_print("목표 (7, 6)으로 변경 dstar_lite_find_proto()로 경로 생성\n");
    coord_set(goal, 7, 6);
    dstar_lite_set_goal(dsl, goal);
    dstar_lite_find_proto(dsl);
    
    g_assert_nonnull(dsl->proto_path);
    path_print(dsl->proto_path);
    dsl_print_ascii_uv(dsl, dsl->proto_path);

    g_print("목표 (7, 6)으로 변경 dstar_lite_find_loop()로 실제 경로 생성\n");
    dstar_lite_find_loop(dsl);
    g_assert_nonnull(dsl->real_path);
    path_print(dsl->real_path);
    dsl_print_ascii_uv(dsl, dsl->real_path);    

    // 정리
    coord_free(c); coord_free(c0); coord_free(c1); coord_free(c2);
    coord_free(start); coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
}

static gpointer run_find_loop(gpointer data) {
    dstar_lite dsl = (dstar_lite)data;
    dstar_lite_find_loop(dsl);  // 무한 루프
    return NULL;
}

static void test_dstar_lite_find_dynamic(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(7, 6);

    map m = map_new_full(10, 10, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    // 초기 경로
    dstar_lite_find_proto(dsl);
    g_assert_nonnull(dsl->proto_path);
    path_print(dsl->proto_path);
    dsl_print_ascii_uv(dsl, dsl->proto_path);

    // 설정
    gint interval_msec = 100;
    dstar_lite_set_interval_msec(dsl, interval_msec);

    dsl->move_fn = move_to;
    dsl->changed_coords_fn = get_changed_coords;

    // 🔹 별도 쓰레드에서 loop 시작
    GThread* loop_thread = g_thread_new("dstar_lite_loop", run_find_loop, dsl);
    g_assert_nonnull(loop_thread);

    coord coord_i = NULL;
    GList* changed_coords = NULL;
    for (guint i = 0; i < 50; i++) {
        g_usleep(interval_msec * 30);

        g_print("인터벌 %dms: 변화 적용 시도\n", i * interval_msec);

        if (i == 2) {
            coord_i = coord_new_full(i + 1, i);
            g_print("블락했다 (%d, %d)\n", coord_get_x(coord_i), coord_get_y(coord_i));

            map_block_coord(dsl->m, coord_get_x(coord_i), coord_get_y(coord_i));

            if (changed_coords != NULL) {
                g_list_free_full(changed_coords, (GDestroyNotify)coord_free);
                // g_list_free(changed_coords);
                changed_coords = NULL;
            }
            changed_coords = g_list_append(changed_coords, coord_copy(coord_i));
            dsl->changed_coords_fn_userdata = changed_coords;

            coord_free(coord_i);
            coord_i = NULL;
            // 이후 DSL 내부에서 복사본만 사용하므로 여기서 바로 free 가능
        }

        // 실시간 경로 출력
        if (dsl->real_path) {
            path_print(dsl->real_path);
            dsl_print_ascii_uv(dsl, dsl->real_path);
        }
        if (dsl->real_path->success) {
            g_print("경로 찾기 성공\n");
            break;
        }
    }

    // 🔚 루프 종료 지시
    // dstar_lite_force_quit(dsl);
    g_thread_join(loop_thread);

    dsl_print_ascii_only_map(dsl);

    path_print(dsl->real_path);
    dsl_print_ascii_uv(dsl, dsl->real_path);

    // 정리
    // g_list_free_full((GList*)dsl->changed_coords_fn_userdata, (GDestroyNotify)coord_free);
    g_list_free_full(changed_coords, (GDestroyNotify)coord_free);

    coord_free(start); 
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);

    coord_free(coord_i);    
}

static void test_dstar_lite_block_all_around_start(void) {
    coord start = coord_new_full(0, 0);
    coord goal = coord_new_full(-9, -9);

    map m = map_new_full(0, 0, MAP_NEIGHBOR_8);
    dstar_lite dsl = dstar_lite_new_full(m, 
        dstar_lite_cost, dstar_lite_heuristic, TRUE);

        dstar_lite_set_start(dsl, start);
        dstar_lite_set_goal(dsl, goal);

    map_block_coord(dsl->m, 1, 0);
    map_block_coord(dsl->m, 1, -1);
    map_block_coord(dsl->m, 0, -1);
    map_block_coord(dsl->m, -1, -1);

    path p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));
    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;

        
    map_block_coord(dsl->m, -1, 0);
    map_block_coord(dsl->m, -1, 1);
    map_block_coord(dsl->m, 0, 1);

    dstar_lite_set_compute_max_retry(dsl, 200);

    p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    g_assert_true(path_get_success(p));
    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;    

    map_block_coord(dsl->m, 1, 1);    

    p = dstar_lite_find(dsl);
    g_assert_nonnull(p);
    g_assert_false(path_get_success(p));
    path_print(p);
    dsl_print_ascii_uv(dsl, p);
    path_free(p);
    p = NULL;        

    path_free(p);
    coord_free(start);
    coord_free(goal);
    dstar_lite_free(dsl);
    map_free(m);
     
}

int main(int argc, char **argv) {
    setlocale(LC_ALL, "ko_KR.UTF-8");  // 💥 핵심
    g_test_init(&argc, &argv, NULL);

    g_test_add_func("/dstar_lite/basic", test_dstar_lite_basic);
    
    g_test_add_func("/dstar_lite/blocked_path", 
        test_dstar_lite_blocked_path);

    g_test_add_func("/dstar_lite/blocked_path_refind_ub1", 
        test_dstar_lite_blocked_path_refind_ub1);        

    g_test_add_func("/dstar_lite/blocked_path_refind_ub2", 
        test_dstar_lite_blocked_path_refind_ub2);

    g_test_add_func("/dstar_lite/blocked_path_refind_ub3", 
        test_dstar_lite_blocked_path_refind_ub3);        

    g_test_add_func("/dstar_lite/blocked_path_refind_ub4", 
        test_dstar_lite_blocked_path_refind_ub4);        

g_test_add_func("/dstar_lite/blocked_path_refind_ub5", 
        test_dstar_lite_blocked_path_refind_ub5);        

g_test_add_func("/dstar_lite/blocked_path_default", 
        test_dstar_lite_blocked_path_default);              

g_test_add_func("/dstar_lite/block_unblock_recover",
    test_dstar_lite_block_unblock_recover);


g_test_add_func("/dstar_lite/find_loop",
    test_dstar_lite_find_loop);    


g_test_add_func("/dstar_lite/find_static", test_dstar_lite_find_static);
g_test_add_func("/dstar_lite/find_dynamic", test_dstar_lite_find_dynamic);

g_test_add_func("/dstar_lite/block_all_around_start", 
    test_dstar_lite_block_all_around_start);


    return g_test_run();
}
