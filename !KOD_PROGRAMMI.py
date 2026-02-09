#
# ВНИМАНИЕ!!!
#
# ЭТО ТЕСТОВАЯ ВЕРСИЯ МАТЕМАТИЧЕСКОГО СПРАВОЧНИКА
# ДАННЫЙ КОД СОЗДАН ЛИШЬ ДЛЯ РЕАЛИЗАЦИИ ПРОЕКТА
#
# Спасибо за внимание!
#




#
# Настройка - 1
# Задачи - 2
# История - 3
# Главное меню - 4
# Справочник - 5
#

# Ввод всех библиотек для выполнения работы программы
import sys

import os

import sqlite3

import random
import time
from fractions import Fraction

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QScrollArea,
    QLineEdit,
    QSizePolicy,
    QTextEdit,
    QSpacerItem,
    QStackedLayout,
    QProgressBar
)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QStackedLayout, 
                             QHBoxLayout, QCheckBox, QRadioButton, QButtonGroup, 
                             QMessageBox, QScrollArea, QFrame, QGridLayout)

from PyQt6.QtGui import QPixmap, QIcon, QAction, QFont, QIntValidator

from PyQt6.QtCore import Qt, QSize

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

## ввод данных для справочника из таблицы

connection = sqlite3.connect('vse_dannie.db')
cursor = connection.cursor()
cursor.execute('SELECT * FROM Dannie')
results = cursor.fetchall()
connection.close()

# # графика
STYLE_SHEET = """
    QMainWindow {
        background-color: #f5f6fa;
    }
    
    QFrame#Card {
        background-color: white;
        border-radius: 15px;
        border: 1px solid #dcdde1;
    }
    
    QLabel {
        color: #2f3640;
        font-family: 'Segoe UI', sans-serif;
    }
    
    QPushButton {
        background-color: #3498db;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        border: none;
    }
    
    QPushButton:hover {
        background-color: #2980b9;
    }
    
    QPushButton#SecondaryBtn {
        background-color: #7f8c8d;
    }
    
    QPushButton#StartBtn {
        background-color: #27ae60;
        font-size: 20px;
    }
    
    QPushButton#StopBtn {
        background-color: #e74c3c;
    }

    QLineEdit {
        border: 2px solid #dcdde1;
        border-radius: 8px;
        padding: 8px;
        background: white;
        selection-background-color: #3498db;
    }
    
    QLineEdit:focus {
        border: 2px solid #3498db;
    }

    QScrollBar:vertical {
        border: none;
        background: #f1f1f1;
        width: 10px;
        border-radius: 5px;
    }
    
    QScrollBar::handle:vertical {
        background: #bdc3c7;
        border-radius: 5px;
    }
"""
class ResultChart(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, (self.ax_time, self.ax_pie) = plt.subplots(1, 2, figsize=(12, 5))
        super().__init__(self.fig)
        self.setParent(parent)

    def update_chart(self, session_stats):
        self.ax_time.clear()
        self.ax_pie.clear()

        if not session_stats:
            return

        ids = [x[0] for x in session_stats]
        times = [x[1] for x in session_stats]
        results = [x[2] for x in session_stats]
        
        line, = self.ax_time.plot(ids, times, marker='o', color='#3498db', 
                                 linewidth=2, markersize=8, label="Время решения")
        for i, txt in enumerate(times):
            self.ax_time.annotate(f"{txt:.1f}с", 
                                 (ids[i], times[i]), 
                                 textcoords="offset points", 
                                 xytext=(0, 10), 
                                 ha='center', 
                                 fontsize=9,
                                 fontweight='bold',
                                 color='#2c3e50')

        self.ax_time.set_title("Скорость решения по задачам", fontsize=14, pad=15)
        self.ax_time.set_xlabel("Номер примера")
        self.ax_time.set_ylabel("Секунды")
        self.ax_time.grid(True, linestyle=':', alpha=0.6)
        self.ax_time.legend(loc="upper right")
        
        if times:
            self.ax_time.set_ylim(0, max(times) * 1.2)

        correct_count = sum(1 for x in results if x)
        wrong_count = len(results) - correct_count
        
        labels = ['Правильно', 'Ошибки']
        sizes = [correct_count, wrong_count]
        colors = ['#2ecc71', '#e74c3c'] 
        
        wedges, texts, autotexts = self.ax_pie.pie(
            sizes, 
            labels=labels, 
            colors=colors, 
            autopct='%1.1f%%', 
            startangle=140, 
            explode=(0.05, 0) if wrong_count > 0 else (0, 0),
            shadow=True,
            textprops={'fontsize': 12}
        )
        
        plt.setp(autotexts, size=11, weight="bold", color="white")
        
        self.ax_pie.set_title("Общая точность", fontsize=14, pad=15)
        self.ax_pie.legend(wedges, labels, title="Результаты", loc="center left", 
                          bbox_to_anchor=(1, 0, 0.5, 1))

        self.fig.tight_layout()
        self.draw()
        
# Создание основного класса приложения
class math_spravochnik(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Математический справочник")
        self.showFullScreen()
        icon = QIcon('Znachok_okna3.ico')
        self.setWindowIcon(icon)
        self.setStyleSheet(STYLE_SHEET)
        self.widjet_glavnogo_menu = QWidget()
        self.setCentralWidget(self.widjet_glavnogo_menu)

        self.vivod_na_ekran = QVBoxLayout(self.widjet_glavnogo_menu)

        self.sbornik_layoutov = QStackedLayout()

        self.vivod_na_ekran.addLayout(self.sbornik_layoutov)


        # Вызов всех классов
        self.trenashor()
        self.menu()
        self.spravochnik()
        self.init_class_selection_ui()
        self.sbornik_layoutov.setCurrentIndex(3)

    def init_class_selection_ui(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Выберите уровень сложности")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 30px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        grid = QGridLayout()
        classes = [
            ("1 Класс", {"ops": [0, 1], "min": 1, "max": 10, "frac": False}),
            ("2-4 Класс", {"ops": [0, 1, 2], "min": 1, "max": 50, "frac": False}),
            ("5 Класс", {"ops": [0, 1, 2, 3], "min": 1, "max": 100, "frac": True}),
            ("6-8 Класс", {"ops": [0, 1, 2, 3], "min": -50, "max": 50, "frac": True, "dec": True}),
        ]

        for i, (name, presets) in enumerate(classes):
            btn = QPushButton(name)
            btn.setFixedSize(200, 60)
            btn.clicked.connect(lambda ch, p=presets: self.apply_preset_and_start(p))
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)

        manual_btn = QPushButton("⚙️ Настроить самому")
        manual_btn.setFixedSize(410, 60)
        manual_btn.setObjectName("SecondaryBtn")
        manual_btn.clicked.connect(lambda: self.sbornik_layoutov.setCurrentIndex(0))
        layout.addWidget(manual_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("Назад в меню")
        back_btn.clicked.connect(self.vozvrashenie_v_menu)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.sbornik_layoutov.insertWidget(5, page)
    def apply_preset_and_start(self, p):
        for cb in self.ops_boxes: cb.setChecked(False)
        for idx in p.get("ops", [0]): self.ops_boxes[idx].setChecked(True)
        self.range_min.setText(str(p.get("min", 1)))
        self.range_max.setText(str(p.get("max", 10)))
        self.cb_frac.setChecked(p.get("frac", False))
        self.cb_decimal.setChecked(p.get("dec", False))
        
        self.start_session()

        
    # СОЗДАНИЕ МЕНЮ
    def menu(self):
        
        widget = QWidget()
        glavnaya_korobka = QVBoxLayout(widget)

        spacer1 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        spacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        Ima = QLabel("Проект для конференции 'Инженеры будущего'\n Разработчик: Савченко А. Г.")
        Ima.setStyleSheet("font-size: 10px;")
        Ima.setAlignment(Qt.AlignmentFlag.AlignLeft)
        glavnaya_korobka.addWidget(Ima)

        Horizont_korobka = QHBoxLayout()
        glavnaya_korobka.addLayout(Horizont_korobka)
        
        
        l = QVBoxLayout()
        Horizont_korobka.addItem(spacer1)
        Horizont_korobka.addLayout(l)
        Horizont_korobka.addItem(spacer2)
        stroka1 = QLabel("Интерактивный математический\n справочник")
        stroka1.setStyleSheet("font-size: 40px; font-weight: 900; color: #2c3e50; letter-spacing: 2px;")
        stroka1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        Horizont_korobka.setSpacing(20)

        spacer3 = QSpacerItem(40, 0, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        spacer4 = QSpacerItem(1, 0, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)

        l.addItem(spacer3)
        l.addWidget(stroka1)

        button1 = QPushButton("Тренажёр")
        button1.setMinimumHeight(70)
        button1.setFixedWidth(400)
        button1.setStyleSheet("font: 20px; font-weight: bold;")
        button1.clicked.connect(self.vibor_TESTIROVANIE)
        l.addWidget(button1, alignment=Qt.AlignmentFlag.AlignCenter)

        button2 = QPushButton("Справочник")
        button2.setMinimumHeight(70)
        button2.setFixedWidth(400)
        button2.setStyleSheet("font: 20px; font-weight: bold;")
        button2.clicked.connect(self.vibor_SPRAVOCHNIK)
        l.addWidget(button2, alignment=Qt.AlignmentFlag.AlignCenter)

        button3 = QPushButton("Выход")
        button3.setFixedWidth(200)
        button3.clicked.connect(self.VYHOD)
        l.addWidget(button3, alignment=Qt.AlignmentFlag.AlignCenter)
        
        l.addItem(spacer4)

        self.sbornik_layoutov.addWidget(widget)
    def trenashor(self):
        self.score = 0
        self.total_attempts = 0
        self.limit = 10
        self.hidden_value = None 
        self.already_answered = False
        self.current_problem_raw_parts = [] 
        self.start_time = 0 
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.sbornik_layoutov = QStackedLayout(self.central_widget)

        self.init_menu_ui()
        self.init_game_ui()
        self.init_history_ui()

    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    def create_small_input(self, text, default_val):
        layout = QHBoxLayout()
        label = QLabel(text)
        label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        edit = QLineEdit(default_val)
        edit.setFixedWidth(45)
        edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        edit.setValidator(QIntValidator(0, 9999))
        edit.setStyleSheet("padding: 3px; border: 1px solid #bdc3c7; border-radius: 4px; background: white;")
        layout.addWidget(label)
        layout.addWidget(edit)
        layout.addStretch()
        return layout, edit

    def format_value_html(self, val, highlight=False, small=False):
        color = "#3498db" if highlight else "#2c3e50"
        font_size = "14px" if small else "18px"
        main_size = "24px" if not small else "16px"

        if isinstance(val, Fraction):
            if val.denominator == 1:
                return f'<b style="color: {color}; font-size: {main_size};">{val.numerator}</b>'
            return (
                f'<table style="display: inline-table; vertical-align: middle; border-collapse: collapse; margin: 0; color: {color};" cellspacing="0" cellpadding="0">'
                f'<tr><td style="border-bottom: 2px solid {color}; text-align: center; padding: 0 2px; font-size: {font_size}; line-height: 1.1; font-weight: bold;">{val.numerator}</td></tr>'
                f'<tr><td style="text-align: center; padding: 0 2px; font-size: {font_size}; line-height: 1.1; font-weight: bold;">{val.denominator}</td></tr>'
                f'</table>'
            )
        if isinstance(val, (float, int)):
            try: prec = int(self.dec_precision.text())
            except: prec = 1
            txt = str(round(float(val), prec)).replace('.', ',')
            if txt.endswith(',0'): txt = txt[:-2]
            return f'<b style="color: {color}; font-size: {main_size};">{txt}</b>'
        return f'<b style="color: {color}; font-size: {main_size};">{val}</b>'

    def assemble_math_html(self, parts, small=False):
        cells = []
        base_size = "32px" if not small else "18px"
        for item in parts:
            if item == "?":
                content = f'<b style="color: #3498db; font-size: {base_size};">X</b>'
            elif isinstance(item, (Fraction, float, int)):
                content = self.format_value_html(item, small=small)
            else:
                content = str(item)
            cells.append(f'<td style="padding: 0 5px; vertical-align: middle; white-space: nowrap;">{content}</td>')
        return f'<table align="center" style="font-size: {base_size}; color: #2c3e50;"><tr>{" ".join(cells)}</tr></table>'

    def make_equation(self, v1, op_char, v2, res):
        op_display = op_char.replace('*', '×').replace('/', '÷')
        mode = 2 if self.pos_group.checkedId() == 1 else random.randint(0, 2)
        if mode == 0: 
            self.hidden_value = v1
            return ["?", op_display, v2, "=", res]
        elif mode == 1: 
            self.hidden_value = v2
            return [v1, op_display, "?", "=", res]
        else: 
            self.hidden_value = res
            return [v1, op_display, v2, "=", "?"]

    # ИНТЕРФЕЙС ЭКРАНОВ
    def init_menu_ui(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(40, 20, 40, 20)

        knopka_na_vihod = QPushButton("Назад в меню")
        knopka_na_vihod.clicked.connect(self.vozvrashenie_v_menu)
        main_layout.addWidget(knopka_na_vihod, alignment=Qt.AlignmentFlag.AlignLeft)
        
        title = QLabel("Настройки тренировки")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)

        ops_frame = QFrame()
        ops_frame.setStyleSheet("background: #dddfff; border-radius: 10px; padding: 10px;")
        ops_layout = QVBoxLayout(ops_frame)
        ops_layout.addWidget(QLabel("<b>1. Математические действия:</b>"))
        
        ops_grid = QGridLayout()
        self.cb_plus = QCheckBox("Сложение (+)"); self.cb_plus.setChecked(True); self.cb_plus.setStyleSheet("background: #dddfff")
        self.cb_minus = QCheckBox("Вычитание (-)"); self.cb_minus.setStyleSheet("background: #dddfff")
        self.cb_mult = QCheckBox("Умножение (×)"); self.cb_mult.setStyleSheet("background: #dddfff")
        self.cb_div = QCheckBox("Деление (÷)"); self.cb_div.setStyleSheet("background: #dddfff")
        self.ops_boxes = [self.cb_plus, self.cb_minus, self.cb_mult, self.cb_div]
        
        ops_grid.addWidget(self.cb_plus, 0, 0); ops_grid.addWidget(self.cb_minus, 0, 1)
        ops_grid.addWidget(self.cb_mult, 1, 0); ops_grid.addWidget(self.cb_div, 1, 1)
        ops_layout.addLayout(ops_grid)
        main_layout.addWidget(ops_frame)

        types_frame = QFrame()
        types_frame.setStyleSheet("background: #dddfff; border-radius: 10px; padding: 15px;")
        types_layout = QVBoxLayout(types_frame)
        stroka = QLabel("<b>2. Настройка чисел и сложности:</b>")
        stroka.setFixedHeight(50);
        types_layout.addWidget(stroka)

        range_lay = QHBoxLayout()
        range_lay.addWidget(QLabel("Целые числа:"))
        _, self.range_min = self.create_small_input("от", "1")
        _, self.range_max = self.create_small_input("до", "10")
        range_lay.addLayout(_)

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        range_lay2 = QHBoxLayout()
        range_lay2.addWidget(QLabel("Длина:"))
        self.diff_group = QButtonGroup(self)
        for i, text in enumerate(["2", "3-4", "5"]):
            rb = QRadioButton(text); rb.setChecked(i==0)
            self.diff_group.addButton(rb, i); range_lay2.addWidget(rb)
        range_lay2.addItem(spacer)
        types_layout.addLayout(range_lay)
        types_layout.addLayout(range_lay2)

        frac_lay = QHBoxLayout()
        self.cb_frac = QCheckBox("Обыкновенные дроби")
        frac_lay.addWidget(self.cb_frac)
        _, self.max_denom = self.create_small_input("Макс. знаменатель:", "10")
        frac_lay.addLayout(_)
        types_layout.addLayout(frac_lay)

        dec_lay = QHBoxLayout()
        self.cb_decimal = QCheckBox("Десятичные дроби")
        dec_lay.addWidget(self.cb_decimal)
        _, self.dec_precision = self.create_small_input("Знаков:", "1")
        dec_lay.addLayout(_)
        types_layout.addLayout(dec_lay)
        main_layout.addWidget(types_frame)

        bottom_grid = QGridLayout()
        pos_box = QFrame(); pos_box.setStyleSheet("background: #dddfff; border-radius: 10px; padding: 10px;")
        pos_lay = QVBoxLayout(pos_box); pos_lay.addWidget(QLabel("<b>3. Позиция X:</b>"))
        self.pos_group = QButtonGroup(self)
        rb_rand = QRadioButton("Случайная"); rb_rand.setChecked(True)
        rb_classic = QRadioButton("Классика"); self.pos_group.addButton(rb_rand, 0); self.pos_group.addButton(rb_classic, 1)
        pos_lay.addWidget(rb_rand); pos_lay.addWidget(rb_classic); bottom_grid.addWidget(pos_box, 0, 0)

        limit_box = QFrame(); limit_box.setStyleSheet("background: #dddfff; border-radius: 10px; padding: 10px;")
        limit_lay = QVBoxLayout(limit_box); limit_lay.addWidget(QLabel("<b>4. Лимит:</b>"))
        _, self.limit_input = self.create_small_input("Примеров:", "10"); limit_lay.addLayout(_)
        bottom_grid.addWidget(limit_box, 0, 1)
        main_layout.addLayout(bottom_grid)

        spacer1 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        main_layout.addItem(spacer1)
        start_btn = QPushButton("Начать тренировку")
        start_btn.setFixedHeight(60); start_btn.setStyleSheet("background: #3498db; color:  White; font-weight: bold; font-size: 18px; border-radius: 15px;")
        start_btn.clicked.connect(self.start_session)
        main_layout.addWidget(start_btn)


        self.sbornik_layoutov.addWidget(page)

    def init_game_ui(self):
        page = QWidget()
        layout = QVBoxLayout(page)
                
        self.stop_btn = QPushButton("Прервать")
        self.stop_btn.setStyleSheet("background: #e74c3c; color: white; font-size: 18px; border-radius: 10px;")
        self.stop_btn.clicked.connect(self.stop_session)

        layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        header = QHBoxLayout()
        self.score_label = QLabel("")
        self.score_label.setStyleSheet("font-size: 16px;")
        header.addWidget(self.score_label); header.addStretch()
        layout.addLayout(header)
        
        self.problem_label = QLabel("")
        self.problem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.problem_label.setStyleSheet("margin: 20px; padding: 100px; background: white; border: 2px solid #ecf0f1; border-radius: 15px;")
        layout.addWidget(self.problem_label)
        
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Введите ответ или оставьте пустым для пропуска...")
        self.answer_input.setFixedHeight(60); self.answer_input.setStyleSheet("font-size: 24px; padding: 10px;")
        self.answer_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer_input.returnPressed.connect(self.handle_return_pressed)
        layout.addWidget(self.answer_input)
        
        self.result_label = QLabel("")
        self.result_label.setMinimumHeight(120); self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_label)
        
        layout.addStretch()
        btn_lay = QHBoxLayout()
        
        self.action_btn = QPushButton("Проверить")
        self.action_btn.setFixedHeight(50)
        self.action_btn.setStyleSheet("background: #3498db; color: white; font-size: 18px; border-radius: 10px;")
        self.action_btn.clicked.connect(self.handle_action_btn)

        btn_lay.addWidget(self.action_btn)
        layout.addLayout(btn_lay)
        
        btn_lay.addWidget(self.action_btn)
        layout.addLayout(btn_lay)
        self.sbornik_layoutov.addWidget(page)

    def init_history_ui(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.history_title = QLabel("Результаты:")
        self.history_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.history_title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.addStretch()
        self.scroll.setWidget(self.history_content)
        layout.addWidget(self.scroll)

        back_btn = QPushButton("Вернуться к выбору сложности")
        back_btn.setFixedHeight(50); back_btn.clicked.connect(lambda: self.sbornik_layoutov.setCurrentIndex(5))
        layout.addWidget(back_btn)
        self.sbornik_layoutov.addWidget(page)

        self.chart = ResultChart()
        self.chart.setMinimumHeight(300)
        layout.insertWidget(1, self.chart)
        
        self.session_stats = [] 
    # ЛОГИКА
    def generate_problem_elements(self):
        allowed_ops = [o for o, cb in zip(['+', '-', '*', '/'], self.ops_boxes) if cb.isChecked()]
        types = [0]
        if self.cb_frac.isChecked(): types.append(1)
        if self.cb_decimal.isChecked(): types.append(2)
        chosen = random.choice(types)
        
        if chosen == 1:
            max_d = int(self.max_denom.text())
            f1 = Fraction(random.randint(self.n_min, self.n_max), random.randint(2, max_d))
            f2 = Fraction(random.randint(self.n_min, self.n_max), random.randint(2, max_d))
            op = random.choice(allowed_ops)
            res = f1 + f2 if op == '+' else f1 - f2 if op == '-' else f1 * f2 if op == '*' else f1 / f2
            return self.make_equation(f1, op, f2, res)
        elif chosen == 2:
            prec = int(self.dec_precision.text())
            d1 = round(random.uniform(self.n_min, self.n_max), prec)
            d2 = round(random.uniform(self.n_min, self.n_max), prec)
            op = random.choice(allowed_ops)
            if op == '/': d2 = d2 if d2 != 0 else 1.0
            res = d1 + d2 if op == '+' else d1 - d2 if op == '-' else d1 * d2 if op == '*' else d1 / d2
            return self.make_equation(d1, op, d2, round(res, prec))
        else:
            diff = self.diff_group.checkedId()
            if diff == 0:
                n2 = random.randint(self.n_min, self.n_max); op = random.choice(allowed_ops)
                if op == '/':
                    res = random.randint(self.n_min, self.n_max); n1 = n2 * res
                else:
                    n1 = random.randint(self.n_min, self.n_max); res = eval(f"{n1}{op}{n2}")
                return self.make_equation(n1, op, n2, res)
            else:
                count = [2, random.randint(3, 4), 5][diff]
                nums = [random.randint(self.n_min, self.n_max) for _ in range(count)]
                curr_ops = [random.choice(allowed_ops) for _ in range(count-1)]
                expr = str(nums[0])
                for i in range(len(curr_ops)): expr = f"({expr}){curr_ops[i]}{nums[i+1]}"
                self.hidden_value = round(float(eval(expr)), 2)
                parts = []
                for i in range(len(nums)):
                    parts.append(nums[i])
                    if i < len(curr_ops): parts.append(curr_ops[i].replace('*','×').replace('/','÷'))
                parts.extend(["=", "?"])
                return parts
            
    def stop_session(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Выход")
        msg.setText("Вы уверены, что хотите прервать тренировку?")
        msg.setIcon(QMessageBox.Icon.Question)

        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        msg.button(QMessageBox.StandardButton.Yes).setText("Да")
        msg.button(QMessageBox.StandardButton.No).setText("Нет")

        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.sbornik_layoutov.setCurrentIndex(5)
    def start_session(self):
        if not any(cb.isChecked() for cb in self.ops_boxes):
            QMessageBox.warning(self, "Ошибка", "Выберите операцию!")
            return
        try:
            self.n_min = int(self.range_min.text())
            self.n_max = int(self.range_max.text())
            self.limit = int(self.limit_input.text())
            while self.history_layout.count() > 1:
                child = self.history_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
        except:
            QMessageBox.warning(self, "Ошибка", "Числовые параметры!")
            return
        self.score = 0; self.total_attempts = 0
        self.session_stats = []
        self.next_question(force_init=True)
    def next_question(self, force_init=False):
        if self.total_attempts >= self.limit:
            self.history_title.setText(f"Тренировка завершена! Итог: {self.score} из {self.limit}")
            self.chart.update_chart(self.session_stats)
            self.sbornik_layoutov.setCurrentIndex(2); return

        self.current_problem_raw_parts = self.generate_problem_elements()
        self.problem_label.setText(self.assemble_math_html(self.current_problem_raw_parts))
        self.answer_input.clear(); self.answer_input.setEnabled(True); self.answer_input.setFocus()
        self.result_label.setText(""); self.already_answered = False
        self.score_label.setText(f"Пример {self.total_attempts + 1} из {self.limit} | Очки: {self.score}")
        self.action_btn.setText("Проверить")
        self.action_btn.setStyleSheet("background: #3498db; color: white; font-size: 18px; border-radius: 10px;")
        self.start_time = time.time()
        self.sbornik_layoutov.setCurrentIndex(1)

    def handle_action_btn(self):
        if not self.already_answered:
            self.check_answer()
        else:
            self.next_question()

    def check_answer(self):
        if self.already_answered: return
        solve_time = time.time() - self.start_time
        user_text = self.answer_input.text().strip().replace(',', '.')
        
        is_skip = (user_text == "")
        self.already_answered = True
        self.answer_input.setEnabled(False)
        self.total_attempts += 1
        is_correct = False

        if not is_skip:
            try:
                val = float(Fraction(user_text)) if '/' in user_text else float(user_text)
                if abs(val - float(self.hidden_value)) < 0.001:
                    is_correct = True; self.score += 1
            except: pass

        if is_correct:
            self.result_label.setText("<b style='color:#27ae60; font-size:26px;'>Правильно!</b>")
        else:
            status_txt = "ПРОПУЩЕНО" if is_skip else "ОШИБКА"
            ans_html = self.format_value_html(self.hidden_value, highlight=True)
            
            msg_html = (
                f"<div style='background: #fdf2f2; border: 1px solid #f5c6cb; border-radius: 10px; padding: 10px;'>"
                f"<table align='center' cellspacing='0' cellpadding='0'><tr>"
                f"<td style='color:#e74c3c; font-size:22px; font-weight:bold; padding-right:15px; vertical-align: middle;'>{status_txt}!</td>"
                f"<td style='color:#2c3e50; font-size:18px; padding-right:10px; vertical-align: middle;'>Правильный ответ:</td>"
                f"<td style='vertical-align: middle;'>{ans_html}</td>"
                f"</tr></table></div>"
            )
            self.result_label.setText(msg_html)

        self.add_to_history(user_text if user_text else "—", is_correct, solve_time)
        self.action_btn.setText("Далее →")
        self.action_btn.setStyleSheet("background: #2ecc71; color: white; font-size: 18px; border-radius: 10px;")

    def add_to_history(self, user_ans, is_ok, s_time):
        row = QFrame()
        row.setStyleSheet(f"background: white; border-radius: 8px; border-left: 5px solid {'#27ae60' if is_ok else '#e74c3c'};")
        row_lay = QHBoxLayout(row)
        hist_parts = [self.hidden_value if p == "?" else p for p in self.current_problem_raw_parts]
        info = QLabel(self.assemble_math_html(hist_parts, small=True))
        time_lbl = QLabel(f"⏱ {s_time:.1f} сек.")
        time_lbl.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        ans_info = QLabel(f"Ваш ответ: <b>{user_ans}</b>")
        ans_info.setStyleSheet(f"color: {'#27ae60' if is_ok else '#e74c3c'};")
        row_lay.addWidget(info); row_lay.addStretch(); row_lay.addWidget(time_lbl); row_lay.addWidget(ans_info)
        self.history_layout.insertWidget(0, row)

        self.session_stats.append((self.total_attempts, s_time, is_ok))
    def handle_return_pressed(self):
        self.handle_action_btn()
    # ОКНО СПРАВОЧНИКА
    def spravochnik(self):
        widjet = QWidget()
        glavnaya_korobka = QVBoxLayout(widjet)
        
        korobka_verh = QHBoxLayout()
        korobka_niz = QHBoxLayout()
        
        glavnaya_korobka.addLayout(korobka_verh)
        glavnaya_korobka.addLayout(korobka_niz)

        button3 = QPushButton("В меню")
        button3.clicked.connect(self.vozvrashenie_v_menu)
        korobka_verh.addWidget(button3)

        okno_s_knopkami = QScrollArea()
        widget_okna = QWidget()
        korob_okna = QVBoxLayout()
        self.slovar = {}

        self.spisok_knopok = []
        
        for i in results:
            btn_name = i[1]
            btn_path = i[2]
            
            self.primer_knopki = QPushButton(btn_name)
            self.primer_knopki.setStyleSheet("""QPushButton {
        background-color: #3498db;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        border: none;
            }""")
            self.slovar[btn_name] = btn_path
            self.primer_knopki.clicked.connect(self.nashatie_primer_knopki)
            
            korob_okna.addWidget(self.primer_knopki)
            self.spisok_knopok.append(self.primer_knopki)

        spacer1 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        korob_okna.addItem(spacer1)

        widget_okna.setLayout(korob_okna)

        okno_s_knopkami.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        okno_s_knopkami.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        okno_s_knopkami.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        okno_s_knopkami.setWidget(widget_okna)

        button3.setMinimumSize(QSize(50,50))
        korobka_niz.addWidget(okno_s_knopkami)

        self.okno_s_textom = QTextEdit()
        korobka_niz.addWidget(self.okno_s_textom)

        self.vvod_poiska = QLineEdit() 
        self.vvod_poiska.setPlaceholderText("Введите название темы...")
        self.vvod_poiska.textChanged.connect(self.filtr_poiska)
        korobka_verh.addWidget(self.vvod_poiska)




        self.sbornik_layoutov.addWidget(widjet)
    def filtr_poiska(self, text):
        search_text = text.lower()
        for btn in self.spisok_knopok:
            if search_text in btn.text().lower():
                btn.show()
            else:
                btn.hide()
    def nashata_knopka1(self, checked):
        pass
    def nashata_knopka2(self, checked):
        pass
    def nashatie_primer_knopki(self, checked):
        knopka = self.sender()
        read_file = open(self.slovar[knopka.text()], "r", encoding='utf-8')
        html_content = read_file.read()
        read_file.close()
        self.okno_s_textom.setHtml(html_content)
        self.okno_s_textom.setReadOnly(True)
    def vozvrashenie_v_menu(self):
        self.sbornik_layoutov.setCurrentIndex(3)
    def vibor_TESTIROVANIE(self, checked):
        self.sbornik_layoutov.setCurrentIndex(5)
    def vibor_SPRAVOCHNIK(self, checked):
        self.sbornik_layoutov.setCurrentIndex(4)
    def VYHOD(self, checked):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = math_spravochnik()
    window.show()
    sys.exit(app.exec())

#### Конец кода программы
