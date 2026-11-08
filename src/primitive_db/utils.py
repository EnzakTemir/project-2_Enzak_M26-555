#!/usr/bin/env python3
import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла (или пустой словарь при ошибке)."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Предупреждение: Файл {filepath} повреждён. Создаю новый.")
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_table_path(table_name):
    """Возвращает путь к файлу данных таблицы, создавая директорию при необходимости."""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Загружает данные таблицы из файла (или пустой список)."""
    filepath = _get_table_path(table_name)
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет данные таблицы в файл."""
    filepath = _get_table_path(table_name)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_table_data(table_name):
    """Удаляет файл данных таблицы, если он существует."""
    filepath = _get_table_path(table_name)
    if os.path.exists(filepath):
        os.remove(filepath)