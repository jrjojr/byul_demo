from PySide6.QtCore import Qt, QPoint, QObject, Slot, Signal

from grid.grid_cell import GridCell, CellStatus, CellFlag, TerrainType
from grid.grid_map import GridMap
from grid.grid_block import GridBlock

from coord import c_coord
from route import calc_direction
from npc.npc import NPC

from utils.log_to_panel import g_logger
import time

class GridMapController(QObject):
    npc_added = Signal(str)
    npc_removed = Signal(str)

    def __init__(self, grid_map: GridMap, parent=None):
        super().__init__()
        self.grid_map = grid_map
        self.parent = parent
        self.npc_dict: dict[str, NPC] = dict()

        self.grid_map.on_npc_spawn = self.on_npc_spawn
        self.grid_map.on_npc_evict = self.on_npc_evict

    def has_npc(self, npc_id):
        if npc_id in self.npc_dict:
            return True
        
        return False
    
    def get_npc(self, npc_id) -> NPC | None:
        return self.npc_dict.get(npc_id)
    
    def add_npc(self, npc_id, start:c_coord):
        # 이미 self가 npc를 가지고 있으며 종료한다.
        if self.has_npc(npc_id):
            return 
        
        npc = NPC(npc_id, self.grid_map, start, cell_size=self.parent.cell_size)
        self.npc_dict[npc_id] = npc
        npc.parent = self
        npc.anim_to_arrived.connect(lambda coord, n=npc: 
                                        self.on_anim_to_arrived(n, coord))

        cell = self.get_cell(npc.start)
        if cell.terrain not in npc.movable_terrain:
            npc.movable_terrain.append(cell.terrain)

        self.place_npc(npc, npc.start)

        self.npc_added.emit(npc_id)

    def remove_npc(self, npc_id):
        # npc 존재 여부 확인
        if not self.has_npc(npc_id):
            g_logger.log_debug(f'npc({npc_id})가 존재하지 않아서 종료한다.')
            return

        # npc 객체 추출
        npc: NPC = self.npc_dict.pop(npc_id)

        # 현재 위치 기준 셀에서 npc 제거
        cell = self.get_cell(npc.start)
        if cell:
            cell.remove_npc(npc_id)
        else:
            g_logger.log_debug(
                f'npc({npc_id})의 위치 셀을 찾을 수 없음: {npc.start}')

        # 관련 리소스 해제 (비동기 스레드 종료 등 추가 처리 필요 시 여기에)
        npc.close()

        # 시그널 전파
        self.npc_removed.emit(npc_id)

    def on_npc_spawn(self, block_key: c_coord):
        """주어진 블락 내 셀에 포함된 npc_id 목록을 기준으로 
        NPC를 생성하여 등록한다."""
        block = self.grid_map.block_cache.get(block_key)
        if block:
            for cell in block.cells.values():
                for npc_id in cell.npc_ids:
                    self.add_npc(npc_id, start=c_coord(cell.x, cell.y))
                    g_logger.log_debug(f"[on_npc_spawn] NPC 생성됨: "
                                    f"{npc_id} @ ({cell.x}, {cell.y})")
        else:
            g_logger.log_debug(f'키 {block_key}에 해당하는 block이 존재하지 않는다')

    def on_npc_evict(self, block_key: c_coord):
        """현재 해당 블락에 위치한 NPC만 찾아서 remove_npc로 제거한다."""

        for npc_id, npc in list(self.npc_dict.items()):  # dict 크기 중간 변경 대비
            npc_block = self.grid_map.coord_to_block(npc.start)
            if npc_block == block_key:
                self.remove_npc(npc_id)
                g_logger.log_debug(
                    f"[on_npc_evict] NPC 제거됨: {npc_id} @ block {block_key}")

    def get_cell(self, coord: c_coord) -> GridCell:
        return self.grid_map.get(coord.x, coord.y)

    def add_obstacle(self, coord: c_coord, npc:NPC):
        cell = self.get_cell(coord)
        if cell and npc:
            # 1. NPC가 모든 지형을 갈 수 있다면 → 장애물 개념 없음
            if not npc.movable_terrain:
                cell.terrain = TerrainType.MOUNTAIN
                g_logger.log_always(
                    f"[SET OBSTACLE] {coord} → {npc.id}는 "
                    f"모든 terrain을 이동 가능함 "
                    f"그래서 가장 어려운 MOUNTAIN으로 설정한다."
                )
                return

            # 2. 현재 terrain이 NPC 기준 이동 가능하다면 → 바꿔야 함
            if cell.terrain in npc.movable_terrain:
                # NPC가 못 가는 terrain 중 하나로 교체 (기본은 MOUNTAIN)
                for terrain in TerrainType:
                    if terrain not in npc.movable_terrain:
                        cell.terrain = terrain
                        g_logger.log_always(
                            f"[SET OBSTACLE] {coord} → terrain = "
                            f"{terrain.name} (not movable by {npc.id})"
                        )
                        return
            else:
                g_logger.log_always(
                    f"[SKIP SET OBSTACLE] {coord} → {npc.id} 기준으로 "
                    f"이미 이동 불가 terrain ({cell.terrain.name})"
                )

    def remove_obstacle(self, coord: c_coord, npc:NPC):
        cell = self.get_cell(coord)
        if cell and npc:
            if not npc.movable_terrain:
                cell.terrain = TerrainType.NORMAL
                g_logger.log_always(
                    f"[REMOVE OBSTACLE] {coord} → {npc.id}는 "
                    f"모든 terrain 이동 가능 → terrain=NORMAL로 초기화"
                )
                return

            if npc.movable_terrain:
                old_terrain = cell.terrain
                new_terrain = npc.movable_terrain[0]
                cell.terrain = new_terrain
                g_logger.log_always(
                    f"[REMOVE OBSTACLE] {coord} → {npc.id} 기준 장애물 제거 "
                    f"({old_terrain.name} → {new_terrain.name})"
                )

    def toggle_obstacle(self, coord: c_coord, npc:NPC):
        cell = self.get_cell(coord)
        if not cell or not npc:
            return

        if cell.terrain not in npc.movable_terrain:
            # 현재 terrain은 NPC 기준 장애물이다 → 해제
            self.remove_obstacle(coord, npc)
        else:
            # 현재 terrain은 NPC가 통과 가능 → 새 장애물 생성
            self.add_obstacle(coord, npc)


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
            self.clear_route()
            npc.move_to(coord)
        else:
            g_logger.log_always(f'{coord}는 장애물 좌표이다.')

    def append_goal(self, npc: NPC, coord: c_coord):
        new_cell = self.get_cell(coord)
        if new_cell:
            new_cell.add_flag(CellFlag.GOAL)
        npc.append_goal(coord)
        self.find_route(npc)

    def find_route(self, npc: NPC):
        if g_logger.debug_mode:
            t0 = time.time()
        # npc.start_finding()
        npc.find()
        if g_logger.debug_mode:
            t1 = time.time()
            elapsed = t1 - t0
            g_logger.log_debug(f'elapsed : {elapsed:.3f} msec')

    def clear_route(self):
        self.grid_map.clear_route_flags()

    @Slot(NPC)
    def to_real_route_cells(self, npc:NPC):
        if not npc.real_queue.empty():
            g_logger.log_debug('real_coord_큐에 쌓인 경로를 가져온다.')
            npc.on_real_route_found()

        route = npc.real_coord_list
        for i in range(len(route)):
            c = route[i]
            if (cell := self.grid_map.get(c.x, c.y)):
                cell.add_flag(CellFlag.ROUTE)
                # cell.route_dir = route.get_direction(i)
                if i < len(route)-1:
                    cell.route_dir = calc_direction(c, route[i+1])
                else:
                    cell.route_dir = calc_direction(route[i-1], c)
        pass

    @Slot(NPC)
    def to_proto_route_cells(self, npc:NPC):
        if not npc.proto_queue.empty():
            g_logger.log_debug('to_proto_큐에 쌓인 경로를 가져온다.')            
            npc.on_proto_route_found()
            
        route = npc.proto_coord_list
        for i in range(len(route)):
            c = route[i]
            if (cell := self.grid_map.get(c.x, c.y)):
                cell.add_flag(CellFlag.ROUTE)
                # cell.route_dir = route.get_direction(i)
                if i < len(route)-1:
                    cell.route_dir = calc_direction(c, route[i+1])
                else:
                    cell.route_dir = calc_direction(route[i-1], c)                    

        pass        

    def place_npc(self, npc: NPC, coord:c_coord):
        # npc가 기존에 있던 셀에서 제거한다.
        cell = self.get_cell(npc.start)
        cell.remove_npc(npc.id)

        # 새로운 위체의 셀에 npc를 추가한다.
        npc.start = coord
        cell = self.get_cell(coord)
        cell.add_npc(npc.id)

        # 경로 제거
        if cell.has_flag(CellFlag.ROUTE):
            cell.remove_flag(CellFlag.ROUTE)

        # 목표 제거
        if cell.has_flag(CellFlag.GOAL):
            cell.remove_flag(CellFlag.GOAL)

    @Slot(c_coord)
    def on_anim_to_arrived(self, npc: NPC, coord: c_coord):
        self.place_npc(npc, coord)

        pass

    @Slot(c_coord)
    def on_move_to_started(self, npc: NPC, coord: c_coord):
        next_cell = self.get_cell(coord)
        next_cell.add(CellFlag.ROUTE)
        next_cell.route_dir = calc_direction(npc.start, coord)

        pass
