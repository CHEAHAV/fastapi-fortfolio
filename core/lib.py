def get_lang(key, params=None, lang="en", path=""):
    if params:
        try:
            return str(key).format(**params)
        except Exception:
            return str(key)
    return str(key)
