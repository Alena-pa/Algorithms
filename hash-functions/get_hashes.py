import pandas as pd

# Читаем твой файл
df = pd.read_excel('data_вар7.xlsx')
# Сохраняем первый столбец в текстовый файл
df.iloc[:, 0].to_csv('hashes_to_crack.txt', index=False, header=False)
print("Готово! Хеши сохранены в hashes_to_crack.txt")