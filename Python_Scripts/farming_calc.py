import requests
import json
import os
from datetime import datetime

# Enable ANSI colors for Windows CMD
os.system("")

BAZAAR_API = "https://api.hypixel.net/v2/skyblock/bazaar"

# Tiers to Rarities and Colors (Russian)
# Order: Редкий (T3) = 1, Необычный (T2) = 2, Обычный (T1) = 3
TIER_MAP = {
    "T3": {"name": "Редкий", "color": "\033[94m", "order": 1},       # Blue
    "T2": {"name": "Необычный", "color": "\033[92m", "order": 2},     # Green
    "T1": {"name": "Обычный", "color": "\033[97m", "order": 3},      # White
    "Pest": {"name": "Вредитель", "color": "\033[95m", "order": 4},   # Purple
}
RESET = "\033[0m"

# CROPS: Base ID -> Enchanted ID -> Higher Tier ID
# Mapping: (Refine Ratio T1->T2, Refine Ratio T2->T3)
CROPS = {
    "Пшеница": {"base": "WHEAT", "e": "ENCHANTED_WHEAT", "b": "ENCHANTED_HAY_BALE", "r1": 160, "r2": 144},
    "Семена пшеницы": {"base": "SEEDS", "e": "ENCHANTED_SEEDS", "b": "BOX_OF_SEEDS", "r1": 160, "r2": 160},
    "Морковь": {"base": "CARROT_ITEM", "e": "ENCHANTED_CARROT", "b": "ENCHANTED_GOLDEN_CARROT", "r1": 160, "r2": 128}, 
    "Картофель": {"base": "POTATO_ITEM", "e": "ENCHANTED_POTATO", "b": "ENCHANTED_BAKED_POTATO", "r1": 160, "r2": 160},
    "Тыква": {"base": "PUMPKIN", "e": "ENCHANTED_PUMPKIN", "b": "POLISHED_PUMPKIN", "r1": 160, "r2": 160},
    "Арбуз": {"base": "MELON", "e": "ENCHANTED_MELON", "b": "ENCHANTED_MELON_BLOCK", "r1": 160, "r2": 160},
    "Грибы (Крас)": {"base": "RED_MUSHROOM", "e": "ENCHANTED_RED_MUSHROOM", "b": "ENCHANTED_HUGE_MUSHROOM_2", "r1": 160, "r2": 160},
    "Грибы (Кор)": {"base": "BROWN_MUSHROOM", "e": "ENCHANTED_BROWN_MUSHROOM", "b": "ENCHANTED_HUGE_MUSHROOM_1", "r1": 160, "r2": 160},
    "Какао-бобы": {"base": "INK_SACK:3", "e": "ENCHANTED_COCOA", "b": "None", "r1": 160, "r2": 0},
    "Кактус": {"base": "CACTUS", "e": "ENCHANTED_CACTUS_GREEN", "b": "ENCHANTED_CACTUS", "r1": 160, "r2": 160},
    "Тростник": {"base": "SUGAR_CANE", "e": "ENCHANTED_SUGAR", "b": "ENCHANTED_SUGAR_CANE", "r1": 160, "r2": 160},
    "Нарост": {"base": "NETHER_STALK", "e": "ENCHANTED_NETHER_STALK", "b": "MUTANT_NETHER_STALK", "r1": 160, "r2": 160},
}

# PEST DROPS & Garden items (All drops, chips, etc.)
PEST_ITEMS = [
    # Chips (Upgrades)
    "OVERDRIVE_GARDEN_CHIP", "SYNTHESIS_GARDEN_CHIP", "VERMIN_VAPORIZER_GARDEN_CHIP", 
    "SOWLEDGE_GARDEN_CHIP", "HYPERCHARGE_GARDEN_CHIP", "CROPSHOT_GARDEN_CHIP", 
    "MECHAMIND_GARDEN_CHIP", "EVERGREEN_GARDEN_CHIP", "RAREFINDER_GARDEN_CHIP", "QUICKDRAW_GARDEN_CHIP",
    # Lumens & Pest special
    "SLUG_JELLY", "CRICKET_LUMEN", "MOTH_LUMEN", "BEETLE_LUMEN", "FLY_LUMEN", "LOCUST_LUMEN", 
    "WORM_LUMEN", "MITE_LUMEN", "MOSQUITO_LUMEN", "RAT_LUMEN",
    "ENCHANTMENT_PESTERMINATOR_1", "ENCHANTMENT_PESTERMINATOR_2", "ENCHANTMENT_PESTERMINATOR_3", 
    "ENCHANTMENT_PESTERMINATOR_4", "ENCHANTMENT_PESTERMINATOR_5",
    "FLY_SWATTER", "PUMPKIN_BOMB", "SHARD_PEST", "MITE_GEL", "MIXED_MITE_GEL", "WORM_MEMBRANE", "JELLY", "POLLEN",
    # Garden Misc
    "ENCHANTED_COMPOST", "COMPOST", "OVERCLOCKER_3000", "ORGANIC_MATTER"
]

def fetch_bazaar_data():
    try:
        response = requests.get(BAZAAR_API, timeout=10)
        return response.json().get("products", {})
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return {}

def get_price(data, item_id, mode="sell"):
    if not item_id or item_id == "None": return 0
    product = data.get(item_id, {})
    if not product: return 0

    if mode == "buy":
        # Buy Instantly = buy_summary[0] (lowest ask — what you PAY to buy now)
        summary = product.get("buy_summary", [])
        return summary[0].get("pricePerUnit", 0) if summary else 0
    else:
        # Sell Instantly = sell_summary[0] (highest bid — what you GET when selling now)
        summary = product.get("sell_summary", [])
        return summary[0].get("pricePerUnit", 0) if summary else 0

def calculate_farming_profits():
    data = fetch_bazaar_data()
    if not data: return

    crop_results = []
    pest_results = []

    # Secondary costs
    p_ench_gold = get_price(data, "ENCHANTED_GOLD", "buy")

    # 1. CROPS (T1 -> T3)
    for name, ids in CROPS.items():
        # Base price (Common) - Sell Offer
        p_base = get_price(data, ids["base"], "sell")
        if p_base > 0:
            crop_results.append({
                "name": f"Сырой {name}",
                "tier_id": "T1",
                "sell_price": p_base,
                "cost": 0,
                "profit": 0,
                "margin": 0
            })

        # Enchanted (Uncommon)
        p_base_buy = get_price(data, ids["base"], "buy")
        p_e = get_price(data, ids["e"], "sell")
        if p_base_buy > 0 and p_e > 0:
            cost = p_base_buy * ids["r1"]
            profit = p_e - cost
            margin = (profit / cost) * 100 if cost > 0 else 0
            crop_results.append({
                "name": f"Энч {name}",
                "tier_id": "T2",
                "sell_price": p_e,
                "cost": cost,
                "profit": profit,
                "margin": margin
            })

        # Higher Tier (Rare) — стоимость крафта из Enchanted предметов (купленных на базаре)
        if ids["b"] != "None":
            p_e_buy = get_price(data, ids["e"], "buy")   # Buy Instantly цена Enchanted
            p_b = get_price(data, ids["b"], "sell")       # Sell Instantly цена результата
            if p_e_buy > 0 and p_b > 0:
                cost = p_e_buy * ids["r2"]   # сколько стоит купить r2 штук Enchanted
                profit = p_b - cost
                margin = (profit / cost) * 100 if cost > 0 else 0
                crop_results.append({
                    "name": f"Высш. {name}",
                    "tier_id": "T3",
                    "sell_price": p_b,
                    "cost": cost,
                    "profit": profit,
                    "margin": margin
                })

    # 2. PEST ITEMS
    for item in PEST_ITEMS:
        p = get_price(data, item, "sell")
        if p > 0:
            pest_results.append({
                "name": item.replace("_", " ").title(),
                "tier_id": "Pest",
                "sell_price": p
            })

    def print_table(title, results):
        if not results: return
        print(f"\n--- {title} ---")
        print(f"{'Предмет':<25} | {'Редкость':<12} | {'Цена прод.':<12} | {'Себестоимость':<12} | {'Профит':<10} | {'Маржа'}")
        print("-" * 98)
        
        # Sort by Rarity Order (T3=1, T2=2, T1=3), then by Profit
        results.sort(key=lambda x: (TIER_MAP.get(x['tier_id'], {}).get('order', 9), -x['profit']))
        
        for r in results:
            tinfo = TIER_MAP.get(r['tier_id'], {"name": "???", "color": ""})
            rarity_str = f"{tinfo['color']}{tinfo['name']:<12}{RESET}"
            
            p_val = r.get('profit', 0)
            p_str = f"{abs(p_val):,.0f}" if p_val != 0 else "---"
            c_str = f"{r.get('cost', 0):,.0f}" if r.get('cost', 0) != 0 else "---"
            m_str = f"{r.get('margin', 0):.1f}%" if r.get('margin', 0) != 0 else "---"
            
            prefix = ""
            if p_val > 0: prefix = "+"
            elif p_val < 0: prefix = "-"
            
            print(f"{r['name']:<25} | {rarity_str} | {r['sell_price']:>12,.0f} | {c_str:>12} | {prefix}{p_str:>10} | {m_str}")

    def print_pest_table(title, results):
        if not results: return
        print(f"\n--- {title} ---")
        print(f"{'Предмет':<30} | {'Редкость':<12} | {'Цена прод.':<15}")
        print("-" * 65)
        results.sort(key=lambda x: x['sell_price'], reverse=True)
        for r in results:
            tinfo = TIER_MAP.get(r['tier_id'], {"name": "Вредитель", "color": "\033[95m"})
            rarity_str = f"{tinfo['color']}{tinfo['name']:<12}{RESET}"
            print(f"{r['name']:<30} | {rarity_str} | {r['sell_price']:>15,.0f}")

    # CLI Output
    print(f"\n[ ОТЧЕТ ПО ФАРМИНГУ - {datetime.now().strftime('%H:%M:%S')} ]")
    print("(Цены: Покупка ингредиентов = Buy Instantly, Продажа результата = Sell Instantly)")
    print_table("КУЛЬТУРЫ (Сортировка по тирам: Синий -> Зеленый -> Белый)", crop_results)
    print_pest_table("ПРЕДМЕТЫ С ВРЕДИТЕЛЕЙ И GARDEN (Сортировка по цене)", pest_results)

    # Save to Markdown
    with open("farming_report.md", "w", encoding="utf-8") as f:
        f.write(f"# Отчет по прибыли в фарминге\n_Создано: {datetime.now().isoformat()}_\n\n")
        f.write("*(Цены: Покупка ингредиентов = Buy Order, Продажа результата = Sell Offer)*\n\n")

        f.write("## Культуры\n")
        f.write("| Предмет | Редкость | Цена прод. | Себест. | Профит | Маржа |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        crop_results.sort(key=lambda x: (TIER_MAP.get(x['tier_id'], {}).get('order', 9), -x['profit']))
        for r in crop_results:
            rname = TIER_MAP.get(r['tier_id'], {}).get('name', '???')
            f.write(f"| {r['name']} | {rname} | {r['sell_price']:,.0f} | {r.get('cost',0):,.0f} | {r.get('profit',0):,.0f} | {r.get('margin',0):.1f}% |\n")
        
        f.write("\n## Предметы с вредителей и Garden\n")
        f.write("| Предмет | Редкость | Цена прод. |\n")
        f.write("| :--- | :--- | :--- |\n")
        pest_results.sort(key=lambda x: x['sell_price'], reverse=True)
        for r in pest_results:
            rname = TIER_MAP.get(r['tier_id'], {}).get('name', 'Вредитель')
            f.write(f"| {r['name']} | {rname} | {r['sell_price']:,.0f} |\n")
            
    print(f"\n✅ Отчет финально обновлен в farming_report.md")

if __name__ == "__main__":
    calculate_farming_profits()
