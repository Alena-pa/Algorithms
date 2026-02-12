import csv
import random
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import math


def calculate_kld(original_probs, anonymized_probs):
    kld = 0.0
    epsilon = 1e-10
    for i in range(len(original_probs)):
        p = original_probs[i] + epsilon
        q = anonymized_probs[i] + epsilon
        if p > 0 and q > 0:
            kld += p * math.log(p / q)
    return kld


def calculate_k_anonymity(df, quasi_identifiers):
    if not quasi_identifiers or df.empty:
        return 0, [], 0.0, 0, pd.DataFrame()

    grouped = df.groupby(quasi_identifiers, dropna=False).size().reset_index(name='count')
    k_values = grouped['count'].values

    min_k = int(np.min(k_values)) if len(k_values) > 0 else 0

    bad_k_mask = grouped['count'] < 10
    bad_k_groups = grouped[bad_k_mask]
    bad_k_values = bad_k_groups['count'].tolist()

    bad_k_percent = (len(bad_k_groups) / len(grouped)) * 100 if len(grouped) > 0 else 0

    k1_groups = grouped[grouped['count'] == 1]
    k1_count = len(k1_groups)

    return min_k, bad_k_values, bad_k_percent, k1_count, grouped


def local_generalization(df, quasi_identifiers):
    df_anon = df.copy()

    if 'ФИО' in df_anon.columns:
        def fio_to_gender(fio):
            if pd.isna(fio) or str(fio).strip() == '':
                return ''
            fio = str(fio).strip().lower()
            women_endings = ['ова', 'ева', 'ина', 'ына', 'ая']
            man_endings = ['ов', 'ев', 'ин', 'ын', 'ий', 'ой', 'юк', 'ко']
            parts = fio.split()
            last_name = parts[0] if parts else fio
            for end in women_endings:
                if last_name.endswith(end):
                    return 'Ж'
            for end in man_endings:
                if last_name.endswith(end):
                    return 'М'
            return 'М'
        df_anon['ФИО'] = df_anon['ФИО'].apply(fio_to_gender)

    if 'Паспорт' in df_anon.columns:
        df_anon['Паспорт'] = 'XX'

    if 'СНИЛС' in df_anon.columns:
        def mask_snils(snils):
            if pd.isna(snils) or str(snils).strip() == '':
                return ''
            snils_str = re.sub(r'\D', '', str(snils))
            if not snils_str:
                return ''
            last_digit = int(snils_str[-1])
            return '0-4' if last_digit <= 4 else '5-9'
        df_anon['СНИЛС'] = df_anon['СНИЛС'].apply(mask_snils)

    if 'Врач' in df_anon.columns:
        mapping = {
            "терапевт": "терапия",
            "невролог": "неврология",
            "психиатр": "неврология",
            "психолог": "неврология",
            "кардиолог": "кардиология",
            "пульмонолог": "пульмонология",
            "гастроэнтеролог": "гастроэнтерология",
            "дерматолог": "дерматология",
            "аллерголог": "дерматология",
            "лор": "оториноларингология",
            "оториноларинголог": "оториноларингология",
            "хирург": "хирургия",
            "травматолог": "хирургия",
            "ортопед": "хирургия",
            "гинеколог": "репродуктивная медицина",
            "уролог": "репродуктивная медицина",
            "нефролог": "репродуктивная медицина",
            "инфекционист": "инфекционные болезни",
            "реаниматолог": "реаниматология"
        }
        df_anon['Врач'] = df_anon['Врач'].str.lower().map(mapping).fillna('прочее')

    if 'Симптомы' in df_anon.columns:
        if 'Врач' in quasi_identifiers and 'Врач' in df_anon.columns:
            df_anon['Симптомы'] = df_anon['Врач']
        else:
            def grouped_symptoms(text):
                if pd.isna(text) or str(text).strip() == '':
                    return ''
                n = len(str(text).split(','))
                return "Мало симптомов" if n <= 5 else "Много симптомов"
            df_anon['Симптомы'] = df_anon['Симптомы'].apply(grouped_symptoms)

    if 'Анализы' in df_anon.columns:
        if 'Врач' in quasi_identifiers and 'Врач' in df_anon.columns:
            df_anon['Анализы'] = df_anon['Врач']
        else:
            def grouped_analyses(text):
                if pd.isna(text) or str(text).strip() == '':
                    return ''
                n = len(str(text).split(','))
                return "Мало анализов" if n <= 3 else "Много анализов"
            df_anon['Анализы'] = df_anon['Анализы'].apply(grouped_analyses)

    for col in ['Дата визита', 'Дата получения', 'Повторный прием']:
        if col in df_anon.columns:
            def mask_date(date_val):
                if pd.isna(date_val) or str(date_val).strip() == '':
                    return ''
                s = str(date_val)
                if len(s) >= 4:
                    try:
                        year = int(s[:4])
                        if 2020 <= year <= 2022:
                            return "2020-2022"
                        elif 2023 <= year <= 2025:
                            return "2023-2025"
                        else:
                            return "Другое"
                    except:
                        return "Некорректная дата"
                return ''
            df_anon[col] = df_anon[col].apply(mask_date)

    if 'Стоимость' in df_anon.columns:
        def local_price(price):
            if pd.isna(price) or str(price).strip() == '':
                return ''
            s = re.sub(r'\D', '', str(price))
            if not s:
                return ''
            val = int(s)
            return "0 - 7000" if val <= 7000 else "> 7000"
        df_anon['Стоимость'] = df_anon['Стоимость'].apply(local_price)

    if 'Карта' in df_anon.columns:
        def detect_card_scheme(card):
            if pd.isna(card) or str(card).strip() == '':
                return ''
            s = re.sub(r'\D', '', str(card))
            if not s:
                return ''
            if s.startswith('4'):
                return 'Visa'
            if len(s) >= 2:
                first2 = int(s[:2])
                if 51 <= first2 <= 55:
                    return 'Mastercard'
            if len(s) >= 6:
                first6 = int(s[:6])
                if 222100 <= first6 <= 272099:
                    return 'Mastercard'
            if len(s) >= 4:
                first4 = int(s[:4])
                if 2200 <= first4 <= 2204:
                    return 'Mir'
            return 'Unknown'
        df_anon['Карта'] = df_anon['Карта'].apply(detect_card_scheme)

    return df_anon


class AnonymizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №2 - Обезличивание данных")
        self.root.geometry("900x700")

        self.input_file = ""
        self.output_file = "Depersonalization.csv"
        self.quasi_identifiers = []
        self.df_original = None
        self.df_anonymized = None

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Обезличивание данных", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="Загрузить файл", command=self.load_file).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Рассчитать K-анонимность", command=self.calculate_k).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Обезличить", command=self.anonymize).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Сохранить датасет", command=self.save_file).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Выход", command=self.root.quit).grid(row=0, column=4, padx=5)

        ttk.Label(frame, text="Выберите квази-идентификаторы:").grid(row=2, column=0, sticky=tk.W, pady=5)

        self.check_vars = {}
        self.identifiers = [
            "ФИО", "Паспорт", "СНИЛС", "Симптомы", "Врач", "Дата визита",
            "Анализы", "Дата получения", "Стоимость", "Карта", "Повторный прием"
        ]

        checkbox_frame = ttk.Frame(frame)
        checkbox_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        for i, ident in enumerate(self.identifiers):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(checkbox_frame, text=ident, variable=var)
            chk.grid(row=i // 3, column=i % 3, sticky=tk.W, padx=10, pady=2)
            self.check_vars[ident] = var

        ttk.Label(frame, text="Топ плохих K-анонимность (K < 10)").grid(row=2, column=2, sticky=tk.W, pady=5, padx=10)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=3, column=2, rowspan=6, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)

        self.tree = ttk.Treeview(tree_frame, columns=("K", "Количество", "Процент"), show="headings", height=10)
        self.tree.heading("K", text="K")
        self.tree.heading("Количество", text="Кол-во групп")
        self.tree.heading("Процент", text="% от всех групп")
        self.tree.column("K", width=50)
        self.tree.column("Количество", width=100)
        self.tree.column("Процент", width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(frame, text="Имя файла ввода:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.input_entry = ttk.Entry(frame, width=50)
        self.input_entry.grid(row=10, column=1, columnspan=2, sticky=tk.W, padx=5)

        ttk.Label(frame, text="Имя файла вывода:").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(frame, width=50)
        self.output_entry.insert(0, "Depersonalization.csv")
        self.output_entry.grid(row=11, column=1, columnspan=2, sticky=tk.W, padx=5)

        result_frame = ttk.LabelFrame(frame, text="Результаты анализа", padding="10")
        result_frame.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.result_text = tk.Text(result_frame, height=8, width=80, wrap="word")
        self.result_text.pack(fill="both", expand=True)

        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        result_scrollbar.pack(side="right", fill="y")

    def load_file(self):
        self.input_file = filedialog.askopenfilename(
            title="Выберите входной CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if self.input_file:
            try:
                try:
                    self.df_original = pd.read_csv(self.input_file, delimiter=';', encoding='utf-8-sig')
                except:
                    self.df_original = pd.read_csv(self.input_file, delimiter=',', encoding='utf-8-sig')

                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, self.input_file)

                msg = f"Файл загружен успешно!\n"
                msg += f"Количество записей: {len(self.df_original)}\n"
                msg += f"Количество столбцов: {len(self.df_original.columns)}\n"
                msg += f"Столбцы: {', '.join(self.df_original.columns.tolist())}"

                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, msg)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def calculate_k(self):
        if self.df_original is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл!")
            return

        self.quasi_identifiers = [ident for ident, var in self.check_vars.items() if var.get()]
        if not self.quasi_identifiers:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы один квази-идентификатор!")
            return

        min_k, bad_k_values, bad_k_percent, k1_count, groups_info = calculate_k_anonymity(
            self.df_original, self.quasi_identifiers
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        if bad_k_values:
            bad_k_counter = Counter(bad_k_values)
            for k_val, count in bad_k_counter.most_common(10):
                percent = (count / len(groups_info)) * 100 if len(groups_info) > 0 else 0
                self.tree.insert("", "end", values=(k_val, count, f"{percent:.2f}%"))

        total_groups = len(groups_info)
        total_records = len(self.df_original)

        msg = f"=== АНАЛИЗ K-АНОНИМНОСТИ (ИСХОДНЫЕ ДАННЫЕ) ===\n\n"
        msg += f"Выбранные квази-идентификаторы: {', '.join(self.quasi_identifiers)}\n\n"
        msg += f"Общее количество записей: {total_records}\n"
        msg += f"Количество уникальных групп: {total_groups}\n"
        msg += f"Минимальное K: {min_k}\n"
        msg += f"Групп с K=1 (уникальные комбинации): {k1_count}\n"
        msg += f"Групп с K<10 (плохие): {len(bad_k_values)} ({bad_k_percent:.2f}% от всех групп)\n\n"

        if total_records <= 51000:
            recommended_k = 10
        elif total_records <= 105000:
            recommended_k = 7
        else:
            recommended_k = 5

        msg += f"Рекомендованное K для датасета размером {total_records}: {recommended_k}\n"

        if min_k >= recommended_k:
            msg += f"✓ Датасет удовлетворяет рекомендованному уровню K-анонимности\n"
        else:
            msg += f"✗ Датасет НЕ удовлетворяет рекомендованному уровню K-анонимности\n"
            msg += f"  Необходимо обезличивание для повышения K до {recommended_k}\n"

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, msg)

    def anonymize(self):
        if self.df_original is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл!")
            return

        all_possible = [
            'ФИО', 'Паспорт', 'СНИЛС', 'Симптомы', 'Врач',
            'Дата визита', 'Анализы', 'Дата получения',
            'Стоимость', 'Карта', 'Повторный прием'
        ]

        try:
            self.df_anonymized = local_generalization(self.df_original, all_possible)
        except Exception as e:
            messagebox.showerror("Ошибка обезличивания", f"Не удалось обезличить данные:\n{str(e)}")
            return

        quasi_for_k = [col for col in all_possible if col in self.df_anonymized.columns]

        min_k_before, _, _, k1_before, groups_before = calculate_k_anonymity(
            self.df_original, quasi_for_k
        )
        min_k_after, bad_k_after, bad_k_percent_after, k1_after, groups_after = calculate_k_anonymity(
            self.df_anonymized, quasi_for_k
        )

        kld_value = 0.0
        if 'Стоимость' in self.df_original.columns and 'Стоимость' in self.df_anonymized.columns:
            try:
                cost_orig = self.df_original['Стоимость'].str.replace(' руб.', '').str.replace(' ', '')
                cost_orig = pd.to_numeric(cost_orig, errors='coerce').dropna()

                cost_anon_dist = self.df_anonymized['Стоимость'].value_counts(normalize=True, dropna=False)

                bins = [0, 1000, 3000, 5000, 7000, 10000, float('inf')]
                labels = ['0-1000', '1001-3000', '3001-5000', '5001-7000', '7001-10000', '10001+']
                cost_orig_binned = pd.cut(cost_orig, bins=bins, labels=labels, right=False)
                cost_orig_dist = cost_orig_binned.value_counts(normalize=True, dropna=False)

                all_categories = set(labels)
                orig_probs = [cost_orig_dist.get(cat, 0) for cat in all_categories]
                anon_probs = [cost_anon_dist.get(cat, 0) for cat in all_categories]

                orig_sum = sum(orig_probs)
                anon_sum = sum(anon_probs)
                if orig_sum > 0:
                    orig_probs = [p / orig_sum for p in orig_probs]
                if anon_sum > 0:
                    anon_probs = [p / anon_sum for p in anon_probs]

                kld_value = calculate_kld(orig_probs, anon_probs)
            except Exception as e:
                pass

        total_records = len(self.df_anonymized)

        msg = f"=== РЕЗУЛЬТАТЫ ОБЕЗЛИЧИВАНИЯ ===\n\n"
        msg += f"--- ДО ОБЕЗЛИЧИВАНИЯ ---\n"
        msg += f"Минимальное K: {min_k_before}\n"
        msg += f"Уникальных групп: {len(groups_before)}\n"
        msg += f"Групп с K=1: {k1_before}\n\n"
        msg += f"--- ПОСЛЕ ОБЕЗЛИЧИВАНИЯ ---\n"
        msg += f"Минимальное K: {min_k_after}\n"
        msg += f"Уникальных групп: {len(groups_after)}\n"
        msg += f"Групп с K=1: {k1_after}\n"
        msg += f"Групп с K<10: {len(bad_k_after)} ({bad_k_percent_after:.2f}%)\n\n"

        msg += f"--- ОЦЕНКА ПОЛЕЗНОСТИ ДАННЫХ ---\n"
        msg += f"KL-дивергенция (по стоимости): {kld_value:.4f}\n"
        if kld_value < 0.1:
            msg += "Отличная сохранность данных (очень низкая потеря информации)\n"
        elif kld_value < 0.5:
            msg += "Хорошая сохранность данных (низкая потеря информации)\n"
        elif kld_value < 1.0:
            msg += "Приемлемая сохранность данных (умеренная потеря информации)\n"
        else:
            msg += "Значительная потеря информации\n"

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, msg)

        messagebox.showinfo("Успех", "Обезличивание выполнено успешно!\nТеперь вы можете сохранить результат.")

    def save_file(self):
        if self.df_anonymized is None:
            messagebox.showwarning("Предупреждение", "Сначала выполните обезличивание!")
            return

        self.output_file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Сохранить обезличенный файл"
        )

        if self.output_file:
            try:
                if self.output_file.endswith('.xlsx'):
                    self.df_anonymized.to_excel(self.output_file, index=False)
                else:
                    self.df_anonymized.to_csv(self.output_file, sep=';', index=False, encoding='utf-8-sig')

                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, self.output_file)
                messagebox.showinfo("Успех", f"Файл успешно сохранен:\n{self.output_file}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnonymizationApp(root)
    root.mainloop()