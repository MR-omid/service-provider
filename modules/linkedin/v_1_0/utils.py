import hashlib
import os
import time

from PIL import Image

from components.Qhttp import Qhttp

def save_image(url, username, process_id):
    """
     :param url:  download content of this url
     :param username:  use for naming files
     :param process_id:  use for saving in correct path
     :return: the path that can download photos
     """

    if username is None:
        return ''

    storage = [
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        '/modules/storage/' + process_id]
    base_path = storage[0]
    relative_path = storage[1]
    img_full_path = base_path + '/' + relative_path + '/'
    thumbnail_full_path = base_path + '/' + relative_path + '/' + 'thumbnail' + '/'
    thumbnail_save_path = ''
    file = str(hashlib.md5(username.encode('utf-8')).hexdigest()) + str(
        hashlib.md5(str(int(round(time.time() * 1000))).encode('utf-8')).hexdigest())
    os.makedirs(img_full_path, exist_ok=True)
    os.makedirs(thumbnail_full_path, exist_ok=True)
    try:  # using Qhttps get request to download
        img_data = Qhttp.get(url, timeout=10).content
        img_save_path = img_full_path + file + '.jpg'
        image = open(img_save_path, 'wb')
        image.write(img_data)
        image.close()
    except Exception:
        return ['', '', '']
    try:
        size = 72, 72
        thumbnail_save_path = thumbnail_full_path + file + '.jpg'
        image = Image.open(img_save_path)
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(thumbnail_save_path, quality=40, optimize=True)
    except Exception:
        pass
    return [img_save_path, thumbnail_save_path, file]
