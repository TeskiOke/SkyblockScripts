/*
 * Mutation Calculator (Chat-optimized Version for JsMacros)
 */
const BAZAAR_API = "https://api.hypixel.net/v2/skyblock/bazaar";

const ITEMS = {
    // T1 - COMMON
    "ASHWREATH": "Ashwreath (T1 Common)",
    "CHOCONUT": "Choconut (T1 Common)",
    "DUSTGRAIN": "Dustgrain (T1 Common)",
    "GLOOMGOURD": "Gloomgourd (T1 Common)",
    "LONELILY": "Lonelily (T1 Common)",
    "SCOURROOT": "Scourroot (T1 Common)",
    "SHADEVINE": "Shadevine (T1 Common)",
    "VEILSHROOM": "Veilshroom (T1 Common)",
    "WITHERBLOOM": "Witherbloom (T1 Common)",
    // T2 - UNCOMMON
    "CHOCOBERRY": "Chocoberry (T2 Uncommon)",
    "CINDERSHADE": "Cindershade (T2 Uncommon)",
    "COALROOT": "Coalroot (T2 Uncommon)",
    "CREAMBLOOM": "Creambloom (T2 Uncommon)",
    "DUSKBLOOM": "Duskbloom (T2 Uncommon)",
    "THORNSHADE": "Thornshade (T2 Uncommon)",
    // T3 - RARE
    "BLASTBERRY": "Blastberry (T3 Rare)",
    "CHEESEBITE": "Cheesebite (T3 Rare)",
    "CHLORONITE": "Chloronite (T3 Rare)",
    "DO_NOT_EAT_SHROOM": "Do-not-eat-shroom (T3 Rare)",
    "FLESHTRAP": "Fleshtrap (T3 Rare)",
    "MAGIC_JELLYBEAN": "Magic Jellybean (T3 Rare)",
    "NOCTILUME": "Noctilume (T3 Rare)",
    "SNOOZLING": "Snoozling (T3 Rare)",
    "SOGGYBUD": "Soggybud (T3 Rare)",
    // T4 - EPIC
    "CHORUS_FRUIT": "Chorus Fruit (T4 Epic)",
    "PLANTBOY_ADVANCE": "PlantBoy Advance (T4 Epic)",
    "PUFFERCLOUD": "Puffercloud (T4 Epic)",
    "SHELLFRUIT": "Shell Fruit (T4 Epic)",
    "STARTLEVINE": "Startle Vine (T4 Epic)",
    "STOPLIGHT_PETAL": "Stoplight Petal (T4 Epic)",
    "THUNDERLING": "Thunderling (T4 Epic)",
    "TURTLELLINI": "Turtlellini (T4 Epic)",
    "ZOMBUD": "Zombud (T4 Epic)",
    // T5 - LEGENDARY
    "ALL_IN_ALOE": "All-in Aloe (T5 Legendary)",
    "DEVOURER": "Devourer (T5 Legendary)",
    "GLASSCORN": "Glasscorn (T5 Legendary)",
    "GODSEED": "Godseed (T5 Legendary)",
    "JERRYFLOWER": "Jerryflower (T5 Legendary)",
    "PHANTOMLEAF": "Phantomleaf (T5 Legendary)",
    "TIMESTALK": "Timestalk (T5 Legendary)"
};

const RECIPES = {
    // T1
    "DUSTGRAIN": {"WHEAT": 4},
    "WITHERBLOOM": {"DEAD_PLANT": 4},
    "CHOCONUT": {"COCOA": 2},
    "ASHWREATH": {"NETHER_STALK": 2},
    "SCOURROOT": {"POTATO_ITEM": 1, "CARROT_ITEM": 1},
    "SHADEVINE": {"CACTUS": 1, "SUGAR_CANE": 1},
    "VEILSHROOM": {"RED_MUSHROOM": 1, "BROWN_MUSHROOM": 1},
    "GLOOMGOURD": {"PUMPKIN": 2, "MELON": 2},
    "LONELILY": {}, 
    // T2
    "CREAMBLOOM": {"CHOCONUT": 8},
    "DUSKBLOOM": {"SUNFLOWER": 2, "MOONFLOWER": 2, "DUSTGRAIN": 2, "SHADEVINE": 2},
    "THORNSHADE": {"WILD_ROSE": 4, "VEILSHROOM": 4},
    "CHOCOBERRY": {"CHOCONUT": 6, "GLOOMGOURD": 2},
    "CINDERSHADE": {"ASHWREATH": 4, "WITHERBLOOM": 4},
    "COALROOT": {"ASHWREATH": 5, "SCOURROOT": 3},
    "SOGGYBUD": {"MELON": 2, "GLOOMGOURD": 2},
    // T3
    "SNOOZLING": {"CREAMBLOOM": 4, "DUSTGRAIN": 3, "WITHERBLOOM": 3, "DUSKBLOOM": 3, "THORNSHADE": 3},
    "CHEESEBITE": {"CREAMBLOOM": 4, "FERMENTO": 4},
    "DO_NOT_EAT_SHROOM": {"VEILSHROOM": 4, "SCOURROOT": 4},
    "MAGIC_JELLYBEAN": {"SUGAR_CANE": 5, "DUSKBLOOM": 3},
    "NOCTILUME": {"DUSKBLOOM": 6, "LONELILY": 6},
    "THUNDERLING": {"SOGGYBUD": 5, "NOCTILUME": 2},
    "BLASTBERRY": {"CHOCOBERRY": 5, "ASHWREATH": 3},
    "CHLORONITE": {"COALROOT": 6, "THORNSHADE": 2},
    "FLESHTRAP": {"CINDERSHADE": 4, "LONELILY": 4},
    // T4
    "CHORUS_FRUIT": {"CHLORONITE": 5, "MAGIC_JELLYBEAN": 3},
    "PLANTBOY_ADVANCE": {"SNOOZLING": 6, "THUNDERLING": 6},
    "PUFFERCLOUD": {"DO_NOT_EAT_SHROOM": 6, "SNOOZLING": 2},
    "STARTLEVINE": {"BLASTBERRY": 4, "CHEESEBITE": 4},
    "TURTLELLINI": {"SOGGYBUD": 4, "CHOCONUT": 4},
    "STOPLIGHT_PETAL": {"SNOOZLING": 2, "NOCTILUME": 2},
    "ZOMBUD": {"WITHERBLOOM": 4, "CINDERSHADE": 2, "FLESHTRAP": 2},
    // T5
    "ALL_IN_ALOE": {"MAGIC_JELLYBEAN": 6, "PLANTBOY_ADVANCE": 2},
    "TIMESTALK": {"SHELLFRUIT": 2, "CHORUS_FRUIT": 2, "STOPLIGHT_PETAL": 4},
    "GLASSCORN": {"STARTLEVINE": 6, "CHLORONITE": 6},
    "DEVOURER": {"PUFFERCLOUD": 4, "ZOMBUD": 4},
    "PHANTOMLEAF": {"CHORUS_FRUIT": 4, "SHELLFRUIT": 4},
    "GODSEED": {"WHEAT": 1, "SUNFLOWER": 1, "MOONFLOWER": 1, "NETHER_STALK": 1, "CACTUS": 1, "SUGAR_CANE": 1, "COCOA": 1, "MELON": 1, "PUMPKIN": 1, "BROWN_MUSHROOM": 1, "RED_MUSHROOM": 1, "POTATO_ITEM": 1, "CARROT_ITEM": 1, "WILD_ROSE": 1}
};

function formatShort(num) {
    if (num === 0) return "-";
    let sign = num < 0 ? "-" : "";
    let val = Math.abs(num);
    if (val >= 1000000) return sign + (val / 1000000).toFixed(1) + "M";
    if (val >= 1000) return sign + (val / 1000).toFixed(1) + "k";
    return sign + Math.floor(val).toString();
}

function getTierColor(tierStr) {
    if (tierStr.indexOf("T5") !== -1) return "§e"; // Legendary - Yellow
    if (tierStr.indexOf("T4") !== -1) return "§d"; // Epic - Purple
    if (tierStr.indexOf("T3") !== -1) return "§9"; // Rare - Blue
    if (tierStr.indexOf("T2") !== -1) return "§a"; // Uncommon - Green
    return "§f"; // T1 Common - White
}

function run() {
    let dateObj = new Date();
    Chat.log("§e[MutationCalc] §fБД обновляется... (" + dateObj.getHours() + ":" + String(dateObj.getMinutes()).padStart(2, "0") + ")");
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

    let results = [];
    
    for (let itemId in ITEMS) {
        if (!products[itemId]) continue;
        
        let nameFull = ITEMS[itemId];
        let sellPrice = products[itemId].quick_status.sellPrice;
        let recipe = RECIPES[itemId];
        let cost = 0;
        let hasRecipe = typeof recipe !== 'undefined';
        
        if (hasRecipe) {
            for (let ingId in recipe) {
                let amount = recipe[ingId];
                if (products[ingId]) {
                    cost += products[ingId].quick_status.buyPrice * amount;
                } else {
                    cost += 100 * amount; // Заглушка
                }
            }
            
            let profit = sellPrice - cost;
            let margin = cost > 0 ? (profit / cost) * 100 : 0;
            
            let nameSplit = nameFull.split(" (");
            let name = nameSplit[0];
            let tier = nameSplit.length > 1 ? nameSplit[1].replace(")", "") : "T1";
            
            results.push({ name: name, tier: tier, sell: sellPrice, cost: cost, profit: profit, margin: margin });
        }
    }
    
    // Сортировка по чистому профиту
    results.sort((a, b) => b.profit - a.profit);
    
    Chat.log(" ");
    Chat.log("§2=== Greenhouse Mutation Profit ===");
    
    // Чтобы чат не улетал в космос, выведем топ-15 выгодных мутаций, или все, если их мало
    let maxDisplay = Math.min(15, results.length);
    for (let i = 0; i < maxDisplay; i++) {
        let r = results[i];
        let color = getTierColor(r.tier);
        
        let sellStr = formatShort(r.sell);
        let costStr = formatShort(r.cost);
        let profStr = formatShort(r.profit);
        if (r.profit > 0) profStr = "+" + profStr;
        
        let pColor = r.profit > 0 ? "§a" : (r.profit < 0 ? "§c" : "§7");
        let mStr = r.margin !== 0 ? r.margin.toFixed(0) + "%" : "-";
        
        Chat.log(color + r.name + " §8| §fПрод: §e" + sellStr + " §8| §fСеб: §c" + costStr + " §8| §fПрофит: " + pColor + profStr + " §7(" + mStr + ")");
    }
    Chat.log(" ");
}
run();
