from PySide6.QtWidgets import QDockWidget, QTabWidget
from PySide6.QtCore import Qt

from ui.console_output import ConsoleOutputWidget
from ui.time_graph_widget import TimeGraphWidget
from ui.time_graph_panel import TimeGraphPanel
from utils.log_to_panel import g_logger

from grid.grid_canvas import GridCanvas

class BottomDockingPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("바텀 패널", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)

        self.parent = parent 

        self.tabs = QTabWidget()
        self.setWidget(self.tabs)

        # Console 탭
        self.console_widget = None
        self.add_console_tab()

        # Time Graph 탭
        self.time_graph_panel = None

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.on_tab_close_requested)

    def add_console_tab(self):
        if self.console_widget is not None:
            return  # 이미 추가됨

        self.console_widget = ConsoleOutputWidget()

        self.tabs.addTab(self.console_widget, "Console")

        # 🔄 탭 전환
        self.tabs.setCurrentWidget(self.console_widget)

        g_logger.log_emitted.connect(self.console_widget.log)

    def remove_console_tab(self):
        if self.console_widget is None:
            return

        index = self.tabs.indexOf(self.console_widget)
        if index != -1:
            self.tabs.removeTab(index)

        self.console_widget = None

    def switch_console_tab(self, checked: bool):
        if checked:
            self.add_console_tab()
        else:
            if self.console_widget:
                self.remove_console_tab()

    def add_time_graph_tab(self):
        if self.time_graph_panel is not None:
            return  # 이미 추가됨

        self.time_graph_panel = TimeGraphPanel()

        self.tabs.addTab(self.time_graph_panel, "Time Graph")

        # 🔄 탭 전환
        self.tabs.setCurrentWidget(self.time_graph_panel)

    def remove_time_graph_tab(self):
        if self.time_graph_panel is None:
            return

        index = self.tabs.indexOf(self.time_graph_panel)
        if index != -1:
            self.tabs.removeTab(index)

        self.time_graph_panel = None

    def switch_time_graph_tab(self, checked: bool):
        if checked:
            self.add_time_graph_tab()
        else:
            if self.time_graph_panel:
                self.remove_time_graph_tab()

    def bind_canvas(self, canvas:GridCanvas):
        if self.time_graph_panel is None:
            self.add_time_graph_tab()

        self.time_graph_panel.bind_canvas(canvas)

    def check_auto_hide(self):
        if self.tabs.count() == 0:
            self.setVisible(False)

    def on_tab_close_requested(self, index: int):
        widget = self.tabs.widget(index)

        # 콘솔 위젯이면 내부 참조도 제거
        if widget == self.console_widget:
            self.parent.actions.console_tab_toggle_action.setChecked(False)
            self.console_widget = None

        elif widget == self.time_graph_panel:
            self.parent.actions.time_graph_tab_toggle_action.setChecked(False)            
            self.time_graph_panel = None

        self.tabs.removeTab(index)
        self.check_auto_hide()
