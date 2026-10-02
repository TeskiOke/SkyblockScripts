import flet as ft
from .base_module import SkyblockModule

class FlippingModule(SkyblockModule):
    def __init__(self):
        super().__init__("Flipping", "swap_horiz")
        self.results_container = ft.Column(scroll="auto", expand=True)

    def build_ui(self):
        return ft.Column([
            ft.Row([
                ft.Text("Bazaar / AH Flipping", size=24, weight="bold"),
                ft.IconButton(icon="refresh", on_click=self.update_table)
            ], alignment="spaceBetween"),
            ft.Divider(),
            ft.Container(content=ft.Text("Module in development...", size=16), padding=20),
            self.results_container
        ], expand=True)

    def update_table(self, e=None):
        pass


if __name__ == "__main__":
    """
    CLI-запуск модуля Flipping.
    Пока логика не реализована, выводим простой markdown-отчёт-заглушку.
    """
    import pathlib
    from datetime import datetime

    project_root = pathlib.Path(__file__).resolve().parents[1]
    out_path = project_root / "flipping_report.md"

    lines = []
    lines.append(f"# Flipping report (stub)")
    lines.append(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_")
    lines.append("")
    lines.append("Модуль флипа ещё в разработке. Здесь позже появятся сделки с Bazaar/AH.")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Markdown report written to: {out_path}")
