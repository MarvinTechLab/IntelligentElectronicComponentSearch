

def get_float_value(data, key, default_value=0.0):
    try:
        value = data.get(key, default_value)
        return float(value) if value else default_value
    except (ValueError, TypeError):
        return default_value


def get_int_value(data, key, default_value=0):
    try:
        value = data.get(key, default_value)
        return int(float(value)) if value else default_value
    except (ValueError, TypeError):
        return default_value