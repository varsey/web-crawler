import re
import os
import shutil
import requests
from threading import Thread
from bs4 import BeautifulSoup


class ThreadWithReturn(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        try:
            if self._target:
                self._return = self._target(*self._args, **self._kwargs)
        finally:
            del self._target, self._args, self._kwargs

    def join(self, timeout=None):
        Thread.join(self, timeout)

        return self._return


class Parser:
    def __init__(self):
        self.ftr_chars = ['?', '.', '\\', '//', ',', '=', '{', '}', '[', ']', '(', ')', '%', '$', '#', '@', '"', "'"]

    def prettify(self, string: str) -> str:
        for i in self.ftr_chars:
            string = string.replace(i, '', -1)

        return string

    def get_imagename(self, string: str) -> str:
        string = self.prettify(string)

        if len(string) > 14:
            string = string[:10]

        if (
                not (
                        string.endswith('.png') or
                        string.endswith('.jpg') or
                        string.endswith('.jpeg')
                )
        ):
            string = string + '.jpg'

        return string

    def request_handle(self, url: str, path: str, name: str) -> dict:
        """ Return tags for the picture from different AI Recognition services"""
        try:
            if not url or not path or not name:
                raise Exception("Not enough arguments")

            r = requests.get(url, stream=True)

            if r.status_code == 200:
                r.raw.decode_content = True

                if not name.endswith('.jpg'):
                    name = name + '.jpg'

                path = os.path.join(path, name)

                with open(path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

                result = {
                    'images': 1,
                }

                return result

        except Exception as e:
            print(e)
            result = {
                'images': 0,
            }
            return result

    def parse(self, html_text: str, main_page: str, path: str) -> dict:
        """ Return tags for all pictures on html page"""
        img_urls, images = set(), 0
        soup = BeautifulSoup(html_text, 'html.parser')
        tags = soup.find_all("img")
        for tag in tags:
            src = tag.get('src') or tag.get('data-src')
            if src:
                if src.startswith('//'):
                    src = 'http:' + src
                if not src.startswith("http"):
                    src = main_page + src[1:]
                img_urls.add(src)

        soup = BeautifulSoup(html_text, 'html.parser')
        tags = soup.find_all("a")
        for tag in tags:
            src = tag.get('src') or tag.get('data-src')
            if src and ('.png' in src or '.jpg' in src or '.jpeg' in src):
                if src.startswith('//'):
                    src = 'http:' + src
                if not src.startswith("http"):
                    src = main_page + src[1:]
                img_urls.add(src)

        links = re.findall('"((http|ftp)s?://.*?)"', html_text)
        for link in links:
            if link and ('.png' in link[0] or '.jpg' in link[0] or '.jpeg' in link[0]):
                if link[0].endswith('?'):
                    img_urls.add(link[0][:-1])
                else:
                    img_urls.add(link[0])

        short_links = re.findall('"(//.*?)"', html_text)
        for link in short_links:
            if link and ('.png' in link[0] or '.jpg' in link[0] or '.jpeg' in link[0]):

                url = link[0] if link[0].startswith('http') else ('http' + link[0])

                if url.endswith('?'):
                    url = url[:-1]
                img_urls.add(url)

        threads = []
        i = 1
        for url in img_urls:
            name = f"{i}-{self.get_imagename(url.split('/')[-1])}"
            _t = ThreadWithReturn(
                target=self.request_handle,
                args=(url, path, name),
            )
            _t.daemon = True
            threads.append(_t)
            _t.start()
            i += 1

        for thread in threads:
            _result = thread.join()
            if _result:
                images += _result['images']

        result = {
            'images': images,
        }

        return result


