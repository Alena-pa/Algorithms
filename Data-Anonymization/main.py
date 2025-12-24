import csv
import random
import os
import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import math


# Для расстояния Кульбака-Лейблера
def calculate_kld(original_probs, anonymized_probs):
    """Расчет KLD = Σ p_i * log(p_i / q_i)"""
    kld = 0.0
    for i in range(len(original_probs)):
        p = original_probs[i]
        q = anonymized_probs[i]
        if p > 0 and q > 0:
            kld += p * math.log(p / q)
    return kld


# Функция для подсчета K-анонимити по выбранным квази-идентификаторам
def calculate_k_anonymity(df, quasi_identifiers):
    grouped = df.groupby(quasi_identifiers).size()
    k_values = grouped.values
    min_k = np.min(k_values) if len(k_values) > 0 else 0
    # Найдем "плохие" K (меньше порога, например, < 10)
    bad_k_values = [k for k in k_values if k < 10]
    bad_k_percent = (len(bad_k_values) / len(k_values)) * 100 if len(k_values) > 0 else 0
    unique_rows = len(grouped)  # при K=1 — это количество уникальных групп
    return min_k, bad_k_values, bad_k_percent, unique_rows


# Локальное обобщение (например, для даты — округление до дня/недели; для стоимости — диапазоны)
def local_generalization(df, quasi_identifiers):
    df_anon = df.copy()

    # Обобщение даты визита и получения (оставляем только дату, без времени)
    if 'Дата визита' in quasi_identifiers or 'Дата получения' in quasi_identifiers:
        for col in ['Дата визита', 'Дата получения']:
            if col in df_anon.columns:
                df_anon[col] = pd.to_datetime(df_anon[col]).dt.date

    # Обобщение стоимости: разбиваем на диапазоны
    if 'Стоимость' in quasi_identifiers:
        bins = [0, 500, 1000, 2000, 5000, 10000, float('inf')]
        labels = ['0-500', '501-1000', '1001-2000', '2001-5000', '5001-10000', '10001+']
        df_anon['Стоимость'] = pd.cut(pd.to_numeric(df_anon['Стоимость'].str.replace(' руб.', ''), errors='coerce'),
                                      bins=bins, labels=labels, right=False)

    # Обобщение ФИО: оставляем только первую букву имени и фамилии
    if 'ФИО' in quasi_identifiers:
        df_anon['ФИО'] = df_anon['ФИО'].apply(
            lambda x: f"{x.split()[0][0]}. {x.split()[1][0]}." if len(x.split()) >= 2 else x)

    # Обобщение паспорта: оставляем только первые 2 цифры серии и последние 2 цифры номера
    if 'Паспорт' in quasi_identifiers:
        def generalize_passport(p):
            parts = p.split()
            if len(parts) == 2:
                series = parts[0][:2] + "**"
                number = "**" + parts[1][-2:]
                return f"{series} {number}"
            return p

        df_anon['Паспорт'] = df_anon['Паспорт'].apply(generalize_passport)

    # Обобщение СНИЛС: оставляем только первые 3 и последние 2 цифры
    if 'СНИЛС' in quasi_identifiers:
        df_anon['СНИЛС'] = df_anon['СНИЛС'].apply(lambda x: x[:3] + "***" + x[-2:] if len(x) == 14 else x)

    # Обобщение карты: маскируем номер
    if 'Карта' in quasi_identifiers:
        def mask_card(card):
            parts = card.split('|')
            if len(parts) >= 3:
                card_num = parts[2].strip().split()
                masked = [card_num[0][:4] + " **** **** " + card_num[3]] if len(card_num) == 4 else [
                    "**** **** **** ****"]
                return f"{parts[0]} | {parts[1]} | {' '.join(masked)}"
            return card

        df_anon['Карта'] = df_anon['Карта'].apply(mask_card)

    return df_anon


class AnonymizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №2 - Обезличивание данных")
        self.root.geometry("800x600")

        self.input_file = ""
        self.output_file = "Depersonalization.csv"
        self.quasi_identifiers = []
        self.df_original = None
        self.df_anonymized = None

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Заголовок
        ttk.Label(frame, text="Обезличивание данных", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2,
                                                                                       pady=10)

        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Загрузить файл", command=self.load_file).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Рассчитать k-anonymity", command=self.calculate_k).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Обезличить", command=self.anonymize).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Сохранить датасет", command=self.save_file).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Выход", command=self.root.quit).grid(row=0, column=4, padx=5)

        # Выбор квази-идентификаторов
        ttk.Label(frame, text="Выберите квази-идентификаторы:").grid(row=2, column=0, sticky=tk.W, pady=5)

        self.check_vars = {}
        identifiers = [
            "ФИО", "Паспорт", "СНИЛС", "Симптомы", "Врач", "Дата визита",
            "Анализы", "Дата получения", "Стоимость", "Карта", "Повторный прием"
        ]

        for i, ident in enumerate(identifiers):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(frame, text=ident, variable=var)
            chk.grid(row=3 + i // 2, column=i % 2, sticky=tk.W, padx=10, pady=2)
            self.check_vars[ident] = var

        # Таблица "Топ плохих k anonymity"
        ttk.Label(frame, text="Топ плохих k anonymity").grid(row=3, column=2, columnspan=2, sticky=tk.W, pady=5)
        self.tree = ttk.Treeview(frame, columns=("K", "Процент"), show="headings", height=5)
        self.tree.heading("K", text="K")
        self.tree.heading("Процент", text="Процент от набора")
        self.tree.column("K", width=50)
        self.tree.column("Процент", width=100)
        self.tree.grid(row=4, column=2, rowspan=5, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)

        # Поля для имён файлов
        ttk.Label(frame, text="Имя файла ввода:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.input_entry = ttk.Entry(frame, width=40)
        self.input_entry.grid(row=10, column=1, sticky=tk.W, padx=5)

        ttk.Label(frame, text="Имя файла вывода:").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(frame, width=40)
        self.output_entry.insert(0, "Depersonalization.csv")
        self.output_entry.grid(row=11, column=1, sticky=tk.W, padx=5)

        # Результаты
        self.result_label = ttk.Label(frame, text="", foreground="blue")
        self.result_label.grid(row=12, column=0, columnspan=2, pady=10)

    def load_file(self):
        self.input_file = filedialog.askopenfilename(title="Выберите входной CSV файл",
                                                     filetypes=[("CSV files", "*.csv")])
        if self.input_file:
            try:
                self.df_original = pd.read_csv(self.input_file, delimiter=';', encoding='utf-8-sig')
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, self.input_file)
                self.result_label.config(text=f"Файл загружен: {len(self.df_original)} записей")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def calculate_k(self):
        if self.df_original is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл!")
            return

        self.quasi_identifiers = [ident for ident, var in self.check_vars.items() if var.get()]
        if not self.quasi_identifiers:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы один квази-идентификатор!")
            return

        min_k, bad_k_values, bad_k_percent, unique_rows = calculate_k_anonymity(self.df_original,
                                                                                self.quasi_identifiers)

        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление "плохих" K
        bad_k_counter = Counter(bad_k_values)
        for k_val, count in bad_k_counter.most_common(5):  # top 5
            percent = (count / len(bad_k_values)) * 100 if bad_k_values else 0
            self.tree.insert("", "end", values=(k_val, f"{percent:.2f}%"))

        # Вывод результата
        msg = f"Минимальное K: {min_k}\nУникальных строк (K=1): {unique_rows}\nПлохих K (<10): {len(bad_k_values)} ({bad_k_percent:.2f}%)"
        self.result_label.config(text=msg)

    def anonymize(self):
        if self.df_original is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл!")
            return

        if not self.quasi_identifiers:
            messagebox.showwarning("Предупреждение", "Выберите квази-идентификаторы для обезличивания!")
            return

        self.df_anonymized = local_generalization(self.df_original, self.quasi_identifiers)

        # Расчет K после обезличивания
        min_k_after, _, _, _ = calculate_k_anonymity(self.df_anonymized, self.quasi_identifiers)

        # Оценка полезности: KLD по распределению стоимости (пример)
        # Сравним распределение стоимости до и после
        cost_orig = pd.to_numeric(self.df_original['Стоимость'].str.replace(' руб.', ''), errors='coerce').dropna()
        cost_anon = pd.to_numeric(self.df_anonymized['Стоимость'].str.replace(' руб.', ''), errors='coerce').dropna()

        # Создадим гистограммы
        bins = np.linspace(0, 10000, 11)
        hist_orig, _ = np.histogram(cost_orig, bins=bins, density=True)
        hist_anon, _ = np.histogram(cost_anon, bins=bins, density=True)

        # Нормализуем (на случай, если сумма не 1)
        hist_orig = hist_orig / np.sum(hist_orig) if np.sum(hist_orig) > 0 else hist_orig
        hist_anon = hist_anon / np.sum(hist_anon) if np.sum(hist_anon) > 0 else hist_anon

        kld_value = calculate_kld(hist_orig, hist_anon)

        msg = f"Обезличивание выполнено.\nНовое минимальное K: {min_k_after}\nKLD (полезность): {kld_value:.4f}"
        self.result_label.config(text=msg)

    def save_file(self):
        if self.df_anonymized is None:
            messagebox.showwarning("Предупреждение", "Сначала выполните обезличивание!")
            return

        self.output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                                        title="Сохранить обезличенный файл")
        if self.output_file:
            self.df_anonymized.to_csv(self.output_file, sep=';', index=False, encoding='utf-8-sig')
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_file)
            messagebox.showinfo("Успех", f"Файл сохранен: {self.output_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnonymizationApp(root)
    root.mainloop()