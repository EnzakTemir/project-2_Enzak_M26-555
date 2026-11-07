"""Модуль для парсинга сложных команд (where, set, values)."""

def parse_value(val_str):
    """Преобразует строку в нужный тип: int, bool или str (без кавычек)."""
    val_str = val_str.strip()
    
    # Убираем кавычки, если это строка
    if (val_str.startswith('"') and val_str.endswith('"')) or \
       (val_str.startswith("'") and val_str.endswith("'")):
        return val_str[1:-1]
    
    if val_str.lower() == "true":
        return True
    if val_str.lower() == "false":
        return False
        
    try:
        return int(val_str)
    except ValueError:
        return val_str


def parse_where(where_str):
    """Парсит строку 'age = 28' в словарь {'age': 28}."""
    if not where_str:
        return None
    parts = where_str.split("=", 1)
    if len(parts) != 2:
        raise ValueError(f"Некорректное условие: {where_str}")
    
    col = parts[0].strip()
    val = parse_value(parts[1])
    return {col: val}


def parse_set(set_str):
    """Парсит строку 'age = 29' в словарь {'age': 29}."""
    return parse_where(set_str)


def parse_values(values_str):
    """Парсит строку '("Sergei", 28, true)' в список [Sergei, 28, True]."""
    # Убираем скобки
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]
    
    result = []
    current = ""
    in_quotes = False
    quote_char = None
    
    for char in values_str:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current += char
        elif char == ',' and not in_quotes:
            result.append(parse_value(current.strip()))
            current = ""
        else:
            current += char
            
    if current.strip():
        result.append(parse_value(current.strip()))
        
    return result