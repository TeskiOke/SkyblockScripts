import requests
from prettytable import PrettyTable
import time

# Список ID предметов на Базаре для мутаций
# Примечание: ID могут отличаться, если Hypixel сменил их в 2026.
ITEMS = {
    # T1 - COMMON
    "ASHWREATH": "Ashwreath (T1 Common)",
    "CHOCONUT": "Choconut (T1 Common)",
    "DUSTGRAIN": "Dustgrain (T1 Common)",
    "GLOOMGOURD": "Gloomgourd (T1 Common)",
    "LONELILY": "Lonelily (T1 Common)",
    "SCOURROOT": "Scourroot (T1 Common)",
    "SHADEVINE": "Shadevine (T1 Common)",
    "VEILSHROOM": "Veilshroom (T1 Common)",
    "WITHERBLOOM": "Witherbloom (T1 Common)",

    # T2 - UNCOMMON
    "CHOCOBERRY": "Chocoberry (T2 Uncommon)",
    "CINDERSHADE": "Cindershade (T2 Uncommon)",
    "COALROOT": "Coalroot (T2 Uncommon)",
    "CREAMBLOOM": "Creambloom (T2 Uncommon)",
    "DUSKBLOOM": "Duskbloom (T2 Uncommon)",
    "THORNSHADE": "Thornshade (T2 Uncommon)",

    # T3 - RARE
    "BLASTBERRY": "Blastberry (T3 Rare)",
    "CHEESEBITE": "Cheesebite (T3 Rare)",
    "CHLORONITE": "Chloronite (T3 Rare)",
    "DO_NOT_EAT_SHROOM": "Do-not-eat-shroom (T3 Rare)",
    "FLESHTRAP": "Fleshtrap (T3 Rare)",
    "MAGIC_JELLYBEAN": "Magic Jellybean (T3 Rare)",
    "NOCTILUME": "Noctilume (T3 Rare)",
    "SNOOZLING": "Snoozling (T3 Rare)",
    "SOGGYBUD": "Soggybud (T3 Rare)",

    # T4 - EPIC
    "CHORUS_FRUIT": "Chorus Fruit (T4 Epic)",
    "PLANTBOY_ADVANCE": "PlantBoy Advance (T4 Epic)",
    "PUFFERCLOUD": "Puffercloud (T4 Epic)",
    "SHELLFRUIT": "Shell Fruit (T4 Epic)",
    "STARTLEVINE": "Startle Vine (T4 Epic)",
    "STOPLIGHT_PETAL": "Stoplight Petal (T4 Epic)",
    "THUNDERLING": "Thunderling (T4 Epic)",
    "TURTLELLINI": "Turtlellini (T4 Epic)",
    "ZOMBUD": "Zombud (T4 Epic)",

    # T5 - LEGENDARY
    "ALL_IN_ALOE": "All-in Aloe (T5 Legendary)",
    "DEVOURER": "Devourer (T5 Legendary)",
    "GLASSCORN": "Glasscorn (T5 Legendary)",
    "GODSEED": "Godseed (T5 Legendary)",
    "JERRYFLOWER": "Jerryflower (T5 Legendary)",
    "PHANTOMLEAF": "Phantomleaf (T5 Legendary)",
    "TIMESTALK": "Timestalk (T5 Legendary)",

    # BASE ITEMS & INGREDIENTS
    "WILD_ROSE": "Wild Rose",
    "SUNFLOWER": "Sunflower",
    "MOONFLOWER": "Moonflower",
    "DEAD_PLANT": "Dead Plant",
    "WHEAT": "Wheat",
    "CARROT_ITEM": "Carrot",
    "POTATO_ITEM": "Potato",
    "PUMPKIN": "Pumpkin",
    "MELON": "Melon",
    "CACTUS": "Cactus",
    "SUGAR_CANE": "Sugar Cane",
    "NETHER_STALK": "Nether Wart",
    "BROWN_MUSHROOM": "Brown Mushroom",
    "RED_MUSHROOM": "Red Mushroom",
    "COCOA": "Cocoa Beans",
    "FERMENTO": "Fermento"
}

# Рецепты (какие ингредиенты нужны для получения 1 единицы мутации)
RECIPES = {
    # T1 - COMMON
    "DUSTGRAIN": {"WHEAT": 4},
    "WITHERBLOOM": {"DEAD_PLANT": 4},
    "CHOCONUT": {"COCOA": 2},
    "ASHWREATH": {"NETHER_STALK": 2}, # + 2 Fire (не на Базаре)
    "SCOURROOT": {"POTATO_ITEM": 1, "CARROT_ITEM": 1},
    "SHADEVINE": {"CACTUS": 1, "SUGAR_CANE": 1},
    "VEILSHROOM": {"RED_MUSHROOM": 1, "BROWN_MUSHROOM": 1},
    "GLOOMGOURD": {"PUMPKIN": 2, "MELON": 2},
    "LONELILY": {}, # Растет в одиночестве, затраты 0
    "ASHWREATH": {"NETHER_STALK": 2},
    
    # T2 - UNCOMMON
    "CREAMBLOOM": {"CHOCONUT": 8},
    "DUSKBLOOM": {"SUNFLOWER": 2, "MOONFLOWER": 2, "DUSTGRAIN": 2, "SHADEVINE": 2},
    "THORNSHADE": {"WILD_ROSE": 4, "VEILSHROOM": 4},
    "CHOCoberry": {"CHOCONUT": 6, "GLOOMGOURD": 2},
    "CINDERSHADE": {"ASHWREATH": 4, "WITHERBLOOM": 4},
    "COALROOT": {"ASHWREATH": 5, "SCOURROOT": 3},
    "SOGGYBUD": {"MELON": 2, "GLOOMGOURD": 2},

    # T3 - RARE
    "SNOOZLING": {
        "CREAMBLOOM": 4,
        "DUSTGRAIN": 3,
        "WITHERBLOOM": 3,
        "DUSKBLOOM": 3,
        "THORNSHADE": 3
    },
    "CHEESEBITE": {"CREAMBLOOM": 4, "FERMENTO": 4},
    "DO_NOT_EAT_SHROOM": {"VEILSHROOM": 4, "SCOURROOT": 4},
    "MAGIC_JELLYBEAN": {"SUGAR_CANE": 5, "DUSKBLOOM": 3},
    "NOCTILUME": {"DUSKBLOOM": 6, "LONELILY": 6},
    "THUNDERLING": {"SOGGYBUD": 5, "NOCTILUME": 2},
    "BLASTBERRY": {"CHOCOBERRY": 5, "ASHWREATH": 3},
    "CHLORONITE": {"COALROOT": 6, "THORNSHADE": 2},
    "FLESHTRAP": {"CINDERSHADE": 4, "LONELILY": 4},

    # T4 - EPIC
    "CHORUS_FRUIT": {"CHLORONITE": 5, "MAGIC_JELLYBEAN": 3},
    "PLANTBOY_ADVANCE": {"SNOOZLING": 6, "THUNDERLING": 6},
    "PUFFERCLOUD": {"DO_NOT_EAT_SHROOM": 6, "SNOOZLING": 2},
    "STARTLEVINE": {"BLASTBERRY": 4, "CHEESEBITE": 4},
    "TURTLELLINI": {"SOGGYBUD": 4, "CHOCONUT": 4},
    "STOPLIGHT_PETAL": {"SNOOZLING": 2, "NOCTILUME": 2},
    "ZOMBUD": {"WITHERBLOOM": 4, "CINDERSHADE": 2, "FLESHTRAP": 2},

    # T5 - LEGENDARY
    "ALL_IN_ALOE": {"MAGIC_JELLYBEAN": 6, "PLANTBOY_ADVANCE": 2},
    "TIMESTALK": {"SHELLFRUIT": 2, "CHORUS_FRUIT": 2, "STOPLIGHT_PETAL": 4},
    "GLASSCORN": {"STARTLEVINE": 6, "CHLORONITE": 6},
    "DEVOURER": {"PUFFERCLOUD": 4, "ZOMBUD": 4},
    "PHANTOMLEAF": {"CHORUS_FRUIT": 4, "SHELLFRUIT": 4},
    "GODSEED": {
        "WHEAT": 1, "SUNFLOWER": 1, "MOONFLOWER": 1, "NETHER_STALK": 1,
        "CACTUS": 1, "SUGAR_CANE": 1, "COCOA": 1, "MELON": 1,
        "PUMPKIN": 1, "BROWN_MUSHROOM": 1, "RED_MUSHROOM": 1, "POTATO_ITEM": 1,
        "CARROT_ITEM": 1, "WILD_ROSE": 1
    }
}

API_URL = "https://api.hypixel.net/v2/skyblock/bazaar"

def get_bazaar_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json().get("products", {})
        else:
            print(f"Ошибка API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка сети: {e}")
        return None

def calculate_profits(data):
    results = []

    for item_id, name in ITEMS.items():
        if item_id not in data:
            continue
            
        sell_price = data[item_id]["quick_status"]["sellPrice"]
        
        # Считаем себестоимость по рецепту
        cost = 0
        has_recipe = item_id in RECIPES
        
        if has_recipe:
            for ing_id, amount in RECIPES[item_id].items():
                if ing_id in data:
                    # Покупаем ингредиенты по цене Insta-Buy
                    cost += data[ing_id]["quick_status"]["buyPrice"] * amount
                else:
                    # Заглушка для предметов вне базара
                    cost += 100 * amount
        
        profit = sell_price - cost
        margin = (profit / cost * 100) if cost > 0 else 0
        
        # Фильтруем вывод: показываем только мутации
        if has_recipe:
            results.append({
                "name": name.split(" (")[0],
                "tier": name.split(" (")[1].replace(")", "") if "(" in name else "-",
                "sell": sell_price,
                "cost": cost,
                "profit": profit,
                "margin": margin
            })

    # Сортировка по чистому профиту (по убыванию)
    results.sort(key=lambda x: x["profit"], reverse=True)

    table = PrettyTable()
    table.field_names = ["Название", "Тир", "Цена продажи", "Себестоимость", "Чистый профит", "Маржа %"]
    table.align = "l"

    for r in results:
        color_start = "\033[92m" if r["profit"] > 0 else "\033[91m"
        color_end = "\033[0m"
        
        table.add_row([
            r["name"], 
            r["tier"],
            f"{r['sell']:,.0f}", 
            f"{r['cost']:,.0f}", 
            f"{color_start}{r['profit']:,.0f}{color_end}", 
            f"{r['margin']:.1f}%"
        ])

    print(table)
    return results

def save_to_markdown(results):
    with open("mutation_report.md", "w", encoding="utf-8") as f:
        f.write("# 🌿 Greenhouse Mutation Profit Report\n\n")
        f.write(f"**Последнее обновление:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Название | Тир | Цена продажи | Себестоимость | Чистый профит | ROI |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        for r in results:
            profit_str = f"**{r['profit']:,.0f}**" if r['profit'] > 0 else f"{r['profit']:,.0f}"
            f.write(f"| {r['name']} | {r['tier']} | {r['sell']:,.0f} | {r['cost']:,.0f} | {profit_str} | {r['margin']:.1f}% |\n")
    
    print("\n✅ Отчет сохранен в mutation_report.md")

if __name__ == "__main__":
    print("--- Greenhouse Mutation Profit Calculator (2026) ---")
    data = get_bazaar_data()
    if data:
        results = calculate_profits(data)
        if results:
            save_to_markdown(results)
    else:
        print("Не удалось получить данные с Базара.")

