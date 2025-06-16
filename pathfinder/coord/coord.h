#ifndef COORD_H
#define COORD_H

#include <glib.h>
#include "byul_config.h"

#ifdef __cplusplus
extern "C" {
#endif

// coord 구조체
typedef struct s_coord {
    gint x;  // x 좌표
    gint y;  // y 좌표
} coord_t;

typedef coord_t* coord;

// start----------------------------------------------------------------------

// coord 생성
BYUL_API coord    coord_new_full(gint x, gint y);

BYUL_API coord    coord_new();

// coord 해제
BYUL_API void     coord_free(coord c);

// coord 해시
BYUL_API guint coord_hash(const coord c);

// coord 비교
BYUL_API gboolean coord_equal(const coord c1, const coord c2);

BYUL_API gint coord_compare(const coord c1, const coord c2);

// coord 깊은 복사
BYUL_API coord coord_copy(const coord c);

// ------------------------------------------------------------------------end

// coord 구조체 전용 함수들
// start----------------------------------------------------------------------

// x 접근자
BYUL_API gint     coord_get_x(const coord c);
// x 설정자
BYUL_API void     coord_set_x(coord c, gint x);

// y 접근자
BYUL_API gint     coord_get_y(const coord c);
// y 설정자
BYUL_API void     coord_set_y(coord c, gint y);

// 좌표를 64비트로 패킹
BYUL_API guint64  coord_pack(const coord c);
// 패킹된 값에서 coord 생성
BYUL_API coord    coord_unpack(guint64 packed);

BYUL_API void     coord_set(coord c, gint x, gint y);

BYUL_API void     coord_fetch(coord c, gint* out_x, gint* out_y);
// ------------------------------------------------------------------------end

// BYUL_API gint coord_compare(gconstpointer a, gconstpointer b);
BYUL_API gint coord_compare(const coord a, const coord b);

#ifdef __cplusplus
}
#endif

#endif // COORD_H
