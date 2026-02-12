import pandas as pd
import subprocess
import os


def load_data(file_path):
    """Читает хеши и контрольные номера из Excel."""
    # dtype=str важен, чтобы хеши не превратились в числа с ошибками
    df = pd.read_excel(file_path, header=None, dtype=str)

    # Хеши из первого столбца
    hashes = df.iloc[:, 0].dropna().tolist()

    # Контрольные номера из третьего столбца (индекс 2)
    known_phones = []
    for i in range(min(5, len(df))):
        val = str(df.iat[i, 2])
        # Очищаем от лишних символов, если они есть
        digits = ''.join(filter(str.isdigit, val))
        if digits:
            known_phones.append(int(digits))

    return hashes, known_phones


def run_hashcat(hashes, hashcat_path, mode, mask):
    """Запускает Hashcat внутри его собственной папки."""
    if not os.path.exists(hashcat_path):
        return []

    hashcat_dir = os.path.dirname(os.path.abspath(hashcat_path))
    tmp_hash_file = os.path.join(hashcat_dir, "temp_hashes.txt")
    tmp_out_file = os.path.join(hashcat_dir, "temp_cracked.txt")

    # Записываем с кодировкой UTF-8
    with open(tmp_hash_file, 'w', encoding='utf-8') as f:
        for h in hashes:
            f.write(f"{h.strip()}\n")

    cmd = [
        os.path.basename(hashcat_path),
        "-m", mode, "-a", "3",
        "temp_hashes.txt", mask,
        "--outfile", "temp_cracked.txt", "--outfile-format", "2",
        "--potfile-disable", "--force"
    ]

    # Запуск в контексте папки Hashcat (решает проблему с OpenCL)
    subprocess.run(cmd, cwd=hashcat_dir)

    cracked = []
    if os.path.exists(tmp_out_file):
        with open(tmp_out_file, 'r', encoding='utf-8') as f:
            cracked = [int(line.strip()) for line in f if line.strip().isdigit()]
        os.remove(tmp_out_file)

    if os.path.exists(tmp_hash_file):
        os.remove(tmp_hash_file)

    return cracked


def find_salt(known_phones, cracked_numbers):
    """Вычисляет соль через пересечение множеств разностей."""
    if not cracked_numbers or not known_phones:
        return None

    sets = []
    for kp in known_phones:
        sets.append({cn - kp for cn in cracked_numbers})

    common = set.intersection(*sets)
    return list(common)[0] if common else None