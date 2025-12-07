import os
import string
import csv


def get_files_in_folder(folder_path, extension='.txt'):
    """
    Получает список файлов в указанной папке с заданным расширением.
    """
    files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(extension):
            files.append(filename)
    return files


def read_text_file(filepath):
    """
    Читает содержимое текстового файла.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"Ошибка: Файл {filepath} не найден"
    except UnicodeDecodeError:
        return "Ошибка: Неверная кодировка файла"


def read_csv_file(filepath):
    """
    Читает CSV-файл и возвращает список словарей.
    """
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.readlines()
            headers = content[0].strip().split(',')

            for line in content[1:]:
                data_dict_for_one_row = {}
                values = line.strip().split(',')
                for i in range(len(values)):
                    data_dict_for_one_row[headers[i]] = values[i]
                data.append(data_dict_for_one_row)

        return data

    except FileNotFoundError:
        print(f"Файл не найден: {filepath}")
        return data

    except Exception as e:
        print(f"Ошибка при чтении файла {filepath}: {e}")
        return data


def write_csv_file(filepath, data, headers):
    """
    Записывает данные в CSV файл.

    Args:
        filepath (str): Полный путь к файлу, включая папку и название файла
        data (list): Список списков [[val1, val2], [val1, val2], ...]
        headers (list): Список заголовков ['col1', 'col2']
    """
    folder = os.path.dirname(filepath)
    os.makedirs(folder, exist_ok=True)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(','.join(headers) + '\n')
            for row in data:
                f.write(','.join(str(v) for v in row) + '\n')
        return True
    except Exception as e:
        print("Ошибка при записи CSV:", e)
        return False
    
def write_text_file(filepath, content):
    """
    Записывает текст в файл (создаёт папку, если её нет).

    Args:
        filepath (str): Полный путь к файлу.
        content (str): Текст для записи.
    """
    folder = os.path.dirname(filepath)
    os.makedirs(folder, exist_ok=True)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Ошибка при записи файла {filepath}: {e}")
        return False
