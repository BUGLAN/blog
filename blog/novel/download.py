import requests

headers = {
    "User - Agent": "Mozilla / 5.0(Windows NT 10.0;"
                    "WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 64.0.3282.168Safari / 537.36"}


class DownLoad:

    @staticmethod
    def download_page(url, **kwargs):
        """
        download html page
        """
        while True:
            try:
                if kwargs and kwargs['params']:
                    r = requests.get(url, headers=headers, params=kwargs["params"], timeout=1.5)
                else:
                    r = requests.get(url, headers=headers, timeout=1.5)
            except requests.exceptions.ConnectionError as e:
                print(e)
            else:
                r.encoding = r.apparent_encoding
                return r.text

    @staticmethod
    def download_file(url):
        """
        download binary file
        like picture videos
        """
        r = requests.get(url, headers=headers)
        return r.content
