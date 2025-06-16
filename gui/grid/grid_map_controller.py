from PySide6.QtCore import Qt, QPoint, QObject, Slot

from grid.grid_cell import GridCell, CellStatus, CellFlag, TerrainType
from grid.grid_map import GridMap

from coord import c_coord
from path import calc_direction
from npc.npc import NPC

from utils.log_to_panel import g_logger
import time

class GridMapController(QObject):
    def __init__(self, grid_map: GridMap, parent=None):
        super().__init__()
        self.grid_map = grid_map
        self.parent = parent
        self.npc_list: list[NPC] = []

    def add_npc(self, npc: NPC):
        self.npc_list.append(npc)
        npc.parent = self
        npc.anim_to_arrived.connect(lambda coord, n=npc: 
                                      self.on_anim_to_arrived(n, coord))
        # 이동 불가한 테란 전부 제거
        # normal로 설정하면 제거된다.
        cell = self.get_cell(npc.start)
        cell.terrain = TerrainType.NORMAL
        self.grid_map.map.unblock(npc.start.x, npc.start.y)
        
        self.place_npc(npc)

    def get_cell(self, coord: c_coord) -> GridCell | None:
        if not coord:
            return None
        return self.grid_map.get(coord.x, coord.y)

    def add_obstacle(self, coord: c_coord):
        cell = self.get_cell(coord)
        if cell:
            cell.terrain = TerrainType.MOUNTAIN
            # self.grid_map.map.block(coord.x, coord.y)

    def remove_obstacle(self, coord: c_coord):
        cell = self.get_cell(coord)
        if cell:
            cell.terrain = TerrainType.NORMAL
            # self.grid_map.map.unblock(coord.x, coord.y)

    def toggle_obstacle(self, coord: c_coord):
        cell = self.get_cell(coord)
        if not cell:
            return
        if cell.terrain == TerrainType.MOUNTAIN:
            self.remove_obstacle(coord)
        else:
            self.add_obstacle(coord)

    def set_start(self, npc: NPC, coord: c_coord):
        new_cell = self.get_cell(coord)
        if new_cell and npc.is_movable(new_cell):
            old_cell = self.get_cell(npc.start)
            if old_cell:
                old_cell.remove_flag(CellFlag.START)
            new_cell.add_flag(CellFlag.START)
            npc.start = coord
            npc.goal = coord
            self.place_npc(npc)
        else:
            g_logger.log_always(f'{coord}는 npc가 이동할 수 없는 테란타입이다.')

    def set_goal(self, npc: NPC, coord: c_coord):
        new_cell = self.get_cell(coord)
        if new_cell and npc.is_movable(new_cell):
            old_cell = self.get_cell(npc.goal)
            old_cell.remove_flag(CellFlag.GOAL)
            for c in npc.flush_goal_q():
                old_cell = self.get_cell(c)
                if old_cell:
                    old_cell.remove_flag(CellFlag.GOAL)

            new_cell.add_flag(CellFlag.GOAL)
            self.clear_path()
            npc.move_to(coord)
        else:
            g_logger.log_always(f'{coord}는 장애물 좌표이다.')

    def append_goal(self, npc: NPC, coord: c_coord):
        new_cell = self.get_cell(coord)
        if new_cell:
            new_cell.add_flag(CellFlag.GOAL)
        npc.append_goal(coord)
        self.find_path(npc)

    def find_path(self, npc: NPC):
        if g_logger.debug_mode:
            t0 = time.time()
        # npc.start_finding()
        npc.find()
        if g_logger.debug_mode:
            t1 = time.time()
            elapsed = t1 - t0
            g_logger.log_debug(f'elapsed : {elapsed:.3f} msec')

    def clear_path(self):
        self.grid_map.clear_path_flags()

    @Slot(NPC)
    def to_real_path_cells(self, npc:NPC):
        if not npc.real_queue.empty():
            g_logger.log_debug('real_coord_큐에 쌓인 경로를 가져온다.')
            npc.on_real_path_found()

        path = npc.real_coord_list
        for i in range(len(path)):
            c = path[i]
            if (cell := self.grid_map.get(c.x, c.y)):
                cell.add_flag(CellFlag.PATH)
                # cell.path_dir = path.get_direction(i)
                if i < len(path)-1:
                    cell.path_dir = calc_direction(c, path[i+1])
                else:
                    cell.path_dir = calc_direction(path[i-1], c)
        pass

    @Slot(NPC)
    def to_proto_path_cells(self, npc:NPC):
        if not npc.proto_queue.empty():
            g_logger.log_debug('to_proto_큐에 쌓인 경로를 가져온다.')            
            npc.on_proto_path_found()
            
        path = npc.proto_coord_list
        for i in range(len(path)):
            c = path[i]
            if (cell := self.grid_map.get(c.x, c.y)):
                cell.add_flag(CellFlag.PATH)
                # cell.path_dir = path.get_direction(i)
                if i < len(path)-1:
                    cell.path_dir = calc_direction(c, path[i+1])
                else:
                    cell.path_dir = calc_direction(path[i-1], c)                    

        pass        

    def place_npc(self, npc: NPC):
        coord = npc.start
        cell = self.get_cell(coord)
        if cell:
            cell.add_npc(npc.id)

            # 경로 제거
            if cell.has_flag(CellFlag.PATH):
                cell.remove_flag(CellFlag.PATH)

            # 목표 제거
            if cell.has_flag(CellFlag.GOAL):
                cell.remove_flag(CellFlag.GOAL)

    def remove_npc(self, npc: NPC):
        coord = npc.start
        cell = self.get_cell(coord)
        if cell:
            cell.remove_npc(npc.id)
            self.grid_map.map.unblock(cell.x, cell.y)

    @Slot(c_coord)
    def on_anim_to_arrived(self, npc: NPC, coord: c_coord):
        self.remove_npc(npc)
        npc.start = coord
        self.place_npc(npc)

        pass

    @Slot(c_coord)
    def on_move_to_started(self, npc: NPC, coord: c_coord):
        # self.remove_npc(npc)
        next_cell = self.get_cell(coord)
        next_cell.add(CellFlag.PATH)
        next_cell.path_dir = calc_direction(npc.start, coord)

        pass
