# dataset_generator.py
import csv
import random
import os
import re
from datetime import datetime, timedelta


class DatasetGenerator:
    def __init__(self, data_path):
        self.DATA_PATH = data_path

    def load_list(self, filename):
        """Загрузка списка из файла"""
        full_path = os.path.join(self.DATA_PATH, filename)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Файл {filename} не найден. Используем тестовые данные.")
            if 'surname' in filename.lower():
                return ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев',
                        'Морозов', 'Новиков', 'Федоров', 'Волков', 'Алексеев', 'Лебедев', 'Семенов']
            elif 'name' in filename.lower():
                return ['Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей', 'Алексей', 'Артем',
                        'Илья', 'Кирилл', 'Михаил', 'Никита', 'Матвей', 'Роман', 'Егор']
            elif 'patronymic' in filename.lower():
                return ['Александрович', 'Дмитриевич', 'Максимович', 'Сергеевич', 'Андреевич',
                        'Алексеевич', 'Артемович', 'Ильич', 'Кириллович', 'Михайлович']
            else:
                return ['Данные 1', 'Данные 2', 'Данные 3', 'Данные 4', 'Данные 5']

    def clean_name(self, text):
        """Очистка имени от специальных символов"""
        text = re.sub(r'\[.*?\]', '', text)
        return text.replace('#', '').strip().lower()

    def get_working_day(self, dt):
        """Корректировка даты на рабочий день и время"""
        if dt.weekday() >= 5:
            dt += timedelta(days=(7 - dt.weekday()))
        if dt.hour < 8 or dt.hour > 18:
            dt = dt.replace(hour=random.randint(9, 17), minute=random.choice([0, 30]))
        return dt

    def generate_dataset(self, size=30000, filename='medical_dataset.csv'):
        """Генерация медицинского датасета"""
        # Загрузка данных
        surnames = self.load_list('surnames.txt')
        names = self.load_list('names.txt')
        patronymics = self.load_list('patronymics.txt')

        bank_names = ['GAZPROMBANK', 'MTS BANK', 'SBERBANK', 'TINKOFF BANK', 'VTB BANK']
        pay_systems = ['MIR', 'VISA', 'MASTERCARD']

        # Если файлы врачей и анализов отсутствуют, создаем тестовые данные
        try:
            # Словари врачей и анализов
            doc_symptoms = {}
            with open(os.path.join(self.DATA_PATH, 'doctors.txt'), 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        name_part, symp_part = line.split(':', 1)
                        name = self.clean_name(name_part)
                        doc_symptoms[name] = [s.strip() for s in symp_part.split(',')]

            doc_tests = {}
            with open(os.path.join(self.DATA_PATH, 'analyses.txt'), 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        name_part, tests_part = line.split(':', 1)
                        name = self.clean_name(name_part)
                        matches = re.findall(r'"(.*?)"\s*:\s*(\d+)', tests_part)
                        tests = [{'n': t_name.strip(), 'p': int(t_price)} for t_name, t_price in matches]
                        if tests:
                            doc_tests[name] = tests

            common_docs = list(set(doc_symptoms.keys()) & set(doc_tests.keys()))
            if not common_docs:
                common_docs = ['терапевт', 'кардиолог', 'невролог', 'гастроэнтеролог']

        except FileNotFoundError:
            print("Файлы врачей и анализов не найдены. Используем тестовые данные.")
            common_docs = ['терапевт', 'кардиолог', 'невролог', 'гастроэнтеролог']
            doc_symptoms = {
                'терапевт': ['кашель', 'температура', 'боль в горле', 'насморк', 'слабость'],
                'кардиолог': ['боль в груди', 'одышка', 'головокружение', 'учащенное сердцебиение'],
                'невролог': ['головная боль', 'головокружение', 'нарушение сна', 'тревожность'],
                'гастроэнтеролог': ['боль в животе', 'тошнота', 'изжога', 'нарушение стула']
            }
            doc_tests = {
                'терапевт': [{'n': 'Общий анализ крови', 'p': 850}, {'n': 'Биохимический анализ', 'p': 1500}],
                'кардиолог': [{'n': 'ЭКГ', 'p': 1200}, {'n': 'УЗИ сердца', 'p': 2500}],
                'невролог': [{'n': 'ЭЭГ', 'p': 1800}, {'n': 'МРТ головного мозга', 'p': 5000}],
                'гастроэнтеролог': [{'n': 'УЗИ брюшной полости', 'p': 2200}, {'n': 'ФГДС', 'p': 3000}]
            }

        # Генерация датасета
        card_limit = {}

        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["ФИО", "Паспорт", "СНИЛС", "Симптомы", "Врач", "Дата визита",
                             "Анализы", "Дата получения", "Стоимость", "Карта", "Повторный прием"])

            for i in range(size):
                doc = random.choice(common_docs)
                fio = f"{random.choice(surnames)} {random.choice(names)} {random.choice(patronymics)}"

                # Симптомы
                if doc in doc_symptoms:
                    symps = ", ".join(random.sample(doc_symptoms[doc], k=min(3, len(doc_symptoms[doc]))))
                else:
                    symps = "общее недомогание"

                # Анализы и стоимость
                if doc in doc_tests:
                    available_tests = doc_tests[doc]
                    k = min(random.randint(1, 3), len(available_tests))
                    current_tests = random.sample(available_tests, k=k)
                    t_names = " + ".join([t['n'] for t in current_tests])
                    total_p = sum(t['p'] for t in current_tests)
                else:
                    t_names = "Общий анализ"
                    total_p = random.randint(500, 3000)

                # Даты
                v_date = self.get_working_day(datetime(2024, random.randint(1, 12),
                                                       random.randint(1, 28), random.randint(8, 17)))
                res_date = self.get_working_day(v_date + timedelta(hours=random.randint(24, 72)))
                re_visit = self.get_working_day(res_date + timedelta(hours=25))

                # Карта
                card = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} " \
                       f"{random.randint(1000, 9999)} {random.randint(1000, 9999)}"
                if card_limit.get(card, 0) >= 5:
                    card = f"4444 {random.randint(1000, 9999)} {random.randint(1000, 9999)} " \
                           f"{random.randint(1000, 9999)}"
                card_limit[card] = card_limit.get(card, 0) + 1

                # Платежная информация
                curr_pay_sys = random.choice(pay_systems)
                pay_info = f"{random.choice(bank_names)} | {curr_pay_sys} | {card}"

                # Паспорт и СНИЛС
                passport = f"{random.randint(10, 99)} {random.randint(10, 99)} {random.randint(100000, 999999)}"
                snils = f"{random.randint(100, 999):03}-{random.randint(100, 999):03}-" \
                        f"{random.randint(100, 999):03} {random.randint(10, 99):02}"

                writer.writerow([
                    fio,
                    passport,
                    snils,
                    symps,
                    doc.capitalize(),
                    v_date.strftime("%Y-%m-%dT%H:%M"),
                    t_names,
                    res_date.strftime("%Y-%m-%dT%H:%M"),
                    f"{total_p} руб.",
                    pay_info,
                    re_visit.strftime("%Y-%m-%dT%H:%M")
                ])

        print(f"Файл {filename} успешно создан! Размер: {size}")
        return filename