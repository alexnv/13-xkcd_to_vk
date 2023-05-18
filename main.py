import logging
import os

import requests
from dotenv import load_dotenv

from common_functions import get_imagefolder, save_image_to_file_from_url, get_file_extension_from_url, \
    get_imagefolder_filename


def fetch_xkcd_comix(comixid = 0):
    url = f"https://xkcd.com/info.0.json"
    if comixid:
        url = f"https://xkcd.com/{comixid}/info.0.json"

    payload ={

    }

    response = requests.get(url, params=payload)
    response.raise_for_status()

    xkcd_comix_info = response.json()
    if xkcd_comix_info['img']:
        index = xkcd_comix_info['num']
        image_extension = get_file_extension_from_url(xkcd_comix_info['img'])
        file_name = get_imagefolder_filename(f'xkcd_{index}{image_extension}')
        logging.info(f"Downloading image from url: {xkcd_comix_info['img']} to {file_name}")
        save_image_to_file_from_url(xkcd_comix_info['img'], file_name)

def setup():
    logging.getLogger().setLevel(logging.INFO)
    load_dotenv()
    get_imagefolder().mkdir(parents=True, exist_ok=True)

def main():
    fetch_xkcd_comix(353)


if __name__ == '__main__':
    setup()
    main()
