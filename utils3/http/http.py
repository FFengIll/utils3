import urllib.request as urllib

import requests

def get_content_size(url, proxy=None):
    """
    通过head方法，仅获取header，并从中抽取必要信息，而不必大量IO，获取content
    :param url:
    :param proxy:
    :return:
    """
    res = requests.head(url, timeout=10, allow_redirects=False)
    size = res.headers['Content-Length']
    return int(size)


def get_redirect_url(url, try_count=1):
    """
    禁止自动处理重定向，并从重定向的location中获取目标url
    :param url:
    :param try_count:
    :return:
    """
    res = requests.get(url, timeout=10, allow_redirects=False)
    return res.headers['location']
