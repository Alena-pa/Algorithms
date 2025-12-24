import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import time
import re
import os

def file_to_list(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]

def list_to_txt(filename, data_list):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data_list:
            f.write(str(item) + '\n')

def hash_data(data, algorithm):
    start = time.time()
    if algorithm == "md5":
        hashed = [hashlib.md5(str(d).encode()).hexdigest() for d in data]
    elif algorithm == "sha1":
        hashed = [hashlib.sha1(str(d).encode()).hexdigest() for d in data]
    elif algorithm == "sha256":
        hashed = [hashlib.sha256(str(d).encode()).hexdigest() for d in data]
    elif algorithm == "sha512":
        hashed = [hashlib.sha512(str(d).encode()).hexdigest() for d in data]
    else:
        raise ValueError("Unsupported algorithm")
    end = time.time()
    return hashed, round(end - start, 4)

def choose_txt(entry):
    path = filedialog.askopenfilename(
        title="Выберите TXT файл",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def encrypt_and_hash():
    path = entry_file.get().strip()
    if not path:
        messagebox.showerror("Ошибка", "Выберите TXT файл.")
        return
    if not os.path.exists(path):
        messagebox.showerror("Ошибка", "Файл не найден.")
        return

    salt_raw = entry_salt.get().strip()
    if not salt_raw:
        messagebox.showerror("Ошибка", "Введите соль.")
        return

    salt_digits = ''.join(ch for ch in salt_raw if ch.isdigit())
    if not salt_digits:
        messagebox.showerror("Ошибка", "Соль должна содержать только цифры.")
        return
    salt = int(salt_digits)

    try:
        lines = file_to_list(path)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")
        return

    encrypted = []
    for line in lines:
        digits = re.sub(r'\D', '', line)
        if digits:
            try:
                val = int(digits) + salt
                encrypted.append(str(val))
            except Exception:
                encrypted.append(line)
        else:
            encrypted.append(line)

    out_dir="hash_out"
    os.makedirs(out_dir, exist_ok=True)

    encrypted_path = os.path.join(out_dir, "encrypted.txt")
    list_to_txt(encrypted_path, encrypted)

    results = {}
    for algo in ("md5", "sha1", "sha256", "sha512"):
        hashed, t = hash_data(encrypted, algo)
        out_file = os.path.join(out_dir, f"hashed_{algo}.txt")
        list_to_txt(out_file, hashed)
        results[algo] = t

    msg = "Шифрование и хеширование завершено!\n\n"
    msg += f"Файл с солью: {os.path.relpath(encrypted_path)}\n\n"
    msg += "Время работы алгоритмов:\n"
    for k, v in results.items():
        msg += f"{k.upper()}: {v} сек\n"

    messagebox.showinfo("Готово", msg)

root = tk.Tk()
root.title("Шифрование + Хеширование (MD5, SHA1, SHA256, SHA512)")
root.geometry("650x320")
root.resizable(False, False)

tk.Label(root, text="Выберите TXT файл:", font=("Arial", 11)).pack(pady=6)
entry_file = tk.Entry(root, width=68)
entry_file.pack(pady=4)
tk.Button(root, text="Обзор", command=lambda: choose_txt(entry_file)).pack(pady=4)

frm_salt = tk.Frame(root)
frm_salt.pack(pady=10)
tk.Label(frm_salt, text="Соль (10-значная, только цифры):", font=("Arial", 10)).grid(row=0, column=0, sticky='w')
entry_salt = tk.Entry(frm_salt, width=24)
entry_salt.grid(row=0, column=1, padx=6)
entry_salt.insert(0, "6681604300")

tk.Label(
    root,
    text="Программа зашифрует все строки и создаст файл encrypted.txt и хеши в папке hash_out.",
    fg="gray",
    wraplength=620,
    justify="center"
).pack(pady=4)

tk.Button(
    root,
    text="Зашифровать и хешировать",
    command=encrypt_and_hash,
    width=30,
    bg="#8fbc8f",
    font=("Arial", 10, "bold")
).pack(pady=12)

tk.Label(
    root,
    text="Результаты: hash_out/encrypted.txt, hash_out/hashed_md5.txt, ...",
    font=("Arial", 9),
    fg="gray",
    wraplength=620,
    justify="center"
).pack(pady=8)

root.mainloop()