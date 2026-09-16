#Pydroid run kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from datetime import datetime

import json
import os

DATA_FILE = "taxi_data.json"
CONFIG_FILE = "taxi_config.json"

BG = get_color_from_hex("#1e1e2e")
CARD = get_color_from_hex("#2a2a3c")
ACCENT = get_color_from_hex("#f9a825")
TEXT = get_color_from_hex("#ffffff")
MUTED = get_color_from_hex("#b0b0c0")
OK = get_color_from_hex("#43a047")
WARN = get_color_from_hex("#e53935")

Window.clearcolor = BG


def pf(s, default=0.0):
    try:
        return float(str(s).replace(",", ".").strip())
    except (ValueError, TypeError):
        return default


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def parse_date(s):
    try:
        return datetime.strptime(str(s).strip(), "%d.%m.%Y")
    except (ValueError, TypeError):
        return None


class Root(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", spacing=dp(4), padding=dp(4), **kw)

        self.records = load_json(DATA_FILE, [])
        if not isinstance(self.records, list):
            self.records = []

        self.cfg = load_json(CONFIG_FILE, None)
        if not isinstance(self.cfg, dict):
            self.cfg = {"tank": 50.0, "norm": 8.5, "current_fuel": 50.0,
                        "last_price": 62.50}
            save_json(CONFIG_FILE, self.cfg)
        if "last_price" not in self.cfg:
            self.cfg["last_price"] = 62.50
            save_json(CONFIG_FILE, self.cfg)

        self.add_widget(Label(
            text="Учёт таксиста v3",
            size_hint_y=None, height=dp(32),
            color=ACCENT, font_size=dp(19), bold=True,
        ))

        self.status = Label(
            text="", size_hint_y=None, height=dp(20),
            color=MUTED, font_size=dp(11),
        )
        self.add_widget(self.status)

        self.body = BoxLayout(orientation="vertical")
        self.add_widget(self.body)

        self.bottom = Label(
            text="", size_hint_y=None, height=dp(24),
            color=TEXT, font_size=dp(12),
        )
        self.add_widget(self.bottom)

        self.refresh()
        self.show_menu()

    def refresh(self):
        c = self.cfg
        self.status.text = (f"Бак {c['tank']:.0f} | "
                            f"сейчас {c['current_fuel']:.1f} | "
                            f"норма {c['norm']:.1f} | "
                            f"цена {c.get('last_price', 62.5):.2f}")
        if self.records:
            km = sum(r.get("mileage", 0) for r in self.records)
            self.bottom.text = f"Смен: {len(self.records)} | Пробег: {km:.0f} км"
        else:
            self.bottom.text = "Записей пока нет"

    def set_body(self, w):
        self.body.clear_widgets()
        self.body.add_widget(w)

    def mk_input(self, hint="", text=""):
        return TextInput(
            hint_text=hint, text=text, multiline=False,
            background_color=CARD, foreground_color=TEXT,
            hint_text_color=MUTED, cursor_color=ACCENT,
            padding=[dp(10), dp(10), dp(10), dp(10)],
            font_size=dp(16), size_hint_y=None, height=dp(48),
        )

    def mk_label(self, text, size=13, color=None, bold=False, height=None):
        lbl = Label(
            text=text, font_size=dp(size), bold=bold,
            color=color or TEXT,
            size_hint_y=None, halign="left", valign="middle",
        )
        lbl.height = dp(height) if height else dp(size + 12)
        lbl.bind(width=lambda *_: setattr(lbl, "text_size", (lbl.width - dp(8), None)))
        return lbl

    def mk_top_bar(self, title):
        bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(4))
        back = Button(
            text="← НАЗАД", background_normal="",
            background_color=CARD, color=TEXT,
            font_size=dp(15), bold=True, size_hint=(0.35, 1),
        )
        back.bind(on_press=self.show_menu)
        bar.add_widget(back)
        bar.add_widget(Label(
            text=title, color=ACCENT,
            font_size=dp(16), bold=True, size_hint=(0.65, 1),
        ))
        return bar

    def mk_big_button(self, text, color, cb):
        b = Button(
            text=text, background_normal="",
            background_color=color,
            color=(0, 0, 0, 1) if color != CARD else TEXT,
            font_size=dp(18), bold=True,
        )
        b.bind(on_press=cb)
        return b

    def show_menu(self, *args):
        menu = GridLayout(cols=3, rows=3, spacing=dp(12),
                          padding=dp(10), size_hint=(1, 1))
        buttons = [
            ("Заправка", ACCENT, self.show_refuel),
            ("Записи", CARD, self.show_records),
            ("ИТОГИ", ACCENT, self.show_totals),
            ("Статистика", CARD, self.show_stats),
            ("Смена", OK, self.show_shift),
            ("Период", CARD, self.show_period),
            ("Настройки", CARD, self.show_settings),
            ("Экспорт", CARD, self.show_export),
            ("Удалить", WARN, self.show_delete),
        ]
        for t, c, cb in buttons:
            menu.add_widget(self.mk_big_button(t, c, cb))
        self.set_body(menu)

    def show_totals(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Итоги"))
        if not self.records:
            box = BoxLayout(orientation="vertical", padding=dp(20))
            box.add_widget(self.mk_label("Записей нет", size=16,
                                         color=MUTED, height=60))
            main.add_widget(box)
            self.set_body(main)
            return
        te = sum(r.get("earnings", 0) for r in self.records)
        td = sum(r.get("dispatcher", 0) for r in self.records)
        tf = sum(r.get("fuel_cost", 0) for r in self.records)
        tc = td + tf
        tn = sum(r.get("net", 0) for r in self.records)
        tk = sum(r.get("mileage", 0) for r in self.records)
        scroll = ScrollView()
        box = BoxLayout(orientation="vertical", spacing=dp(10),
                        size_hint_y=None, padding=dp(10))
        box.bind(minimum_height=box.setter("height"))
        box.add_widget(self.mk_label("ЧИСТАЯ ПРИБЫЛЬ", size=14,
                                     color=MUTED, height=22))
        box.add_widget(self.mk_label(f"{tn:.0f} руб.", size=40,
                                     bold=True, color=OK, height=60))
        box.add_widget(self.mk_label("РАСХОДЫ", size=14,
                                     color=MUTED, height=22))
        box.add_widget(self.mk_label(f"{tc:.0f} руб.", size=30,
                                     bold=True, color=WARN, height=50))
        details = (f"Заработано: {te:.0f} руб.\n\n"
                   f"  Диспетчер: {td:.0f} руб.\n"
                   f"  Топливо: {tf:.0f} руб.\n\n"
                   f"Смен: {len(self.records)}\n"
                   f"Пробег: {tk:.0f} км")
        box.add_widget(self.mk_label(details, size=14, color=TEXT, height=200))
        scroll.add_widget(box)
        main.add_widget(scroll)
        self.set_body(main)

    def show_shift(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Новая смена"))
        scroll = ScrollView()
        form = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=dp(4))
        form.bind(minimum_height=form.setter("height"))
        today = datetime.now().strftime("%d.%m.%Y")
        form.add_widget(self.mk_label("Дата (ДД.ММ.ГГГГ)", color=MUTED))
        date_in = self.mk_input("", today)
        form.add_widget(date_in)
        form.add_widget(self.mk_label("Заработок за день (руб)", color=MUTED))
        earn_in = self.mk_input("", "")
        form.add_widget(earn_in)
        form.add_widget(self.mk_label("Диспетчер (руб)", color=MUTED))
        disp_in = self.mk_input("", "0")
        form.add_widget(disp_in)
        form.add_widget(self.mk_label("Пробег (км)", color=MUTED))
        km_in = self.mk_input("", "")
        form.add_widget(km_in)
        form.add_widget(self.mk_label("Расход л/100км", color=MUTED))
        cons_in = self.mk_input("", f"{self.cfg['norm']:.2f}")
        form.add_widget(cons_in)
        saved_price = self.cfg.get("last_price", 62.50)
        form.add_widget(self.mk_label("Цена топлива (руб/л)", color=MUTED))
        price_in = self.mk_input("", f"{saved_price:.2f}")
        form.add_widget(price_in)
        result_lbl = self.mk_label("", size=13, color=OK, height=200)
        form.add_widget(result_lbl)
        scroll.add_widget(form)
        main.add_widget(scroll)
        save_btn = Button(
            text="СОХРАНИТЬ СМЕНУ", background_normal="",
            background_color=OK, color=(0, 0, 0, 1),
            font_size=dp(17), bold=True,
            size_hint_y=None, height=dp(55),
        )
        main.add_widget(save_btn)

        def on_save(*_):
            km = pf(km_in.text)
            if km <= 0:
                result_lbl.color = WARN
                result_lbl.text = "Пробег должен быть больше 0"
                return
            earn = pf(earn_in.text)
            disp = pf(disp_in.text)
            cons = pf(cons_in.text, self.cfg["norm"])
            price = pf(price_in.text, 0)
            used = km * cons / 100
            fuel_cost = used * price
            net = earn - disp - fuel_cost
            record = {
                "date": date_in.text.strip() or today,
                "earnings": earn, "dispatcher": disp, "mileage": km,
                "consumption": cons, "fuel_used": used,
                "fuel_price": price, "fuel_cost": fuel_cost, "net": net,
            }
            self.records.append(record)
            save_json(DATA_FILE, self.records)
            self.cfg["current_fuel"] = max(0.0, self.cfg["current_fuel"] - used)
            self.cfg["last_price"] = price
            save_json(CONFIG_FILE, self.cfg)
            self.refresh()
            result_lbl.color = OK
            result_lbl.text = (f"Сохранено!\n{record['date']}\n"
                               f"Топливо: {fuel_cost:.0f} руб.\n"
                               f"Чистыми: {net:.0f} руб.\n"
                               f"В баке: {self.cfg['current_fuel']:.1f} л")

        save_btn.bind(on_press=on_save)
        self.set_body(main)

    def show_refuel(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Заправка"))
        tank = self.cfg["tank"]
        cur = self.cfg["current_fuel"]
        free = tank - cur
        scroll = ScrollView()
        form = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=dp(4))
        form.bind(minimum_height=form.setter("height"))
        form.add_widget(self.mk_label(f"Объём бака: {tank:.1f} л",
                                      size=15, color=TEXT, height=30))
        form.add_widget(self.mk_label(f"Сейчас в баке: {cur:.2f} л",
                                      size=15, color=TEXT, height=30))
        form.add_widget(self.mk_label(f"Свободно: {free:.2f} л",
                                      size=18, bold=True,
                                      color=OK, height=40))
        form.add_widget(self.mk_label("Сколько заправил (л)", color=MUTED))
        liters_in = self.mk_input("литров", "")
        form.add_widget(liters_in)
        result_lbl = self.mk_label("", size=13, color=OK, height=120)
        form.add_widget(result_lbl)
        scroll.add_widget(form)
        main.add_widget(scroll)
        save_btn = Button(
            text="СОХРАНИТЬ ЗАПРАВКУ", background_normal="",
            background_color=OK, color=(0, 0, 0, 1),
            font_size=dp(17), bold=True,
            size_hint_y=None, height=dp(55),
        )
        main.add_widget(save_btn)

        def on_save(*_):
            liters = pf(liters_in.text)
            if liters <= 0:
                result_lbl.color = WARN
                result_lbl.text = "Введи количество литров"
                return
            new_level = self.cfg["current_fuel"] + liters
            if new_level > tank:
                new_level = tank
            added = new_level - self.cfg["current_fuel"]
            self.cfg["current_fuel"] = new_level
            save_json(CONFIG_FILE, self.cfg)
            self.refresh()
            result_lbl.color = OK
            result_lbl.text = (f"Заправлено!\n"
                               f"Залито: {added:.2f} л\n"
                               f"Теперь в баке: {self.cfg['current_fuel']:.2f} л")

        save_btn.bind(on_press=on_save)
        self.set_body(main)

    def show_records(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Записи"))
        main.add_widget(self.mk_label(
            "Тапни запись — откроется редактирование",
            size=12, color=MUTED, height=26))
        scroll = ScrollView()
        box = BoxLayout(orientation="vertical", spacing=dp(6),
                        size_hint_y=None, padding=dp(6))
        box.bind(minimum_height=box.setter("height"))
        if not self.records:
            box.add_widget(self.mk_label("Записей нет", size=16,
                                         color=MUTED, height=60))
        else:
            for i, r in enumerate(self.records):
                def make_cb(idx):
                    def cb(*_):
                        self.show_edit(idx)
                    return cb
                btn = Button(
                    text=(f"{i+1}. {r.get('date','?')} — {r.get('net',0):.0f} руб.\n"
                          f"Зар: {r.get('earnings',0):.0f} | "
                          f"Дисп: {r.get('dispatcher',0):.0f} | "
                          f"{r.get('mileage',0):.0f} км"),
                    background_normal="",
                    background_color=CARD, color=TEXT,
                    font_size=dp(13), bold=True,
                    size_hint_y=None, height=dp(64),
                    halign="left",
                )
                btn.bind(on_press=make_cb(i))
                box.add_widget(btn)
        scroll.add_widget(box)
        main.add_widget(scroll)
        self.set_body(main)

    def show_edit(self, idx):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Изменить смену"))
        r = self.records[idx]
        scroll = ScrollView()
        form = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=dp(4))
        form.bind(minimum_height=form.setter("height"))
        form.add_widget(self.mk_label("Дата (ДД.ММ.ГГГГ)", color=MUTED))
        date_in = self.mk_input("", r.get("date", ""))
        form.add_widget(date_in)
        form.add_widget(self.mk_label("Заработок за день (руб)", color=MUTED))
        earn_in = self.mk_input("", str(r.get("earnings", "")))
        form.add_widget(earn_in)
        form.add_widget(self.mk_label("Диспетчер (руб)", color=MUTED))
        disp_in = self.mk_input("", str(r.get("dispatcher", 0)))
        form.add_widget(disp_in)
        form.add_widget(self.mk_label("Пробег (км)", color=MUTED))
        km_in = self.mk_input("", str(r.get("mileage", "")))
        form.add_widget(km_in)
        form.add_widget(self.mk_label("Расход л/100км", color=MUTED))
        cons_in = self.mk_input("", str(r.get("consumption", "8.50")))
        form.add_widget(cons_in)
        form.add_widget(self.mk_label("Цена топлива (руб/л)", color=MUTED))
        price_in = self.mk_input("", str(r.get("fuel_price", "0")))
        form.add_widget(price_in)
        result_lbl = self.mk_label("", size=13, color=OK, height=160)
        form.add_widget(result_lbl)
        scroll.add_widget(form)
        main.add_widget(scroll)
        save_btn = Button(
            text="ОБНОВИТЬ", background_normal="",
            background_color=OK, color=(0, 0, 0, 1),
            font_size=dp(17), bold=True,
            size_hint_y=None, height=dp(55),
        )
        main.add_widget(save_btn)

        def on_save(*_):
            km = pf(km_in.text)
            if km <= 0:
                result_lbl.color = WARN
                result_lbl.text = "Пробег должен быть больше 0"
                return
            earn = pf(earn_in.text)
            disp = pf(disp_in.text)
            cons = pf(cons_in.text, self.cfg["norm"])
            price = pf(price_in.text, 0)
            used = km * cons / 100
            fuel_cost = used * price
            net = earn - disp - fuel_cost
            self.records[idx] = {
                "date": date_in.text.strip() or r.get("date", ""),
                "earnings": earn, "dispatcher": disp, "mileage": km,
                "consumption": cons, "fuel_used": used,
                "fuel_price": price, "fuel_cost": fuel_cost, "net": net,
            }
            save_json(DATA_FILE, self.records)
            self.cfg["last_price"] = price
            save_json(CONFIG_FILE, self.cfg)
            self.refresh()
            result_lbl.color = OK
            result_lbl.text = (f"Обновлено!\n"
                               f"{self.records[idx]['date']}\n"
                               f"Топливо: {fuel_cost:.0f} руб.\n"
                               f"Чистыми: {net:.0f} руб.")

        save_btn.bind(on_press=on_save)
        self.set_body(main)

    def show_stats(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(2), padding=dp(2))
        main.add_widget(self.mk_top_bar("Статистика"))
        if not self.records:
            box = BoxLayout(orientation="vertical", padding=dp(20))
            box.add_widget(self.mk_label("Записей нет", size=16,
                                         color=MUTED, height=60))
            main.add_widget(box)
            self.set_body(main)
            return
        recs = self.records
        n = len(recs)
        te = sum(r.get("earnings", 0) for r in recs)
        td = sum(r.get("dispatcher", 0) for r in recs)
        tf = sum(r.get("fuel_cost", 0) for r in recs)
        tc = td + tf
        tn = sum(r.get("net", 0) for r in recs)
        tk = sum(r.get("mileage", 0) for r in recs)
        tu = sum(r.get("fuel_used", 0) for r in recs)
        table = GridLayout(cols=3, size_hint_y=None, spacing=dp(2), padding=dp(2))
        table.bind(minimum_height=table.setter("height"))
        table.add_widget(self.mk_label("Показатель", size=15,
                                       color=ACCENT, bold=True, height=42))
        table.add_widget(self.mk_label("Сумма", size=15,
                                       color=ACCENT, bold=True, height=42))
        table.add_widget(self.mk_label("Средн.", size=15,
                                       color=ACCENT, bold=True, height=42))
        rows = [
            ("Заработано", f"{te:.0f} руб.", f"{te/n:.0f} руб.", TEXT, False),
            ("Диспетчер", f"{td:.0f} руб.", f"{td/n:.0f} руб.", TEXT, False),
            ("Топливо", f"{tf:.0f} руб.", f"{tf/n:.0f} руб.", TEXT, False),
            ("РАСХОДЫ", f"{tc:.0f} руб.", f"{tc/n:.0f} руб.", WARN, True),
            ("ЧИСТЫМИ", f"{tn:.0f} руб.", f"{tn/n:.0f} руб.", OK, True),
            ("Пробег", f"{tk:.0f} км", f"{tk/n:.0f} км", TEXT, False),
            ("Топл. израсх.", f"{tu:.1f} л", f"{tu/n:.1f} л", TEXT, False),
        ]
        for name, s, a, col, bold in rows:
            table.add_widget(self.mk_label(name, size=16, color=col, bold=bold, height=46))
            table.add_widget(self.mk_label(s, size=16, color=col, bold=bold, height=46))
            table.add_widget(self.mk_label(a, size=16, color=col, bold=bold, height=46))
        scroll = ScrollView()
        scroll.add_widget(table)
        main.add_widget(scroll)
        best = max(recs, key=lambda r: r.get("net", 0))
        worst = min(recs, key=lambda r: r.get("net", 0))
        main.add_widget(self.mk_label(
            f"Лучший: {best.get('date','?')} — {best.get('net',0):.0f} руб.",
            size=14, color=OK, height=28))
        main.add_widget(self.mk_label(
            f"Худший: {worst.get('date','?')} — {worst.get('net',0):.0f} руб.",
            size=14, color=WARN, height=28))
        self.set_body(main)

    def show_period(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Период"))
        form = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(10),
                         size_hint_y=None, height=dp(200))
        form.add_widget(self.mk_label("Дата начала (ДД.ММ.ГГГГ)", color=MUTED))
        start_in = self.mk_input("", "01.01.2026")
        form.add_widget(start_in)
        form.add_widget(self.mk_label("Дата окончания (ДД.ММ.ГГГГ)", color=MUTED))
        end_in = self.mk_input("", datetime.now().strftime("%d.%m.%Y"))
        form.add_widget(end_in)
        result_lbl = self.mk_label("", size=13, color=WARN, height=30)
        form.add_widget(result_lbl)
        show_btn = Button(
            text="ПОКАЗАТЬ", background_normal="",
            background_color=OK, color=(0, 0, 0, 1),
            font_size=dp(17), bold=True,
            size_hint_y=None, height=dp(55),
        )
        scroll = ScrollView()
        results_box = BoxLayout(orientation="vertical", spacing=dp(6),
                                size_hint_y=None, padding=dp(6))
        results_box.bind(minimum_height=results_box.setter("height"))
        scroll.add_widget(results_box)

        def on_show(*_):
            results_box.clear_widgets()
            s = parse_date(start_in.text)
            e = parse_date(end_in.text)
            if not s or not e:
                result_lbl.text = "Неверный формат даты"
                return
            result_lbl.text = ""
            filtered = []
            for r in self.records:
                d = parse_date(r.get("date", ""))
                if d and s <= d <= e:
                    filtered.append(r)
            if not filtered:
                results_box.add_widget(self.mk_label(
                    "За этот период записей нет",
                    size=14, color=MUTED, height=50))
                return
            n = len(filtered)
            te = sum(r.get("earnings", 0) for r in filtered)
            td = sum(r.get("dispatcher", 0) for r in filtered)
            tf = sum(r.get("fuel_cost", 0) for r in filtered)
            tc = td + tf
            tn = sum(r.get("net", 0) for r in filtered)
            tk = sum(r.get("mileage", 0) for r in filtered)
            table = GridLayout(cols=3, size_hint_y=None, spacing=dp(2), padding=dp(2))
            table.bind(minimum_height=table.setter("height"))
            table.add_widget(self.mk_label("Показатель", size=15,
                                           color=ACCENT, bold=True, height=42))
            table.add_widget(self.mk_label("Сумма", size=15,
                                           color=ACCENT, bold=True, height=42))
            table.add_widget(self.mk_label("Средн.", size=15,
                                           color=ACCENT, bold=True, height=42))
            rows = [
                ("Смен", f"{n}", "—", TEXT, False),
                ("Заработано", f"{te:.0f} руб.", f"{te/n:.0f} руб.", TEXT, False),
                ("Диспетчер", f"{td:.0f} руб.", f"{td/n:.0f} руб.", TEXT, False),
                ("Топливо", f"{tf:.0f} руб.", f"{tf/n:.0f} руб.", TEXT, False),
                ("РАСХОДЫ", f"{tc:.0f} руб.", f"{tc/n:.0f} руб.", WARN, True),
                ("ЧИСТЫМИ", f"{tn:.0f} руб.", f"{tn/n:.0f} руб.", OK, True),
                ("Пробег", f"{tk:.0f} км", f"{tk/n:.0f} км", TEXT, False),
            ]
            for name, s_, a_, col, bold in rows:
                table.add_widget(self.mk_label(name, size=15, color=col, bold=bold, height=42))
                table.add_widget(self.mk_label(s_, size=15, color=col, bold=bold, height=42))
                table.add_widget(self.mk_label(a_, size=15, color=col, bold=bold, height=42))
            results_box.add_widget(table)

        show_btn.bind(on_press=on_show)
        main.add_widget(form)
        main.add_widget(show_btn)
        main.add_widget(scroll)
        self.set_body(main)

    def show_settings(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Настройки"))
        scroll = ScrollView()
        form = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=dp(4))
        form.bind(minimum_height=form.setter("height"))
        form.add_widget(self.mk_label("Объём бака (л)", color=MUTED))
        tank_in = self.mk_input("", f"{self.cfg['tank']:.1f}")
        form.add_widget(tank_in)
        form.add_widget(self.mk_label("Норма расхода", color=MUTED))
        norm_in = self.mk_input("", f"{self.cfg['norm']:.2f}")
        form.add_widget(norm_in)
        form.add_widget(self.mk_label("Остаток в баке (л)", color=MUTED))
        cur_in = self.mk_input("", f"{self.cfg['current_fuel']:.2f}")
        form.add_widget(cur_in)
        form.add_widget(self.mk_label("Цена топлива по умолчанию (руб/л)",
                                      color=MUTED))
        price_in = self.mk_input("", f"{self.cfg.get('last_price', 62.50):.2f}")
        form.add_widget(price_in)
        scroll.add_widget(form)
        main.add_widget(scroll)
        save_btn = Button(
            text="СОХРАНИТЬ", background_normal="",
            background_color=OK, color=(0, 0, 0, 1),
            font_size=dp(17), bold=True,
            size_hint_y=None, height=dp(55),
        )
        main.add_widget(save_btn)

        def on_save(*_):
            self.cfg["tank"] = pf(tank_in.text, 50)
            self.cfg["norm"] = pf(norm_in.text, 8.5)
            self.cfg["current_fuel"] = min(
                pf(cur_in.text, self.cfg["tank"]),
                self.cfg["tank"],
            )
            self.cfg["last_price"] = pf(price_in.text, 62.50)
            save_json(CONFIG_FILE, self.cfg)
            self.refresh()

        save_btn.bind(on_press=on_save)
        self.set_body(main)

    def show_export(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Экспорт"))
        box = BoxLayout(orientation="vertical", padding=dp(20))
        box.add_widget(self.mk_label("Экспорт (позже)", size=16,
                                     color=MUTED, height=60))
        main.add_widget(box)
        self.set_body(main)

    def show_delete(self, *args):
        main = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(4))
        main.add_widget(self.mk_top_bar("Удалить"))
        if not self.records:
            box = BoxLayout(orientation="vertical", padding=dp(20))
            box.add_widget(self.mk_label("Записей нет", size=16,
                                         color=MUTED, height=60))
            main.add_widget(box)
            self.set_body(main)
            return

        def del_last(*_):
            if self.records:
                self.records.pop()
                save_json(DATA_FILE, self.records)
                self.refresh()
                self.show_delete()

        btn = Button(
            text="УДАЛИТЬ ПОСЛЕДНЮЮ", background_normal="",
            background_color=WARN, color=(1, 1, 1, 1),
            font_size=dp(16), bold=True,
            size_hint_y=None, height=dp(55),
        )
        btn.bind(on_press=del_last)
        main.add_widget(btn)

        def clear_all(*_):
            self.records = []
            save_json(DATA_FILE, self.records)
            self.refresh()
            self.show_delete()

        btn2 = Button(
            text="ОЧИСТИТЬ ВСЁ", background_normal="",
            background_color=
