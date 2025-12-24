import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import subprocess, os, shutil

def file_to_list(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [ln.strip() for ln in f if ln.strip()]

def list_to_txt(filename, data_list):
    with open(filename, 'w', encoding='utf-8') as f:
        for it in data_list:
            f.write(str(it) + '\n')

def excel_read(path):
    return pd.read_excel(path, header=None, dtype=str)

def detect_hash_algo_from_hex(h):
    h = h.strip().lower()
    if h.startswith('0x'):
        h = h[2:]
    L = len(h)
    if all(c in '0123456789abcdef' for c in h):
        if L == 32: return 'md5', '0'
        if L == 40: return 'sha1', '100'
        if L == 64: return 'sha256', '1400'
        if L == 128: return 'sha512', '1700'
    return None, None

def find_salt_by_intersection(phones, decimals):
    res = [[d - phones[i] for d in decimals] for i in range(5)]
    s_all = set(res[0]) & set(res[1]) & set(res[2]) & set(res[3]) & set(res[4])
    candidates = [s for s in s_all if len(str(abs(s))) == 10]
    return candidates[0] if candidates else None

def run_hashcat(hashcat_path, hashfile, mode, mask, out_file):
    if shutil.which(hashcat_path) is None and not os.path.isfile(hashcat_path):
        raise FileNotFoundError(f"hashcat не найден по пути {hashcat_path}")
    if os.path.exists(out_file):
        os.remove(out_file)
    cmd = [
        hashcat_path, '-m', str(mode), '-a', '3', hashfile, mask,
        '--outfile-format', '2', '-o', out_file,
        '--potfile-disable', '--force', '--quiet'
    ]
    print("Running:", ' '.join(cmd))
    subprocess.run(cmd)

def parse_hashcat_output_file(out_file):
    plains = []
    if not os.path.exists(out_file):
        return plains
    for ln in file_to_list(out_file):
        if ':' in ln:
            plains.append(''.join(ch for ch in ln.split(':', 1)[1] if ch.isdigit()))
        else:
            plains.append(''.join(ch for ch in ln if ch.isdigit()))
    return plains

def choose_file(entry):
    path = filedialog.askopenfilename(
        title="Выберите Excel-файл с хэшами",
        filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")]
    )
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def choose_hashcat(entry):
    path = filedialog.askopenfilename(
        title="Выберите исполняемый файл hashcat",
        filetypes=[("Все файлы", "*.*")]
    )
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def start_process():
    xlsx_path = entry_file.get().strip()
    hashcat_path = entry_hashcat.get().strip() or 'hashcat'

    if not xlsx_path:
        messagebox.showerror("Ошибка", "Выберите Excel-файл.")
        return

    try:
        df = excel_read(xlsx_path)
    except Exception as e:
        messagebox.showerror("Ошибка чтения Excel", str(e))
        return

    phones = []
    for i in range(5):
        v = str(df.iat[i, 2])
        phones.append(int(''.join(ch for ch in v if ch.isdigit())))

    hashes = [str(df.iat[i, 0]).strip() for i in range(len(df)) if pd.notna(df.iat[i, 0])]
    algo, mode = detect_hash_algo_from_hex(hashes[0])
    if algo is None:
        messagebox.showerror("Ошибка", "Не удалось определить алгоритм по длине хэша.")
        return

    messagebox.showinfo("Определён алгоритм", f"{algo.upper()} (mode {mode})")

    base_dir = os.path.dirname(xlsx_path) or '.'
    out_dir = os.path.join(base_dir, "decode_out")
    os.makedirs(out_dir, exist_ok=True)

    tmp_hashfile = os.path.join(out_dir, "tmp_hashes.txt")
    list_to_txt(tmp_hashfile, hashes)

    found_path = os.path.join(out_dir, "found.txt")
    run_hashcat(hashcat_path, tmp_hashfile, mode, "?d?d?d?d?d?d?d?d?d?d?d", found_path)

    plains = parse_hashcat_output_file(found_path)
    if not plains:
        messagebox.showwarning("Hashcat", "Не найдено совпадений.")
        return

    decimals = [int(p) for p in plains if p.isdigit()]
    numbers_path = os.path.join(out_dir, "numbers_only.txt")
    list_to_txt(numbers_path, decimals)

    salt = find_salt_by_intersection(phones, decimals)
    if salt is None:
        messagebox.showwarning("Результат", "10-значная соль не найдена.")
        return

    decoded = [d - salt for d in decimals]
    decoded_path = os.path.join(out_dir, "decode_phones.txt")
    list_to_txt(decoded_path, decoded)

    messagebox.showinfo(
        "Готово",
        f"Соль найдена: {salt}\n"
        f"Файлы сохранены в папке:\n{out_dir}"
    )

root = tk.Tk()
root.title("Hash Deobfuscation Tool (decode_out)")
root.geometry("850x320")

frm = tk.Frame(root)
frm.pack(padx=10, pady=10, fill='x')

tk.Label(frm, text="Excel-файл (.xlsx):").grid(row=0, column=0, sticky='e')
entry_file = tk.Entry(frm, width=60)
entry_file.grid(row=0, column=1, padx=5)
tk.Button(frm, text="Обзор", command=lambda: choose_file(entry_file)).grid(row=0, column=2)

tk.Label(frm, text="Путь до hashcat:").grid(row=1, column=0, sticky='e')
entry_hashcat = tk.Entry(frm, width=60)
entry_hashcat.grid(row=1, column=1, padx=5)
tk.Button(frm, text="Обзор", command=lambda: choose_hashcat(entry_hashcat)).grid(row=1, column=2)

tk.Button(
    root, text="Запустить расшифровку",
    command=start_process, bg="#8fbc8f", width=40
).pack(pady=20)

tk.Label(
    root,
    text="Все результаты сохраняются в папку decode_out рядом с Excel-файлом.",
    fg='gray'
).pack()

root.mainloop()