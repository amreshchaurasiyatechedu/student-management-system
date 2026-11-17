def _positive_id(value):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None

    if isinstance(value, str) and not value.strip():
        return None
    try:
        object_id = int(value)
    except (TypeError, ValueError):
        return None
    return object_id if object_id > 0 else None
