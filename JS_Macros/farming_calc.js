/*
 * Farming Calculator (Chat-optimized Version)
 * Переписано для красивого отображения в игровом чате с сокращениями k / M.
 */

const BAZAAR_API = "https://api.hypixel.net/v2/skyblock/bazaar";

const TIER_MAP = {
    "T3": {name: "Редкий", color: "§9", order: 1},       
    "T2": {name: "Необычный", color: "§a", order: 2},     
    "T1": {name: "Обычный", color: "§f", order: 3},      
    "Pest": {name: "Вредитель", color: "§d", order: 4}   
};

const CROPS = {
    "Пшеница": {base: "WHEAT", e: "ENCHANTED_WHEAT", b: "ENCHANTED_HAY_BALE", r1: 160, r2: 144},
    "Семена пш.": {base: "SEEDS", e: "ENCHANTED_SEEDS", b: "BOX_OF_SEEDS", r1: 160, r2: 160},
    "Морковь": {base: "CARROT_ITEM", e: "ENCHANTED_CARROT", b: "ENCHANTED_GOLDEN_CARROT", r1: 160, r2: 128}, 
    "Картофель": {base: "POTATO_ITEM", e: "ENCHANTED_POTATO", b: "ENCHANTED_BAKED_POTATO", r1: 160, r2: 160},
    "Тыква": {base: "PUMPKIN", e: "ENCHANTED_PUMPKIN", b: "POLISHED_PUMPKIN", r1: 160, r2: 160},
    "Арбуз": {base: "MELON", e: "ENCHANTED_MELON", b: "ENCHANTED_MELON_BLOCK", r1: 160, r2: 160},
    "Гриб(Крас)": {base: "RED_MUSHROOM", e: "ENCHANTED_RED_MUSHROOM", b: "ENCHANTED_HUGE_MUSHROOM_2", r1: 160, r2: 160},
    "Гриб(Кор)": {base: "BROWN_MUSHROOM", e: "ENCHANTED_BROWN_MUSHROOM", b: "ENCHANTED_HUGE_MUSHROOM_1", r1: 160, r2: 160},
    "Какао": {base: "INK_SACK:3", e: "ENCHANTED_COCOA", b: "None", r1: 160, r2: 0},
    "Кактус": {base: "CACTUS", e: "ENCHANTED_CACTUS_GREEN", b: "ENCHANTED_CACTUS", r1: 160, r2: 160},
    "Тростник": {base: "SUGAR_CANE", e: "ENCHANTED_SUGAR", b: "ENCHANTED_SUGAR_CANE", r1: 160, r2: 160},
    "Нарост": {base: "NETHER_STALK", e: "ENCHANTED_NETHER_STALK", b: "MUTANT_NETHER_STALK", r1: 160, r2: 160}
};

const PEST_ITEMS = [
    "OVERDRIVE_GARDEN_CHIP", "SYNTHESIS_GARDEN_CHIP", "VERMIN_VAPORIZER_GARDEN_CHIP", 
    "SOWLEDGE_GARDEN_CHIP", "HYPERCHARGE_GARDEN_CHIP", "CROPSHOT_GARDEN_CHIP", 
    "MECHAMIND_GARDEN_CHIP", "EVERGREEN_GARDEN_CHIP", "RAREFINDER_GARDEN_CHIP", "QUICKDRAW_GARDEN_CHIP",
    "SLUG_JELLY", "CRICKET_LUMEN", "MOTH_LUMEN", "BEETLE_LUMEN", "FLY_LUMEN", "LOCUST_LUMEN", 
    "WORM_LUMEN", "MITE_LUMEN", "MOSQUITO_LUMEN", "RAT_LUMEN",
    "ENCHANTMENT_PESTERMINATOR_1", "ENCHANTMENT_PESTERMINATOR_2", "ENCHANTMENT_PESTERMINATOR_3", 
    "ENCHANTMENT_PESTERMINATOR_4", "ENCHANTMENT_PESTERMINATOR_5",
    "FLY_SWATTER", "PUMPKIN_BOMB", "SHARD_PEST", "MITE_GEL", "MIXED_MITE_GEL", "WORM_MEMBRANE", "JELLY", "POLLEN",
    "ENCHANTED_COMPOST", "COMPOST", "OVERCLOCKER_3000", "ORGANIC_MATTER"
];

function getPrice(products, itemId, mode) {
    if (!itemId || itemId === "None") return 0;
    let product = products[itemId];
    if (!product) return 0;

    let summary = mode === "buy" ? product.buy_summary : product.sell_summary;
    return (summary && summary.length > 0) ? summary[0].pricePerUnit : 0;
}

// Форматер для сокращения нулей (k / M)
function formatShort(num) {
    if (num === 0) return "---";
    let sign = num < 0 ? "-" : "";
    let val = Math.abs(num);
    if (val >= 1000000) {
        return sign + (val / 1000000).toFixed(1) + "M";
    } else if (val >= 1000) {
        return sign + (val / 1000).toFixed(1) + "k";
    } else {
        return sign + Math.floor(val).toString();
    }
}

function run() {
    let dateObj = new Date();
    Chat.log("§e[FarmingCalc] §fЦены обновляются... (" + dateObj.getHours() + ":" + String(dateObj.getMinutes()).padStart(2, "0") + ")");
    
    let rawData = "";
    try {
        let URL = Java.type("java.net.URL");
        let Scanner = Java.type("java.util.Scanner");
        let conn = new URL(BAZAAR_API).openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        let scanner = new Scanner(conn.getInputStream());
        rawData = scanner.useDelimiter("\\A").next();
        scanner.close();
    } catch(e) {
        Chat.log("§c[FarmingCalc] Ошибка API: " + e);
        return;
    }
    
    let data;
    try {
        data = JSON.parse(rawData);
    } catch(e) {
        Chat.log("§c[FarmingCalc] Ошибка разбора JSON.");
        return;
    }
    
    let products = data.products;
    if (!products) return;

    let cropResults = [];
    let pestResults = [];
    
    // --- 1. CROPS ---
    for (let cropName in CROPS) {
        let ids = CROPS[cropName];
        
        // Сырой T1
        let pBaseSell = getPrice(products, ids.base, "sell");
        if (pBaseSell > 0) {
            cropResults.push({ name: cropName, tierId: "T1", sell: pBaseSell, cost: 0, profit: 0, margin: 0 });
        }
        
        // Энч T2
        let pBaseBuy = getPrice(products, ids.base, "buy");
        let pESell = getPrice(products, ids.e, "sell");
        if (pBaseBuy > 0 && pESell > 0) {
            let cost = pBaseBuy * ids.r1;
            let profit = pESell - cost;
            let margin = cost > 0 ? (profit / cost) * 100 : 0;
            cropResults.push({ name: "Энч. " + cropName, tierId: "T2", sell: pESell, cost: cost, profit: profit, margin: margin });
        }
        
        // Высш T3
        if (ids.b !== "None") {
            let pEBuy = getPrice(products, ids.e, "buy");
            let pBSell = getPrice(products, ids.b, "sell");
            if (pEBuy > 0 && pBSell > 0) {
                let cost = pEBuy * ids.r2;
                let profit = pBSell - cost;
                let margin = cost > 0 ? (profit / cost) * 100 : 0;
                cropResults.push({ name: "Высш. " + cropName, tierId: "T3", sell: pBSell, cost: cost, profit: profit, margin: margin });
            }
        }
    }
    
    // --- 2. PEST ITEMS ---
    for (let i = 0; i < PEST_ITEMS.length; i++) {
        let item = PEST_ITEMS[i];
        let p = getPrice(products, item, "sell");
        if (p > 0) {
            // Чуть укорачиваем длинные названия
            let niceName = item.replace(/_GARDEN_CHIP/g, " Chip").replace(/_LUMEN/g, " Lumen");
            niceName = niceName.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
            pestResults.push({ name: niceName, tierId: "Pest", sell: p });
        }
    }
    
    // --- СОРТИРОВКА ---
    cropResults.sort((a, b) => {
        let oA = TIER_MAP[a.tierId].order;
        let oB = TIER_MAP[b.tierId].order;
        if (oA !== oB) return oA - oB;
        return b.profit - a.profit;
    });
    
    pestResults.sort((a, b) => b.sell - a.sell);

    // --- ВЫВОД В ЧАТ (ОПТИМИЗИРОВАННЫЙ ПОД ИГРУ) ---
    Chat.log(" ");
    Chat.log("§2=== КУЛЬТУРЫ ===");
    
    for (let i = 0; i < cropResults.length; i++) {
        let r = cropResults[i];
        let color = TIER_MAP[r.tierId].color;
        
        let sellStr = formatShort(r.sell);
        let costStr = formatShort(r.cost);
        let profStr = formatShort(r.profit);
        if (r.profit > 0) profStr = "+" + profStr;
        
        let pColor = r.profit > 0 ? "§a" : (r.profit < 0 ? "§c" : "§7");
        let mStr = r.margin !== 0 ? r.margin.toFixed(0) + "%" : "-";
        
        // ФОРМАТ: [ЦВЕТ]Предмет | Прод: 15.5k | Себ: 10.2k | Профит: +5.3k (50%)
        Chat.log(color + r.name + " §8| §fПрод: §e" + sellStr + " §8| §fСеб: §c" + costStr + " §8| §fПрофит: " + pColor + profStr + " §7(" + mStr + ")");
    }
    
    Chat.log(" ");
    Chat.log("§d=== ВРЕДИТЕЛИ И САД ===");
    
    for (let i = 0; i < pestResults.length; i++) {
        let r = pestResults[i];
        let color = TIER_MAP[r.tierId].color;
        let sellStr = formatShort(r.sell);
        
        // ФОРМАТ: [ЦВЕТ]Предмет | Цена: 1.5M
        Chat.log(color + r.name + " §8| §fЦена: §e" + sellStr);
    }
    
    Chat.log(" ");
}

run();
