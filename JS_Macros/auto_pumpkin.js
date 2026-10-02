/*
 * Smart Auto Pumpkin (Coordinate-Based with Admin Protection)
 * Опирается на координаты Z, использует W для автоматического смещения по X.
 * Конечная координата остановки по X: -96.
 */

const TARGET_YAW = 90;
const TARGET_PITCH = -58.95;
const LOOK_TIME_MS = 2000;

// Базовые границы грядки по Z (длина поля)
const Z_BASE_NORTH = -238.2; 
const Z_BASE_SOUTH = 238.2;  

// Функция для получения случайной погрешности (от -0.15 до +0.15 блока)
function getZBoundRandom(base) {
    return base + (Math.random() * 0.3 - 0.15);
}

let currentZNorth = getZBoundRandom(Z_BASE_NORTH);
let currentZSouth = getZBoundRandom(Z_BASE_SOUTH);

// Конечная точка по X (когда X станет меньше или равен -95.5 - стоп)
const END_X = -95.5; 

const EDGE_PAUSE_BASE_MS = 1000; 

// Функция для рандомной паузы смещения (база + до 400мс разброса)
function getRandomPause() {
    return EDGE_PAUSE_BASE_MS + (Math.random() * 400);
}

// Залипание в телефон (25% шанс постоять от 2 до 6 сек)
const SOCIAL_PAUSE_CHANCE = 0.25; 
function getSocialPauseDuration() {
    return 2000 + (Math.random() * 4000);
}


let lastX, lastY, lastZ;
let stuckTicks = 0;

function checkStuck() {
    let p = Player.getPlayer();
    if (!lastX) {
        lastX = p.getX(); lastY = p.getY(); lastZ = p.getZ();
        return false;
    }
    
    let dx = p.getX() - lastX;
    let dy = p.getY() - lastY;
    let dz = p.getZ() - lastZ;
    let distSq = dx*dx + dy*dy + dz*dz;
    
    // Если сдвинулись меньше чем на миллиметр
    if (distSq < 0.001) {
        stuckTicks++;
    } else {
        stuckTicks = 0;
    }
    
    lastX = p.getX(); lastY = p.getY(); lastZ = p.getZ();
    
    // Застревание через 2.5 секунды
    return stuckTicks > 50;
}

function stoppableSleep(durationMs) {
    let tickCount = Math.floor(durationMs / 50);
    if (tickCount < 1) tickCount = 1;

    for (let i = 0; i < tickCount; i++) {
        if (!GlobalVars.getBoolean("is_auto_pumpkin")) return false;
        
        // Постоянно дублируем зажатие W, чтобы не слетело
        KeyBind.keyBind("key.forward", true);
        
        Time.sleep(50);
    }
    return true; 
}

function smoothLookRandom(targetYaw, targetPitch, durationMs) {
    let p = Player.getPlayer();
    let startYaw = p.getYaw();
    let startPitch = p.getPitch();
    let diffYaw = ((targetYaw - startYaw + 180) % 360) - 180;
    if (diffYaw < -180) diffYaw += 360;
    let diffPitch = targetPitch - startPitch;
    
    let stepMs = 10;
    let tickCount = Math.floor(durationMs / stepMs); 
    if (tickCount < 1) tickCount = 1;

    for (let i = 1; i <= tickCount; i++) {
        let t = i / tickCount;
        let easeT = -(Math.cos(Math.PI * t) - 1) / 2;
        let jYaw = (Math.random() - 0.5) * 0.3;
        let jPitch = (Math.random() - 0.5) * 0.3;
        if (i === tickCount) { jYaw = 0; jPitch = 0; }
        
        p.lookAt(startYaw + diffYaw * easeT + jYaw, startPitch + diffPitch * easeT + jPitch);
        Time.sleep(stepMs);
    }
    p.lookAt(targetYaw, targetPitch);
}

function adminEvasion() {
    GlobalVars.putBoolean("is_auto_pumpkin", false);
    
    // Громкий звук (наковальня) для привлечения внимания
    World.playSound("block.anvil.land", 1.0, 1.0);
    Time.sleep(100);
    World.playSound("block.anvil.land", 1.0, 1.0);
    
    // Экстренно бросаем всё (attack выключится в finally)
    KeyBind.keyBind("key.left", false);
    KeyBind.keyBind("key.right", false);
    KeyBind.keyBind("key.forward", false);
    
    // Удивленный взгляд в сторону
    let p = Player.getPlayer();
    smoothLookRandom(p.getYaw() + 70, 15, 1200);
}

function runMacro() {
    GlobalVars.putBoolean("is_auto_pumpkin", true);
    let p = Player.getPlayer();
    
    try {
        // Звук старта (высокий писк)
        World.playSound("block.note_block.pling", 1.0, 2.0);
        
        // Наводка (с возможностью прервать)
        let steps = Math.floor(LOOK_TIME_MS / 10);
        let startYaw = p.getYaw();
        let startPitch = p.getPitch();
        let diffYaw = ((TARGET_YAW - startYaw + 180) % 360) - 180;
        if (diffYaw < -180) diffYaw += 360;
        let diffPitch = TARGET_PITCH - startPitch;
        
        for (let i = 1; i <= steps; i++) {
            if (!GlobalVars.getBoolean("is_auto_pumpkin")) return;
            let t = i / steps;
            let easeT = -(Math.cos(Math.PI * t) - 1) / 2;
            p.lookAt(startYaw + diffYaw * easeT, startPitch + diffPitch * easeT);
            Time.sleep(10);
        }
        p.lookAt(TARGET_YAW, TARGET_PITCH);
        
        // Звук готовности
        World.playSound("entity.experience_orb.pickup", 0.5, 1.0);
        
        // Кликаем единожды ЛКМ для Toggle Attack
        KeyBind.keyBind("key.attack", true);
        Time.sleep(50);
        KeyBind.keyBind("key.attack", false);
        
        // Включаем основное движение (Зажимаем W)
        KeyBind.keyBind("key.forward", true);
        
        // Изначальное направление определяем по тому, куда смотрит игрок ПЕРЕД стартом
        // 0 = Юг (+Z), 180 = Север (-Z). Мы просто смотрим, куда повернута камера.
        let normYaw = ((startYaw + 180) % 360) - 180;
        if (normYaw < -180) normYaw += 360;
        let direction = (Math.abs(normYaw) <= 90) ? "LEFT" : "RIGHT"; 
        
        // Звуковой индикатор стороны (короткий щелчок)
        World.playSound("block.note_block.hat", 0.5, direction === "LEFT" ? 2.0 : 0.5);
        
        // Внутренняя функция для "Залипания в телефон"
        function triggerSocialPause() {
            if (Math.random() < SOCIAL_PAUSE_CHANCE) {
                // ПРИОСТАНАВЛИВАЕМ ДВИЖЕНИЕ (но копание через Toggle Attack остается включенным!)
                KeyBind.keyBind("key.left", false);
                KeyBind.keyBind("key.right", false);
                KeyBind.keyBind("key.forward", false);
                
                let duration = getSocialPauseDuration();
                // Звук уведомления на "телефоне" (легкий динь)
                World.playSound("block.note_block.bell", 0.3, 1.5);
                
                if (!stoppableSleep(duration)) return false;
                
                // Возвращаем движение (W)
                KeyBind.keyBind("key.forward", true);
                return true;
            }
            return true;
        }
        
        if (direction === "LEFT") KeyBind.keyBind("key.left", true);
        else KeyBind.keyBind("key.right", true);
        
        while (GlobalVars.getBoolean("is_auto_pumpkin")) {
            p = Player.getPlayer();
            let currentZ = p.getZ();
            let currentX = p.getX();
            
            if (direction === "LEFT") {
                // Идем к Югу (+238) c учетом рандомного смещения
                if (currentZ >= currentZSouth) {
                    // Финальная проверка: если мы уже на координате X <= -95.5 - завершаем макрос!
                    if (currentX <= END_X) break;
                    
                    World.playSound("block.note_block.hat", 0.3, 1.0);
                    KeyBind.keyBind("key.left", false);
                    stuckTicks = -40; // Иммунитет к застреванию во время смещения о стену
                    
                    // Ждем рандомное время смещения
                    if (!stoppableSleep(getRandomPause())) break;
                    
                    // ШАНС ЗАЛИПНУТЬ В ТЕЛЕФОН
                    if (!triggerSocialPause()) break;
                    
                    // Обновляем границы на следующий проход (чтобы каждый круг был разным)
                    currentZSouth = getZBoundRandom(Z_BASE_SOUTH);
                    
                    direction = "RIGHT";
                    KeyBind.keyBind("key.right", true);
                }
            } else {
                // Идем к Северу (-238) c учетом рандомного смещения
                if (currentZ <= currentZNorth) {
                    if (currentX <= END_X) break;
                    
                    World.playSound("block.note_block.hat", 0.3, 1.0);
                    KeyBind.keyBind("key.right", false);
                    stuckTicks = -40; 
                    
                    // Ждем рандомное время смещения
                    if (!stoppableSleep(getRandomPause())) break;
                    
                    // ШАНС ЗАЛИПНУТЬ В ТЕЛЕФОН
                    if (!triggerSocialPause()) break;
                    
                    // Обновляем границы на следующий проход (чтобы каждый круг был разным)
                    currentZNorth = getZBoundRandom(Z_BASE_NORTH);
                    
                    direction = "LEFT";
                    KeyBind.keyBind("key.left", true);
                }
            }
            
            if (checkStuck()) {
                adminEvasion();
                break;
            }
            
            if (!stoppableSleep(50)) break; 
        }
        
    } finally {
        GlobalVars.putBoolean("is_auto_pumpkin", false);
        
        // Отжимаем Toggle Attack одиночным кликом
        KeyBind.keyBind("key.attack", true);
        Time.sleep(50);
        KeyBind.keyBind("key.attack", false);
        
        KeyBind.keyBind("key.left", false);
        KeyBind.keyBind("key.right", false);
        KeyBind.keyBind("key.forward", false);
        
        // Звук конца (низкий писк)
        World.playSound("block.note_block.pling", 1.0, 0.5);
    }
}

// Запуск или остановка
if (GlobalVars.getBoolean("is_auto_pumpkin") === true) {
    GlobalVars.putBoolean("is_auto_pumpkin", false);
} else {
    runMacro();
}
