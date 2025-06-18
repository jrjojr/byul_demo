from PySide6.QtWidgets import (
    QMenuBar, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtGui import QAction, QKeySequence
from dialogs.goto_dialog import GotoDialog
from ui.actions import Actions

class MenuBar(QMenuBar):
    def __init__(self, actions:Actions, parent):
        super().__init__(parent)

        self.actions = actions
        self.parent = parent
        
        self._setup_menus()

        self.parent.side_panel.visibilityChanged.connect(
            self.actions.side_panel_toggle_action.setChecked)
                
        self.parent.bottom_panel.visibilityChanged.connect(
            self.actions.bottom_panel_toggle_action.setChecked)

    def _setup_menus(self):
        self._setup_file_menu()
        self._setup_edit_menu()
        self._setup_tool_menu()
        self._setup_view_menu()
        self._setup_help_menu()

    def _setup_file_menu(self):
        file_menu = self.addMenu("&File")

        file_menu.addAction(self.actions.load_action)
        file_menu.addAction(self.actions.save_action)

        file_menu.addSeparator()

        file_menu.addAction(self.actions.exit_action)

    def _setup_edit_menu(self):
        edit_menu = self.addMenu("&Edit")

        edit_menu.addAction(self.actions.set_start_action)
        edit_menu.addAction(self.actions.append_goal_action)
        edit_menu.addAction(self.actions.add_obstacle_action)
        edit_menu.addAction(self.actions.remove_obstacle_action)

        edit_menu.addSeparator()
        
        edit_menu.addAction(self.actions.find_path_action)
        edit_menu.addAction(self.actions.clear_path_action)

    def _setup_tool_menu(self):
        tool_menu = self.addMenu("&Tool")

        tool_menu.addAction(self.actions.goto_action)

    def _setup_view_menu(self):
        view_menu = self.addMenu("&View")

        view_menu.addAction(self.actions.side_panel_toggle_action)
        view_menu.addAction(self.actions.bottom_panel_toggle_action)

        view_menu.addSeparator()

        view_menu.addAction(self.actions.console_tab_toggle_action)
        view_menu.addAction(self.actions.time_graph_tab_toggle_action)

        view_menu.addSeparator()

        view_menu.addAction(self.actions.fullscreen_action)

    def _setup_help_menu(self):
        help_menu = self.addMenu("&Help")
        # future help actions
