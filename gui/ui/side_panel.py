from PySide6.QtWidgets import QDockWidget, QTabWidget
from PySide6.QtCore import Qt

from grid.canvas_setting_widget import CanvasSettingWidget  # 외부 정의된 설정 위젯
from grid.grid_canvas import GridCanvas

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
        self.canvas_setting_widget = CanvasSettingWidget()
        self.tabs.addTab(self.canvas_setting_widget, "GridCanvas")

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.on_tab_close_requested)
        
    def bind_canvas(self, canvas:GridCanvas):
        self.canvas_setting_widget.bind_canvas(canvas)

    def check_auto_hide(self):
        if self.tabs.count() == 0:
            self.setVisible(False)  # 또는 self.parent().removeDockWidget(self)

    def on_tab_close_requested(self, index: int):
        widget = self.tabs.widget(index)

        # 내부 위젯 참조 제거 (옵션)
        if widget == self.canvas_setting_widget:
            self.canvas_setting_widget = None

        self.tabs.removeTab(index)
        self.check_auto_hide()
