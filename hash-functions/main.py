import hashlib
import pandas as pd
import os
from collections import Counter
import subprocess
import random
import tempfile
import time

KNOWN_NUMBERS = [
    89869713494,
    89856644737,
    89638074671,
    89699947643,
    89686430975
]

HASH_ID = {
    'md5': 0,
    'sha1': 100,
    'sha256': 1400,
    'sha3-256': 17400
}

HASH_FUNCTIONS = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha256': hashlib.sha256,
    'sha3-256': hashlib.sha3_256
}


def read_numbers_from_csv(file_path):
    try:
        df = pd.read_csv(file_path, header=None)
        data = df.iloc[:, 0].dropna().astype(str).tolist()
        return data
    except Exception as e:
        print(f"Failed to read file: {e}")
        return []


def parse_hashcat_output(lines):
    cracked = []
    for line in lines:
        line = line.strip()
        if not line or ':' not in line:
            continue
        cracked_value = int(line.split(":")[1])
        cracked.append(cracked_value)
    return cracked


def find_salt(original_numbers, cracked_numbers):
    cracked_nums_int = [int(x) for x in cracked_numbers]
    delta_sets = []
    for original in original_numbers:
        deltas = set(cracked - original for cracked in cracked_numbers)
        delta_sets.append(deltas)
    salt = set.intersection(*delta_sets)
    salt_list = list(salt)
    if salt_list:
        return salt_list[0]
    else:
        return 0


def decrypt_hashes(file_path, algorithm="md5"):
    start_time = time.time()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hashcat = os.path.join(current_dir, "hashcat-7.1.2", "hashcat.exe")
    result_file = os.path.join(current_dir, "cracked_numbers.csv")

    print(f"Reading hashes from: {file_path}")
    hashes = read_numbers_from_csv(file_path)
    if not hashes:
        print("No hashes found in file")
        return

    cracked_hashes = [h for h in hashes]
    mask = "?d" * 11

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_hash_file:
        for h in cracked_hashes:
            temp_hash_file.write(f"{h}\n")
        temp_hash_file_path = temp_hash_file.name

    with tempfile.NamedTemporaryFile(mode='r+', delete=False) as temp_output_file:
        temp_output_file_path = temp_output_file.name

    print(f"Running hashcat with algorithm: {algorithm}")
    hashcat_command = [
        hashcat, "--potfile-disable", "-a", "3", "-m", str(HASH_ID[algorithm]),
        "-w", "4", "-o", temp_output_file_path, temp_hash_file_path, mask
    ]

    try:
        result = subprocess.run(
            hashcat_command,
            cwd=os.path.join(current_dir, "hashcat-7.1.2"),
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Hashcat error: {result.stderr}")
            return
    except Exception as e:
        print(f"Hashcat error: {e}")
        return

    with open(temp_output_file_path, "r") as f:
        cracked_output_lines = f.readlines()

    cracked_nums = parse_hashcat_output(cracked_output_lines)
    print(f"Successfully cracked {len(cracked_nums)} hashes")

    salt = find_salt(KNOWN_NUMBERS, cracked_nums)

    with open(result_file, "w") as f:
        for num in cracked_nums:
            f.write(f"{num - salt}\n")

    elapsed = time.time() - start_time
    print(f"Results saved to: {result_file}")
    print(f"Found salt: {salt}")
    print(f"Execution time: {elapsed:.2f} seconds")

    os.remove(temp_hash_file_path)
    os.remove(temp_output_file_path)


def encrypt_numbers(algorithm, file_path, salt_length=5):
    start_time = time.time()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    result_file = os.path.join(current_dir, "hashed_numbers.csv")

    print(f"Reading numbers from: {file_path}")
    numbers = [int(n) for n in read_numbers_from_csv(file_path)]

    salt = int(''.join(random.choices('123456789', k=1)) +
               ''.join(random.choices('0123456789', k=int(salt_length) - 1)))
    print(f"Generated salt: {salt}")

    with open(result_file, 'w') as hash_file:
        for number in numbers:
            salted_number = number + salt
            hash_func = HASH_FUNCTIONS[algorithm]
            hashed = hash_func(str(salted_number).encode()).hexdigest()
            hash_file.write(hashed + '\n')

    elapsed = time.time() - start_time
    print(f"Results saved to: {result_file}")
    print(f"Execution time: {elapsed:.2f} seconds")


def main():
    print("1. Encrypt numbers")
    print("2. Decrypt hashes")

    choice = input("\nSelect operation: ").strip()

    if choice == "1":
        file_path = input("Enter path to csv file: ").strip()
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        print("\nAvailable algorithms: md5, sha1, sha256, sha512")
        algorithm = input("Select algorithm (default: md5): ").strip().lower() or "md5"
        if algorithm not in HASH_FUNCTIONS:
            print(f"Invalid algorithm. Using md5")
            algorithm = "md5"

        salt_length = input("Enter salt length (default: 8): ").strip() or "8"
        encrypt_numbers(algorithm, file_path, int(salt_length))

    elif choice == "2":
        file_path = input("Enter path to csv file: ").strip()
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        print("\nAvailable algorithms: md5, sha1, sha256, sha3-256")
        algorithm = input("Select algorithm (default: md5): ").strip().lower() or "md5"
        if algorithm not in HASH_FUNCTIONS:
            print(f"Invalid algorithm. Using md5")
            algorithm = "md5"

        decrypt_hashes(file_path, algorithm)

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
