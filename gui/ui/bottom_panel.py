from PySide6.QtWidgets import QDockWidget, QTabWidget
from PySide6.QtCore import Qt

from ui.console_output import ConsoleOutputWidget
from ui.loop_time_graph_widget import LoopTimeGraphWidget
from ui.loop_time_graph_panel import LoopTimeGraphPanel
from utils.log_to_panel import g_logger


class BottomDockingPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("바텀 패널", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)

        self.tabs = QTabWidget()
        self.setWidget(self.tabs)

        # Console 탭은 항상 존재
        self.console_widget = ConsoleOutputWidget()
        self.tabs.addTab(self.console_widget, "Console")

        # Loop Graph 관련은 조건부로 추가됨
        self.loop_graph_panel = None
        self.loop_graph_widget = None  # 외부 참조를 위한 placeholder

    # def add_loop_graph_tab(self):
    #     if self.loop_graph_panel is not None:
    #         return  # 이미 추가됨

    #     self.loop_graph_panel = LoopTimeGraphPanel()
    #     self.loop_graph_widget = self.loop_graph_panel.graph_widget
    #     self.tabs.addTab(self.loop_graph_panel, "Loop Graph")

    def add_loop_graph_tab(self):
        if self.loop_graph_panel is not None:
            return  # 이미 추가됨

        self.loop_graph_panel = LoopTimeGraphPanel()
        self.loop_graph_widget = self.loop_graph_panel.graph_widget

        self.tabs.addTab(self.loop_graph_panel, "Loop Graph")

        # 🔄 탭 전환
        self.tabs.setCurrentWidget(self.loop_graph_panel)

    def remove_loop_graph_tab(self):
        if self.loop_graph_panel is None:
            return

        index = self.tabs.indexOf(self.loop_graph_panel)
        if index != -1:
            self.tabs.removeTab(index)

        self.loop_graph_panel = None
        self.loop_graph_widget = None
