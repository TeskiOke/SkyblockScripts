import requests
import json
import os
from datetime import datetime

# Enable ANSI colors for Windows CMD
os.system("")

BAZAAR_API = "https://api.hypixel.net/v2/skyblock/bazaar"

# Tiers to Rarities and Colors (Translated to Russian)
# Order: Легендарный (T5)=1, Эпический (T4)=2, Редкий (T3)=3, Необычный (T2)=4, Обычный (T1)=5
TIER_MAP = {
    "T5": {"name": "Легендарный", "color": "\033[93m", "order": 1},   # Yellow
    "T4": {"name": "Эпический", "color": "\033[95m", "order": 2},     # Purple
    "T3": {"name": "Редкий", "color": "\033[94m", "order": 3},       # Blue
    "T2": {"name": "Необычный", "color": "\033[92m", "order": 4},     # Green
    "T1": {"name": "Обычный", "color": "\033[97m", "order": 5},      # White
    "CH Item": {"name": "Особый", "color": "\033[96m", "order": 6},   # Cyan
}
RESET = "\033[0m"

# GEMS: 80x lower tier -> 1x higher tier
GEM_TYPES = ["RUBY", "AMBER", "SAPPHIRE", "JADE", "AMETHYST", "TOPAZ", "OPAL", "JASPER", "ONYX", "AQUAMARINE", "CITRINE", "PERIDOT"]
GEM_TIERS = ["ROUGH", "FLAWED", "FINE", "FLAWLESS", "PERFECT"]

# ORES: 160x raw -> 1x Enchanted, 160x Enchanted -> 1x Enchanted Block
ORES = {
    "COAL": {"raw": "COAL", "e": "ENCHANTED_COAL", "eb": "ENCHANTED_COAL_BLOCK"},
    "IRON": {"raw": "IRON_INGOT", "e": "ENCHANTED_IRON", "eb": "ENCHANTED_IRON_BLOCK"},
    "GOLD": {"raw": "GOLD_INGOT", "e": "ENCHANTED_GOLD", "eb": "ENCHANTED_GOLD_BLOCK"},
    "DIAMOND": {"raw": "DIAMOND", "e": "ENCHANTED_DIAMOND", "eb": "ENCHANTED_DIAMOND_BLOCK"},
    "EMERALD": {"raw": "EMERALD", "e": "ENCHANTED_EMERALD", "eb": "ENCHANTED_EMERALD_BLOCK"},
    "LAPIS": {"raw": "INK_SACK:4", "e": "ENCHANTED_LAPIS_LAZULI", "eb": "ENCHANTED_LAPIS_LAZULI_BLOCK"},
    "REDSTONE": {"raw": "REDSTONE", "e": "ENCHANTED_REDSTONE", "eb": "ENCHANTED_REDSTONE_BLOCK"},
    "QUARTZ": {"raw": "QUARTZ", "e": "ENCHANTED_QUARTZ", "eb": "ENCHANTED_QUARTZ_BLOCK"},
    "OBSIDIAN": {"raw": "OBSIDIAN", "e": "ENCHANTED_OBSIDIAN", "eb": "None"},
    "GLOWSTONE": {"raw": "GLOWSTONE_DUST", "e": "ENCHANTED_GLOWSTONE_DUST", "eb": "ENCHANTED_GLOWSTONE"},
}

# CRYSTAL HOLLOWS / MISC MINING
CH_ITEMS = [
    "GEMSTONE_MIXTURE", "REFINED_DIAMOND", "REFINED_GOLD", "REFINED_MITHRIL", "REFINED_TITANIUM",
    "MITHRIL_PLATES", "GLACITE_JEWEL", "PYSCHO_JETPACK_CHASSIS", "SYNTHETIC_HEART", "CONTROL_SWITCH",
    "ELECTRON_TRANSMITTER", "FTX_3070", "ROBOTRON_REFLECTOR", "DIVAN_FRAGMENT",
    "CORLEONITE", "JUNGLE_KEY", "UMBER_KEY", "TUNGSTEN_KEY", "SKELETON_KEY", "AMBER_MATERIAL", 
    "PREHISTORIC_EGG", "GOBLIN_EGG", "GOBLIN_EGG_RED", "GOBLIN_EGG_BLUE", "GOBLIN_EGG_GREEN", "GOBLIN_EGG_YELLOW"
]

def fetch_bazaar_data():
    try:
        response = requests.get(BAZAAR_API, timeout=10)
        return response.json().get("products", {})
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return {}

def get_price(data, item_id, mode="any"):
    if not item_id or item_id == "None": return 0
    product = data.get(item_id, {})
    status = product.get("quick_status", {})
    if not status: return 0
    
    # Always use sellPrice (Bid) to show "Liquid Value".
    # This ensures that (Material_Price * Q) correctly compares against Result_Price.
    return status.get("sellPrice", 0)

def calculate_mining_profits():
    data = fetch_bazaar_data()
    if not data: return

    gem_results = []
    ore_results = []
    ch_results = []

    # 1. GEMS (T1 -> T5)
    for gtype in GEM_TYPES:
        for i in range(len(GEM_TIERS) - 1):
            lower = f"{GEM_TIERS[i]}_{gtype}_GEM"
            higher = f"{GEM_TIERS[i+1]}_{gtype}_GEM"
            
            p_lower = get_price(data, lower, "buy")
            p_higher = get_price(data, higher, "sell")
            
            if p_lower > 0 and p_higher > 0:
                cost = p_lower * 80
                profit = p_higher - cost
                margin = (profit / cost) * 100 if cost > 0 else 0
                gem_results.append({
                    "name": f"{GEM_TIERS[i+1]} {gtype}",
                    "tier_id": f"T{i+2}",
                    "sell_price": p_higher,
                    "cost": cost,
                    "profit": profit,
                    "margin": margin
                })

    # 2. ORES (T1 -> T3)
    for ore, ids in ORES.items():
        # raw -> e (T1 -> T2)
        p_raw = get_price(data, ids["raw"], "buy")
        p_e = get_price(data, ids["e"], "sell")
        if p_raw > 0 and p_e > 0:
            cost = p_raw * 160
            profit = p_e - cost
            margin = (profit / cost) * 100 if cost > 0 else 0
            ore_results.append({
                "name": f"Энч {ore}",
                "tier_id": "T2",
                "sell_price": p_e,
                "cost": cost,
                "profit": profit,
                "margin": margin
            })
        
        # e -> eb (T2 -> T3)
        if ids["eb"] != "None":
            p_e_buy = get_price(data, ids["e"], "buy")
            p_eb = get_price(data, ids["eb"], "sell")
            if p_e_buy > 0 and p_eb > 0:
                cost = p_e_buy * 160
                profit = p_eb - cost
                margin = (profit / cost) * 100 if cost > 0 else 0
                ore_results.append({
                    "name": f"Энч блок {ore}",
                    "tier_id": "T3",
                    "sell_price": p_eb,
                    "cost": cost,
                    "profit": profit,
                    "margin": margin
                })
        
        # Raw price (T1)
        p_raw_sell = get_price(data, ids["raw"], "sell")
        if p_raw_sell > 0:
            ore_results.append({
                "name": f"Сырой {ore}",
                "tier_id": "T1",
                "sell_price": p_raw_sell,
                "cost": 0,
                "profit": 0,
                "margin": 0
            })

    # 3. Crystal Hollows Items
    for item in CH_ITEMS:
        p = get_price(data, item, "sell")
        if p > 0:
            ch_results.append({
                "name": item.replace("_", " ").title(),
                "tier_id": "CH Item",
                "sell_price": p,
                "cost": 0,
                "profit": 0,
                "margin": 0
            })

    def print_table(title, results, sort_key="profit"):
        if not results: return
        print(f"\n--- {title} ---")
        print(f"{'Предмет':<20} | {'Редкость':<10} | {'Цена прод.':<12} | {'Стоим. ингр.':<12} | {'Профит':<10} | {'Маржа'}")
        print("-" * 88)
        
        # Sort by Profit (Descending) as preferred by user
        results.sort(key=lambda x: x[sort_key], reverse=True)
        
        for r in results:
            tinfo = TIER_MAP.get(r['tier_id'], {"name": "???", "color": ""})
            rarity_str = f"{tinfo['color']}{tinfo['name']:<10}{RESET}"
            
            profit_val = r['profit']
            profit_str = f"{abs(profit_val):,.0f}" if profit_val != 0 else "---"
            cost_str = f"{r['cost']:,.0f}" if r['cost'] != 0 else "---"
            margin_str = f"{r['margin']:.1f}%" if r['margin'] != 0 else "---"
            
            prefix = ""
            if profit_val > 0: prefix = "+"
            elif profit_val < 0: prefix = "-"
            
            print(f"{r['name']:<20} | {rarity_str} | {r['sell_price']:>12,.0f} | {cost_str:>12} | {prefix}{profit_str:>10} | {margin_str}")

    def print_ch_table(title, results):
        if not results: return
        print(f"\n--- {title} ---")
        print(f"{'Предмет':<25} | {'Редкость':<10} | {'Цена продажи':<15}")
        print("-" * 55)
        results.sort(key=lambda x: x['sell_price'], reverse=True)
        for r in results:
            tinfo = TIER_MAP.get(r['tier_id'], {"name": "Особый", "color": "\033[96m"})
            rarity_str = f"{tinfo['color']}{tinfo['name']:<10}{RESET}"
            print(f"{r['name']:<25} | {rarity_str} | {r['sell_price']:>15,.0f}")

    print(f"\n[ ОТЧЕТ ПО МАЙНИНГУ - {datetime.now().strftime('%H:%M:%S')} ]")
    print("(Все цены: Sell Instantly / Цена продажи на Базаре)")
    print_table("РУДЫ (Сортировка по профиту)", ore_results, "profit")
    print_table("ДРАГОЦЕННЫЕ КАМНИ", gem_results, "profit")
    print_ch_table("CRYSTAL HOLLOWS (Рыночные цены)", ch_results)

    # Save to Markdown
    with open("mining_report.md", "w", encoding="utf-8") as f:
        f.write(f"# Отчет по прибыли в майнинге\n_Создано: {datetime.now().isoformat()}_\n\n")
        f.write("*(Цены: Покупка ингредиентов = Buy Order, Продажа результата = Sell Offer)*\n\n")
        
        for title, res, itype in [("Руды (Сортировка по профиту)", ore_results, "standard"), 
                                  ("Драгоценные камни (Гемстоуны)", gem_results, "standard"), 
                                  ("Crystal Hollows", ch_results, "ch")]:
            f.write(f"## {title}\n")
            if itype == "standard":
                f.write("| Предмет | Редкость | Цена продажи | Цена крафта | Профит | Маржа |\n")
                f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
                # Sort by Profit (Descending)
                res.sort(key=lambda x: x['profit'], reverse=True)
                for r in res:
                    rname = TIER_MAP.get(r['tier_id'], {}).get('name', '???')
                    f.write(f"| {r['name']} | {rname} | {r['sell_price']:,.0f} | {r['cost']:,.0f} | {r['profit']:,.0f} | {r['margin']:.1f}% |\n")
            else:
                f.write("| Предмет | Редкость | Цена продажи |\n")
                f.write("| :--- | :--- | :--- |\n")
                res.sort(key=lambda x: x['sell_price'], reverse=True)
                for r in res:
                    rname = TIER_MAP.get(r['tier_id'], {}).get('name', 'Особый')
                    f.write(f"| {r['name']} | {rname} | {r['sell_price']:,.0f} |\n")
            f.write("\n")
            
    print(f"\n✅ Обновленный отчет сохранен в mining_report.md")

if __name__ == "__main__":
    calculate_mining_profits()
