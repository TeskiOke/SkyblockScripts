import flet as ft

AVAILABLE_MODULES = {
    "Greenhouse":  {"icon": "nature",     "short": "GH", "desc": "Расчёт мутаций теплицы"},
    "Farming":     {"icon": "grass",      "short": "FM", "desc": "Анализ фермерства"},
    "Mining":      {"icon": "landscape",  "short": "MN", "desc": "Прибыльность шахт"},
    "Flipping":    {"icon": "swap_horiz", "short": "FL", "desc": "Флиппинг Bazaar/AH"},
}

def make_circle(content_ctrl, size=46, bgcolor="#2a2a2a", on_click=None, selected=False):
    return ft.Container(
        content=content_ctrl,
        width=size,
        height=size,
        border_radius=size // 2,
        bgcolor="#1e3a5f" if selected else bgcolor,
        alignment=ft.Alignment.CENTER,
        on_click=on_click,
        ink=True,
    )

def main(page: ft.Page):
    page.title = "Skyblock Magister Terminal"
    page.theme_mode = "dark"
    page.window_width  = 1300
    page.window_height = 950
    page.padding = 0
    page.window_bgcolor = "#050505"
    page.bgcolor = "#050505"

    active = []
    state = {"idx": None, "tray_open": False}

    def render():
        page.controls.clear()

        tray_open = state["tray_open"]

        # --- SLIM RAIL (Иконки слева) ---
        # Кнопка добавления модуля
        add_circle = make_circle(
            ft.Text("+", size=24, weight="bold", color="#ffffff"),
            bgcolor="#2e7d32",
            on_click=open_add_dialog,
        )

        # Кнопка открытия/закрытия трея
        tray_circle = make_circle(
            ft.Text("V" if not tray_open else "A", size=20, weight="bold", color="#dddddd"),
            bgcolor="#252525",
            on_click=toggle_tray,
        )

        module_circles = []
        for i, m in enumerate(active):
            selected = (i == state["idx"])
            info = AVAILABLE_MODULES.get(m["name"], {})
            short = info.get("short", m["name"][:2].upper())
            module_circles.append(
                make_circle(
                    ft.Text(short, size=13, weight="bold",
                            color="#ffffff" if selected else "#aaaaaa"),
                    selected=selected,
                    bgcolor="#1a1a1a",
                    on_click=lambda e, idx=i: select_module(idx),
                )
            )

        rail_children = [add_circle, tray_circle]
        if tray_open:
            # Кружки модулей показываем только когда открыт трей
            rail_children.append(ft.Container(height=10))
            rail_children.extend(module_circles)

        rail_column = ft.Column(
            rail_children,
            spacing=12,
            horizontal_alignment="center",
        )

        slim_rail = ft.Container(
            content=rail_column,
            width=70,
            bgcolor="#050505",
            padding=ft.padding.symmetric(vertical=16, horizontal=0),
        )

        # --- EXTENDED TRAY (Выдвижная панель) ---
        if tray_open:
            tray_items = []
            for i, m in enumerate(active):
                selected = (i == state["idx"])
                tray_items.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            m["icon"],
                                            size=20,
                                            color="#ffffff" if selected else "#888888",
                                        ),
                                        ft.Text(
                                            m["name"],
                                            size=15,
                                            color="#ffffff" if selected else "#cccccc",
                                            weight="bold" if selected else "normal",
                                        ),
                                    ],
                                    spacing=12,
                                    vertical_alignment="center",
                                ),
                                ft.Row(
                                    [
                                        ft.TextButton(
                                            "Удалить конфиг",
                                            icon="delete",
                                            style=ft.ButtonStyle(
                                                color="#ff6666",
                                                padding=0,
                                            ),
                                            on_click=lambda e, n=m["name"]: remove_module(n),
                                        )
                                    ],
                                    alignment="end",
                                ),
                            ]
                        ),
                        padding=ft.padding.symmetric(horizontal=12, vertical=12),
                        border_radius=8,
                        bgcolor="#1e3a5f" if selected else "#1a1a1a",
                        on_click=lambda e, idx=i: select_module(idx),
                        ink=True,
                    )
                )

            tray_panel = ft.Container(
                content=ft.Column(tray_items, spacing=4),
                width=240,
                bgcolor="#050505",
                padding=ft.padding.symmetric(vertical=16, horizontal=8),
            )
        else:
            tray_panel = ft.Container(width=0, padding=0, margin=0)

        # --- MAIN BODY (Основной контент) ---
        if not active or state["idx"] is None:
            body = ft.Container(
                bgcolor="#050505",
                expand=True,
                content=ft.Column(
                    [
                        ft.Icon("dashboard", size=80, color="#444444"),
                        ft.Text("Skyblock Magister Terminal", size=28, weight="bold"),
                        ft.Text(
                            "Нажмите зелёный + слева сверху, чтобы подключить модуль.",
                            size=15,
                            color="#888888",
                        ),
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=16,
                    expand=True,
                ),
            )
        else:
            m = active[state["idx"]]

            work_area = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(m["desc"], size=15, color="#888888"),
                        ft.Container(height=20),
                        ft.Container(
                            content=ft.Text(
                                "[ Содержимое модуля будет здесь ]",
                                size=14,
                                color="#888888",
                            ),
                            border=ft.border.all(1, "#333333"),
                            border_radius=8,
                            padding=40,
                            expand=True,
                            bgcolor="#050505",
                        ),
                        ft.Row(
                            [
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.FloatingActionButton(
                                        icon="play_arrow",
                                        bgcolor="#2e7d32",
                                        tooltip="Запустить скрипт модуля",
                                        on_click=lambda e, n=m["name"]: run_module(n),
                                    ),
                                ),
                            ],
                            alignment="end",
                        ),
                    ],
                    expand=True,
                    spacing=16,
                ),
                padding=30,
                expand=True,
            )

            body = ft.Container(
                bgcolor="#050505",
                expand=True,
                content=ft.Column(
                    [
                        # Заголовок модуля
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(m["icon"], size=32),
                                    ft.Text(m["name"], size=26, weight="bold"),
                                    ft.Container(expand=True),
                                    ft.ElevatedButton(
                                        "Удалить модуль",
                                        icon="delete",
                                        bgcolor="#7a2222",
                                        color="white",
                                        on_click=lambda e, n=m["name"]: remove_module(n),
                                    ),
                                ],
                                vertical_alignment="center",
                            ),
                            padding=ft.padding.symmetric(horizontal=30, vertical=20),
                        ),
                        ft.Divider(height=1, color="#333333"),
                        work_area,
                    ],
                    expand=True,
                    spacing=0,
                ),
            )

        main_layout = ft.Row(
            [
                slim_rail,
                ft.VerticalDivider(width=1, color="#222222"),
                tray_panel,
                ft.VerticalDivider(width=1, color="#222222") if tray_open else ft.Container(width=0),
                body,
            ],
            expand=True,
            spacing=0,
        )

        page.add(
            ft.Container(
                content=main_layout,
                bgcolor="#050505",
                expand=True,
            )
        )
        page.update()

    # --- Actions ---
    def toggle_tray(e):
        state["tray_open"] = not state["tray_open"]
        render()

    def select_module(idx):
        state["idx"] = idx
        render()

    def add_module(name):
        info = AVAILABLE_MODULES[name]
        active.append({"name": name, "icon": info["icon"], "desc": info["desc"]})
        state["idx"] = len(active) - 1
        render()

    def remove_module(name):
        active[:] = [m for m in active if m["name"] != name]
        state["idx"] = 0 if active else None
        render()

    def run_module(name):
        # Заглушка запуска — позже сюда подставим реальный вызов скрипта
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Запуск модуля: {name} (пока заглушка)"),
            open=True,
        )
        page.update()

    def open_add_dialog(e):
        active_names = {m["name"] for m in active}
        available = {k: v for k, v in AVAILABLE_MODULES.items() if k not in active_names}

        if not available:
            page.snack_bar = ft.SnackBar(ft.Text("Все модули уже добавлены!"), open=True)
            page.update()
            return

        def pick(name, dlg):
            dlg.open = False
            page.update()
            add_module(name)

        btns = [
            ft.ElevatedButton(
                f"{name}  —  {v['desc']}",
                icon=v["icon"],
                width=400,
                on_click=lambda e, n=name: pick(n, dlg),
            )
            for name, v in available.items()
        ]

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Добавить модуль"),
            content=ft.Column(btns, spacing=10, tight=True),
            actions=[ft.TextButton("Отмена", on_click=lambda e: close_dlg(dlg))],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def close_dlg(dlg):
        dlg.open = False
        page.update()

    render()

ft.app(target=main)
