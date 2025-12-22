import csv
import random
import os
import re
from datetime import datetime, timedelta

DATA_PATH = r"C:\Users\Alena\source\repos\Algorithms\Dataset\Dataset\data"

def load_list(filename):
    full_path = os.path.join(DATA_PATH, filename)
    with open(full_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def clean_name(text):
    text = re.sub(r'\[.*?\]', '', text)
    return text.replace('#', '').strip().lower()

surnames = load_list('surnames.txt')
names = load_list('names.txt')
patronymics = load_list('patronymics.txt')

doc_symptoms = {}
with open(os.path.join(DATA_PATH, 'doctors.txt'), 'r', encoding='utf-8') as f:
    for line in f:
        if ':' in line:
            name_part, symp_part = line.split(':', 1)
            name = clean_name(name_part)
            doc_symptoms[name] = [s.strip() for s in symp_part.split(',')]

doc_tests = {}
with open(os.path.join(DATA_PATH, 'analyses.txt'), 'r', encoding='utf-8') as f:
    for line in f:
        if ':' in line:
            name_part, tests_part = line.split(':', 1)
            name = clean_name(name_part)
            matches = re.findall(r'"(.*?)"\s*:\s*(\d+)', tests_part)
            tests = []
            for t_name, t_price in matches:
                tests.append({'n': t_name.strip(), 'p': int(t_price)})
            if tests:
                doc_tests[name] = tests

if 'лор' in doc_tests: doc_tests['отоларинголог'] = doc_tests['лор']

common_docs = list(set(doc_symptoms.keys()) & set(doc_tests.keys()))

def get_working_day(dt):
    if dt.weekday() >= 5:
        dt += timedelta(days=(7 - dt.weekday()))
    if dt.hour < 8 or dt.hour > 18:
        dt = dt.replace(hour=random.randint(9, 17), minute=random.choice([0, 30]))
    return dt

def generate_passport():
    mode = random.choice(['RU', 'BY', 'KZ'])
    if mode == 'RU':
        return f"{random.randint(10, 99)} {random.randint(10, 99)} {random.randint(100000, 999999)}"
    elif mode == 'BY':
        return f"AB{random.randint(1000000, 9999999)}"
    else:
        return f"N{random.randint(10000000, 99999999)}"

card_limit = {}
bank_names = ['GAZPROMBANK', 'MTS BANK', 'SBERBANK OF RUSSIA', 'TINKOFF BANK', 'VTB BANK']
pay_systems = ['MIR', 'VISA', 'MASTERCARD']

with open('medical_dataset.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(["ФИО", "Паспорт", "СНИЛС", "Симптомы", "Врач", "Дата визита",
                     "Анализы", "Дата получения", "Стоимость", "Карта", "Повторный прием"])

    for _ in range(50000):
        doc = random.choice(common_docs)
        fio = f"{random.choice(surnames)} {random.choice(names)} {random.choice(patronymics)}"
        symps = ", ".join(random.sample(doc_symptoms[doc], k=random.randint(1, 3)))
        current_tests = random.sample(doc_tests[doc], k=random.randint(1, min(len(doc_tests[doc]), 3)))
        t_names = " + ".join([t['n'] for t in current_tests])
        total_p = sum(t['p'] for t in current_tests)
        v_date = get_working_day(datetime(2024, random.randint(1, 12), random.randint(1, 28), random.randint(8, 17)))
        res_date = get_working_day(v_date + timedelta(hours=random.randint(24, 72)))
        re_visit = get_working_day(res_date + timedelta(hours=25))
        card = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        if card_limit.get(card, 0) >= 5:
            card = f"4444 {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        card_limit[card] = card_limit.get(card, 0) + 1
        pay_info = f"{random.choice(bank_names)} | {random.choice(pay_systems)} | {card}"
        writer.writerow([
            fio, generate_passport(),
            f"{random.randint(100, 999):03}-{random.randint(100, 999):03}-{random.randint(100, 999):03} {random.randint(10, 99):02}",
            symps, doc.capitalize(), v_date.strftime("%Y-%m-%dT%H:%M"),
            t_names, res_date.strftime("%Y-%m-%dT%H:%M"), f"{total_p} руб.",
            pay_info, re_visit.strftime("%Y-%m-%dT%H:%M")
        ])

print("Файл успешно создан!")
