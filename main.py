import requests
from src.Parser import Parser


def main():
    p = Parser()
    response = requests.get("https://yandex.ru/images/search?text=ночной%20чикаго%20фото", timeout=5)
    print(p.parse(response.text, 'https://yandex.ru/', '.'))


if __name__ == '__main__':
    main()
