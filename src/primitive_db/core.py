#!/usr/bin/env python3
VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = []
    seen_names = set()
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata

        name, _, col_type = col.partition(":")
        if not name or not col_type or col_type not in VALID_TYPES:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata

        if name in seen_names:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata

        seen_names.add(name)
        parsed_columns.append({"name": name, "type": col_type})

    user_id = None
    final_columns = []
    for c in parsed_columns:
        if c["name"].upper() == "ID":
            c["name"] = "ID"  # нормализуем регистр
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


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")