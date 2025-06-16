from PySide6.QtWidgets import QDockWidget, QTabWidget
from PySide6.QtCore import Qt

from grid.grid_settings import GridSettingsWidget  # 외부 정의된 설정 위젯

class SideDockingPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("설정 패널", parent)
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
            )
        self.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable
            )

        self.tabs = QTabWidget()
        self.setWidget(self.tabs)

        # 탭 추가: GridCanvas 관련 설정
        self.canvas_settings_widget = GridSettingsWidget()
        self.tabs.addTab(self.canvas_settings_widget, "GridCanvas")

    def bind_canvas(self, canvas):
        """GridCanvas 객체를 설정 위젯에 연결"""
        self.canvas = canvas        
        self.canvas_settings_widget.bind_canvas(canvas)
        self.canvas.grid_changed.connect(self.on_canvas_grid_changed)        

    def refresh_all(self):
        """외부에서 수동으로 전체 패널 갱신 요청 시"""
        self.canvas_settings_widget.refresh()

    def on_canvas_grid_changed(self, grid_width:int, grid_height:int):
        self.canvas_settings_widget.refresh()
