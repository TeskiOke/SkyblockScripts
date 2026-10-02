import flet as ft
import requests
from .base_module import SkyblockModule

class MiningModule(SkyblockModule):
    def __init__(self):
        self.results_container = ft.Column(scroll="auto", expand=True)
        super().__init__("Mining", "landscape")
        self.api_url = "https://api.hypixel.net/v2/skyblock/bazaar"
        self.minerals = {
            "Flawless Gems": ["FLAWLESS_RUBY_GEM", "FLAWLESS_AMETHYST_GEM", "FLAWLESS_SAPPHIRE_GEM", "FLAWLESS_JADE_GEM", "FLAWLESS_AMBER_GEM", "FLAWLESS_TOPAZ_GEM"],
            "Rough Gems": ["ROUGH_RUBY_GEM", "ROUGH_AMETHYST_GEM", "ROUGH_SAPPHIRE_GEM", "ROUGH_JADE_GEM", "ROUGH_AMBER_GEM", "ROUGH_TOPAZ_GEM"],
            "Ores": ["ENCHANTED_COAL", "ENCHANTED_IRON", "ENCHANTED_GOLD", "ENCHANTED_DIAMOND", "ENCHANTED_EMERALD", "ENCHANTED_QUARTZ"]
        }

    def build_ui(self):
        return ft.Column([
            ft.Row([
                ft.Text("Mining Profitability", size=24, weight="bold"),
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
                for group_name, items in self.minerals.items():
                    rows = [
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(item_id.replace("_", " ").title())),
                            ft.DataCell(ft.Text(f"{data[item_id]['quick_status']['sellPrice']:,.1f}")),
                        ])
                        for item_id in items if item_id in data
                    ]
                    cards.append(ft.Card(content=ft.Container(padding=10, content=ft.Column([
                        ft.Text(group_name, weight="bold", size=16),
                        ft.DataTable(columns=[ft.DataColumn(ft.Text("Item")), ft.DataColumn(ft.Text("Sell Price"), numeric=True)], rows=rows)
                    ]))))
                self.results_container.controls = cards
                if e: e.page.update()
        except Exception as ex:
            print(f"Mining error: {ex}")


if __name__ == "__main__":
    """
    CLI-запуск модуля Mining.
    Формирует markdown-отчёт, похожий на greenhouse_mutations.md:
    для каждой руды/гема показывает цену продажи, цену покупки,
    профит и ROI.
    """
    import pathlib
    from datetime import datetime

    mod = MiningModule()

    try:
        resp = requests.get(mod.api_url, timeout=5)
        resp.raise_for_status()
        data = resp.json().get("products", {})

        project_root = pathlib.Path(__file__).resolve().parents[1]
        out_path = project_root / "mining_report.md"

        lines = []
        lines.append("# Mining profitability report")
        lines.append(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_")
        lines.append("")
        lines.append("| Name | Group | Tier | Sell | Buy | Profit | ROI |")
        lines.append("|------|-------|------|------|-----|--------|-----|")

        # Простые теги тиров по порядку внутри группы
        tier_labels = ["T1", "T2", "T3", "T4", "T5"]

        for group_name, items in mod.minerals.items():
            for idx, item_id in enumerate(items):
                if item_id not in data:
                    continue
                qs = data[item_id]["quick_status"]
                sell = qs.get("sellPrice", 0.0)
                buy = qs.get("buyPrice", 0.0)
                cost = buy
                profit = sell - cost
                roi = (profit / cost * 100) if cost > 0 else 0.0
                pretty_name = item_id.replace("_", " ").title()
                tier = tier_labels[idx] if idx < len(tier_labels) else f"T{idx+1}"
                lines.append(
                    f"| {pretty_name} | {group_name} | {tier} | "
                    f"{sell:.1f} | {cost:.1f} | {profit:.1f} | {roi:.1f}% |"
                )

        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Markdown report written to: {out_path}")

    except Exception as ex:
        print(f"[mining CLI] error: {ex}")
