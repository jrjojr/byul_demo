# 리팩터링된 GridCanvas - View 전용, 오프스크린 렌더링 최적화
from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPixmap, QMouseEvent, QWheelEvent, 
    QCursor, QPen, QBrush
)
from PySide6.QtCore import (
    Qt, QPoint, Signal, Slot, QTimer, QRect, QEvent, QLine
)

from grid.grid_cell import GridCell, CellStatus, CellFlag, TerrainType
from grid.grid_map import GridMap
from grid.grid_map_controller import GridMapController
from coord import c_coord
from path import PathDir
import time
from utils.log_to_panel import g_logger
from utils.mouse_input_handler import MouseInputHandler

from npc.npc import NPC

from pathlib import Path

from config import IMAGES_PATH
DEFAULT_OBSTACLE_PATH = IMAGES_PATH / 'byul_world_obstacle.png'
DEFAULT_OBSTACLE_FOR_NPC_PATH = IMAGES_PATH / 'byul_world_obstacle_for_npc.png'

DEFAULT_START_PATH = IMAGES_PATH / 'byul_world_start.png'
DEFAULT_GOAL_PATH = IMAGES_PATH / 'byul_world_goal.png'
DEFAULT_EMPTY_PATH = IMAGES_PATH / 'byul_world_empty.png'

DEFAULT_NPC_PATH = IMAGES_PATH / 'npc/byul_world_npc_un.png'
SELECTED_NPC_PATH = IMAGES_PATH / 'npc/byul_world_npc_sl.png'

from utils.image_loader import load_image

class GridCanvas(QWidget):
    '''GridCanvas는 사용자와의 상호 작용을 담당하며,
       오프스크린 렌더링을 통해 성능을 최적화한다.'''
    grid_changed = Signal(int, int)
    cell_size_changed = Signal(int)
    key_pressed = Signal()
    key_released = Signal()

    draw_cells_elapsed = Signal(float)
    draw_cells_started = Signal(float)
    draw_cells_ended = Signal(float)

    npc_selected = Signal(NPC)

    def __init__(self, grid_map: GridMap, msec_per_frame=30, parent=None):
        super().__init__(parent)

        self.grid_map = grid_map
        self.grid_map_ctr = GridMapController(self.grid_map, parent=self)

        self.cell_size = 80

        self.min_size_for_text = 50
        self.grid_width = 11
        self.grid_height = 11
        self.setMinimumSize(500, 500)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self._pressed_keys = set()

        self.cached_pixmap = None
        self.needs_redraw = True
        self.icon_cache = {}

        self.default_empty_cell_color = QColor(30, 30, 30)

        self.logic_timer = QTimer(self)
        self.logic_timer.timeout.connect(self._tick)
        self.logic_timer.start(msec_per_frame)

        self.wheel_timer = QTimer()
        self.wheel_timer.setSingleShot(True)
        self.wheel_timer.timeout.connect(self.change_grid_from_window)

        self.change_grid_from_window()
        self.grid_changed.connect(self.grid_map.set_buffer_width_height)
        self.grid_map.buffer_changed.connect(self.request_redraw)

        self.click_mode = "select_npc"

        # 예: 초기화 시 핸들러 연결
        self.mouse_handler = MouseInputHandler(self)
        self.mouse_handler.clicked.connect(self._on_clicked)
        self.mouse_handler.mouse_moved.connect(self._on_mouse_moved)
        self.mouse_handler.double_clicked.connect(self._on_dbl_clicked)
        self.last_mouse_pos = QPoint()

        # self.cell_size_changed.connect(self.grid_map_ctr.npc.set_cell_size)
        self.cell_size_changed.connect(self.on_cell_size_changed)
        self.set_cell_size(80)

        # self.npc_selected.connect(self.on_npc_selected)
        # self.request_redraw()
        self.selected_npc = None
        self.selected_npc_image = None

    def request_redraw(self):
        self.needs_redraw = True

    # def showEvent(self, event):
    #     super().showEvent(event)
    #     self._tick()  # 첫 틱 강제 실행
    #     self.request_redraw()


    def showEvent(self, event):
        super().showEvent(event)
        npc_id = NPC.generate_random_npc_id()
        npc = NPC(npc_id, self.grid_map, cell_size=self.cell_size)
        QTimer.singleShot(1000, lambda: 
                          self.grid_map_ctr.add_npc(npc)
        )
        g_logger.log_always(
            f"최초의 NPC 추가됨: {npc_id} at ({npc.start.x},{npc.start.y})")
        # print(f"최초의 NPC 추가됨: {npc_id} at ({npc.start.x},{npc.start.y})")
        self.selected_npc = npc
        self.selected_npc_image = load_image(SELECTED_NPC_PATH)                

    def enterEvent(self, event):
        if not self.hasFocus():
            self.setFocus(Qt.OtherFocusReason)
            g_logger.log_debug('GridCanvas가 잃었던 포커스를 다시 회복했다')
        super().enterEvent(event)

    def resizeEvent(self, event):
        self.change_grid_from_window()
        self.request_redraw()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.cached_pixmap:
            painter.drawPixmap(0, 0, self.cached_pixmap)

    def _tick(self):
        now = time.time()
        if not hasattr(self, "_last_tick_time") or self._last_tick_time is None:
            self._last_tick_time = now
            return

        elapsed_sec = now - self._last_tick_time
        self._last_tick_time = now

        # 키 입력 등은 중앙 tick에서 처리하도록 이동
        if self.grid_map_ctr.npc_list:
            for npc in self.grid_map_ctr.npc_list:
                npc.on_tick(elapsed_sec)

        self.move_from_keys(self._pressed_keys)
        self.grid_map.update_buffer_cells()

        if self.needs_redraw:
            self.draw_cells_to_pixmap()
            self.needs_redraw = False

        self.update()

    def draw_cells_to_pixmap(self):
        if g_logger.debug_mode:
            t0 = time.time()
            self.draw_cells_started.emit(t0)

        w, h = self.width(), self.height()
        self.cached_pixmap = QPixmap(w, h)
        self.cached_pixmap.fill(Qt.darkGray)

        painter = QPainter(self.cached_pixmap)
        painter.setFont(QFont("Courier", 8))

        font = QFont("Courier", 10)
        pen_black = QPen(Qt.black)
        brush_empty = QBrush(self.default_empty_cell_color)

        center_x, center_y = self.grid_map.get_center()
        min_x = center_x - (self.grid_width // 2)
        min_y = center_y - (self.grid_height // 2)

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                gx = min_x + x
                gy = min_y + y
                px, py = self.convert_pos_grid_to_win(x, y)
                cell = self.grid_map.get(gx, gy)

                if cell is None:
                    painter.setBrush(brush_empty)
                    painter.drawRect(px, py, self.cell_size, self.cell_size)
                    continue

                # painter.setBrush(cell.get_color())
                # painter.drawRect(px, py, self.cell_size, self.cell_size)

                icon_path = Path()

                if cell.terrain == TerrainType.MOUNTAIN:
                    icon_path = DEFAULT_OBSTACLE_PATH
                    # self.selected_npc.finder.map.block(cell.x, cell.y)                    
                    pass
                elif not cell.terrain in self.selected_npc.movable_terrain:
                    icon_path = DEFAULT_OBSTACLE_FOR_NPC_PATH
                    # self.selected_npc.finder.map.block(cell.x, cell.y)
                    pass
                elif cell.status == CellStatus.NPC:
                    # start = c_coord(cell.x, cell.y)
                    # npc = NPC(cell.npc_ids[0], self.grid_map, start,
                    #           cell_size=self.cell_size)
                    # self.grid_map_ctr.add_npc(npc) 
                    icon_path = DEFAULT_NPC_PATH
                    pass
                else:
                    icon_path = DEFAULT_EMPTY_PATH
                    if cell.has_flag(CellFlag.PATH):
                        icon_path = cell.get_path_image()
                        pass                    
                    if cell.has_flag(CellFlag.START):
                        icon_path = DEFAULT_START_PATH
                        pass
                    if cell.has_flag(CellFlag.GOAL):
                        icon_path = DEFAULT_GOAL_PATH
                        pass                

                if icon_path:
                    icon = self.get_icon(icon_path)
                    painter.drawPixmap(
                        px, py, self.cell_size, self.cell_size, icon)

                if self.cell_size > self.min_size_for_text:
                    painter.setPen(pen_black)
                    painter.setFont(font)
                    painter.drawText(px, py, self.cell_size, self.cell_size, 
                                     Qt.AlignCenter, cell.text())

        for npc in self.grid_map_ctr.npc_list:
            npc_phantom_start = npc.phantom_start
            win_pos_x, win_pos_y = self.get_win_pos_at_coord(npc_phantom_start)

            if win_pos_x and win_pos_y:
                npc.draw_npc( painter, win_pos_x, win_pos_y)
                
        if self.selected_npc:
            npc_phantom_start = self.selected_npc.phantom_start
            win_pos_x, win_pos_y = self.get_win_pos_at_coord(npc_phantom_start)
            if win_pos_x and win_pos_y:
                self.draw_selected_npc(painter, win_pos_x, win_pos_y,
                                        self.selected_npc.disp_dx, 
                                        self.selected_npc.disp_dy)

        if self.last_mouse_pos:
            self.draw_hover_cell(painter, self.last_mouse_pos)

        painter.end()

        if g_logger.debug_mode:
            t1 = time.time()
            elapsed = (t1 - t0) * 1000
            QTimer.singleShot(0, lambda: self.draw_cells_ended.emit(t1))
            QTimer.singleShot(0, lambda: self.draw_cells_elapsed.emit(elapsed))

    def get_icon(self, path):
        if path not in self.icon_cache:
            self.icon_cache[path] = QPixmap(path)
        return self.icon_cache[path]

    # 나머지: 입력 처리, hover 표시, 클릭 처리 등은 원래 코드 유지
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            if self.window().isFullScreen():
                self.window().toggle_fullscreen()
                return
        elif key == Qt.Key_Space:
            cell = self.get_cell_at_win_pos(
                self.last_mouse_pos.x(), self.last_mouse_pos.y())
            c = c_coord(cell.x, cell.y)
            self.grid_map_ctr.toggle_obstacle(c)

        # print(f"[KEY] {event.key()}, focus: {self.hasFocus()}")            

        # 나머지는 일반 키로 취급
        self._pressed_keys.add(key)
        self.key_pressed.emit()

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self._pressed_keys.discard(event.key())
        self.key_released.emit()        

    # 마우스 이동 시 위치 저장 후 업데이트
    def _on_mouse_moved(self, event: QMouseEvent):
        self.last_mouse_pos = event.position().toPoint()
        # self.update()

    def focusOutEvent(self, event):
        self._pressed_keys.clear()
        super().focusOutEvent(event)

    def event(self, event):
        if event.type() == QEvent.WindowDeactivate:
            self._pressed_keys.clear()
        return super().event(event)

    def _on_clicked(self, event: QMouseEvent):
        pos = event.position().toPoint()

        if event.button() == Qt.LeftButton:
            self._handle_left_click(pos)

        elif event.button() == Qt.RightButton:
            if event.modifiers() & Qt.ShiftModifier:
                self._handle_shift_right_click(pos)
            else:
                self._handle_right_click(pos)

        elif event.button() == Qt.MiddleButton:
            cell = self.get_cell_at_win_pos(pos.x(), pos.y())
            if cell:
                g_logger.log_always(
                    f"중간 클릭 at {pos.x()}, {pos.y()}, 셀 키 ({cell.x},{cell.y})")
                self.grid_map.set_center(cell.x, cell.y)

    def _on_dbl_clicked(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # 더블 클릭 위치
            pos = event.position().toPoint()
            cell = self.get_cell_at_win_pos(pos.x(), pos.y())
            g_logger.log_always(
                f"더블 클릭 at {pos.x()}, {pos.y()}, 셀 키 ({cell.x},{cell.y})")    
        # self.update()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        scale = 1.1 if delta > 0 else 1 / 1.1
        new_size = max(10, min(self.cell_size * scale, 
                               min(self.width(), self.height())))
        
        self.set_cell_size(int(new_size))
        self.wheel_timer.start(50)
        # self.update()

    def convert_pos_grid_to_win(self, cx, cy):
        margin_x = (self.width() - self.grid_width * self.cell_size) // 2
        margin_y = (self.height() - self.grid_height * self.cell_size) // 2
        return margin_x + cx * self.cell_size, margin_y + cy * self.cell_size

    def convert_pos_win_to_grid(self, x, y):
        margin_x = (self.width() - self.grid_width * self.cell_size) // 2
        margin_y = (self.height() - self.grid_height * self.cell_size) // 2
        return (x - margin_x) // self.cell_size, \
            (y - margin_y) // self.cell_size

    def change_grid_from_window(self):
        w = self.width()
        h = self.height()
        self.grid_width = ((w - self.cell_size) // self.cell_size | 1)
        self.grid_height = ((h - self.cell_size) // self.cell_size | 1)

        self.grid_changed.emit(self.grid_width, self.grid_height)

    def draw_hover_cell(self, painter: QPainter, pos: QPoint, cell_size=80):

        # mouse_pos = self.mapFromGlobal(QCursor.pos())

        # x = mouse_pos.x()
        # y = mouse_pos.y()

        x, y = pos.x(), pos.y()

        canvas_width = self.width()
        canvas_height = self.height()

        cell = self.get_cell_at_win_pos(x, y)
        if not cell:
            center_x, center_y = self.grid_map.get_center()
            cell = self.grid_map.get(center_x, center_y)

        # 셀 사각형 기본 위치는 마우스 위치 기준
        # rect_x = (x // cell_size) * cell_size
        # rect_y = (y // cell_size) * cell_size

        rect_x = x
        rect_y = y
        

        # 오른쪽/아래쪽 경계에 가까우면 왼쪽/위쪽으로 이동
        if rect_x + cell_size > canvas_width:
            rect_x = max(0, canvas_width - cell_size)
        if rect_y + cell_size > canvas_height:
            rect_y = max(0, canvas_height - cell_size)

        rect = QRect(rect_x, rect_y, cell_size, cell_size)

        # 배경: 반투명 검정
        painter.setBrush(QColor(0, 0, 0, 127))
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)

        # 텍스트: 흰색
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(rect, Qt.AlignCenter, cell.text())

    def get_cell_at_mouse(self):
        pos = self.last_mouse_pos
        cx, cy = self.convert_pos_win_to_grid(pos.x(), pos.y())
        center_x, center_y = self.grid_map.get_center()

        if not (0 <= cx < self.grid_width and 0 <= cy < self.grid_height):
            return None  # 마우스가 그리드 바깥이면 None

        gx = center_x - self.grid_width // 2 + cx
        gy = center_y - self.grid_height // 2 + cy
        return self.grid_map.get(gx, gy)  # 셀이 존재하지 않으면 자동으로 None
   
    def get_cell_at_win_pos(self, x, y):
        cx, cy = self.convert_pos_win_to_grid(x, y)
        cx = min(max(cx, 0), self.grid_width - 1)
        cy = min(max(cy, 0), self.grid_height - 1)

        center_x, center_y = self.grid_map.get_center()
        gx = center_x - self.grid_width // 2 + cx
        gy = center_y - self.grid_height // 2 + cy

        return self.grid_map.get(gx, gy)

    def get_cell_at_grid(self, grid_x:int, grid_y:int):
        center_x, center_y = self.grid_map.get_center()
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            gx = center_x - self.grid_width // 2 + grid_x
            gy = center_y - self.grid_height // 2 + grid_y
            return self.grid_map.get(gx, gy)
        return None
    
    def get_grid_at_cell(self, cell: GridCell):
        cx, cy = cell.x, cell.y
        center_x, center_y = self.grid_map.get_center()

        grid_x = cx - (center_x - self.grid_width // 2)
        grid_y = cy - (center_y - self.grid_height // 2)

        # 바깥이면 가장 가까운 경계로 클램프
        grid_x = min(max(grid_x, 0), self.grid_width - 1)
        grid_y = min(max(grid_y, 0), self.grid_height - 1)

        return grid_x, grid_y

    def get_grid_at_coord(self, coord:c_coord):
        cx, cy = coord.x, coord.y
        center_x, center_y = self.grid_map.get_center()

        grid_x = cx - (center_x - self.grid_width // 2)
        grid_y = cy - (center_y - self.grid_height // 2)

        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return grid_x, grid_y
        return None, None
    
    def get_win_pos_at_grid(self, grid_x:int, grid_y:int):
        pos_x, pos_y = self.convert_pos_grid_to_win(grid_x, grid_y)
        return pos_x, pos_y
    
    def get_win_pos_at_coord(self, coord:c_coord):
        gx, gy = self.get_grid_at_coord(coord)

        if gx == None or gy == None:
            return None, None
        
        return self.get_win_pos_at_grid(gx, gy)
    
    def set_cell_size(self, cell_size:int):
        self.cell_size = cell_size
        self.cell_size_changed.emit(cell_size)

    def _handle_left_click(self, pos:QPoint):
        x = pos.x()
        y = pos.y()
        cell = self.get_cell_at_win_pos(x, y)
        gx = cell.x
        gy = cell.y

        coord = c_coord(gx, gy)
        if self.click_mode == "select_npc":
            npc = self.get_first_npc_in_cell(cell)
            if npc:
                self.selected_npc = npc
                self.npc_selected.emit(npc)
                g_logger.log_always(f"✅ 선택된 NPC: {npc.id}")
            else:
                g_logger.log_always("⚠️ 해당 셀에 NPC가 없습니다.")
        
        elif self.click_mode == "add_npc":
            npc_id = NPC.generate_random_npc_id()
            npc = NPC(npc_id, self.grid_map,cell_size=self.cell_size)
            npc.start = coord
            self.grid_map_ctr.add_npc(npc)
            g_logger.log_always(f"NPC 추가됨: {npc_id} at ({coord.x},{coord.y})")

        elif self.click_mode == "remove_npc":
            if cell.npc_ids:
                npc_id = cell.npc_ids[0]  # 임시로 첫 NPC만 제거
                npc = next((n for n in self.grid_map_ctr.npc_list if n.id == npc_id), None)
                if npc:
                    self.grid_map_ctr.remove_npc(npc)
                    self.grid_map_ctr.npc_list.remove(npc)
                    g_logger.log_always(f"NPC 제거됨: {npc_id} at ({coord.x},{coord.y})")

        elif self.click_mode == "obstacle":
            g_logger.log_debug(f"장애물 추가: ({gx}, {gy})")            
            self.grid_map_ctr.add_obstacle(coord)

    def _handle_right_click(self, pos:QPoint):
        x = pos.x()
        y = pos.y()
        # gx, gy = self.convert_pos_win_to_grid(x, y)
        cell = self.get_cell_at_win_pos(x, y)        
        gx = cell.x
        gy = cell.y
        
        coord = c_coord(gx, gy)

        if self.click_mode == "select_npc":
            if self.selected_npc:
                g_logger.log_always(f"🔴 목표 위치 설정: ({gx}, {gy})")
                self.grid_map_ctr.set_goal(self.selected_npc, coord)
            
            else:
                g_logger.log_always("⚠️ 현재 선택된 NPC가 없습니다.")

        elif self.click_mode == "obstacle":
            g_logger.log_debug(f"장애물 제거: ({gx}, {gy})")
            self.grid_map_ctr.remove_obstacle(coord)

    def _handle_shift_right_click(self, pos:QPoint):
        x = pos.x()
        y = pos.y()
        # gx, gy = self.convert_pos_win_to_grid(x, y)
        cell = self.get_cell_at_win_pos(x, y)        
        gx = cell.x
        gy = cell.y
        
        coord = c_coord(gx, gy)

        if self.click_mode == "select_npc":
            if self.selected_npc:
                g_logger.log_always(f"🔴 목표 위치 추가: ({gx}, {gy})")
                self.grid_map_ctr.append_goal(self.selected_npc, coord)
            else:
                g_logger.log_always("⚠️ 현재 선택된 NPC가 없습니다.")

    def set_click_mode(self, mode: str):
        g_logger.log_debug(f"🛠️ 클릭 모드 전환됨: {mode}")        
        self.click_mode = mode

    def move_from_keys(self, pressed_keys):
        # g_logger.log_debug(f'move_From_keys는 동작하나? : {pressed_keys}')
        dx = dy = 0
        if Qt.Key_Left in pressed_keys:
            dx -= 1
        if Qt.Key_Right in pressed_keys:
            dx += 1
        if Qt.Key_Up in pressed_keys:
            dy -= 1
        if Qt.Key_Down in pressed_keys:
            dy += 1
        self.grid_map.move_center(dx, dy)
    
    @Slot(int, int)
    def on_center_change(self, x:int, y:int):
        pass

    def get_first_npc_in_cell(self, cell: GridCell) -> NPC | None:
        if not cell.npc_ids:
            return None
        first_id = cell.npc_ids[0]
        return next(
            (npc for npc in self.grid_map_ctr.npc_list if npc.id == first_id), 
            None)
    

    @Slot(int)
    def on_cell_size_changed(self, cell_size:int):
        if self.grid_map_ctr.npc_list:
            for npc in self.grid_map_ctr.npc_list:
                npc.set_cell_size(cell_size)
    @Slot(NPC)
    def on_npc_selected(self, npc:NPC):
        # self.grid_map_ctr.to_proto_path_cells(npc)
        # self.grid_map_ctr.to_real_path_cells(npc)
        npc_coord = npc.start
        cell:GridCell = self.grid_map_ctr.get_cell(npc_coord)
        if cell:
            cell.add(CellFlag.START)

    def draw_selected_npc(self, painter, win_pos_x:int, win_pos_y:int, 
                          disp_dx:float, disp_dy:float):
        '''실제 디바이스에 이미지를 그린다.
        '''
        x = win_pos_x +  int(disp_dx)
        y = win_pos_y +  int(disp_dy)

        # 배경: 반투명 검정
        # rect = QRect(x, y, self.m_cell_size, self.m_cell_size)
        # painter.setBrush(QColor(0, 0, 0, 127))
        # painter.setPen(Qt.NoPen)
        # painter.drawRect(rect)

        image = self.selected_npc_image
        painter.drawPixmap(
                x, y, self.cell_size, self.cell_size, image)
