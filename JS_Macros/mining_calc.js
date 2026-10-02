/*
 * Mining Calculator (Chat-optimized Version for JsMacros)
 */
const BAZAAR_API = "https://api.hypixel.net/v2/skyblock/bazaar";

const TIER_MAP = {
    "T5": {name: "Легендарный", color: "§e"},   
    "T4": {name: "Эпический", color: "§d"},     
    "T3": {name: "Редкий", color: "§9"},       
    "T2": {name: "Необычный", color: "§a"},     
    "T1": {name: "Обычный", color: "§f"},      
    "CH Item": {name: "Особый", color: "§b"}   
};

const GEM_TYPES = ["RUBY", "AMBER", "SAPPHIRE", "JADE", "AMETHYST", "TOPAZ", "OPAL", "JASPER", "ONYX", "AQUAMARINE", "CITRINE", "PERIDOT"];
const GEM_TIERS = ["ROUGH", "FLAWED", "FINE", "FLAWLESS", "PERFECT"];

const ORES = {
    "COAL": {raw: "COAL", e: "ENCHANTED_COAL", eb: "ENCHANTED_COAL_BLOCK"},
    "IRON": {raw: "IRON_INGOT", e: "ENCHANTED_IRON", eb: "ENCHANTED_IRON_BLOCK"},
    "GOLD": {raw: "GOLD_INGOT", e: "ENCHANTED_GOLD", eb: "ENCHANTED_GOLD_BLOCK"},
    "DIAMOND": {raw: "DIAMOND", e: "ENCHANTED_DIAMOND", eb: "ENCHANTED_DIAMOND_BLOCK"},
    "EMERALD": {raw: "EMERALD", e: "ENCHANTED_EMERALD", eb: "ENCHANTED_EMERALD_BLOCK"},
    "LAPIS": {raw: "INK_SACK:4", e: "ENCHANTED_LAPIS_LAZULI", eb: "ENCHANTED_LAPIS_LAZULI_BLOCK"},
    "REDSTONE": {raw: "REDSTONE", e: "ENCHANTED_REDSTONE", eb: "ENCHANTED_REDSTONE_BLOCK"},
    "QUARTZ": {raw: "QUARTZ", e: "ENCHANTED_QUARTZ", eb: "ENCHANTED_QUARTZ_BLOCK"},
    "OBSIDIAN": {raw: "OBSIDIAN", e: "ENCHANTED_OBSIDIAN", eb: "None"},
    "GLOWSTONE": {raw: "GLOWSTONE_DUST", e: "ENCHANTED_GLOWSTONE_DUST", eb: "ENCHANTED_GLOWSTONE"}
};

const CH_ITEMS = [
    "GEMSTONE_MIXTURE", "REFINED_DIAMOND", "REFINED_GOLD", "REFINED_MITHRIL", "REFINED_TITANIUM",
    "MITHRIL_PLATES", "GLACITE_JEWEL", "PYSCHO_JETPACK_CHASSIS", "SYNTHETIC_HEART", "CONTROL_SWITCH",
    "ELECTRON_TRANSMITTER", "FTX_3070", "ROBOTRON_REFLECTOR", "DIVAN_FRAGMENT",
    "CORLEONITE", "JUNGLE_KEY", "UMBER_KEY", "TUNGSTEN_KEY", "SKELETON_KEY", "AMBER_MATERIAL", 
    "PREHISTORIC_EGG", "GOBLIN_EGG", "GOBLIN_EGG_RED", "GOBLIN_EGG_BLUE", "GOBLIN_EGG_GREEN", "GOBLIN_EGG_YELLOW"
];

function getPrice(products, itemId, mode) {
    if (!itemId || itemId === "None") return 0;
    let product = products[itemId];
    if (!product) return 0;
    let status = product.quick_status;
    return status ? status.sellPrice : 0;
}

function formatShort(num) {
    if (num === 0) return "-";
    let sign = num < 0 ? "-" : "";
    let val = Math.abs(num);
    if (val >= 1000000) return sign + (val / 1000000).toFixed(1) + "M";
    if (val >= 1000) return sign + (val / 1000).toFixed(1) + "k";
    return sign + Math.floor(val).toString();
}

function run() {
    let dateObj = new Date();
    Chat.log("§e[MiningCalc] §fБД обновляется... (" + dateObj.getHours() + ":" + String(dateObj.getMinutes()).padStart(2, "0") + ")");
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
        Chat.log("§cОшибка API: " + e);
        return;
    }
    
    let data;
    try {
        data = JSON.parse(rawData);
    } catch(e) {
        Chat.log("§cОшибка парсинга JSON.");
        return;
    }
    
    let products = data.products;
    if (!products) return;

    let gemResults = [];
    let oreResults = [];
    let chResults = [];

    // 1. GEMS (T1 -> T5)
    for (let g = 0; g < GEM_TYPES.length; g++) {
        let gtype = GEM_TYPES[g];
        for (let i = 0; i < GEM_TIERS.length - 1; i++) {
            let lower = GEM_TIERS[i] + "_" + gtype + "_GEM";
            let higher = GEM_TIERS[i+1] + "_" + gtype + "_GEM";
            
            let p_lower = getPrice(products, lower, "buy");
            let p_higher = getPrice(products, higher, "sell");
            
            if (p_lower > 0 && p_higher > 0) {
                let cost = p_lower * 80;
                let profit = p_higher - cost;
                let margin = cost > 0 ? (profit / cost) * 100 : 0;
                gemResults.push({
                    name: GEM_TIERS[i+1] + " " + gtype,
                    tierId: "T" + (i+2),
                    sell: p_higher,
                    cost: cost,
                    profit: profit,
                    margin: margin
                });
            }
        }
    }

    // 2. ORES (T1 -> T3)
    for (let ore in ORES) {
        let ids = ORES[ore];
        
        let p_raw = getPrice(products, ids.raw, "buy");
        let p_e = getPrice(products, ids.e, "sell");
        if (p_raw > 0 && p_e > 0) {
            let cost = p_raw * 160;
            let profit = p_e - cost;
            let margin = cost > 0 ? (profit / cost) * 100 : 0;
            oreResults.push({ name: "Энч " + ore, tierId: "T2", sell: p_e, cost: cost, profit: profit, margin: margin });
        }
        
        if (ids.eb !== "None") {
            let p_e_buy = getPrice(products, ids.e, "buy");
            let p_eb = getPrice(products, ids.eb, "sell");
            if (p_e_buy > 0 && p_eb > 0) {
                let cost = p_e_buy * 160;
                let profit = p_eb - cost;
                let margin = cost > 0 ? (profit / cost) * 100 : 0;
                oreResults.push({ name: "Энч блок " + ore, tierId: "T3", sell: p_eb, cost: cost, profit: profit, margin: margin });
            }
        }
    }

    // 3. Crystal Hollows Items
    for (let i = 0; i < CH_ITEMS.length; i++) {
        let item = CH_ITEMS[i];
        let p = getPrice(products, item, "sell");
        if (p > 0) {
            let niceName = item.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
            chResults.push({ name: niceName, tierId: "CH Item", sell: p, cost: 0, profit: 0, margin: 0 });
        }
    }

    function printTable(title, resultsList, limit) {
        if (!resultsList || resultsList.length === 0) return;
        Chat.log(" ");
        Chat.log("§2=== " + title + " ===");
        
        resultsList.sort((a, b) => b.profit - a.profit);
        let maxL = Math.min(limit, resultsList.length);
        
        for (let i = 0; i < maxL; i++) {
            let r = resultsList[i];
            let color = TIER_MAP[r.tierId].color;
            
            let sellStr = formatShort(r.sell);
            let costStr = formatShort(r.cost);
            let profStr = formatShort(r.profit);
            if (r.profit > 0) profStr = "+" + profStr;
            
            let pColor = r.profit > 0 ? "§a" : (r.profit < 0 ? "§c" : "§7");
            let mStr = r.margin !== 0 ? r.margin.toFixed(0) + "%" : "-";
            
            Chat.log(color + r.name + " §8| §fПрод: §e" + sellStr + " §8| §fСеб: §c" + costStr + " §8| §fПрофит: " + pColor + profStr + " §7(" + mStr + ")");
        }
    }

    function printCHTable(title, resultsList, limit) {
        if (!resultsList || resultsList.length === 0) return;
        Chat.log(" ");
        Chat.log("§b=== " + title + " ===");
        
        resultsList.sort((a, b) => b.sell - a.sell);
        let maxL = Math.min(limit, resultsList.length);
        
        for (let i = 0; i < maxL; i++) {
            let r = resultsList[i];
            let color = TIER_MAP[r.tierId].color;
            let sellStr = formatShort(r.sell);
            Chat.log(color + r.name + " §8| §fЦена: §e" + sellStr);
        }
    }

    Chat.log("§e[ ОТЧЕТ ПО МАЙНИНГУ ]");
    printTable("РУДЫ (Топ-10)", oreResults, 10);
    printTable("ДРАГОЦЕННЫЕ КАМНИ (Топ-10)", gemResults, 10);
    printCHTable("CRYSTAL HOLLOWS", chResults, 10);
    Chat.log(" ");
}

run();
