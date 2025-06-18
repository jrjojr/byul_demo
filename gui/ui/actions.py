from PySide6.QtWidgets import (
    QMenuBar, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import QObject


from dialogs.goto_dialog import GotoDialog

from utils.log_to_panel import g_logger

class Actions(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parent = parent

        load_action = QAction("&Load Grid Data", parent)
        load_action.setShortcut(QKeySequence.Open)
        load_action.triggered.connect(self.on_load_action_triggered)
        self.load_action = load_action

        save_action = QAction("&Save Grid Data", parent)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.on_save_action_triggered)
        self.save_action = save_action

        exit_action = QAction("E&xit", parent)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(QApplication.instance().quit)
        self.exit_action = exit_action

        set_start_action = QAction("Set &Start", parent)
        set_start_action.triggered.connect(
            self.on_set_start_action_triggered)
        self.set_start_action = set_start_action

        append_goal_action = QAction("Set &Goal", parent)
        append_goal_action.triggered.connect(
            self.on_append_goal_action_triggered)
        self.append_goal_action = append_goal_action

        add_obstacle_action = QAction("Add &Obstacle", parent)
        add_obstacle_action.triggered.connect(
            self.on_add_obstacle_action_triggered)
        self.add_obstacle_action = add_obstacle_action

        remove_obstacle_action = QAction("Remove Obstacle", parent)
        remove_obstacle_action.triggered.connect(
            self.on_remove_obstacle_action_triggered)
        self.remove_obstacle_action = remove_obstacle_action

        find_route_action = QAction("&Find Route", parent)
        find_route_action.triggered.connect(
            self.on_find_route_action_triggered)
        self.find_route_action = find_route_action

        clear_route_action = QAction("&Clear Route", parent)
        clear_route_action.triggered.connect(
            self.on_clear_route_action_triggered)
        self.clear_route_action = clear_route_action

        goto_action = QAction("&Move to Center", parent)
        goto_action.setShortcut("Ctrl+G")
        goto_action.triggered.connect(self.on_goto_action_triggered)
        self.goto_action = goto_action

        side_panel_toggle_action = QAction(
            "Side Panel Toggle", parent, checkable=True)
        side_panel_toggle_action.setChecked(True)
        side_panel_toggle_action.triggered.connect(
            self.on_side_panel_toggle_action_triggered)
        self.side_panel_toggle_action = side_panel_toggle_action

        self.bottom_panel_toggle_action = QAction(
            "Bottom Panel", parent, checkable=True)
        self.bottom_panel_toggle_action.setChecked(True)
        self.bottom_panel_toggle_action.triggered.connect(
            self.on_bottom_panel_toggle_action_triggered)

        self.console_tab_toggle_action = QAction(
            "Console Tab", parent, checkable=True)
        self.console_tab_toggle_action.setChecked(True)
        self.console_tab_toggle_action.setData("Console")
        self.console_tab_toggle_action.triggered.connect(
            self.on_console_tab_toggle_action_triggered)
        
        self.time_graph_tab_toggle_action = QAction(
            "Time Graph Tab", parent, checkable=True)
        self.time_graph_tab_toggle_action.setChecked(False)
        self.time_graph_tab_toggle_action.setData("Time Graph")
        self.time_graph_tab_toggle_action.triggered.connect(
            self.on_time_graph_tab_toggle_action_triggered)
        
        self.fullscreen_action = QAction("Full Screen", parent, checkable=True)
        self.fullscreen_action.setShortcut("F11")
        self.fullscreen_action.setChecked(False)
        self.fullscreen_action.triggered.connect(
            self.on_fullscreen_action_triggered)
        
        self.select_npc_action = QAction('NPC 선택', parent)
        self.select_npc_action.setToolTip(
            '화면의 셀을 클릭하면 가장 첫 번째 NPC를 선택합니다')
        self.select_npc_action.triggered.connect(
            self.on_select_npc_action_triggered)
        
        self.add_npc_action = QAction('NPC 추가', parent)
        self.add_npc_action.setToolTip(
            '화면의 셀을 클릭하면 랜덤 ID로 NPC를 추가합니다')
        self.add_npc_action.triggered.connect(
            self.on_add_npc_action_triggered)
        
        self.remove_npc_action = QAction('NPC 제거', parent)
        self.remove_npc_action.setToolTip(
            '화면의 셀을 클릭하면 해당 좌표의 NPC를 제거합니다')
        self.remove_npc_action.triggered.connect(
            self.on_remove_npc_action_triggered)        
        
        self.clear_route_action = QAction('경로 초기화', parent)
        self.clear_route_action.setToolTip(
            '모든 ROUTE 플래그를 제거합니다')
        self.clear_route_action.triggered.connect(
            self.on_clear_route_action_triggered)
        
        self.view_proto_route_action = QAction('npc의 초기 경로 보기', parent)
        self.view_proto_route_action.setToolTip(
            'npc의 초기 경로를 보여준다')
        self.view_proto_route_action.triggered.connect(
            self.on_view_proto_route_action_triggered)

        self.view_real_route_action = QAction('npc의 실제 경로 보기', parent)
        self.view_real_route_action.setToolTip(
            'npc의 실제 경로를 보여준다')
        self.view_real_route_action.triggered.connect(
            self.on_view_real_route_action_triggered)
        
        self.clear_proto_route_action = QAction('npc의 초기 경로 삭제', parent)
        self.clear_proto_route_action.setToolTip(
            'npc의 초기 경로를 삭제한다')
        self.clear_proto_route_action.triggered.connect(
            self.on_clear_proto_route_action_triggered)        

        self.clear_real_route_action = QAction('npc의 실제 경로 삭제', parent)
        self.clear_real_route_action.setToolTip(
            'npc의 실제 경로를 삭제한다')
        self.clear_real_route_action.triggered.connect(
            self.on_clear_real_route_action_triggered)
        
    def on_load_action_triggered(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, 
            "Open Grid File", "", "JSON Files (*.json)")
        
        if file_path:
            try:
                self.parent.canvas.load_from_file(file_path)
            except Exception as e:
                QMessageBox.critical(self.parent, "Load Error", str(e))

    def on_save_action_triggered(self):
        file_path, _ = QFileDialog.getSaveFileName(self.parent, 
            "Save Grid File", "grid_data.json", "JSON Files (*.json)")
        
        if file_path:
            try:
                self.parent.canvas.save_to_file(file_path)
            except Exception as e:
                QMessageBox.critical(self.parent, "Save Error", str(e))

    def on_set_start_action_triggered(self):
        self.parent.grid_ctr.set_start_from_selection()

    def on_append_goal_action_triggered(self):
        self.parent.grid_ctr.append_goal_from_selection()

    def on_add_obstacle_action_triggered(self):
        self.parent.grid_ctr.add_obstacle_from_selection()

    def on_remove_obstacle_action_triggered(self):
        self.parent.grid_ctr.remove_obstacle_from_selection()

    def on_find_route_action_triggered(self):
        self.parent.grid_ctr.find_route()
    
    def on_clear_route_action_triggered(self):
        self.parent.grid_ctr.clear_route()

    def on_goto_action_triggered(self):
        dialog = GotoDialog()
        if dialog.exec():
            gx, gy = dialog.get_coords()
            self.parent.grid_canvas.grid_map.set_center(gx, gy)

    def on_side_panel_toggle_action_triggered(self, checked):
        self.parent.side_panel.setVisible(checked)

    def on_bottom_panel_toggle_action_triggered(self, checked):
        if checked:
            if self.parent.bottom_panel.time_graph_panel:
                self.parent.bottom_panel.time_graph_panel.graph_widget.resume()
        else:
            if self.parent.bottom_panel.time_graph_panel:
                self.parent.bottom_panel.time_graph_panel.graph_widget.pause()

        self.parent.bottom_panel.setVisible(checked)

    def on_console_tab_toggle_action_triggered(self, checked):
        if checked:
            self.parent.bottom_panel.add_console_tab()
        else:
            self.parent.bottom_panel.remove_console_tab()

        tab_widget = self.parent.bottom_panel.tabs
        tab_name = self.sender().data()

        for i in range(tab_widget.count()):
            if tab_widget.tabText(i) == tab_name:
                tab_widget.setTabVisible(i, checked)
                return

    def on_time_graph_tab_toggle_action_triggered(self, checked: bool):
        if checked:
            self.parent.bottom_panel.bind_canvas(self.parent.grid_canvas)
            self.parent.bottom_panel.add_time_graph_tab()
        else:
            self.parent.bottom_panel.remove_time_graph_tab()

        tab_widget = self.parent.bottom_panel.tabs
        tab_name = self.sender().data()

        for i in range(tab_widget.count()):
            if tab_widget.tabText(i) == tab_name:
                tab_widget.setTabVisible(i, checked)
                return        

    def on_fullscreen_action_triggered(self):
        self.parent.toggle_fullscreen

    def on_select_npc_action_triggered(self):
        self.parent.grid_canvas.set_click_mode('select_npc')
        setting_widget = self.parent.side_panel.canvas_setting_widget
        setting_widget.set_combo_click_mode('select_npc')

    def on_add_npc_action_triggered(self):
        self.parent.grid_canvas.set_click_mode('add_npc')        
        setting_widget = self.parent.side_panel.canvas_setting_widget
        setting_widget.set_combo_click_mode('add_npc')        

    def on_remove_npc_action_triggered(self):
        self.parent.grid_canvas.set_click_mode('remove_npc')     
        setting_widget = self.parent.side_panel.canvas_setting_widget
        setting_widget.set_combo_click_mode('remove_npc')        

    def on_clear_route_action_triggered(self):
        self.parent.grid_canvas.grid_map_ctr.clear_route()

    def on_view_proto_route_action_triggered(self):
        self.parent.grid_canvas.grid_map_ctr.to_proto_route_cells(
            self.parent.grid_canvas.selected_npc)

    def on_view_real_route_action_triggered(self):
        self.parent.grid_canvas.grid_map_ctr.to_real_route_cells(
            self.parent.grid_canvas.selected_npc)

    def on_clear_proto_route_action_triggered(self):
        if self.parent.grid_canvas.selected_npc:
            self.parent.grid_canvas.selected_npc.clear_proto_route()
        else:
            g_logger.log_always(f'현재 선택된 npc가 없어여')

    def on_clear_real_route_action_triggered(self):
        if self.parent.grid_canvas.selected_npc:
            self.parent.grid_canvas.selected_npc.clear_real_route()
        else:
            g_logger.log_always(f'현재 선택된 npc가 없어여')            

