#!/usr/bin/env python3
import shlex

from primitive_db import core, utils

DB_META_PATH = "db_meta.json"


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print_help()
    metadata = utils.load_metadata(DB_META_PATH)

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
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

        command, rest = args[0], args[1:]

        if command == "exit":
            break

        elif command == "help":
            print_help()

        elif command == "list_tables":
            core.list_tables(metadata)

        elif command == "create_table":
            if len(rest) < 2:
                print(
                    "Некорректное значение: укажите имя таблицы и хотя бы один "
                    "столбец. Попробуйте снова."
                )
                continue

            table_name, columns = rest[0], rest[1:]
            existed_before = table_name in metadata
            metadata = core.create_table(metadata, table_name, columns)
            if not existed_before and table_name in metadata:
                utils.save_metadata(DB_META_PATH, metadata)

        elif command == "drop_table":
            if len(rest) != 1:
                print(
                    "Некорректное значение: укажите только имя таблицы. "
                    "Попробуйте снова."
                )
                continue

            table_name = rest[0]
            existed_before = table_name in metadata
            metadata = core.drop_table(metadata, table_name)
            if existed_before and table_name not in metadata:
                utils.save_metadata(DB_META_PATH, metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")