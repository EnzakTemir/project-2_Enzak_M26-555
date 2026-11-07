#!/usr/bin/env python3
"""Модуль с основной логикой управления таблицами базы данных."""
from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors


def _parse_column(col_string):
    """Вспомогательная функция для разбора строки 'имя:тип'."""
    if ":" not in col_string:
        return None
    name, _, col_type = col_string.partition(":")
    if not name or not col_type or col_type not in VALID_TYPES or " " in name:
        return None
    return name, col_type


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт новую таблицу с указанными столбцами."""
    if not table_name:
        print("Ошибка: Имя таблицы не может быть пустым.")
        return metadata

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = []
    seen_names = set()

    for col in columns:
        parsed = _parse_column(col)
        if not parsed:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata

        name, col_type = parsed
        if name in seen_names:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata

        seen_names.add(name)
        parsed_columns.append({"name": name, "type": col_type})

    user_id = None
    final_columns = []
    for c in parsed_columns:
        if c["name"].upper() == "ID":
            c["name"] = "ID"
            c["type"] = "int"
            user_id = c
        else:
            final_columns.append(c)

    if user_id is None:
        final_columns.insert(0, {"name": "ID", "type": "int"})
    else:
        final_columns.insert(0, user_id)

    metadata[table_name] = {"columns": final_columns}
    cols_str = ", ".join(f'{c["name"]}:{c["type"]}' for c in final_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata


@confirm_action
@handle_db_errors
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных по её имени."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Выводит список всех существующих таблиц."""
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")


@handle_db_errors
def insert(metadata, table_name, table_data, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    schema = metadata[table_name]["columns"]
    data_columns = [col for col in schema if col["name"] != "ID"]

    if len(values) != len(data_columns):
        print(f"Ошибка: Неверное количество значений. Ожидалось {len(data_columns)}.")
        return table_data

    for col, val in zip(data_columns, values):
        expected_type = col["type"]
        if expected_type == "bool" and not isinstance(val, bool):
            print(f'Ошибка: Неверный тип для столбца "{col["name"]}". Ожидался bool.')
            return table_data
        elif expected_type == "int" and not isinstance(val, int):
            print(f'Ошибка: Неверный тип для столбца "{col["name"]}". Ожидался int.')
            return table_data
        elif expected_type == "str" and not isinstance(val, str):
            print(f'Ошибка: Неверный тип для столбца "{col["name"]}". Ожидался str.')
            return table_data

    if table_data:
        new_id = max(row["ID"] for row in table_data) + 1
    else:
        new_id = 1

    new_row = {"ID": new_id}
    for col, val in zip(data_columns, values):
        new_row[col["name"]] = val

    table_data.append(new_row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_data, where_clause=None):
    """Возвращает записи, подходящие под условие where."""
    if not where_clause:
        return table_data
    result = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break
        if match:
            result.append(row)
    return result


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи, подходящие под where_clause."""
    updated_id = None
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break

        if match:
            for col, new_val in set_clause.items():
                row[col] = new_val
            updated_id = row.get("ID")
            break  # Обновляем только первую подходящую запись для точного вывода

    if updated_id is not None:
        print(f'Запись с ID={updated_id} в таблице успешно обновлена.')
    else:
        print("Записи для обновления не найдены.")
    return table_data


@confirm_action
@handle_db_errors
def delete(table_data, where_clause):
    """Удаляет записи, подходящие под where_clause."""
    deleted_id = None
    new_data = []
    
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break
        
        if match and deleted_id is None:
            deleted_id = row.get("ID")
            # Не добавляем в new_data (удаляем)
        else:
            new_data.append(row)

    if deleted_id is not None:
        print(f'Запись с ID={deleted_id} успешно удалена из таблицы.')
    else:
        print("Записи для удаления не найдены.")
    return new_data


def create_cached_selector():
    """Создает функцию select с кэшированием результатов (замыкание)."""
    cache = {}
    def cached_select(table_data, where_clause=None):
        key = (str(table_data), str(where_clause))
        if key not in cache:
            print("[CACHE] Выполняю поиск и сохраняю в кэш...")
            cache[key] = select(table_data, where_clause)
        else:
            print("[CACHE] Беру результат из кэша!")
        return cache[key]
    return cached_select