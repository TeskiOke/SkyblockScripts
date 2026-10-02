# Skyblock RPG Scripts

Набор инструментов для Hypixel Skyblock: JS-макросы для JsMacros и Python-утилиты для анализа экономики, калькуляций и трекинга.

---

## Структура

```
JS_Macros/       — Скрипты для JsMacros (запускаются в Minecraft)
Python_Scripts/  — Консольные утилиты (калькуляторы, парсеры, трекеры)
modules/         — Общие Python-модули
```

---

## JS_Macros

Скрипты для мода [JsMacros](https://github.com/xy2z/JsMacros) — запускаются прямо внутри Minecraft, выводят результаты в чат через `Chat.log()`.

Все калькуляторы тянут актуальные цены с **Hypixel Bazaar API** (`api.hypixel.net/v2/skyblock/bazaar`) в реальном времени.

| Файл | Назначение |
|---|---|
| `auto_farm.js` | Автофарм по координатам с Admin Check: если персонаж не двигается несколько тиков — останавливается |
| `auto_pumpkin.js` | Автофарм тыквы |
| `farming_calc.js` | Доходность фармы: считает монеты/час по всем культурам через T1→T2→T3 конвертацию, включая Pest-дропы |
| `mining_calc.js` | Доходность майнинга: руды по тирам, самоцветы (12 типов × 5 тиров), Crystal Hollows предметы |
| `mutation_calc.js` | Цены на все Garden Mutations предметы по тирам редкости (Common/Uncommon/Rare и выше) |

---

## Python_Scripts

Консольные утилиты — запускаются отдельно от Minecraft.

| Файл | Назначение |
|---|---|
| `farming_calc.py` | Расширенный калькулятор фармы с цветным выводом в терминал, Pest-дропы, Garden Chips |
| `mining_calc.py` | Калькулятор майнинга: руды, самоцветы, CH-предметы с ценами с Bazaar |
| `mutation_calc.py` | Калькулятор мутаций Garden |
| `session_tracker.py` | Трекер сессий ПК: парсит Windows Event Log (6005/6006/6008/1074) — считает время работы компьютера и потреблённые кВт·ч |
| `fetch_stats.py` | Парсер sky.shiiyu.moe — сохраняет HTML со статистикой игрока |
| `main.py` | Главный Flet-терминал: объединяет все модули в одно окно с боковой навигацией |
| `spp_monitor.py` | SPP-монитор Honor наушников (Python-порт, дублирует HonorEarbudsManager) |
| `steam_tester.py` | Утилита тестирования Steam API |

### Запуск главного терминала
```bash
pip install flet requests
python main.py
```

### Запуск отдельного калькулятора
```bash
pip install requests
python farming_calc.py
```

---

## modules/

Общие модули, используемые `main.py`:

| Файл | Назначение |
|---|---|
| `base_module.py` | Базовый класс модуля с общим интерфейсом |
| `farming.py` | Логика модуля фармы |
| `mining.py` | Логика модуля майнинга |
| `flipping.py` | Логика модуля флиппинга (Bazaar/AH) |
| `greenhouse.py` | Логика модуля теплицы |

---

## Требования

**JS_Macros:** Minecraft с установленным модом JsMacros (совместим с Forge/Fabric)

**Python_Scripts:**
```
requests
flet      # только для main.py
```
