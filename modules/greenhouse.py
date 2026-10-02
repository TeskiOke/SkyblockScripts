import flet as ft
import requests
from .base_module import SkyblockModule

class GreenhouseModule(SkyblockModule):
    def __init__(self):
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Название")),
                ft.DataColumn(ft.Text("Тир")),
                ft.DataColumn(ft.Text("Цена продажи"), numeric=True),
                ft.DataColumn(ft.Text("Себестоимость"), numeric=True),
                ft.DataColumn(ft.Text("Профит"), numeric=True),
                ft.DataColumn(ft.Text("ROI")),
            ],
            rows=[]
        )
        super().__init__("Greenhouse", "nature")
        self.api_url = "https://api.hypixel.net/v2/skyblock/bazaar"
        self.items_config = {
            "DUSTGRAIN": "Dustgrain (T1 Common)", "WITHERBLOOM": "Witherbloom (T1 Common)",
            "CHOCONUT": "Choconut (T1 Common)", "ASHWREATH": "Ashwreath (T1 Common)",
            "SCOURROOT": "Scourroot (T1 Common)", "SHADEVINE": "Shadevine (T1 Common)",
            "VEILSHROOM": "Veilshroom (T1 Common)", "GLOOMGOURD": "Gloomgourd (T1 Common)",
            "LONELILY": "Lonelily (T1 Common)", "CHOCOBERRY": "Chocoberry (T2 Uncommon)",
            "CINDERSHADE": "Cindershade (T2 Uncommon)", "COALROOT": "Coalroot (T2 Uncommon)",
            "CREAMBLOOM": "Creambloom (T2 Uncommon)", "DUSKBLOOM": "Duskbloom (T2 Uncommon)",
            "THORNSHADE": "Thornshade (T2 Uncommon)", "BLASTBERRY": "Blastberry (T3 Rare)",
            "CHEESEBITE": "Cheesebite (T3 Rare)", "CHLORONITE": "Chloronite (T3 Rare)",
            "DO_NOT_EAT_SHROOM": "Do-not-eat-shroom (T3 Rare)", "FLESHTRAP": "Fleshtrap (T3 Rare)",
            "MAGIC_JELLYBEAN": "Magic Jellybean (T3 Rare)", "NOCTILUME": "Noctilume (T3 Rare)",
            "SNOOZLING": "Snoozling (T3 Rare)", "SOGGYBUD": "Soggybud (T3 Rare)",
            "CHORUS_FRUIT": "Chorus Fruit (T4 Epic)", "PLANTBOY_ADVANCE": "PlantBoy Advance (T4 Epic)",
            "PUFFERCLOUD": "Puffercloud (T4 Epic)", "SHELLFRUIT": "Shell Fruit (T4 Epic)",
            "STARTLEVINE": "Startle Vine (T4 Epic)", "STOPLIGHT_PETAL": "Stoplight Petal (T4 Epic)",
            "THUNDERLING": "Thunderling (T4 Epic)", "TURTLELLINI": "Turtlellini (T4 Epic)",
            "ZOMBUD": "Zombud (T4 Epic)", "ALL_IN_ALOE": "All-in Aloe (T5 Legendary)",
            "DEVOURER": "Devourer (T5 Legendary)", "GLASSCORN": "Glasscorn (T5 Legendary)",
            "GODSEED": "Godseed (T5 Legendary)", "PHANTOMLEAF": "Phantomleaf (T5 Legendary)",
            "TIMESTALK": "Timestalk (T5 Legendary)"
        }
        self.recipes = {
            "DUSTGRAIN": {"WHEAT": 4}, "WITHERBLOOM": {"DEAD_PLANT": 4},
            "CHOCONUT": {"COCOA": 2}, "ASHWREATH": {"NETHER_STALK": 2},
            "SCOURROOT": {"POTATO_ITEM": 1, "CARROT_ITEM": 1},
            "SHADEVINE": {"CACTUS": 1, "SUGAR_CANE": 1},
            "VEILSHROOM": {"RED_MUSHROOM": 1, "BROWN_MUSHROOM": 1},
            "GLOOMGOURD": {"PUMPKIN": 2, "MELON": 2}, "LONELILY": {},
            "CREAMBLOOM": {"CHOCONUT": 8},
            "DUSKBLOOM": {"DUSTGRAIN": 2, "SHADEVINE": 2},
            "THORNSHADE": {"WILD_ROSE": 4, "VEILSHROOM": 4},
            "CHOCOBERRY": {"CHOCONUT": 6, "GLOOMGOURD": 2},
            "CINDERSHADE": {"ASHWREATH": 4, "WITHERBLOOM": 4},
            "COALROOT": {"ASHWREATH": 5, "SCOURROOT": 3},
            "SOGGYBUD": {"MELON": 2, "GLOOMGOURD": 2},
            "SNOOZLING": {"CREAMBLOOM": 4, "DUSTGRAIN": 3, "WITHERBLOOM": 3, "DUSKBLOOM": 3, "THORNSHADE": 3},
            "CHEESEBITE": {"CREAMBLOOM": 4},
            "DO_NOT_EAT_SHROOM": {"VEILSHROOM": 4, "SCOURROOT": 4},
            "MAGIC_JELLYBEAN": {"SUGAR_CANE": 5, "DUSKBLOOM": 3},
            "NOCTILUME": {"DUSKBLOOM": 6, "LONELILY": 6},
            "THUNDERLING": {"SOGGYBUD": 5, "NOCTILUME": 2},
            "BLASTBERRY": {"CHOCOBERRY": 5, "ASHWREATH": 3},
            "CHLORONITE": {"COALROOT": 6, "THORNSHADE": 2},
            "FLESHTRAP": {"CINDERSHADE": 4, "LONELILY": 4},
            "CHORUS_FRUIT": {"CHLORONITE": 5, "MAGIC_JELLYBEAN": 3},
            "PLANTBOY_ADVANCE": {"SNOOZLING": 6, "THUNDERLING": 6},
            "PUFFERCLOUD": {"DO_NOT_EAT_SHROOM": 6, "SNOOZLING": 2},
            "STARTLEVINE": {"BLASTBERRY": 4, "CHEESEBITE": 4},
            "TURTLELLINI": {"SOGGYBUD": 4, "CHOCONUT": 4},
            "STOPLIGHT_PETAL": {"SNOOZLING": 2, "NOCTILUME": 2},
            "ZOMBUD": {"WITHERBLOOM": 4, "CINDERSHADE": 2, "FLESHTRAP": 2},
            "ALL_IN_ALOE": {"MAGIC_JELLYBEAN": 6, "PLANTBOY_ADVANCE": 2},
            "TIMESTALK": {"CHORUS_FRUIT": 2, "STOPLIGHT_PETAL": 4},
            "GLASSCORN": {"STARTLEVINE": 6, "CHLORONITE": 6},
            "DEVOURER": {"PUFFERCLOUD": 4, "ZOMBUD": 4},
            "PHANTOMLEAF": {"CHORUS_FRUIT": 4},
            "GODSEED": {"WHEAT": 1, "NETHER_STALK": 1, "CACTUS": 1, "SUGAR_CANE": 1, "COCOA": 1, "MELON": 1, "PUMPKIN": 1, "BROWN_MUSHROOM": 1, "RED_MUSHROOM": 1, "POTATO_ITEM": 1, "CARROT_ITEM": 1}
        }

    def build_ui(self):
        return ft.Column([
            ft.Row([
                ft.Text("Greenhouse Mutation Profit", size=24, weight="bold"),
                ft.IconButton(icon="refresh", on_click=self.update_table)
            ], alignment="spaceBetween"),
            ft.Divider(),
            ft.ListView(controls=[self.table], expand=True)
        ], expand=True)

    def update_table(self, e=None):
        try:
            r = requests.get(self.api_url, timeout=5)
            if r.status_code == 200:
                data = r.json().get("products", {})
                results = []
                for item_id, name in self.items_config.items():
                    if item_id in data and item_id in self.recipes:
                        sell = data[item_id]["quick_status"]["sellPrice"]
                        cost = sum(
                            data[ing]["quick_status"]["buyPrice"] * amt
                            for ing, amt in self.recipes[item_id].items()
                            if ing in data
                        )
                        profit = sell - cost
                        margin = (profit / cost * 100) if cost > 0 else 0
                        tier = name.split("(")[1].replace(")", "") if "(" in name else "-"
                        results.append({"name": name.split(" (")[0], "tier": tier, "sell": sell, "cost": cost, "profit": profit, "margin": margin})
                results.sort(key=lambda x: x["profit"], reverse=True)
                self.table.rows = [
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(r["name"])),
                        ft.DataCell(ft.Text(r["tier"])),
                        ft.DataCell(ft.Text(f"{r['sell']:,.0f}")),
                        ft.DataCell(ft.Text(f"{r['cost']:,.0f}")),
                        ft.DataCell(ft.Text(f"{r['profit']:,.0f}", color="green" if r["profit"] > 0 else "red", weight="bold")),
                        ft.DataCell(ft.Text(f"{r['margin']:.1f}%")),
                    ]) for r in results
                ]
                if e: e.page.update()
        except Exception as ex:
            print(f"Greenhouse error: {ex}")


if __name__ == "__main__":
    """
    CLI-запуск модуля.
    При запуске `python -m modules.greenhouse` или `python modules/greenhouse.py`
    формирует markdown-файл с расчётом мутаций.
    """
    import pathlib
    from datetime import datetime

    mod = GreenhouseModule()

    try:
        resp = requests.get(mod.api_url, timeout=5)
        resp.raise_for_status()
        data = resp.json().get("products", {})

        results = []
        for item_id, name in mod.items_config.items():
            if item_id in data and item_id in mod.recipes:
                sell = data[item_id]["quick_status"]["sellPrice"]
                cost = sum(
                    data[ing]["quick_status"]["buyPrice"] * amt
                    for ing, amt in mod.recipes[item_id].items()
                    if ing in data
                )
                profit = sell - cost
                margin = (profit / cost * 100) if cost > 0 else 0
                tier = name.split("(")[1].replace(")", "") if "(" in name else "-"
                results.append(
                    {
                        "name": name.split(" (")[0],
                        "tier": tier,
                        "sell": sell,
                        "cost": cost,
                        "profit": profit,
                        "margin": margin,
                    }
                )

        results.sort(key=lambda x: x["profit"], reverse=True)

        project_root = pathlib.Path(__file__).resolve().parents[1]
        out_path = project_root / "greenhouse_mutations.md"

        lines = []
        lines.append(f"# Greenhouse mutations report\n")
        lines.append(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_\n")
        lines.append("")
        lines.append("| Name | Tier | Sell | Cost | Profit | ROI |")
        lines.append("|------|------|------|------|--------|-----|")

        for r in results:
            lines.append(
                f"| {r['name']} | {r['tier']} | {r['sell']:.0f} | {r['cost']:.0f} | "
                f"{r['profit']:.0f} | {r['margin']:.1f}% |"
            )

        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Markdown report written to: {out_path}")

    except Exception as ex:
        print(f"[greenhouse CLI] error: {ex}")
