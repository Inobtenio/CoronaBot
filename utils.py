import time
import urllib.parse

def decode(bytes):
    return bytes.decode().strip()

def no_cache_params():
    return dict(at=time.time())

def url(host, path, params={}):
    if not params: return urllib.parse.urljoin(host, path)
    full_path = path + '?' + urllib.parse.urlencode(params)
    return urllib.parse.urljoin(host, full_path)
