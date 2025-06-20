from PySide6.QtCore import Qt, QPoint, QObject, Slot, Signal, QTimer

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

        cell = self.get_cell(start)
        if not cell:
            g_logger.log_debug(f'왜 셀이 없지? add_npc 종료한다.')
            return 

        npc = NPC(npc_id, self.grid_map, start, cell_size=self.parent.cell_size)
        self.npc_dict[npc_id] = npc
        npc.parent = self
        npc.anim_to_arrived.connect(lambda coord, n=npc: 
                                        self.on_anim_to_arrived(n, coord))

        
        if cell.terrain not in npc.movable_terrain:
            npc.movable_terrain.append(cell.terrain)

        self.place_npc_to_cell(npc, start)

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
            cell.remove_npc_id(npc_id)
        else:
            g_logger.log_debug(
                f'npc({npc_id})의 위치 셀을 찾을 수 없음: {npc.start}')

        # 관련 리소스 해제 (비동기 스레드 종료 등 추가 처리 필요 시 여기에)
        npc.close()

        # 시그널 전파
        self.npc_removed.emit(npc_id)

    def on_npc_spawn(self, block_key: c_coord):
        block = self.grid_map.block_cache.get(block_key)
        if not block:
            return

        # self._pending_npcs = []
        pending_npcs = []
        for cell in block.cells.values():
            for npc_id in cell.npc_ids:
                # self._pending_npcs.append((npc_id, c_coord(cell.x, cell.y)))
                pending_npcs.append((npc_id, c_coord(cell.x, cell.y)))

        # self._spawn_next_npc_batch()
        self._spawn_npc_batch(pending_npcs)

    # def _spawn_next_npc_batch(self, batch_size: int = 10):
    #     count = 0
    #     while self._pending_npcs and count < batch_size:
    #         npc_id, coord = self._pending_npcs.pop(0)
    #         self.add_npc(npc_id, start=coord)
    #         count += 1

    #     if self._pending_npcs:
    #         QTimer.singleShot(2, lambda: self._spawn_next_npc_batch(batch_size))

    def _spawn_npc_batch(self, pending_npcs: list[tuple[str, c_coord]], batch_size: int = 10):
        if not pending_npcs:
            return

        def run_batch():
            count = 0
            while pending_npcs and count < batch_size:
                npc_id, coord = pending_npcs.pop(0)
                self.add_npc(npc_id, coord)
                count += 1

            if pending_npcs:
                QTimer.singleShot(2, run_batch)

        run_batch()

    # def on_npc_evict(self, block_key: c_coord):
    #     # self._pending_npc_removals = []
    #     pending_npc_removals = []

    #     for npc_id, npc in self.npc_dict.items():
    #         if npc == self.parent.selected_npc:
    #             self.parent.selected_npc = None
    #         key_for_npc = self.grid_map.get_origin(npc.start.x, npc.start.y)
    #         if key_for_npc == block_key:
    #             # self._pending_npc_removals.append(npc_id)
    #             self.pending_npc_removals.append(npc_id)                

    #     self._evict_next_npc_batch()

    # def _evict_next_npc_batch(self, batch_size: int = 10):
    #     count = 0
    #     while self._pending_npc_removals and count < batch_size:
    #         npc_id = self._pending_npc_removals.pop(0)
    #         self.remove_npc(npc_id)
    #         g_logger.log_debug(f"[on_npc_evict:batch] NPC 제거됨: {npc_id}")
    #         count += 1

    #     if self._pending_npc_removals:
    #         QTimer.singleShot(2, lambda: self._evict_next_npc_batch(batch_size))

    def on_npc_evict(self, block_key: c_coord):
        # 지역 리스트 생성 (공유 필드 대신)
        pending_npc_removals = []

        for npc_id, npc in self.npc_dict.items():
            if npc == self.parent.selected_npc:
                self.parent.selected_npc = None

            key_for_npc = self.grid_map.get_origin(npc.start.x, npc.start.y)
            if key_for_npc == block_key:
                pending_npc_removals.append(npc_id)

        self._evict_npc_batch(pending_npc_removals)

    def _evict_npc_batch(self, pending_npc_removals: list[str], 
                        batch_size: int = 10):
        if not pending_npc_removals:
            return

        def run_batch():
            count = 0
            while pending_npc_removals and count < batch_size:
                npc_id = pending_npc_removals.pop(0)
                self.remove_npc(npc_id)
                g_logger.log_debug(f"[on_npc_evict:batch] NPC 제거됨: {npc_id}")
                count += 1

            if pending_npc_removals:
                QTimer.singleShot(2, run_batch)

        run_batch()

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
            self.place_npc_to_cell(npc)
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

        route = npc.real_route
        for i in range(len(route)):
            c = route.get_coord_at(i)
            if (cell := self.grid_map.get(c.x, c.y)):
                cell.add_flag(CellFlag.ROUTE)
        pass

    @Slot(NPC)
    def to_proto_route_cells(self, npc:NPC):
        if not npc.proto_queue.empty():
            g_logger.log_debug('to_proto_큐에 쌓인 경로를 가져온다.')            
            npc.on_proto_route_found()

        route = npc.proto_route
        for i in range(len(route)):
            c = route.get_coord_at(i)
            if (cell := self.grid_map.get(c.x, c.y)):
                cell.add_flag(CellFlag.ROUTE)
        pass        

    def place_npc_to_cell(self, npc: NPC, coord:c_coord):
        # npc가 기존에 있던 셀에서 제거한다.
        cell = self.get_cell(npc.start)
        cell.remove_npc_id(npc.id)

        # 새로운 위체의 셀에 npc를 추가한다.
        npc.start = coord
        cell = self.get_cell(coord)
        cell.add_npc_id(npc.id)

        # 경로 제거
        if cell.has_flag(CellFlag.ROUTE):
            cell.remove_flag(CellFlag.ROUTE)

        # 목표 제거
        if cell.has_flag(CellFlag.GOAL):
            cell.remove_flag(CellFlag.GOAL)

    @Slot(c_coord)
    def on_anim_to_arrived(self, npc: NPC, coord: c_coord):
        self.place_npc_to_cell(npc, coord)

        pass
