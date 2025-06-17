from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt



class ToolbarPanel(QToolBar):
    """
    메인 툴바 패널
    - 클릭 모드 전환: NPC 추가/제거
    - 명령 실행: 경로 찾기, 초기화 등
    """

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        self.setMovable(True)
        self.setFloatable(True)
        self.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)

        self._actions: dict[str, QAction] = {}
        self._mode_callback = None  # GridViewer에 전달될 모드 콜백
        self._command_callback = None  # GridMapController에 전달될 명령 콜백

        self._setup_actions()

    def _setup_actions(self):
        self.add_action(
            "NPC 선택", lambda: self._change_mode("select_npc"),
            "화면의 셀을 클릭하면 가장 첫 번째 NPC를 선택합니다"
        )        
        self.add_action(
            "NPC 추가", lambda: self._change_mode("spawn_npc"),
            "화면의 셀을 클릭하면 랜덤 ID로 NPC를 추가합니다"
        )
        self.add_action(
            "NPC 제거", lambda: self._change_mode("remove_npc"),
            "화면의 셀을 클릭하면 해당 좌표의 NPC를 제거합니다"
        )
        self.add_action(
            "경로 초기화", lambda: self._execute_command("clear_path"),
            "모든 PATH 플래그를 제거합니다"
        )
        self.add_action(
            "npc의 초기 경로 보기", lambda: self._execute_command("view_proto_path"),
            "npc의 초기 경로를 보여준다"
        )
        self.add_action(
            "npc의 동적 경로 보기", lambda: self._execute_command("view_real_path"),
            "npc의 동적 경로를 보여준다"
        )
        self.add_action(
            "npc의 초기 경로 삭제", lambda: self._execute_command("clear_proto_path"),
            "npc의 초기 경로를 삭제한다"
        )                
        self.add_action(
            "npc의 동적 경로 삭제", lambda: self._execute_command("clear_real_path"),
            "npc의 동적 경로를 삭제한다"
        )        


    def set_mode_callback(self, callback):
        """GridViewer에 등록할 모드 변경 콜백"""
        self._mode_callback = callback

    def set_command_callback(self, callback):
        """GridMapController에 등록할 명령 실행 콜백"""
        self._command_callback = callback

    def _change_mode(self, mode: str):
        if self._mode_callback:
            self._mode_callback(mode)

    def _execute_command(self, command: str):
        if self._command_callback:
            self._command_callback(command)

    def add_action(self, name: str, callback, tooltip: str = None):
        action = QAction(name, self)
        action.triggered.connect(callback)
        if tooltip:
            action.setToolTip(tooltip)
        self.addAction(action)
        self._actions[name] = action

    def get_action(self, name: str) -> QAction | None:
        return self._actions.get(name)

