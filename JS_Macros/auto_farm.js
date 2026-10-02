/*
 * Smart Auto Farm (Coordinate-Based with Admin Protection)
 * Опирается на координаты Z, умеет останавливаться на нужной высоте.
 * Встроена защита от блокировок пути (отвод камеры и остановка).
 */

const TARGET_YAW = 90;
const TARGET_PITCH = -1.2;
const LOOK_TIME_MS = 2000;

// Границы маршрута по Z
const Z_BOUND_NORTH = -238.1; // Крайний север
const Z_BOUND_SOUTH = 238.1;  // Крайний юг

// Конечный этаж для остановки макроса
const END_Y = 67.5; 

const EDGE_PAUSE_MS = 500; // Пауза перед разворотом и падением


// Глобальные переменные для детекта застревания (Admin Check)
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
    
    // Если мы за тик сдвинулись меньше чем на миллиметр (уперлись в стену/админа/стекло)
    if (distSq < 0.001) {
        stuckTicks++;
    } else {
        stuckTicks = 0;
    }
    
    lastX = p.getX(); lastY = p.getY(); lastZ = p.getZ();
    
    // Если мы "копаем", но стоим физически на месте больше 2.5 секунд (50 тиков) во время активной фазы
    return stuckTicks > 50;
}

// Специальный сортер времени
function stoppableSleep(durationMs) {
    let tickCount = Math.floor(durationMs / 50);
    if (tickCount < 1) tickCount = 1;

    for (let i = 0; i < tickCount; i++) {
        if (!GlobalVars.getBoolean("is_auto_farming")) return false;
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
        let jYaw = (Math.random() - 0.5) * 0.5;
        let jPitch = (Math.random() - 0.5) * 0.5;
        if (i === tickCount) { jYaw = 0; jPitch = 0; }
        
        p.lookAt(startYaw + diffYaw * easeT + jYaw, startPitch + diffPitch * easeT + jPitch);
        Time.sleep(stepMs);
    }
    p.lookAt(targetYaw, targetPitch);
}

function adminEvasion() {
    GlobalVars.putBoolean("is_auto_farming", false);
    
    // Громкий и неприятный звук админ-чека (наковальня)
    World.playSound("block.anvil.land", 1.0, 1.0);
    Time.sleep(100);
    World.playSound("block.anvil.land", 1.0, 1.0);
    
    // Экстренно бросаем всё
    KeyBind.keyBind("key.attack", false);
    KeyBind.keyBind("key.left", false);
    KeyBind.keyBind("key.right", false);
    
    // Имитация человека: от испуга/неожиданности удивленно смотрим вбок на препятствие или админа
    // Поворачиваем камеру на 70 градусов в сторону и питч в 15 (смотрим чуть в центр)
    let p = Player.getPlayer();
    smoothLookRandom(p.getYaw() + 70, 15, 1200);
}

function runMacro() {
    GlobalVars.putBoolean("is_auto_farming", true);
    let p = Player.getPlayer();
    
    try {
        // Звук начала макроса (высокая нота)
        World.playSound("block.note_block.pling", 1.0, 2.0);
        
        // Стартовая наводка (с возможностью прервать)
        let steps = Math.floor(LOOK_TIME_MS / 10);
        let startYaw = p.getYaw();
        let startPitch = p.getPitch();
        let diffYaw = ((TARGET_YAW - startYaw + 180) % 360) - 180;
        if (diffYaw < -180) diffYaw += 360;
        let diffPitch = TARGET_PITCH - startPitch;
        
        for (let i = 1; i <= steps; i++) {
            if (!GlobalVars.getBoolean("is_auto_farming")) return;
            let t = i / steps;
            let easeT = -(Math.cos(Math.PI * t) - 1) / 2;
            p.lookAt(startYaw + diffYaw * easeT, startPitch + diffPitch * easeT);
            Time.sleep(10);
        }
        p.lookAt(TARGET_YAW, TARGET_PITCH);
        
        // Тихий звук готовности
        World.playSound("entity.experience_orb.pickup", 0.5, 1.0);
        
        // Автомагически понимаем, куда нам сейчас нужно идти (если Z отрицательный, идем к +238, то есть LEFT)
        let direction = (p.getZ() < 0) ? "LEFT" : "RIGHT"; 
        
        // Кликаем один раз ЛКМ для активации мода Toggle Attack (залипание кнопки атаки)
        KeyBind.keyBind("key.attack", true);
        Time.sleep(50);
        KeyBind.keyBind("key.attack", false);
        
        // Зажимаем начальное направление движения
        if (direction === "LEFT") {
            KeyBind.keyBind("key.left", true);
        } else {
            KeyBind.keyBind("key.right", true);
        }
        
        // Запускаем основной цикл макроса
        while (GlobalVars.getBoolean("is_auto_farming")) {
            p = Player.getPlayer();
            let currentZ = p.getZ();
            let currentY = p.getY();
            
            if (direction === "LEFT") {
                // Проверям дошли ли до конца линии (+238)
                if (currentZ >= Z_BOUND_SOUTH) {
                    // Звук падения/разворота
                    World.playSound("block.note_block.hat", 0.5, 1.0);
                    
                    // Ждем РЕАЛЬНОГО падения (высота Y должна уменьшиться)
                    let startY = currentY;
                    while (p.getY() > startY - 0.5 && GlobalVars.getBoolean("is_auto_farming")) {
                        if (checkStuck()) { adminEvasion(); break; }
                        Time.sleep(50);
                        p = Player.getPlayer();
                    }
                    
                    KeyBind.keyBind("key.left", false);
                    direction = "RIGHT";
                    stuckTicks = -40; // Даем 2 секунды иммунитета на падение
                    if (!GlobalVars.getBoolean("is_auto_farming")) break;
                    if (!stoppableSleep(EDGE_PAUSE_MS)) break;
                    
                    // После паузы зажимаем движение в другую сторону
                    KeyBind.keyBind("key.right", true);
                }
            } else {
                // Проверям дошли ли до конца линии (-238)
                if (currentZ <= Z_BOUND_NORTH) {
                    
                    // ЕСЛИ МЫ ДОШЛИ ДО КОНЦА И МЫ НА ПОСЛЕДНЕМ ЭТАЖЕ (Y <= 67.5) -> ВЫКЛЮЧАЕМСЯ!!!
                    if (currentY <= END_Y) {
                        GlobalVars.putBoolean("is_auto_farming", false);
                        break;
                    }
                    
                    // Звук падения/разворота
                    World.playSound("block.note_block.hat", 0.5, 1.0);
                    
                    // Ждем РЕАЛЬНОГО падения (высота Y должна уменьшиться)
                    let startY = currentY;
                    while (p.getY() > startY - 0.5 && GlobalVars.getBoolean("is_auto_farming")) {
                        if (checkStuck()) { adminEvasion(); break; }
                        Time.sleep(50);
                        p = Player.getPlayer();
                    }
                    
                    KeyBind.keyBind("key.right", false);
                    direction = "LEFT";
                    stuckTicks = -40; // Защита от детекта застревания во время падения вниз
                    if (!GlobalVars.getBoolean("is_auto_farming")) break;
                    if (!stoppableSleep(EDGE_PAUSE_MS)) break;
                    
                    // После паузы зажимаем движение в другую сторону
                    KeyBind.keyBind("key.left", true);
                }
            }
            
            // Если мы летим в стену и корды не меняются - либо это баг, либо перед нами стоит АДМИН
            if (checkStuck()) {
                adminEvasion();
                break; // Скрипт мгновенно прекратит работу
            }
            
            // Спим 1 тик
            if (!stoppableSleep(50)) break; 
        }
        
    } finally {
        GlobalVars.putBoolean("is_auto_farming", false);
        // Отключаем режим Toggle Attack одиночным кликом ЛКМ
        KeyBind.keyBind("key.attack", true);
        Time.sleep(50);
        KeyBind.keyBind("key.attack", false);
        
        // Страховочное отжатие всего остального
        KeyBind.keyBind("key.left", false);
        KeyBind.keyBind("key.right", false);
        KeyBind.keyBind("key.forward", false);
        
        // Звук выключения (низкая нота)
        World.playSound("block.note_block.pling", 1.0, 0.5);
    }
}

// Обработчик кнопки как переключатель включить/выключить
if (GlobalVars.getBoolean("is_auto_farming") === true) {
    GlobalVars.putBoolean("is_auto_farming", false);
} else {
    runMacro();
}
