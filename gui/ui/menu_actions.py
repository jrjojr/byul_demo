from PySide6.QtWidgets import (
    QMenuBar, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtGui import QAction, QKeySequence
from dialogs.goto_dialog import GotoDialog

class MenuBar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._setup_menus()

    def _setup_menus(self):
        self._setup_file_menu()
        self._setup_edit_menu()
        self._setup_tool_menu()
        self._setup_view_menu()
        self._setup_help_menu()

    def _setup_file_menu(self):
        file_menu = self.addMenu("&File")

        load_action = QAction("&Load Grid Data", self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.triggered.connect(self.load_grid)
        file_menu.addAction(load_action)

        save_action = QAction("&Save Grid Data", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_grid)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(exit_action)

    def _setup_edit_menu(self):
        edit_menu = self.addMenu("&Edit")

        set_start_action = QAction("Set &Start", self)
        set_start_action.triggered.connect(lambda: 
            self.parent.grid_ctr.set_start_from_selection())
        
        edit_menu.addAction(set_start_action)

        append_goal_action = QAction("Set &Goal", self)
        append_goal_action.triggered.connect(lambda: 
            self.parent.grid_ctr.append_goal_from_selection())
        
        edit_menu.addAction(append_goal_action)

        add_obstacle_action = QAction("Add &Obstacle", self)
        add_obstacle_action.triggered.connect(lambda: 
            self.parent.grid_ctr.add_obstacle_from_selection())
        
        edit_menu.addAction(add_obstacle_action)

        remove_obstacle_action = QAction("Remove Obstacle", self)
        remove_obstacle_action.triggered.connect(lambda: 
            self.parent.grid_ctr.remove_obstacle_from_selection())
        
        edit_menu.addAction(remove_obstacle_action)

        edit_menu.addSeparator()

        find_path_action = QAction("&Find Path", self)
        find_path_action.triggered.connect(lambda: 
            self.parent.grid_ctr.find_path())
        
        edit_menu.addAction(find_path_action)

        clear_path_action = QAction("&Clear Path", self)
        clear_path_action.triggered.connect(lambda: 
            self.parent.grid_ctr.clear_path())
        
        edit_menu.addAction(clear_path_action)

    def _setup_tool_menu(self):
        tool_menu = self.addMenu("&Tool")

        goto_action = QAction("&Move to Center", self)
        goto_action.setShortcut("Ctrl+G")
        goto_action.triggered.connect(self.show_goto_dialog)
        tool_menu.addAction(goto_action)

    def _setup_view_menu(self):
        view_menu = self.addMenu("&View")

        self.action_side_panel = QAction("Side Panel", self, checkable=True)
        self.action_side_panel.setChecked(True)
        self.action_side_panel.triggered.connect(self.toggle_side_panel)
        view_menu.addAction(self.action_side_panel)

        self.action_bottom_panel = QAction(
            "Bottom Panel", self, checkable=True)
        
        self.action_bottom_panel.setChecked(True)
        self.action_bottom_panel.triggered.connect(self.toggle_bottom_panel)
        view_menu.addAction(self.action_bottom_panel)

        view_menu.addSeparator()

        self.action_console_tab = QAction("Console Tab", self, checkable=True)
        self.action_console_tab.setChecked(True)
        self.action_console_tab.triggered.connect(lambda checked: 
            self.toggle_bottom_tab("Console", checked))
        
        view_menu.addAction(self.action_console_tab)

        self.action_loopgraph_tab = QAction(
            "Loop Graph Tab", self, checkable=True)
        
        self.action_loopgraph_tab.setChecked(False)
        # self.action_loopgraph_tab.setChecked(True)
        self.action_loopgraph_tab.triggered.connect(lambda checked: 
            self.toggle_bottom_tab("Loop Graph", checked))
        
        view_menu.addAction(self.action_loopgraph_tab)

        self.parent.side_panel.visibilityChanged.connect(
            self.action_side_panel.setChecked)
        
        self.parent.bottom_panel.visibilityChanged.connect(
            self.action_bottom_panel.setChecked)
        
        view_menu.addSeparator()

        fullscreen_action = QAction("Full Screen", self, checkable=True)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.parent.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        self._action_fullscreen = fullscreen_action

    def _setup_help_menu(self):
        help_menu = self.addMenu("&Help")
        # future help actions

    def load_grid(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, 
            "Open Grid File", "", "JSON Files (*.json)")
        
        if file_path:
            try:
                self.parent.canvas.load_from_file(file_path)
            except Exception as e:
                QMessageBox.critical(self.parent, "Load Error", str(e))

    def save_grid(self):
        file_path, _ = QFileDialog.getSaveFileName(self.parent, 
            "Save Grid File", "grid_data.json", "JSON Files (*.json)")
        
        if file_path:
            try:
                self.parent.canvas.save_to_file(file_path)
            except Exception as e:
                QMessageBox.critical(self.parent, "Save Error", str(e))

    def show_goto_dialog(self):
        dialog = GotoDialog()
        if dialog.exec():
            gx, gy = dialog.get_coords()
            self.parent.grid_canvas.grid_map.set_center(gx, gy)

    def toggle_side_panel(self, visible):
        self.parent.side_panel.setVisible(visible)

    def toggle_bottom_panel(self, visible):
        self.parent.bottom_panel.setVisible(visible)

    def toggle_bottom_tab(self, tab_name, visible):
        tab_widget = self.parent.bottom_panel.tabs
        for i in range(tab_widget.count()):
            if tab_widget.tabText(i) == tab_name:
                tab_widget.setTabVisible(i, visible)
                return
