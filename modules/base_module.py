import flet as ft

class SkyblockModule:
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

    def build_ui(self):
        return ft.Column([ft.Text(f"Module {self.name}")])

    def update_table(self, e=None):
        pass
