import requests


user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 ' \
             'Safari/537.36 OPR/26.0.1656.60 '

headers = {'User-Agent': user_agent}

proxypool_url = 'http://127.0.0.1:5555/random'
target_url = 'http://httpbin.org/get'


def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    return requests.get(proxypool_url).text.strip()


def crawl(url, proxy):
    """
    use proxy to crawl page
    :param url: page url
    :param proxy: proxy, such as 8.8.8.8:8888
    :return: html
    """
    proxies = {'http': 'http://' + proxy}
    print(proxies)
    return requests.get(url, headers=headers, proxies=proxies).text


def main():
    """
    main method, entry point
    :return: none
    """
    proxy = get_random_proxy()
    print('get random proxy', proxy)
    html = crawl(target_url, proxy)
    print(html)


if __name__ == '__main__':
    main()