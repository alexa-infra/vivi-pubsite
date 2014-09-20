from jinja2 import contextfunction
from urllib.parse import urlparse, urljoin

@contextfunction
def get_url(context, path):
    if not path:
        return ''
    site = context['site']
    absurl = urljoin(site.url, path)
    return urlparse(absurl).path

@contextfunction
def url_for(context, path):
    if not path:
        return ''
    site = context['site']
    absurl = urljoin(site.url, path)
    return urlparse(absurl).path

@contextfunction
def get_absolute_url(context, path):
    if not path:
        return ''
    site = context['site']
    return urljoin(site.url, path)

@contextfunction
def absolute_url_for(context, path):
    if not path:
        return ''
    site = context['site']
    return urljoin(site.url, path)

functions = [url_for, absolute_url_for, get_url, get_absolute_url]
