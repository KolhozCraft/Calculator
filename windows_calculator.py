"""
Калькулятор на customtkinter в стиле Windows 11.

Режимы (все полностью рабочие):
  - Обычный
  - Инженерный        (тригонометрия, логарифмы, степени, факториал, DEG/RAD)
  - Построение графиков (встроенный график функции y=f(x), нужен matplotlib)
  - Программист       (HEX/DEC/OCT/BIN, битовые операции, разрядность)
  - Вычисление даты   (разница дат / добавить-вычесть дни)
  - Конвертер         (13 категорий единиц измерения)

Запуск: python windows_calculator.py
Требуется: pip install customtkinter matplotlib
"""

import sys
import math
import datetime
import customtkinter as ctk

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

APP_NAME = "Калькулятор"
APP_PRODUCT = "Windows Style Calculator"
APP_COMPANY = "ky4ka-boroxla"
APP_VERSION = "0.3.2"

THEMES = {
    "dark": {
        "bg": "#202020",
        "display_fg": "#FFFFFF",
        "mem_row_fg": "#7a7a7a",
        "func_btn": "#2b2b2b",
        "func_btn_hover": "#3d3d3d",
        "num_btn": "#2b2b2b",
        "num_btn_hover": "#3d3d3d",
        "eq_btn": "#4cc2ff",
        "eq_btn_hover": "#3db0ec",
        "eq_fg": "#000000",
        "icon_fg": "#c8c8c8",
        "icon_hover": "#2b2b2b",
        "history_bg": "#2b2b2b",
        "history_item_hover": "#3d3d3d",
        "history_expr_fg": "#a0a0a0",
        "history_result_fg": "#FFFFFF",
        "sidebar_active_bg": "#3d5875",
        "sidebar_active_fg": "#8fd0ff",
        "sidebar_section_fg": "#8a8a8a",
        "entry_bg": "#2b2b2b",
        "border": "#3d3d3d",
    },
    "light": {
        "bg": "#f3f3f3",
        "display_fg": "#000000",
        "mem_row_fg": "#7a7a7a",
        "func_btn": "#e9e9e9",
        "func_btn_hover": "#d9d9d9",
        "num_btn": "#fbfbfb",
        "num_btn_hover": "#e5e5e5",
        "eq_btn": "#0067c0",
        "eq_btn_hover": "#005ba1",
        "eq_fg": "#FFFFFF",
        "icon_fg": "#5a5a5a",
        "icon_hover": "#e5e5e5",
        "history_bg": "#ffffff",
        "history_item_hover": "#e9e9e9",
        "history_expr_fg": "#6b6b6b",
        "history_result_fg": "#000000",
        "sidebar_active_bg": "#cfe8ff",
        "sidebar_active_fg": "#0067c0",
        "sidebar_section_fg": "#6b6b6b",
        "entry_bg": "#ffffff",
        "border": "#d9d9d9",
    },
}

FONT_DISPLAY = ("Segoe UI", 44)
FONT_BTN = ("Segoe UI", 18)
FONT_BTN_SM = ("Segoe UI", 14)
FONT_MEM = ("Segoe UI", 14)
FONT_ICON = ("Segoe UI", 15)
FONT_MDL2 = ("Segoe MDL2 Assets", 15)
FONT_HIST_EXPR = ("Segoe UI", 12)
FONT_HIST_RESULT = ("Segoe UI", 18)

CONVERTER_UNITS = {
    "Длина": {
        "мм": 0.001, "см": 0.01, "м": 1, "км": 1000,
        "дюйм": 0.0254, "фут": 0.3048, "ярд": 0.9144, "миля": 1609.344,
    },
    "Вес и масса": {
        "мг": 0.000001, "г": 0.001, "кг": 1, "т": 1000,
        "унция": 0.0283495, "фунт": 0.453592,
    },
    "Объём": {
        "мл": 0.001, "л": 1, "м\u00B3": 1000,
        "галлон (US)": 3.78541, "пинта (US)": 0.473176,
    },
    "Площадь": {
        "см\u00B2": 0.0001, "м\u00B2": 1, "км\u00B2": 1_000_000,
        "гектар": 10000, "акр": 4046.86,
    },
    "Скорость": {
        "м/с": 1, "км/ч": 0.277778, "миля/ч": 0.44704, "узел": 0.514444,
    },
    "Время": {
        "с": 1, "мин": 60, "ч": 3600, "сутки": 86400, "неделя": 604800,
    },
    "Энергия": {
        "Дж": 1, "кДж": 1000, "кал": 4.184, "ккал": 4184, "кВт\u00B7ч": 3_600_000,
    },
    "Мощность": {
        "Вт": 1, "кВт": 1000, "л.с.": 735.499,
    },
    "Данные": {
        "бит": 1, "байт": 8, "КБ": 8 * 1024, "МБ": 8 * 1024**2,
        "ГБ": 8 * 1024**3, "ТБ": 8 * 1024**4,
    },
    "Давление": {
        "Па": 1, "кПа": 1000, "бар": 100000, "атм": 101325, "мм рт.ст.": 133.322,
    },
    "Угол": {
        "градус": 1, "радиан": 57.29578, "градиан": 0.9,
    },
    "Валюта": {
        "RUB": 1, "USD": 95, "EUR": 103, "GBP": 120, "CNY": 13,
    },
}
CONVERTER_CATEGORY_ORDER = [
    "Валюта", "Объём", "Длина", "Вес и масса", "Температура",
    "Энергия", "Площадь", "Скорость", "Время", "Мощность",
    "Данные", "Давление", "Угол",
]
TEMPERATURE_UNITS = ["\u00B0C", "\u00B0F", "K"]


def convert_temperature(value: float, from_u: str, to_u: str) -> float:
    if from_u == "\u00B0C":
        c = value
    elif from_u == "\u00B0F":
        c = (value - 32) * 5 / 9
    else:
        c = value - 273.15

    if to_u == "\u00B0C":
        return c
    elif to_u == "\u00B0F":
        return c * 9 / 5 + 32
    else:
        return c + 273.15


class WindowsStyleCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("340x600")
        self.minsize(320, 520)

        self.theme_name = "dark"
        ctk.set_appearance_mode("dark")

        self.current_mode = "Обычный"
        self.always_on_top = False
        self.sidebar_visible = False
        self.angle_unit = "deg"

        self.available_modes = [
            "Обычный",
            "Инженерный",
            "Построение графиков",
            "Программист",
            "Вычисление даты",
        ]
        self.converter_categories = CONVERTER_CATEGORY_ORDER

        self.mode_icons = {
            "Обычный": "\u229E",
            "Инженерный": "\u2211",
            "Построение графиков": "\u222B",
            "Программист": "\u2328",
            "Вычисление даты": "\u25A4",
        }
        self.converter_icons = {
            "Валюта": "$", "Объём": "\u25B3", "Длина": "\u2194",
            "Вес и масса": "\u2696", "Температура": "\u2103", "Энергия": "\u26A1",
            "Площадь": "\u25A6", "Скорость": "\u27A4", "Время": "\u23F1",
            "Мощность": "\u23FB", "Данные": "\u25A5", "Давление": "\u21CA",
            "Угол": "\u2220",
        }

        self.current_value = "0"
        self.stored_value = None
        self.pending_op = None
        self.reset_on_next_digit = False

        self.history = []
        self.history_visible = False

        self.configure(fg_color=self._c("bg"))
        self._build_shell()
        self._build_standard_content()

    def _c(self, key):
        return THEMES[self.theme_name][key]

    def _build_shell(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=36)
        top_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        top_bar.grid_columnconfigure(1, weight=1)

        self.hamburger_btn = ctk.CTkButton(
            top_bar, text="\uE700", font=FONT_MDL2, fg_color="transparent",
            hover_color=self._c("icon_hover"), text_color=self._c("icon_fg"),
            width=32, height=28, command=self.toggle_sidebar,
        )
        self.hamburger_btn.grid(row=0, column=0, sticky="w")

        self.mode_label = ctk.CTkLabel(
            top_bar, text=self.current_mode, font=("Segoe UI", 15, "bold"),
            text_color=self._c("display_fg"), anchor="w",
        )
        self.mode_label.grid(row=0, column=1, sticky="w", padx=(4, 0))

        self.pin_btn = ctk.CTkButton(
            top_bar, text="\uE840", font=FONT_MDL2, fg_color="transparent",
            hover_color=self._c("icon_hover"), text_color=self._c("icon_fg"),
            width=32, height=28, command=self.toggle_always_on_top,
        )
        self.pin_btn.grid(row=0, column=2, sticky="e")

        self.history_toggle_btn = ctk.CTkButton(
            top_bar, text="\uE81C", font=FONT_MDL2, fg_color="transparent",
            hover_color=self._c("icon_hover"), text_color=self._c("icon_fg"),
            width=32, height=28, command=self.toggle_history,
        )
        self.history_toggle_btn.grid(row=0, column=3, sticky="e")

        self.sidebar_frame = ctk.CTkScrollableFrame(
            self, fg_color=self._c("history_bg"), width=240, height=480
        )
        self.sidebar_header = ctk.CTkLabel(
            self.sidebar_frame, text=APP_NAME, font=("Segoe UI", 14, "bold"),
            text_color=self._c("display_fg"), anchor="w",
        )
        self.sidebar_header.pack(fill="x", padx=8, pady=(4, 8))

        self.mode_sidebar_buttons = {}
        for mode in self.available_modes:
            icon = self.mode_icons.get(mode, "")
            b = ctk.CTkButton(
                self.sidebar_frame, text=f"{icon}   {mode}", font=("Segoe UI", 14),
                anchor="w", corner_radius=6, fg_color="transparent",
                hover_color=self._c("history_item_hover"), text_color=self._c("display_fg"),
                height=36, command=lambda m=mode: self.select_mode(m),
            )
            b.pack(fill="x", padx=6, pady=1)
            self.mode_sidebar_buttons[mode] = b

        self.converter_section_label = ctk.CTkLabel(
            self.sidebar_frame, text="Преобразователь", font=("Segoe UI", 12, "bold"),
            text_color=self._c("sidebar_section_fg"), anchor="w",
        )
        self.converter_section_label.pack(fill="x", padx=8, pady=(14, 4))

        self.converter_sidebar_buttons = []
        for cat in self.converter_categories:
            icon = self.converter_icons.get(cat, "")
            b = ctk.CTkButton(
                self.sidebar_frame, text=f"{icon}   {cat}", font=("Segoe UI", 14),
                anchor="w", corner_radius=6, fg_color="transparent",
                hover_color=self._c("history_item_hover"), text_color=self._c("display_fg"),
                height=34, command=lambda c=cat: self.select_converter(c),
            )
            b.pack(fill="x", padx=6, pady=1)
            self.converter_sidebar_buttons.append(b)

        sep = ctk.CTkFrame(self.sidebar_frame, fg_color=self._c("mem_row_fg"), height=1)
        sep.pack(fill="x", padx=8, pady=10)

        self.settings_menu_btn = ctk.CTkButton(
            self.sidebar_frame, text="\u2699 Параметры", font=("Segoe UI", 14),
            anchor="w", corner_radius=6, fg_color="transparent",
            hover_color=self._c("history_item_hover"), text_color=self._c("history_expr_fg"),
            height=36, command=self.show_settings,
        )
        self.settings_menu_btn.pack(fill="x", padx=6, pady=(0, 8))

        self._highlight_active_mode()
        self.bind("<Configure>", self._on_window_resize)

        self.history_frame = ctk.CTkScrollableFrame(self, fg_color=self._c("history_bg"), height=150)
        self.history_placeholder = ctk.CTkLabel(
            self.history_frame, text="Здесь появится история",
            font=FONT_HIST_EXPR, text_color=self._c("history_expr_fg"),
        )
        self.history_placeholder.pack(pady=20)

        self.content_frame = ctk.CTkFrame(self, fg_color=self._c("bg"))
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _clear_content(self):
        for child in self.content_frame.winfo_children():
            child.destroy()

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self._resize_sidebar()
            self.sidebar_frame.place(x=0, y=36)
            self.sidebar_frame.lift()
        else:
            self.sidebar_frame.place_forget()

    def _resize_sidebar(self):
        self.update_idletasks()
        full_height = max(self.winfo_height() - 36, 300)
        self.sidebar_frame.configure(height=full_height)

    def _on_window_resize(self, event=None):
        if self.sidebar_visible:
            self._resize_sidebar()

    def _highlight_active_mode(self):
        for mode, btn in self.mode_sidebar_buttons.items():
            if mode == self.current_mode:
                btn.configure(fg_color=self._c("sidebar_active_bg"), text_color=self._c("sidebar_active_fg"))
            else:
                btn.configure(fg_color="transparent", text_color=self._c("display_fg"))

    def select_mode(self, mode: str):
        self.toggle_sidebar()
        if mode == self.current_mode:
            return
        self.current_mode = mode
        self.mode_label.configure(text=mode)
        self._highlight_active_mode()
        self._clear_content()

        if mode == "Обычный":
            self._build_standard_content()
        elif mode == "Инженерный":
            self._build_engineering_content()
        elif mode == "Вычисление даты":
            self._build_date_content()
        elif mode == "Построение графиков":
            self._build_graphing_content()
        elif mode == "Программист":
            self._build_programmer_content()
        else:
            self._build_not_implemented_content(mode)

    def select_converter(self, category: str):
        self.toggle_sidebar()
        self.current_mode = "Конвертер"
        self.mode_label.configure(text=f"Конвертер \u2014 {category}")
        self._highlight_active_mode()
        self._clear_content()
        self._build_converter_content(category)

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.attributes("-topmost", self.always_on_top)
        self.pin_btn.configure(text_color=self._c("eq_btn") if self.always_on_top else self._c("icon_fg"))

    def _build_not_implemented_content(self, mode: str):
        wrap = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        wrap.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            wrap, text=f"Режим «{mode}»", font=("Segoe UI", 18, "bold"),
            text_color=self._c("display_fg"),
        ).pack(pady=(60, 10))
        ctk.CTkLabel(
            wrap, text="Ещё не реализован в этой версии.",
            font=("Segoe UI", 13), text_color=self._c("history_expr_fg"),
        ).pack()

    def show_settings(self):
        self.toggle_sidebar()
        if getattr(self, "_settings_win", None) is not None and self._settings_win.winfo_exists():
            self._settings_win.lift()
            self._settings_win.focus_force()
            return
        win = ctk.CTkToplevel(self)
        self._settings_win = win
        win.title("Параметры")
        win.geometry("280x220")
        win.resizable(False, False)
        win.configure(fg_color=self._c("bg"))
        win.transient(self)
        win.after(50, win.grab_set)

        ctk.CTkLabel(win, text="Параметры", font=("Segoe UI", 16, "bold"),
                     text_color=self._c("display_fg")).pack(pady=(20, 12), padx=20)
        ctk.CTkButton(win, text="\u2600 Светлая / тёмная тема", anchor="w",
                      fg_color=self._c("func_btn"), hover_color=self._c("func_btn_hover"),
                      text_color=self._c("display_fg"), command=self.toggle_theme
                      ).pack(fill="x", padx=20, pady=4)
        ctk.CTkButton(win, text="\u2139 О программе", anchor="w",
                      fg_color=self._c("func_btn"), hover_color=self._c("func_btn_hover"),
                      text_color=self._c("display_fg"), command=self.show_about
                      ).pack(fill="x", padx=20, pady=4)
        ctk.CTkButton(win, text="Закрыть", fg_color=self._c("eq_btn"),
                      hover_color=self._c("eq_btn_hover"), text_color=self._c("eq_fg"),
                      command=win.destroy).pack(pady=(16, 10))

    def show_about(self):
        if getattr(self, "_about_win", None) is not None and self._about_win.winfo_exists():
            self._about_win.lift()
            self._about_win.focus_force()
            return
        win = ctk.CTkToplevel(self)
        self._about_win = win
        win.title("О программе")
        win.geometry("280x260")
        win.resizable(False, False)
        win.configure(fg_color=self._c("bg"))
        win.transient(self)
        win.after(50, win.grab_set)

        ctk.CTkLabel(win, text=APP_PRODUCT, font=("Segoe UI", 18, "bold"),
                     text_color=self._c("display_fg")).pack(pady=(24, 4), padx=20)
        ctk.CTkLabel(win, text=f"Версия {APP_VERSION}", font=("Segoe UI", 13),
                     text_color=self._c("history_expr_fg")).pack(pady=(0, 16))
        ctk.CTkLabel(win, text=f"Разработчик: {APP_COMPANY}", font=("Segoe UI", 13),
                     text_color=self._c("history_expr_fg")).pack(pady=(0, 4))
        ctk.CTkLabel(win, text="Калькулятор в стиле Windows 11", font=("Segoe UI", 12),
                     text_color=self._c("history_expr_fg"), justify="center").pack(pady=(0, 20))
        ctk.CTkButton(win, text="OK", width=100, fg_color=self._c("eq_btn"),
                      hover_color=self._c("eq_btn_hover"), text_color=self._c("eq_fg"),
                      command=win.destroy).pack(pady=(0, 10))

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        ctk.set_appearance_mode(self.theme_name)

        self.configure(fg_color=self._c("bg"))
        self.content_frame.configure(fg_color=self._c("bg"))
        self.history_frame.configure(fg_color=self._c("history_bg"))
        self.sidebar_frame.configure(fg_color=self._c("history_bg"))
        self.mode_label.configure(text_color=self._c("display_fg"))

        self.hamburger_btn.configure(hover_color=self._c("icon_hover"), text_color=self._c("icon_fg"))
        self.pin_btn.configure(
            hover_color=self._c("icon_hover"),
            text_color=self._c("eq_btn") if self.always_on_top else self._c("icon_fg"),
        )
        self.history_toggle_btn.configure(hover_color=self._c("icon_hover"), text_color=self._c("icon_fg"))

        self.sidebar_header.configure(text_color=self._c("display_fg"))
        for b in self.mode_sidebar_buttons.values():
            b.configure(hover_color=self._c("history_item_hover"))
        self._highlight_active_mode()

        self.converter_section_label.configure(text_color=self._c("sidebar_section_fg"))
        for b in self.converter_sidebar_buttons:
            b.configure(hover_color=self._c("history_item_hover"), text_color=self._c("display_fg"))
        self.settings_menu_btn.configure(hover_color=self._c("history_item_hover"), text_color=self._c("history_expr_fg"))

        self._refresh_history_ui()
        self._clear_content()
        if self.current_mode == "Обычный":
            self._build_standard_content()
        elif self.current_mode == "Инженерный":
            self._build_engineering_content()
        elif self.current_mode == "Вычисление даты":
            self._build_date_content()
        elif self.current_mode == "Конвертер":
            cat = self.mode_label.cget("text").split("\u2014")[-1].strip()
            self._build_converter_content(cat if cat in CONVERTER_UNITS else "Валюта")
        elif self.current_mode == "Построение графиков":
            self._build_graphing_content()
        elif self.current_mode == "Программист":
            self._build_programmer_content()
        else:
            self._build_not_implemented_content(self.current_mode)

    def toggle_history(self):
        self.history_visible = not self.history_visible
        if self.history_visible:
            self.history_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(6, 0))
        else:
            self.history_frame.grid_forget()

    def _add_history_entry(self, expression: str, result: str):
        self.history.append((expression, result))
        if len(self.history) > 50:
            self.history.pop(0)
        self._refresh_history_ui()

    def _refresh_history_ui(self):
        for child in self.history_frame.winfo_children():
            child.destroy()
        if not self.history:
            ctk.CTkLabel(self.history_frame, text="Здесь появится история",
                         font=FONT_HIST_EXPR, text_color=self._c("history_expr_fg")).pack(pady=20)
            return
        for expression, result in reversed(self.history):
            item = ctk.CTkFrame(self.history_frame, fg_color="transparent")
            item.pack(fill="x", padx=6, pady=4)
            expr_lbl = ctk.CTkLabel(item, text=expression, font=FONT_HIST_EXPR,
                                    text_color=self._c("history_expr_fg"), anchor="e", justify="right")
            expr_lbl.pack(fill="x")
            res_lbl = ctk.CTkLabel(item, text=result, font=FONT_HIST_RESULT,
                                   text_color=self._c("history_result_fg"), anchor="e", justify="right")
            res_lbl.pack(fill="x")
            for widget in (item, expr_lbl, res_lbl):
                widget.bind("<Button-1>", lambda e, r=result: self._use_history_result(r))

    def _use_history_result(self, result: str):
        if self.current_mode not in ("Обычный", "Инженерный"):
            return
        self.current_value = result.replace(",", ".")
        self.reset_on_next_digit = True
        self._update_display()

    def _build_standard_content(self):
        self._build_display_area()
        self._build_mem_row()
        self._build_standard_grid()

    def _build_display_area(self):
        display_frame = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        display_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(5, 5))
        display_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.expr_var = ctk.StringVar(value="")
        self.expr_label = ctk.CTkLabel(display_frame, textvariable=self.expr_var, font=("Segoe UI", 14),
                                       text_color=self._c("history_expr_fg"), anchor="e", justify="right")
        self.expr_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        self.display_var = ctk.StringVar(value=self.current_value.replace(".", ","))
        self.display_label = ctk.CTkLabel(display_frame, textvariable=self.display_var, font=FONT_DISPLAY,
                                          text_color=self._c("display_fg"), anchor="e", justify="right")
        self.display_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

    def _build_mem_row(self):
        mem_frame = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        mem_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        for i in range(6):
            mem_frame.grid_columnconfigure(i, weight=1)
        self.mem_buttons = []
        mem_labels = ["MC", "MR", "M+", "M-", "MS", "M\u25BE"]
        for i, lbl in enumerate(mem_labels):
            cmd = self.show_about if lbl == "M\u25BE" else (lambda: None)
            b = ctk.CTkButton(mem_frame, text=lbl, font=FONT_MEM, fg_color="transparent",
                              hover_color=self._c("func_btn"), text_color=self._c("mem_row_fg"),
                              height=32, command=cmd)
            b.grid(row=0, column=i, sticky="ew", padx=2)
            self.mem_buttons.append(b)

    def _build_standard_grid(self):
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        btn_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        self.content_frame.grid_rowconfigure(2, weight=1)
        for i in range(4):
            btn_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):
            btn_frame.grid_rowconfigure(i, weight=1)

        layout = [
            ("%", 0, 0, lambda: self.on_special("percent"), "func"),
            ("CE", 0, 1, self.on_ce, "func"),
            ("C", 0, 2, self.on_c, "func"),
            ("\u232B", 0, 3, self.on_backspace, "func"),
            ("1/x", 1, 0, lambda: self.on_special("inv"), "func"),
            ("x\u00B2", 1, 1, lambda: self.on_special("sqr"), "func"),
            ("\u00B2\u221Ax", 1, 2, lambda: self.on_special("sqrt"), "func"),
            ("\u00F7", 1, 3, lambda: self.on_operator("/"), "func"),
            ("7", 2, 0, lambda: self.on_digit("7"), "num"),
            ("8", 2, 1, lambda: self.on_digit("8"), "num"),
            ("9", 2, 2, lambda: self.on_digit("9"), "num"),
            ("\u00D7", 2, 3, lambda: self.on_operator("*"), "func"),
            ("4", 3, 0, lambda: self.on_digit("4"), "num"),
            ("5", 3, 1, lambda: self.on_digit("5"), "num"),
            ("6", 3, 2, lambda: self.on_digit("6"), "num"),
            ("\u2212", 3, 3, lambda: self.on_operator("-"), "func"),
            ("1", 4, 0, lambda: self.on_digit("1"), "num"),
            ("2", 4, 1, lambda: self.on_digit("2"), "num"),
            ("3", 4, 2, lambda: self.on_digit("3"), "num"),
            ("+", 4, 3, lambda: self.on_operator("+"), "func"),
            ("\u207A\u2044\u208B", 5, 0, self.on_sign, "num"),
            ("0", 5, 1, lambda: self.on_digit("0"), "num"),
            (",", 5, 2, self.on_decimal, "num"),
            ("=", 5, 3, self.on_equals, "eq"),
        ]
        self._build_button_grid(btn_frame, layout)

    def _build_button_grid(self, parent, layout):
        """Общая утилита: создаёт кнопки из списка (текст,row,col,cmd,style) и красит их."""
        buttons = []
        for text, row, col, cmd, style in layout:
            btn = ctk.CTkButton(parent, text=text, font=FONT_BTN, corner_radius=6, command=cmd)
            btn.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
            buttons.append((btn, style))
        for btn, style in buttons:
            if style == "func":
                btn.configure(fg_color=self._c("func_btn"), hover_color=self._c("func_btn_hover"), text_color=self._c("display_fg"))
            elif style == "eq":
                btn.configure(fg_color=self._c("eq_btn"), hover_color=self._c("eq_btn_hover"), text_color=self._c("eq_fg"))
            else:
                btn.configure(fg_color=self._c("num_btn"), hover_color=self._c("num_btn_hover"), text_color=self._c("display_fg"))
        return buttons

    def _format(self, value: float) -> str:
        if value != value:
            return "Ошибка"
        if value in (float("inf"), float("-inf")):
            return "Ошибка"
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.10g}"

    def _update_display(self):
        self.display_var.set(self.current_value.replace(".", ","))

    def _op_symbol(self, op):
        return {"+": "+", "-": "\u2212", "*": "\u00D7", "/": "\u00F7",
                "^": "^", "%": "mod"}.get(op, op)

    def on_digit(self, d: str):
        if self.reset_on_next_digit or self.current_value == "0":
            self.current_value = d
            self.reset_on_next_digit = False
        else:
            if len(self.current_value.replace("-", "").replace(".", "")) >= 16:
                return
            self.current_value += d
        self._update_display()

    def on_decimal(self):
        if self.reset_on_next_digit:
            self.current_value = "0"
            self.reset_on_next_digit = False
        if "." not in self.current_value:
            self.current_value += "."
        self._update_display()

    def on_sign(self):
        try:
            self.current_value = self._format(-float(self.current_value))
            self._update_display()
        except ValueError:
            pass

    def on_backspace(self):
        if self.reset_on_next_digit:
            return
        if len(self.current_value) <= 1 or (len(self.current_value) == 2 and self.current_value.startswith("-")):
            self.current_value = "0"
        else:
            self.current_value = self.current_value[:-1]
        self._update_display()

    def on_c(self):
        self.current_value = "0"
        self.stored_value = None
        self.pending_op = None
        self.reset_on_next_digit = False
        self.expr_var.set("")
        self._update_display()

    def on_ce(self):
        self.current_value = "0"
        self.reset_on_next_digit = False
        self._update_display()

    def on_operator(self, op: str):
        if self.pending_op and not self.reset_on_next_digit:
            self.on_equals()
        self.stored_value = float(self.current_value)
        self.pending_op = op
        self.reset_on_next_digit = True
        self.expr_var.set(f"{self._format(self.stored_value)} {self._op_symbol(op)}".replace(".", ","))

    def on_equals(self):
        if self.pending_op is None or self.stored_value is None:
            return
        try:
            a = self.stored_value
            b = float(self.current_value)
            expression = (f"{self._format(a)} {self._op_symbol(self.pending_op)} {self._format(b)} =").replace(".", ",")

            if self.pending_op == "+":
                result = a + b
            elif self.pending_op == "-":
                result = a - b
            elif self.pending_op == "*":
                result = a * b
            elif self.pending_op == "/":
                result = a / b if b != 0 else float("nan")
            elif self.pending_op == "^":
                result = math.pow(a, b)
            elif self.pending_op == "%":
                result = math.fmod(a, b) if b != 0 else float("nan")
            else:
                result = b

            self.current_value = self._format(result)
            self.expr_var.set(expression)
            self._add_history_entry(expression, self.current_value.replace(".", ","))
        except (ValueError, ZeroDivisionError, OverflowError):
            self.current_value = "Ошибка"
        self.pending_op = None
        self.stored_value = None
        self.reset_on_next_digit = True
        self._update_display()

    def on_special(self, kind: str):
        try:
            val = float(self.current_value)
            ang = math.radians(val) if self.angle_unit == "deg" else val

            if kind == "percent":
                result, expr_text = val / 100, f"%({self._format(val)})"
            elif kind == "inv":
                result, expr_text = 1 / val, f"1/({self._format(val)})"
            elif kind == "sqr":
                result, expr_text = val * val, f"sqr({self._format(val)})"
            elif kind == "sqrt":
                result, expr_text = math.sqrt(val), f"\u221A({self._format(val)})"
            elif kind == "sin":
                result, expr_text = math.sin(ang), f"sin({self._format(val)})"
            elif kind == "cos":
                result, expr_text = math.cos(ang), f"cos({self._format(val)})"
            elif kind == "tan":
                result, expr_text = math.tan(ang), f"tan({self._format(val)})"
            elif kind == "log":
                result, expr_text = math.log10(val), f"log({self._format(val)})"
            elif kind == "ln":
                result, expr_text = math.log(val), f"ln({self._format(val)})"
            elif kind == "factorial":
                result, expr_text = float(math.factorial(int(val))), f"{self._format(val)}!"
            elif kind == "abs":
                result, expr_text = abs(val), f"|{self._format(val)}|"
            elif kind == "pi":
                result, expr_text = math.pi, "\u03C0"
            elif kind == "e":
                result, expr_text = math.e, "e"
            else:
                return

            self.current_value = self._format(result)
            expr_final = f"{expr_text} =".replace(".", ",")
            self.expr_var.set(expr_final)
            self._add_history_entry(expr_final, self.current_value.replace(".", ","))
        except (ValueError, ZeroDivisionError, OverflowError):
            self.current_value = "Ошибка"
        self.reset_on_next_digit = True
        self._update_display()

    def _build_engineering_content(self):
        self._build_display_area()

        sci_frame = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        sci_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))
        for i in range(4):
            sci_frame.grid_columnconfigure(i, weight=1)

        self.angle_toggle_btn = ctk.CTkButton(
            sci_frame, text="DEG" if self.angle_unit == "deg" else "RAD", font=FONT_BTN_SM,
            corner_radius=6, fg_color=self._c("func_btn"), hover_color=self._c("func_btn_hover"),
            text_color=self._c("display_fg"), command=self._toggle_angle_unit,
        )
        self.angle_toggle_btn.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        sci_layout_rest = [
            ("sin", 0, 1, lambda: self.on_special("sin"), "func"),
            ("cos", 0, 2, lambda: self.on_special("cos"), "func"),
            ("tan", 0, 3, lambda: self.on_special("tan"), "func"),
            ("log", 1, 0, lambda: self.on_special("log"), "func"),
            ("ln", 1, 1, lambda: self.on_special("ln"), "func"),
            ("\u03C0", 1, 2, lambda: self.on_special("pi"), "func"),
            ("e", 1, 3, lambda: self.on_special("e"), "func"),
            ("x\u02B8", 2, 0, lambda: self.on_operator("^"), "func"),
            ("n!", 2, 1, lambda: self.on_special("factorial"), "func"),
            ("|x|", 2, 2, lambda: self.on_special("abs"), "func"),
            ("mod", 2, 3, lambda: self.on_operator("%"), "func"),
        ]
        self._build_button_grid(sci_frame, sci_layout_rest)
        for i in range(3):
            sci_frame.grid_rowconfigure(i, weight=1)

        self._build_mem_row_at(row=2)
        self._build_standard_grid_at(row=3)

    def _toggle_angle_unit(self):
        self.angle_unit = "rad" if self.angle_unit == "deg" else "deg"
        self.angle_toggle_btn.configure(text="DEG" if self.angle_unit == "deg" else "RAD")

    def _build_mem_row_at(self, row):
        mem_frame = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        mem_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=(0, 5))
        for i in range(6):
            mem_frame.grid_columnconfigure(i, weight=1)
        self.mem_buttons = []
        mem_labels = ["MC", "MR", "M+", "M-", "MS", "M\u25BE"]
        for i, lbl in enumerate(mem_labels):
            cmd = self.show_about if lbl == "M\u25BE" else (lambda: None)
            b = ctk.CTkButton(mem_frame, text=lbl, font=FONT_MEM, fg_color="transparent",
                              hover_color=self._c("func_btn"), text_color=self._c("mem_row_fg"),
                              height=30, command=cmd)
            b.grid(row=0, column=i, sticky="ew", padx=2)
            self.mem_buttons.append(b)

    def _build_standard_grid_at(self, row):
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        btn_frame.grid(row=row, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.content_frame.grid_rowconfigure(row, weight=1)
        for i in range(4):
            btn_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):
            btn_frame.grid_rowconfigure(i, weight=1)

        layout = [
            ("%", 0, 0, lambda: self.on_special("percent"), "func"),
            ("CE", 0, 1, self.on_ce, "func"),
            ("C", 0, 2, self.on_c, "func"),
            ("\u232B", 0, 3, self.on_backspace, "func"),
            ("1/x", 1, 0, lambda: self.on_special("inv"), "func"),
            ("x\u00B2", 1, 1, lambda: self.on_special("sqr"), "func"),
            ("\u00B2\u221Ax", 1, 2, lambda: self.on_special("sqrt"), "func"),
            ("\u00F7", 1, 3, lambda: self.on_operator("/"), "func"),
            ("7", 2, 0, lambda: self.on_digit("7"), "num"),
            ("8", 2, 1, lambda: self.on_digit("8"), "num"),
            ("9", 2, 2, lambda: self.on_digit("9"), "num"),
            ("\u00D7", 2, 3, lambda: self.on_operator("*"), "func"),
            ("4", 3, 0, lambda: self.on_digit("4"), "num"),
            ("5", 3, 1, lambda: self.on_digit("5"), "num"),
            ("6", 3, 2, lambda: self.on_digit("6"), "num"),
            ("\u2212", 3, 3, lambda: self.on_operator("-"), "func"),
            ("1", 4, 0, lambda: self.on_digit("1"), "num"),
            ("2", 4, 1, lambda: self.on_digit("2"), "num"),
            ("3", 4, 2, lambda: self.on_digit("3"), "num"),
            ("+", 4, 3, lambda: self.on_operator("+"), "func"),
            ("\u207A\u2044\u208B", 5, 0, self.on_sign, "num"),
            ("0", 5, 1, lambda: self.on_digit("0"), "num"),
            (",", 5, 2, self.on_decimal, "num"),
            ("=", 5, 3, self.on_equals, "eq"),
        ]
        self._build_button_grid(btn_frame, layout)

    def _build_date_content(self):
        wrap = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        wrap.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.date_sub_mode = getattr(self, "date_sub_mode", "diff")

        tabs = ctk.CTkFrame(wrap, fg_color=self._c("func_btn"), corner_radius=8)
        tabs.pack(fill="x", pady=(0, 16))
        self.date_tab_diff_btn = ctk.CTkButton(
            tabs, text="Разница дат", corner_radius=6,
            fg_color=self._c("eq_btn") if self.date_sub_mode == "diff" else "transparent",
            text_color=self._c("eq_fg") if self.date_sub_mode == "diff" else self._c("display_fg"),
            hover_color=self._c("func_btn_hover"),
            command=lambda: self._set_date_sub_mode("diff"),
        )
        self.date_tab_diff_btn.pack(side="left", expand=True, fill="x", padx=3, pady=3)
        self.date_tab_addsub_btn = ctk.CTkButton(
            tabs, text="Добавить/вычесть дни", corner_radius=6,
            fg_color=self._c("eq_btn") if self.date_sub_mode == "addsub" else "transparent",
            text_color=self._c("eq_fg") if self.date_sub_mode == "addsub" else self._c("display_fg"),
            hover_color=self._c("func_btn_hover"),
            command=lambda: self._set_date_sub_mode("addsub"),
        )
        self.date_tab_addsub_btn.pack(side="left", expand=True, fill="x", padx=3, pady=3)

        self.date_body = ctk.CTkFrame(wrap, fg_color=self._c("bg"))
        self.date_body.pack(fill="both", expand=True)

        if self.date_sub_mode == "diff":
            self._build_date_diff_ui()
        else:
            self._build_date_addsub_ui()

    def _set_date_sub_mode(self, mode):
        self.date_sub_mode = mode
        self._clear_content()
        self._build_date_content()

    def _date_row(self, parent, label_text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=6)
        ctk.CTkLabel(row, text=label_text, font=("Segoe UI", 13), text_color=self._c("history_expr_fg"),
                    width=90, anchor="w").pack(side="left")
        today = datetime.date.today()
        d_var = ctk.StringVar(value=str(today.day))
        m_var = ctk.StringVar(value=str(today.month))
        y_var = ctk.StringVar(value=str(today.year))
        for var, width, ph in ((d_var, 45, "ДД"), (m_var, 45, "ММ"), (y_var, 65, "ГГГГ")):
            e = ctk.CTkEntry(row, textvariable=var, width=width, placeholder_text=ph,
                             fg_color=self._c("entry_bg"), border_color=self._c("border"),
                             text_color=self._c("display_fg"))
            e.pack(side="left", padx=3)
        return d_var, m_var, y_var

    def _build_date_diff_ui(self):
        self.date_start_vars = self._date_row(self.date_body, "От:")
        self.date_end_vars = self._date_row(self.date_body, "До:")

        self.date_result_label = ctk.CTkLabel(
            self.date_body, text="", font=("Segoe UI", 16, "bold"),
            text_color=self._c("display_fg"), justify="center",
        )
        self.date_result_label.pack(pady=(20, 10))

        ctk.CTkButton(
            self.date_body, text="Вычислить", fg_color=self._c("eq_btn"),
            hover_color=self._c("eq_btn_hover"), text_color=self._c("eq_fg"),
            command=self._compute_date_diff,
        ).pack(pady=6)

    def _compute_date_diff(self):
        try:
            d1, m1, y1 = (int(v.get()) for v in self.date_start_vars)
            d2, m2, y2 = (int(v.get()) for v in self.date_end_vars)
            date1 = datetime.date(y1, m1, d1)
            date2 = datetime.date(y2, m2, d2)
            delta = (date2 - date1).days
            self.date_result_label.configure(
                text=f"{abs(delta)} дн.\n({delta} дней от первой даты ко второй)"
            )
        except (ValueError, TypeError):
            self.date_result_label.configure(text="Проверьте корректность введённых дат")

    def _build_date_addsub_ui(self):
        self.date_base_vars = self._date_row(self.date_body, "Дата:")

        op_row = ctk.CTkFrame(self.date_body, fg_color="transparent")
        op_row.pack(fill="x", pady=6)
        self.date_op_var = ctk.StringVar(value="+")
        ctk.CTkLabel(op_row, text="Действие:", font=("Segoe UI", 13),
                    text_color=self._c("history_expr_fg"), width=90, anchor="w").pack(side="left")
        ctk.CTkOptionMenu(op_row, variable=self.date_op_var, values=["+", "-"], width=70,
                          fg_color=self._c("func_btn"), button_color=self._c("func_btn"),
                          button_hover_color=self._c("func_btn_hover")).pack(side="left", padx=3)

        days_row = ctk.CTkFrame(self.date_body, fg_color="transparent")
        days_row.pack(fill="x", pady=6)
        ctk.CTkLabel(days_row, text="Кол-во дней:", font=("Segoe UI", 13),
                    text_color=self._c("history_expr_fg"), width=90, anchor="w").pack(side="left")
        self.date_days_var = ctk.StringVar(value="0")
        ctk.CTkEntry(days_row, textvariable=self.date_days_var, width=90,
                    fg_color=self._c("entry_bg"), border_color=self._c("border"),
                    text_color=self._c("display_fg")).pack(side="left", padx=3)

        self.date_result_label2 = ctk.CTkLabel(
            self.date_body, text="", font=("Segoe UI", 16, "bold"),
            text_color=self._c("display_fg"), justify="center",
        )
        self.date_result_label2.pack(pady=(20, 10))

        ctk.CTkButton(
            self.date_body, text="Вычислить", fg_color=self._c("eq_btn"),
            hover_color=self._c("eq_btn_hover"), text_color=self._c("eq_fg"),
            command=self._compute_date_addsub,
        ).pack(pady=6)

    def _compute_date_addsub(self):
        try:
            d1, m1, y1 = (int(v.get()) for v in self.date_base_vars)
            base = datetime.date(y1, m1, d1)
            n_days = int(self.date_days_var.get())
            delta = datetime.timedelta(days=n_days)
            result = base + delta if self.date_op_var.get() == "+" else base - delta
            weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
            self.date_result_label2.configure(
                text=f"{result.strftime('%d.%m.%Y')}\n({weekdays[result.weekday()]})"
            )
        except (ValueError, TypeError):
            self.date_result_label2.configure(text="Проверьте корректность введённых данных")

    def _build_converter_content(self, category: str):
        if category not in CONVERTER_UNITS and category != "Температура":
            category = "Валюта"

        wrap = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        wrap.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.content_frame.grid_rowconfigure(0, weight=1)

        cat_row = ctk.CTkFrame(wrap, fg_color="transparent")
        cat_row.pack(fill="x", pady=(0, 16))
        self.converter_category_var = ctk.StringVar(value=category)
        ctk.CTkOptionMenu(
            cat_row, variable=self.converter_category_var,
            values=self.converter_categories, width=200,
            fg_color=self._c("func_btn"), button_color=self._c("func_btn"),
            button_hover_color=self._c("func_btn_hover"),
            command=self._on_converter_category_change,
        ).pack(fill="x")

        if category == "Валюта":
            note = ctk.CTkLabel(
                wrap, text="Курсы приблизительные и заданы статически в коде,\nне используются для реальных операций.",
                font=("Segoe UI", 11), text_color=self._c("history_expr_fg"), justify="center",
            )
            note.pack(pady=(0, 10))
            self.converter_currency_note = note
        else:
            self.converter_currency_note = None

        units = TEMPERATURE_UNITS if category == "Температура" else list(CONVERTER_UNITS[category].keys())

        from_row = ctk.CTkFrame(wrap, fg_color="transparent")
        from_row.pack(fill="x", pady=6)
        self.converter_from_var = ctk.StringVar(value="1")
        self.converter_from_unit_var = ctk.StringVar(value=units[0])
        entry_from = ctk.CTkEntry(from_row, textvariable=self.converter_from_var, width=110,
                                  fg_color=self._c("entry_bg"), border_color=self._c("border"),
                                  text_color=self._c("display_fg"), font=("Segoe UI", 16))
        entry_from.pack(side="left", padx=(0, 6))
        ctk.CTkOptionMenu(from_row, variable=self.converter_from_unit_var, values=units, width=120,
                          fg_color=self._c("func_btn"), button_color=self._c("func_btn"),
                          button_hover_color=self._c("func_btn_hover"),
                          command=lambda _=None: self._recompute_converter()).pack(side="left")

        swap_row = ctk.CTkFrame(wrap, fg_color="transparent")
        swap_row.pack(fill="x", pady=2)
        ctk.CTkButton(swap_row, text="\u21C5", width=40, fg_color=self._c("func_btn"),
                     hover_color=self._c("func_btn_hover"), text_color=self._c("display_fg"),
                     command=self._swap_converter_units).pack()

        to_row = ctk.CTkFrame(wrap, fg_color="transparent")
        to_row.pack(fill="x", pady=6)
        self.converter_to_var = ctk.StringVar(value="")
        self.converter_to_unit_var = ctk.StringVar(value=units[1] if len(units) > 1 else units[0])
        entry_to = ctk.CTkEntry(to_row, textvariable=self.converter_to_var, width=110, state="disabled",
                                fg_color=self._c("entry_bg"), border_color=self._c("border"),
                                text_color=self._c("display_fg"), font=("Segoe UI", 16))
        entry_to.pack(side="left", padx=(0, 6))
        ctk.CTkOptionMenu(to_row, variable=self.converter_to_unit_var, values=units, width=120,
                          fg_color=self._c("func_btn"), button_color=self._c("func_btn"),
                          button_hover_color=self._c("func_btn_hover"),
                          command=lambda _=None: self._recompute_converter()).pack(side="left")

        self.converter_from_var.trace_add("write", lambda *a: self._recompute_converter())
        self._recompute_converter()

    def _on_converter_category_change(self, category):
        self.mode_label.configure(text=f"Конвертер \u2014 {category}")
        self._clear_content()
        self._build_converter_content(category)

    def _swap_converter_units(self):
        f, t = self.converter_from_unit_var.get(), self.converter_to_unit_var.get()
        self.converter_from_unit_var.set(t)
        self.converter_to_unit_var.set(f)
        self._recompute_converter()

    def _recompute_converter(self):
        try:
            value = float(self.converter_from_var.get().replace(",", "."))
            category = self.converter_category_var.get()
            fu, tu = self.converter_from_unit_var.get(), self.converter_to_unit_var.get()

            if category == "Температура":
                result = convert_temperature(value, fu, tu)
            else:
                table = CONVERTER_UNITS[category]
                base = value * table[fu]
                result = base / table[tu]

            self.converter_to_var.set(self._format(result))
        except (ValueError, KeyError, ZeroDivisionError):
            self.converter_to_var.set("")

    _GRAPH_SAFE_NAMES = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
        "abs": abs, "pi": math.pi, "e": math.e, "pow": pow,
        "exp": math.exp,
    }

    def _build_graphing_content(self):
        if not MATPLOTLIB_AVAILABLE:
            wrap = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
            wrap.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.content_frame.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(
                wrap, text="Для графиков нужен пакет matplotlib",
                font=("Segoe UI", 16, "bold"), text_color=self._c("display_fg"),
            ).pack(pady=(60, 10))
            ctk.CTkLabel(
                wrap, text="Установите его командой:\npip install matplotlib\nи перезапустите программу.",
                font=("Segoe UI", 13), text_color=self._c("history_expr_fg"), justify="center",
            ).pack()
            return

        wrap = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        wrap.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.content_frame.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(2, weight=1)

        fn_row = ctk.CTkFrame(wrap, fg_color="transparent")
        fn_row.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        fn_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(fn_row, text="y =", font=("Segoe UI", 14),
                    text_color=self._c("display_fg")).grid(row=0, column=0, padx=(0, 6))
        self.graph_fn_var = ctk.StringVar(value="sin(x)")
        entry = ctk.CTkEntry(fn_row, textvariable=self.graph_fn_var,
                             fg_color=self._c("entry_bg"), border_color=self._c("border"),
                             text_color=self._c("display_fg"), font=("Segoe UI", 14))
        entry.grid(row=0, column=1, sticky="ew")
        entry.bind("<Return>", lambda e: self._plot_graph())

        range_row = ctk.CTkFrame(wrap, fg_color="transparent")
        range_row.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(range_row, text="X от", font=("Segoe UI", 13),
                    text_color=self._c("history_expr_fg")).pack(side="left")
        self.graph_xmin_var = ctk.StringVar(value="-10")
        ctk.CTkEntry(range_row, textvariable=self.graph_xmin_var, width=60,
                    fg_color=self._c("entry_bg"), border_color=self._c("border"),
                    text_color=self._c("display_fg")).pack(side="left", padx=4)
        ctk.CTkLabel(range_row, text="до", font=("Segoe UI", 13),
                    text_color=self._c("history_expr_fg")).pack(side="left")
        self.graph_xmax_var = ctk.StringVar(value="10")
        ctk.CTkEntry(range_row, textvariable=self.graph_xmax_var, width=60,
                    fg_color=self._c("entry_bg"), border_color=self._c("border"),
                    text_color=self._c("display_fg")).pack(side="left", padx=4)
        ctk.CTkButton(range_row, text="Построить", fg_color=self._c("eq_btn"),
                     hover_color=self._c("eq_btn_hover"), text_color=self._c("eq_fg"),
                     command=self._plot_graph).pack(side="left", padx=(10, 0))

        plot_area = ctk.CTkFrame(wrap, fg_color=self._c("bg"))
        plot_area.grid(row=2, column=0, sticky="nsew")
        self.graph_plot_area = plot_area

        self.graph_error_label = ctk.CTkLabel(
            wrap, text="", font=("Segoe UI", 12), text_color="#ff6b6b",
        )
        self.graph_error_label.grid(row=3, column=0, sticky="w", pady=(4, 0))

        self._plot_graph()

    def _safe_eval_fn(self, expr: str, x_val: float):
        names = dict(self._GRAPH_SAFE_NAMES)
        names["x"] = x_val
        return eval(expr, {"__builtins__": {}}, names)

    def _plot_graph(self):
        if not MATPLOTLIB_AVAILABLE:
            return
        for child in self.graph_plot_area.winfo_children():
            child.destroy()
        self.graph_error_label.configure(text="")

        try:
            x_min = float(self.graph_xmin_var.get())
            x_max = float(self.graph_xmax_var.get())
            if x_min >= x_max:
                raise ValueError("X от должно быть меньше X до")

            n_points = 400
            step = (x_max - x_min) / n_points
            xs, ys = [], []
            expr = self.graph_fn_var.get()
            for i in range(n_points + 1):
                xv = x_min + i * step
                try:
                    yv = self._safe_eval_fn(expr, xv)
                    if isinstance(yv, complex):
                        yv = float("nan")
                except (ValueError, ZeroDivisionError, OverflowError):
                    yv = float("nan")
                xs.append(xv)
                ys.append(yv)

            is_dark = self.theme_name == "dark"
            fig = Figure(figsize=(4, 3), dpi=100)
            fig.patch.set_facecolor(self._c("bg"))
            ax = fig.add_subplot(111)
            ax.set_facecolor(self._c("bg"))
            line_color = self._c("eq_btn")
            text_color = self._c("display_fg")
            ax.plot(xs, ys, color=line_color, linewidth=2)
            ax.axhline(0, color=self._c("history_expr_fg"), linewidth=0.8)
            ax.axvline(0, color=self._c("history_expr_fg"), linewidth=0.8)
            ax.tick_params(colors=text_color, labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(self._c("history_expr_fg"))
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_plot_area)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as exc:
            self.graph_error_label.configure(text=f"Ошибка в функции: {exc}")

    _PROG_WORD_BITS = {"BYTE": 8, "WORD": 16, "DWORD": 32, "QWORD": 64}

    def _build_programmer_content(self):
        self.prog_value = getattr(self, "prog_value", 0)
        self.prog_base = getattr(self, "prog_base", "DEC")
        self.prog_word = getattr(self, "prog_word", "DWORD")
        self.prog_pending_op = None
        self.prog_stored = None
        self.prog_reset_next = False

        wrap = ctk.CTkFrame(self.content_frame, fg_color=self._c("bg"))
        wrap.grid(row=0, column=0, sticky="nsew", padx=10, pady=(5, 5))
        self.content_frame.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        self.prog_display_var = ctk.StringVar(value="0")
        ctk.CTkLabel(
            wrap, textvariable=self.prog_display_var, font=FONT_DISPLAY,
            text_color=self._c("display_fg"), anchor="e", justify="right",
        ).pack(fill="x", padx=10, pady=(6, 4))

        reprs_frame = ctk.CTkFrame(wrap, fg_color=self._c("func_btn"), corner_radius=8)
        reprs_frame.pack(fill="x", padx=4, pady=(0, 8))
        self.prog_repr_vars = {}
        for base in ("HEX", "DEC", "OCT", "BIN"):
            row = ctk.CTkFrame(reprs_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row, text=base, width=40, font=("Segoe UI", 12),
                        text_color=self._c("history_expr_fg"), anchor="w").pack(side="left")
            var = ctk.StringVar(value="0")
            ctk.CTkLabel(row, textvariable=var, font=("Segoe UI", 13),
                        text_color=self._c("display_fg"), anchor="e").pack(side="right")
            self.prog_repr_vars[base] = var

        word_row = ctk.CTkFrame(wrap, fg_color="transparent")
        word_row.pack(fill="x", pady=(0, 6))
        self.prog_word_var = ctk.StringVar(value=self.prog_word)
        ctk.CTkOptionMenu(
            word_row, variable=self.prog_word_var, values=list(self._PROG_WORD_BITS.keys()),
            width=110, fg_color=self._c("func_btn"), button_color=self._c("func_btn"),
            button_hover_color=self._c("func_btn_hover"), command=self._on_prog_word_change,
        ).pack(side="left")

        base_row = ctk.CTkFrame(wrap, fg_color="transparent")
        base_row.pack(fill="x", pady=(0, 8))
        self.prog_base_buttons = {}
        for base in ("HEX", "DEC", "OCT", "BIN"):
            b = ctk.CTkButton(
                base_row, text=base, width=60, corner_radius=6,
                fg_color=self._c("eq_btn") if base == self.prog_base else self._c("func_btn"),
                text_color=self._c("eq_fg") if base == self.prog_base else self._c("display_fg"),
                hover_color=self._c("func_btn_hover"),
                command=lambda b=base: self._set_prog_base(b),
            )
            b.pack(side="left", padx=2, expand=True, fill="x")
            self.prog_base_buttons[base] = b

        bit_ops_frame = ctk.CTkFrame(wrap, fg_color="transparent")
        bit_ops_frame.pack(fill="x", pady=(0, 6))
        for i in range(4):
            bit_ops_frame.grid_columnconfigure(i, weight=1)
        bit_ops_layout = [
            ("AND", 0, 0, lambda: self._prog_operator("AND"), "func"),
            ("OR", 0, 1, lambda: self._prog_operator("OR"), "func"),
            ("XOR", 0, 2, lambda: self._prog_operator("XOR"), "func"),
            ("NOT", 0, 3, self._prog_not, "func"),
            ("<<", 1, 0, lambda: self._prog_operator("LSH"), "func"),
            (">>", 1, 1, lambda: self._prog_operator("RSH"), "func"),
            ("MOD", 1, 2, lambda: self._prog_operator("MOD"), "func"),
        ]
        self._build_button_grid(bit_ops_frame, bit_ops_layout)
        for i in range(2):
            bit_ops_frame.grid_rowconfigure(i, weight=1)

        keys_frame = ctk.CTkFrame(wrap, fg_color=self._c("bg"))
        keys_frame.pack(fill="both", expand=True)
        for i in range(4):
            keys_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):
            keys_frame.grid_rowconfigure(i, weight=1)

        keys_layout = [
            ("A", 0, 0, lambda: self._prog_digit("A"), "num", True),
            ("B", 0, 1, lambda: self._prog_digit("B"), "num", True),
            ("C", 0, 2, lambda: self._prog_digit("C"), "num", True),
            ("D", 0, 3, lambda: self._prog_digit("D"), "num", True),

            ("E", 1, 0, lambda: self._prog_digit("E"), "num", True),
            ("F", 1, 1, lambda: self._prog_digit("F"), "num", True),
            ("\u232B", 1, 2, self._prog_backspace, "func", False),
            ("CE", 1, 3, self._prog_clear, "func", False),

            ("7", 2, 0, lambda: self._prog_digit("7"), "num", True),
            ("8", 2, 1, lambda: self._prog_digit("8"), "num", True),
            ("9", 2, 2, lambda: self._prog_digit("9"), "num", True),
            ("\u00F7", 2, 3, lambda: self._prog_operator("DIV"), "func", False),

            ("4", 3, 0, lambda: self._prog_digit("4"), "num", True),
            ("5", 3, 1, lambda: self._prog_digit("5"), "num", True),
            ("6", 3, 2, lambda: self._prog_digit("6"), "num", True),
            ("\u00D7", 3, 3, lambda: self._prog_operator("MUL"), "func", False),

            ("1", 4, 0, lambda: self._prog_digit("1"), "num", True),
            ("2", 4, 1, lambda: self._prog_digit("2"), "num", True),
            ("3", 4, 2, lambda: self._prog_digit("3"), "num", True),
            ("\u2212", 4, 3, lambda: self._prog_operator("SUB"), "func", False),

            ("\u00B1", 5, 0, self._prog_sign, "func", False),
            ("0", 5, 1, lambda: self._prog_digit("0"), "num", True),
            ("+", 5, 2, lambda: self._prog_operator("ADD"), "func", False),
            ("=", 5, 3, self._prog_equals, "eq", False),
        ]

        self.prog_hex_buttons = {}
        for text, row, col, cmd, style, is_hex_digit in keys_layout:
            btn = ctk.CTkButton(keys_frame, text=text, font=FONT_BTN, corner_radius=6, command=cmd)
            btn.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
            self._style_single_button(btn, style)
            if is_hex_digit:
                self.prog_hex_buttons[text] = btn

        self._prog_update_key_states()
        self._prog_refresh_display()

    def _style_single_button(self, btn, style):
        if style == "func":
            btn.configure(fg_color=self._c("func_btn"), hover_color=self._c("func_btn_hover"), text_color=self._c("display_fg"))
        elif style == "eq":
            btn.configure(fg_color=self._c("eq_btn"), hover_color=self._c("eq_btn_hover"), text_color=self._c("eq_fg"))
        else:
            btn.configure(fg_color=self._c("num_btn"), hover_color=self._c("num_btn_hover"), text_color=self._c("display_fg"))

    def _prog_mask(self):
        bits = self._PROG_WORD_BITS[self.prog_word]
        return (1 << bits) - 1

    def _prog_apply_mask(self, value: int) -> int:
        mask = self._prog_mask()
        value &= mask
        bits = self._PROG_WORD_BITS[self.prog_word]
        if value >= (1 << (bits - 1)):
            return value - (1 << bits)
        return value

    def _on_prog_word_change(self, word):
        self.prog_word = word
        self.prog_value = self._prog_apply_mask(self.prog_value)
        self._prog_update_key_states()
        self._prog_refresh_display()

    def _set_prog_base(self, base):
        self.prog_base = base
        for b, btn in self.prog_base_buttons.items():
            btn.configure(
                fg_color=self._c("eq_btn") if b == base else self._c("func_btn"),
                text_color=self._c("eq_fg") if b == base else self._c("display_fg"),
            )
        self._prog_update_key_states()
        self._prog_refresh_display()

    def _prog_update_key_states(self):
        allowed_digits = {
            "BIN": set("01"),
            "OCT": set("01234567"),
            "DEC": set("0123456789"),
            "HEX": set("0123456789ABCDEF"),
        }[self.prog_base]
        for key, btn in self.prog_hex_buttons.items():
            enabled = key in allowed_digits
            btn.configure(state="normal" if enabled else "disabled")

    def _prog_digit(self, d: str):
        base_map = {"BIN": 2, "OCT": 8, "DEC": 10, "HEX": 16}
        base = base_map[self.prog_base]
        current = 0 if self.prog_reset_next else self.prog_value
        if self.prog_reset_next:
            self.prog_reset_next = False
        cur_str = self._int_to_base(current if current >= 0 else current, base).lstrip("-")
        if cur_str == "0":
            cur_str = ""
        new_str = cur_str + d
        try:
            self.prog_value = int(new_str, base)
        except ValueError:
            return
        self.prog_value = self._prog_apply_mask(self.prog_value)
        self._prog_refresh_display()

    def _int_to_base(self, value: int, base: int) -> str:
        if base == 10:
            return str(value)
        neg = value < 0
        value = abs(value)
        digits = "0123456789ABCDEF"
        if value == 0:
            s = "0"
        else:
            s = ""
            while value:
                s = digits[value % base] + s
                value //= base
        return ("-" + s) if neg else s

    def _prog_refresh_display(self):
        base_map = {"BIN": 2, "OCT": 8, "DEC": 10, "HEX": 16}
        self.prog_display_var.set(self._int_to_base(self.prog_value, base_map[self.prog_base]))
        mask = self._prog_mask()
        unsigned = self.prog_value & mask
        self.prog_repr_vars["HEX"].set(self._int_to_base(unsigned, 16))
        self.prog_repr_vars["DEC"].set(str(self.prog_value))
        self.prog_repr_vars["OCT"].set(self._int_to_base(unsigned, 8))
        self.prog_repr_vars["BIN"].set(self._int_to_base(unsigned, 2))

    def _prog_clear(self):
        self.prog_value = 0
        self.prog_stored = None
        self.prog_pending_op = None
        self.prog_reset_next = False
        self._prog_refresh_display()

    def _prog_backspace(self):
        base_map = {"BIN": 2, "OCT": 8, "DEC": 10, "HEX": 16}
        base = base_map[self.prog_base]
        s = self._int_to_base(self.prog_value, base)
        neg = s.startswith("-")
        digits = s.lstrip("-")
        digits = digits[:-1] if len(digits) > 1 else "0"
        s = ("-" + digits) if neg and digits != "0" else digits
        self.prog_value = int(s, base)
        self._prog_refresh_display()

    def _prog_sign(self):
        self.prog_value = self._prog_apply_mask(-self.prog_value)
        self._prog_refresh_display()

    def _prog_not(self):
        self.prog_value = self._prog_apply_mask(~self.prog_value)
        self._prog_refresh_display()

    def _prog_operator(self, op: str):
        if self.prog_pending_op and not self.prog_reset_next:
            self._prog_equals()
        self.prog_stored = self.prog_value
        self.prog_pending_op = op
        self.prog_reset_next = True

    def _prog_equals(self):
        if self.prog_pending_op is None or self.prog_stored is None:
            return
        a, b = self.prog_stored, self.prog_value
        op = self.prog_pending_op
        try:
            if op == "AND":
                result = a & b
            elif op == "OR":
                result = a | b
            elif op == "XOR":
                result = a ^ b
            elif op == "LSH":
                result = a << b
            elif op == "RSH":
                result = a >> b
            elif op == "MOD":
                result = a % b if b != 0 else 0
            elif op == "ADD":
                result = a + b
            elif op == "SUB":
                result = a - b
            elif op == "MUL":
                result = a * b
            elif op == "DIV":
                result = a // b if b != 0 else 0
            else:
                result = b
            self.prog_value = self._prog_apply_mask(result)
        except (ValueError, OverflowError):
            self.prog_value = 0
        self.prog_pending_op = None
        self.prog_stored = None
        self.prog_reset_next = True
        self._prog_refresh_display()


if __name__ == "__main__":
    if "--version" in sys.argv or "-v" in sys.argv:
        print(f"{APP_PRODUCT} v{APP_VERSION}")
        print(f"Компания: {APP_COMPANY}")
        sys.exit(0)

    app = WindowsStyleCalculator()
    app.mainloop()
