import flet as ft
import requests
from .base_module import SkyblockModule

class FarmingModule(SkyblockModule):
    def __init__(self):
        self.results_container = ft.Column(scroll="auto", expand=True)
        super().__init__("Farming", "grass")
        self.api_url = "https://api.hypixel.net/v2/skyblock/bazaar"
        self.crops = {
            "Wheat": ["WHEAT", "ENCHANTED_WHEAT", "ENCHANTED_HAY_BALE"],
            "Carrot": ["CARROT_ITEM", "ENCHANTED_CARROT", "ENCHANTED_GOLDEN_CARROT"],
            "Potato": ["POTATO_ITEM", "ENCHANTED_POTATO", "ENCHANTED_BAKED_POTATO"],
            "Sugar Cane": ["SUGAR_CANE", "ENCHANTED_SUGAR", "ENCHANTED_SUGAR_CANE"],
            "Pumpkin": ["PUMPKIN", "POLISHED_PUMPKIN"],
            "Melon": ["MELON", "ENCHANTED_MELON", "ENCHANTED_MELON_BLOCK"],
            "Cactus": ["CACTUS", "ENCHANTED_CACTUS", "ENCHANTED_CACTUS_GREEN"],
            "Cocoa": ["COCOA", "ENCHANTED_COCOA"],
            "Nether Wart": ["NETHER_STALK", "ENCHANTED_NETHER_STALK"],
            "Mushroom": ["BROWN_MUSHROOM", "RED_MUSHROOM", "ENCHANTED_BROWN_MUSHROOM", "ENCHANTED_RED_MUSHROOM"]
        }

    def build_ui(self):
        return ft.Column([
            ft.Row([
                ft.Text("Farming Analysis", size=24, weight="bold"),
                ft.IconButton(icon="refresh", on_click=self.update_table)
            ], alignment="spaceBetween"),
            ft.Divider(),
            self.results_container
        ], expand=True)

    def update_table(self, e=None):
        try:
            r = requests.get(self.api_url, timeout=5)
            if r.status_code == 200:
                data = r.json().get("products", {})
                cards = []
                for crop_name, variants in self.crops.items():
                    rows = [
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(v.replace("_", " ").title())),
                            ft.DataCell(ft.Text(f"{data[v]['quick_status']['sellPrice']:,.1f}")),
                        ])
                        for v in variants if v in data
                    ]
                    cards.append(ft.Card(content=ft.Container(padding=10, content=ft.Column([
                        ft.Text(crop_name, weight="bold", size=16),
                        ft.DataTable(columns=[ft.DataColumn(ft.Text("Item")), ft.DataColumn(ft.Text("Sell Price"), numeric=True)], rows=rows)
                    ]))))
                self.results_container.controls = cards
                if e: e.page.update()
        except Exception as ex:
            print(f"Farming error: {ex}")


if __name__ == "__main__":
    """
    CLI-запуск модуля Farming.
    Формирует markdown-отчёт в формате, похожем на greenhouse_mutations.md:
    для каждой культуры и её тиров показывает цену продажи, цену покупки,
    профит и ROI.
    """
    import pathlib
    from datetime import datetime

    mod = FarmingModule()

    try:
        resp = requests.get(mod.api_url, timeout=5)
        resp.raise_for_status()
        data = resp.json().get("products", {})

        project_root = pathlib.Path(__file__).resolve().parents[1]
        out_path = project_root / "farming_report.md"

        lines = []
        lines.append("# Farming profitability report")
        lines.append(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_")
        lines.append("")
        lines.append("| Name | Crop | Tier | Sell | Buy | Profit | ROI |")
        lines.append("|------|------|------|------|-----|--------|-----|")

        tier_labels = ["T1", "T2", "T3", "T4"]

        for crop_name, variants in mod.crops.items():
            for idx, v in enumerate(variants):
                if v not in data:
                    continue
                qs = data[v]["quick_status"]
                sell = qs.get("sellPrice", 0.0)
                buy = qs.get("buyPrice", 0.0)
                cost = buy
                profit = sell - cost
                roi = (profit / cost * 100) if cost > 0 else 0.0
                pretty_name = v.replace("_", " ").title()
                tier = tier_labels[idx] if idx < len(tier_labels) else f"T{idx+1}"
                lines.append(
                    f"| {pretty_name} | {crop_name} | {tier} | "
                    f"{sell:.1f} | {cost:.1f} | {profit:.1f} | {roi:.1f}% |"
                )

        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Markdown report written to: {out_path}")

    except Exception as ex:
        print(f"[farming CLI] error: {ex}")
