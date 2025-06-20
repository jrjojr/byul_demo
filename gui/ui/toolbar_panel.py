from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from  ui.actions import Actions



class ToolbarPanel(QToolBar):
    """
    메인 툴바 패널
    - 클릭 모드 전환: NPC 추가/제거
    - 명령 실행: 경로 찾기, 초기화 등
    """

    def __init__(self, actions:Actions, parent):
        super().__init__("Main Toolbar", parent)

        self.actions = actions
        self.setMovable(True)
        self.setFloatable(True)
        self.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)

        self._mode_callback = None  # GridViewer에 전달될 모드 콜백
        self._command_callback = None  # GridMapController에 전달될 명령 콜백

        self.addAction(self.actions.select_npc_action)
        self.addAction(self.actions.spawn_npc_at_action)
        self.addAction(self.actions.despawn_npc_at_action)
        self.addAction(self.actions.clear_route_action)
        self.addAction(self.actions.view_proto_route_action)
        self.addAction(self.actions.view_real_route_action)
        self.addAction(self.actions.clear_proto_route_action)
        self.addAction(self.actions.clear_real_route_action)        
