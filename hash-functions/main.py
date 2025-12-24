import pandas as pd
import openpyxl
import os

# --- НАСТРОЙКИ ---
# Укажи точное имя своего файла Excel
FILE_NAME = 'data_вар7.xlsx'
# Файл, куда ты сохранишь расшифрованные хеши (11-значные числа)
CRACKED_FILE = 'numbers_only.txt'
# Итоговый результат
RESULT_FILE = 'final_phones.txt'


def main():
    print(f"--- Запуск деобфускации для {FILE_NAME} ---")

    # 1. Читаем Excel
    try:
        # Для работы этого шага нужен: pip install openpyxl
        df = pd.read_excel(FILE_NAME)
    except Exception as e:
        print(f"Ошибка при чтении Excel: {e}")
        return

    # 2. Берем известные номера (они в 3-м столбце)
    # dropna() убирает пустые клетки, astype(int) делает числами
    known_phones = df.iloc[:, 2].dropna().astype(int).tolist()

    if not known_phones:
        print("Ошибка: Не нашли открытых номеров в 3-м столбце Excel.")
        return

    print(f"Найдено открытых номеров (образцов): {len(known_phones)}")

    # 3. Загружаем числа после взлома MD5
    if not os.path.exists(CRACKED_FILE):
        print(f"Ошибка: Файл {CRACKED_FILE} не найден!")
        print(f"Инструкция: Скопируй хеши из Excel, взломай их и сохрани числа в {CRACKED_FILE}")
        return

    with open(CRACKED_FILE, 'r') as f:
        decimals = [int(line.strip()) for line in f if line.strip()]

    # 4. Вычисляем соль (Salt)
    # Соль — это число, которое прибавили к каждому номеру
    possible_salts = []
    for phone in known_phones:
        # Для каждого известного номера смотрим, какая разница с расшифрованными числами
        deltas = {d - phone for d in decimals}
        possible_salts.append(deltas)

    # Ищем общее число (пересечение), которое подошло ко всем номерам
    common_salt = set.intersection(*possible_salts)

    if not common_salt:
        print("Ошибка: Соль не найдена. Возможно, хеши расшифрованы неверно.")
        return

    found_salt = list(common_salt)[0]
    print(f"Успех! Твоя секретная соль: {found_salt}")

    # 5. Восстанавливаем все номера
    print("Восстанавливаем базу...")
    final_numbers = [d - found_salt for d in decimals]

    # Сохраняем
    with open(RESULT_FILE, 'w') as f:
        for num in final_numbers:
            f.write(f"{num}\n")

    print(f"Готово! Все номера (всего {len(final_numbers)} шт.) сохранены в {RESULT_FILE}")


if __name__ == "__main__":
    main()