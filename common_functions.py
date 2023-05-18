import os
from pathlib import Path
from urllib.parse import urlsplit, unquote

import requests


def save_image_to_file_from_url(image_url, file_name, payload=None):
    response = requests.get(image_url, params=payload)
    response.raise_for_status()

    with open(file_name, 'wb') as file:
        file.write(response.content)


def get_file_extension_from_url(url):
    url_structure = urlsplit(url)
    path = unquote(url_structure.path)

    head, tail = os.path.split(path)
    root, ext = os.path.splitext(tail)

    return ext


def get_imagefolder_filename(filename):
    "Функция возвращает путь к файлу в каталоге изображений. Путь не зависит от ОС"
    return Path.cwd() / 'images' / f'{filename}'


def get_imagefolder():
    "Функция возвращает путь к каталогу изображений. Путь не зависит от ОС"
    return Path.cwd() / 'images'