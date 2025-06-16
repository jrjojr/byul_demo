import sys

from gui.config import BYUL_WORLD_ENV_PATH, BYUL_WORLD_PATH, WRAPPER_PATH
# config 로딩용 로딩을 해야 필요한 디렉토리가 추가된다 sys.path에...
print(f'BYUL_WORLD_ENV_PATH : {BYUL_WORLD_ENV_PATH}')
print(f'BYUL_WORLD_PATH : {BYUL_WORLD_PATH}')
print(f'WRAPPER_PATH : {WRAPPER_PATH}')    

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QCursor, QKeyEvent
from PySide6.QtCore import QTimer, Qt, QEvent

from grid.grid_map import GridMap
from grid.grid_canvas import GridCanvas

from ui.menu_actions import MenuBar
from ui.side_panel import SideDockingPanel
from ui.bottom_panel import BottomDockingPanel
from ui.toolbar_panel import ToolbarPanel

from utils.log_to_panel import g_logger

class GridViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Viewer")

        QApplication.instance().focusWindowChanged.connect(
            self._on_focus_window_changed)

        # === Core Components ===
        self.grid_map = GridMap()
        self.grid_canvas = GridCanvas(self.grid_map, parent=self)
        self.setCentralWidget(self.grid_canvas)

        # === Dock Panels ===
        self.bottom_panel = BottomDockingPanel(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_panel)
        
        g_logger.log_emitted.connect(self.bottom_panel.console_widget.log)

        self.side_panel = SideDockingPanel(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.side_panel)

        self.setMenuBar(MenuBar(self))
        self.menuBar().action_loopgraph_tab.triggered.connect(
            self.on_loopgraph_tab_toggled
        )
        self.menuBar()._action_fullscreen.setChecked(False)

        self.toolbar_panel = ToolbarPanel(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar_panel)
        # 툴바에 콜백 연결
        self.toolbar_panel.set_command_callback(self._handle_toolbar_command)
        self.toolbar_panel.set_mode_callback(
            self.grid_canvas.set_click_mode)        

        # === UI Finalization ===
        self.bottom_panel.console_widget.log("✅ Console log test")
        QTimer.singleShot(100, self.center_window)
        QTimer.singleShot(0, self.grid_canvas.setFocus)

    def center_window(self):
        screen = QApplication.screenAt(QCursor.pos()) or \
                 QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        size = self.frameGeometry()
        self.move(
(screen_geometry.width() - size.width()) // 2 + screen_geometry.x(),
(screen_geometry.height() - size.height()) // 2 + screen_geometry.y()
        )

    def on_loopgraph_tab_toggled(self, checked: bool):
        if checked:
            self.bottom_panel.add_loop_graph_tab()
            self.bottom_panel.loop_graph_widget.resume()
            self.bottom_panel.loop_graph_widget.bind_canvas(self.grid_canvas)
        else:
            if self.bottom_panel.loop_graph_widget:
                self.bottom_panel.loop_graph_widget.pause()
            self.bottom_panel.remove_loop_graph_tab()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            # ⇨ 일반 모드로 복귀
            self.side_panel.show()
            self.bottom_panel.show()
            self.toolbar_panel.show()
            self.menuBar().show()
            self.showNormal()
            self.menuBar()._action_fullscreen.setChecked(False)
        else:
            # ⇨ 풀스크린 진입
            self.side_panel.hide()
            self.bottom_panel.hide()
            # self.toolbar_panel.hide()
            self.menuBar().hide()
            self.showFullScreen()
            self.grid_canvas.setFocus()
            self.menuBar()._action_fullscreen.setChecked(True)

    def _on_focus_window_changed(self, window):
        if window != self.window():
            # 다른 창으로 전환됨
            self.grid_canvas._pressed_keys.clear()

    def _on_focus_window_changed(self, window):
        if window != self.window():
            for key in list(self.grid_canvas._pressed_keys):
                fake_release = QKeyEvent(QEvent.KeyRelease, key, Qt.NoModifier)
                self.keyReleaseEvent(fake_release)
            self.grid_canvas._pressed_keys.clear()            

    def _handle_toolbar_command(self, command: str):
        if command == "find_path":
            self.grid_canvas.grid_map_ctr.find_path(self.grid_canvas.selected_npc)
        elif command == "clear_path":
            self.grid_canvas.grid_map_ctr.clear_path()
        elif command == "view_proto_path":
            self.grid_canvas.grid_map_ctr.to_proto_path_cells(self.grid_canvas.selected_npc)
        elif command == "view_real_path":
            self.grid_canvas.grid_map_ctr.to_real_path_cells(self.grid_canvas.selected_npc)            
        elif command == "clear_proto_path":
            self.grid_canvas.selected_npc.clear_proto_path()            
        elif command == "clear_real_path":
            self.grid_canvas.selected_npc.clear_real_path()                        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = GridViewer()
    viewer.resize(1000, 900)
    viewer.show()
    sys.exit(app.exec())
