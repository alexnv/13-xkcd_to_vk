import argparse
import logging
import os
import pathlib
import random
import sys

import requests
from dotenv import load_dotenv

VK_ACCESS_TOKEN = ""
VK_GROUPID = ""
VK_APIVERSION = "5.131"

from common_functions import get_imagefolder, save_image_to_file_from_url, get_file_extension_from_url, \
    get_imagefolder_filename


def fetch_xkcd_comix(comixid=0):
    url = f"https://xkcd.com/info.0.json"
    if comixid:
        url = f"https://xkcd.com/{comixid}/info.0.json"

    payload = {

    }
    logging.info(f"Получаем информацию по комиксу {comixid} по адресу {url}")
    response = requests.get(url, params=payload)
    response.raise_for_status()

    xkcd_comix_info = response.json()
    if xkcd_comix_info['img']:
        index = xkcd_comix_info['num']
        image_extension = get_file_extension_from_url(xkcd_comix_info['img'])
        file_name = get_imagefolder_filename(f'xkcd_{index}{image_extension}')
        logging.info(f"Скачиваем файл по адресу: {xkcd_comix_info['img']} в {file_name}")
        save_image_to_file_from_url(xkcd_comix_info['img'], file_name)
        comix_comment = xkcd_comix_info['alt']
        return (file_name, comix_comment)
    return None


def vk_getuploadurl(vk_groupid="", vk_accesstoken=""):
    url = f"https://api.vk.com/method/photos.getWallUploadServer"
    payload = {
        "access_token": vk_accesstoken,
        "v": VK_APIVERSION,
        "group_id": vk_groupid
    }

    logging.info(f"Получаем адрес VK для загрузки изображения для группы {VK_GROUPID}")
    response = requests.get(url, params=payload)
    response.raise_for_status()

    response_or_error = response.json()
    if 'response' in response_or_error:
        return response_or_error['response']['upload_url']
    elif 'error' in response_or_error:
        logging.error(f"Ошибка получения адреса загрузки изображения. Детали {response_or_error['error']['error_msg']}")
        return None


def vk_upload_file(url, filename, vk_groupid="", vk_accesstoken=""):
    logging.info(f"Загружаем файл {filename} по адресу {url}")
    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()

        response_or_error = response.json()
        if 'photo' in response_or_error:
            return response_or_error
        elif 'error' in response_or_error:
            logging.error(
                f"Ошибка загрузки изображения. Детали {response_or_error['error']['error_msg']}")
            return None


def vk_save_photo_to_wall(photoObject, vk_groupid="", vk_accesstoken=""):
    url = f"https://api.vk.com/method/photos.saveWallPhoto"
    payload = {
        "access_token": vk_accesstoken,
        "v": VK_APIVERSION,
        "group_id": vk_groupid,
        "photo": photoObject['photo'],
        "server": photoObject['server'],
        "hash": photoObject['hash']
    }

    logging.info(f"Сохранение фотографии в группу {vk_groupid}")
    response = requests.get(url, params=payload)
    response.raise_for_status()
    response_or_error = response.json()
    if 'response' in response_or_error:
        return response_or_error['response']
    elif 'error' in response_or_error:
        logging.error(
            f"Ошибка сохранения изображения. Детали {response_or_error['error']['error_msg']}")
        return None


def vk_publish_photo(vk_saved_photo, photo_comment, vk_groupid, vk_accesstoken):
    url = f"https://api.vk.com/method/wall.post"
    attachments = ""
    for vk_photo in vk_saved_photo:
        attachments += f"photo{vk_photo['owner_id']}_{vk_photo['id']}"
    payload = {
        "access_token": vk_accesstoken,
        "v": VK_APIVERSION,
        "group_id": vk_groupid,
        "owner_id": "-" + vk_groupid,
        "from_group": "1",
        "message": photo_comment,
        "attachments": attachments
    }
    logging.info(f"Публикация фотографии на странице группы {vk_groupid}")
    response = requests.get(url, params=payload)
    response.raise_for_status()
    response_or_error = response.json()

    if 'response' in response_or_error:
        return response_or_error['response']
    elif 'error' in response_or_error:
        logging.error(
            f"Ошибка сохранения изображения. Детали {response_or_error['error']['error_msg']}")
        return None


def upload_photo_to_vk(filename, photo_comment, vk_groupid="", vk_accesstoken=""):
    upload_url = vk_getuploadurl(vk_groupid, vk_accesstoken)
    if upload_url:
        vk_photo = vk_upload_file(upload_url, filename, vk_groupid, vk_accesstoken)
        if vk_photo:
            vk_saved_photo = vk_save_photo_to_wall(vk_photo, vk_groupid, vk_accesstoken)
            if vk_saved_photo:
                vk_post = vk_publish_photo(vk_saved_photo, photo_comment, vk_groupid, vk_accesstoken)
                return True


def setup():
    logging.getLogger().setLevel(logging.INFO)
    get_imagefolder().mkdir(parents=True, exist_ok=True)
    load_dotenv()


def init_args():
    random_comix_id = random.randrange(1, 300)
    parser = argparse.ArgumentParser(description='Программа загружает фото XKCD и публикует на стену VK')
    parser.add_argument('id', help='Номер комикса, если не указан будет сохранен случайный комикс', nargs='?',
                        default=random_comix_id)

    return parser.parse_args(sys.argv[1:])


def main():
    setup()
    args = init_args()
    VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN", "")
    VK_GROUPID = os.getenv("VK_GROUPID", "")

    if not VK_ACCESS_TOKEN:
        logging.error("Не задано значение переменной окружения VK_ACCESS_TOKEN")
        exit()
    if not VK_GROUPID:
        logging.error("Не задано значение переменной окружения VK_GROUPID")
        exit()
    comix_id = int(args.id)
    logging.info(f"Скачиваем комикс с номером {comix_id}")
    comix_filename, comix_comment = fetch_xkcd_comix(comix_id)
    if comix_filename:
        uploaded = upload_photo_to_vk(comix_filename, comix_comment, vk_accesstoken=VK_ACCESS_TOKEN,
                                      vk_groupid=VK_GROUPID)
        if uploaded:
            logging.info(f"Комикс успешно опубликован! Удаляем файл комикса {comix_filename}")
            pathlib.Path.unlink(comix_filename)


if __name__ == '__main__':
    main()
