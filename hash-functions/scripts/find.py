from collections import Counter

KNOWN_NUMBERS = [
    89869713494,
    89856644737,
    89638074671,
    89699947643,
    89686430975
]

CRACKED_NUMBERS = [
    91159290010,
    91849545766,
    91018053961,
    91087667314,
    91159395328
]

def find_salt(original_numbers, cracked_nums):
    cracked_nums_int = [int(x) for x in cracked_nums]
    delta_sets = []
    for origin in original_numbers:
        deltas = set(crack - origin for crack in cracked_nums_int)
        delta_sets.append(deltas)
    salt = set.intersection(*delta_sets)
    salt_list = list(salt)
    if salt_list:
        return salt_list[0]
    else:
        return 0

if __name__ == "__main__":
    salt = find_salt(KNOWN_NUMBERS, CRACKED_NUMBERS)
    print(f"Salt found: {salt}")