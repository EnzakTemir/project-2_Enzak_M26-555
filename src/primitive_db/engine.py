#!/usr/bin/env python3
"""Модуль для запуска, игрового цикла и парсинга команд."""
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db import core, parser, utils
from primitive_db.constants import (
    CMD_CREATE,
    CMD_DELETE,
    CMD_DROP,
    CMD_EXIT,
    CMD_HELP,
    CMD_INFO,
    CMD_INSERT,
    CMD_LIST,
    CMD_SELECT,
    CMD_UPDATE,
    META_FILE,
)


def welcome():
    """Приветствует пользователя и показывает краткую справку.
    
    (Реализовано в рамках 1-го этапа. Вызывается по желанию).
    """
    name = prompt.string("May I have your name? ")
    print(f"\nПривет, {name}!")
    print("***База данных***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def print_help():
    """Выводит полную справку по доступным командам."""
    print("\n***Управление таблицами***")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, ...) "
        "- создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def display_table(rows, columns):
    """Выводит данные в красивом формате с помощью PrettyTable."""
    table = PrettyTable()
    table.field_names = columns
    for row in rows:
        table.add_row([row.get(col, "") for col in columns])
    print(table)


def run():
    """Основной цикл программы."""
    print_help()  # Выводим справку один раз при старте

    metadata = utils.load_metadata(META_FILE)

    while True:
        try:
            user_input = input(">>> Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]

        if command == CMD_EXIT:
            break

        elif command == CMD_HELP:
            print_help()

        elif command == CMD_LIST:
            core.list_tables(metadata)

        elif command == CMD_CREATE:
            if len(args) < 3:
                print("Некорректное значение: укажите имя таблицы и столбцы.")
                continue
            table_name, columns = args[1], args[2:]
            existed_before = table_name in metadata
            metadata = core.create_table(metadata, table_name, columns)
            if not existed_before and table_name in metadata:
                utils.save_metadata(META_FILE, metadata)

        elif command == CMD_DROP:
            if len(args) != 2:
                print("Некорректное значение: укажите только имя таблицы.")
                continue
            table_name = args[1]
            existed_before = table_name in metadata
            metadata = core.drop_table(metadata, table_name)
            if existed_before and table_name not in metadata:
                utils.save_metadata(META_FILE, metadata)
                # При удалении таблицы не забываем удалить и её файл данных
                utils.delete_table_data(table_name)

        # --- CRUD КОМАНДЫ ---
        elif command == CMD_INSERT:
            try:
                table_name = args[2]
                values_str = " ".join(args[4:])
                values = parser.parse_values(values_str)

                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                table_data = utils.load_table_data(table_name)
                new_data = core.insert(metadata, table_name, table_data, values)
                utils.save_table_data(table_name, new_data)
            except IndexError:
                print("Некорректный синтаксис insert.")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif command == CMD_SELECT:
            try:
                table_name = args[2]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                where_clause = None
                if len(args) > 3:
                    if args[3] != "where":
                        print("Некорректный синтаксис select.")
                        continue
                    where_str = " ".join(args[4:])
                    where_clause = parser.parse_where(where_str)

                table_data = utils.load_table_data(table_name)
                result = core.select(table_data, where_clause)

                columns = [col["name"] for col in metadata[table_name]["columns"]]
                display_table(result, columns)

            except IndexError:
                print("Некорректный синтаксис select.")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif command == CMD_UPDATE:
            try:
                table_name = args[1]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                set_idx = args.index("set")
                where_idx = args.index("where")

                set_str = " ".join(args[set_idx + 1:where_idx])
                where_str = " ".join(args[where_idx + 1:])

                set_clause = parser.parse_set(set_str)
                where_clause = parser.parse_where(where_str)

                table_data = utils.load_table_data(table_name)
                new_data = core.update(table_data, set_clause, where_clause)
                utils.save_table_data(table_name, new_data)

            except (IndexError, ValueError) as e:
                print(f"Некорректный синтаксис update: {e}")

        elif command == CMD_DELETE:
            try:
                table_name = args[2]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                where_str = " ".join(args[4:])
                where_clause = parser.parse_where(where_str)

                table_data = utils.load_table_data(table_name)
                new_data = core.delete(table_data, where_clause)
                utils.save_table_data(table_name, new_data)

            except (IndexError, ValueError) as e:
                print(f"Некорректный синтаксис delete: {e}")

        elif command == CMD_INFO:
            if len(args) != 2:
                print("Некорректное значение: укажите имя таблицы.")
                continue
            table_name = args[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            schema = metadata[table_name]["columns"]
            cols_str = ", ".join(f'{c["name"]}:{c["type"]}' for c in schema)
            table_data = utils.load_table_data(table_name)

            print(f"Таблица: {table_name}")
            print(f"Столбцы: {cols_str}")
            print(f"Количество записей: {len(table_data)}")

        else:
            print(f"Функции {command} нет. Попробуйте снова.")