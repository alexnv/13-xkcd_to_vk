import argparse
import logging
import os
import pathlib
import random
import sys

import requests
from dotenv import load_dotenv

VK_APIVERSION = "5.131"
MAX_COMIX = 999

from common_functions import save_image_to_file_from_url, get_file_extension_from_url


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
        file_name = pathlib.Path.cwd() / 'images' / f'xkcd_{index}{image_extension}'
        logging.info(f"Скачиваем файл по адресу: {xkcd_comix_info['img']} в {file_name}")
        save_image_to_file_from_url(xkcd_comix_info['img'], file_name)
        comix_comment = xkcd_comix_info['alt']
        return file_name, comix_comment
    return None

def parse_vk_response(response, result_key, operation):
    if result_key in response:
        return response[result_key]
    elif 'error' in response:
        logging.error(f"Ошибка {operation}. Детали {response['error']['error_msg']}")
        return None

def get_image_upload_url(vk_groupid, vk_accesstoken):
    url = f"https://api.vk.com/method/photos.getWallUploadServer"
    payload = {
        "access_token": vk_accesstoken,
        "v": VK_APIVERSION,
        "group_id": vk_groupid
    }

    logging.info(f"Получаем адрес VK для загрузки изображения для группы {vk_groupid}")
    response = requests.get(url, params=payload)
    response.raise_for_status()

    response_or_error = response.json()
    result = parse_vk_response(response_or_error, 'response', 'Получение адреса загрузки изображения')
    if result:
        return result['upload_url']

    return None


def upload_file(url, filename):
    logging.info(f"Загружаем файл {filename} по адресу {url}")
    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
    response.raise_for_status()

    response_or_error = response.json()
    result = parse_vk_response(response_or_error, 'photo', 'Загрузка изображения')
    if result:
        return result['photo'], result['server'], result['hash']

    return None



def save_photo_to_wall(photo, server, hash, vk_groupid, vk_accesstoken):
    url = f"https://api.vk.com/method/photos.saveWallPhoto"
    payload = {
        "access_token": vk_accesstoken,
        "v": VK_APIVERSION,
        "group_id": vk_groupid,
        "photo": photo,
        "server": server,
        "hash": hash
    }

    logging.info(f"Сохранение фотографии в группу {vk_groupid}")
    response = requests.get(url, params=payload)
    response.raise_for_status()
    response_or_error = response.json()
    result = parse_vk_response(response_or_error, 'response', 'Сохранение изображения')
    if result:
        return result

    return None


def publish_photo(vk_saved_photo, photo_comment, vk_groupid, vk_accesstoken):
    url = f"https://api.vk.com/method/wall.post"
    attachments = ""
    attachments += f"photo{vk_saved_photo['owner_id']}_{vk_saved_photo['id']}"
    payload = {
        "access_token": vk_accesstoken,
        "v": VK_APIVERSION,
        "group_id": vk_groupid,
        "owner_id": f"-{vk_groupid}",
        "from_group": "1",
        "message": photo_comment,
        "attachments": attachments
    }
    logging.info(f"Публикация фотографии на странице группы {vk_groupid}")
    response = requests.get(url, params=payload)
    response.raise_for_status()
    response_or_error = response.json()
    result = parse_vk_response(response_or_error, 'response', 'Сохранение изображения')
    if result:
        return result

    return None


def upload_photo_to_vk(filename, photo_comment, vk_groupid, vk_accesstoken):
    upload_url = get_image_upload_url(vk_groupid, vk_accesstoken)
    if not upload_url:
        return False
    photo, server, photo_hash = upload_file(upload_url, filename, vk_groupid, vk_accesstoken)
    if not photo:
        return False
    vk_saved_photo = save_photo_to_wall(photo, server, photo_hash, vk_groupid, vk_accesstoken)
    if not vk_saved_photo:
        return False
    vk_post = publish_photo(vk_saved_photo[0], photo_comment, vk_groupid, vk_accesstoken)
    if not vk_post:
        return False
    return True


def setup():
    logging.getLogger().setLevel(logging.INFO)
    image_folder = pathlib.Path.cwd() / 'images'
    image_folder.mkdir(parents=True, exist_ok=True)
    load_dotenv()


def init_args():
    random_comix_id = random.randrange(1, MAX_COMIX)
    parser = argparse.ArgumentParser(description='Программа загружает фото XKCD и публикует на стену VK')
    parser.add_argument('id', help='Номер комикса, если не указан будет сохранен случайный комикс', nargs='?',
                        default=random_comix_id, type=int)

    return parser.parse_args(sys.argv[1:])


def main():
    setup()
    args = init_args()
    vk_access_token = os.getenv("VK_ACCESS_TOKEN", "")
    vk_groupid = os.getenv("VK_GROUPID", "")

    if not vk_access_token:
        logging.error("Не задано значение переменной окружения VK_ACCESS_TOKEN")
        sys.exit()
    if not vk_groupid:
        logging.error("Не задано значение переменной окружения VK_GROUPID")
        sys.exit()
    comix_id = args.id
    try:
        logging.info(f"Скачиваем комикс с номером {comix_id}")
        comix_filename, comix_comment = fetch_xkcd_comix(comix_id)
        if not comix_filename:
            return
        uploaded = upload_photo_to_vk(comix_filename, comix_comment, vk_accesstoken=vk_access_token,
                                      vk_groupid=vk_groupid)
        if uploaded:
            logging.info(f"Комикс успешно опубликован! Удаляем файл комикса {comix_filename}")
            pathlib.Path.unlink(comix_filename)
    finally:
        if pathlib.Path.exists(comix_filename):
            pathlib.Path.unlink(comix_filename)


if __name__ == '__main__':
    main()
