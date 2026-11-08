#!/usr/bin/env python3

from primitive_db.decorators import (
    confirm_action,
    handle_db_errors,
    log_time,
)

VALID_TYPES = {"int", "str", "bool"}


def _parse_column(col_string):
    """Разбирает строку вида 'имя:тип' на кортеж (имя, тип)."""
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
        raise ValueError("Имя таблицы не может быть пустым.")

    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    parsed_columns = []
    seen_names = set()

    for col in columns:
        parsed = _parse_column(col)
        if not parsed:
            raise ValueError(f"Некорректное значение: {col}. Попробуйте снова.")

        name, col_type = parsed
        if name in seen_names:
            raise ValueError(f"Некорректное значение: {col}. Попробуйте снова.")

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


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных по её имени."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
def list_tables(metadata):
    """Выводит список всех существующих таблиц."""
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")


@log_time
@handle_db_errors
def insert(metadata, table_name, table_data, values):
    """Добавляет новую запись в таблицу, проверяя количество и типы значений."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    schema = metadata[table_name]["columns"]
    data_columns = [col for col in schema if col["name"] != "ID"]

    if len(values) != len(data_columns):
        raise ValueError(
            f"Неверное количество значений. Ожидалось {len(data_columns)}."
        )

    for col, val in zip(data_columns, values):
        expected_type = col["type"]
        if expected_type == "bool" and not isinstance(val, bool):
            raise ValueError(f'Неверный тип для столбца "{col["name"]}". Ожидался bool.') # noqa: E501
        elif expected_type == "int" and (
            isinstance(val, bool) or not isinstance(val, int)
        ):
            raise ValueError(f'Неверный тип для столбца "{col["name"]}". Ожидался int.')
        elif expected_type == "str" and not isinstance(val, str):
            raise ValueError(f'Неверный тип для столбца "{col["name"]}". Ожидался str.')

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


@log_time
@handle_db_errors
def select(table_data, where_clause=None):
    """Возвращает записи, подходящие под условие where (или все записи)."""
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
def update(table_data, set_clause, where_clause, table_name):
    """Обновляет записи, подходящие под where_clause, новыми значениями из set_clause.""" # noqa: E501
    updated_ids = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break

        if match:
            for col, new_val in set_clause.items():
                row[col] = new_val
            updated_ids.append(row.get("ID"))

    for uid in updated_ids:
        print(f'Запись с ID={uid} в таблице "{table_name}" успешно обновлена.')

    if not updated_ids:
        print("Записи для обновления не найдены.")
    return table_data


@confirm_action("удаление записи")
@handle_db_errors
def delete(table_data, where_clause, table_name):
    """Удаляет записи, подходящие под where_clause, и возвращает новые данные."""
    deleted_ids = []
    new_data = []

    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break

        if match:
            deleted_ids.append(row.get("ID"))
        else:
            new_data.append(row)

    for did in deleted_ids:
        print(f'Запись с ID={did} успешно удалена из таблицы "{table_name}".')

    if not deleted_ids:
        print("Записи для удаления не найдены.")
    return new_data