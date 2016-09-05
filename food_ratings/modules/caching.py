from werkzeug.contrib.cache import FileSystemCache, SimpleCache
import os
import tempfile

def get_cache_dir():
    temp_dir_path = tempfile.gettempdir()
    return os.path.join(temp_dir_path, 'food-demo') if temp_dir_path else None
    
def init_cache(app):
    cache_timeout = 24 * 60 * 60
    temp_dir_path = get_cache_dir()
    if temp_dir_path:
        app.logger.info(temp_dir_path)
        app.cache = FileSystemCache(temp_dir_path, default_timeout=cache_timeout)
    else:
        app.cache = SimpleCache(default_timeout=cache_timeout)

def clear_cache(app):
    result = app.cache.clear()

    temp_dir_path = get_cache_dir()
    if not result and os.path.exists(temp_dir_path):
        for file in os.scandir(temp_dir_path):
            os.remove(file.path)
        result = True

    return result
