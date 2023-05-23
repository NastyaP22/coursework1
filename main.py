import os
from datetime import datetime
import json

import requests
from dotenv import load_dotenv

load_dotenv()

class CopyVkPhotos:

    def __init__(self):
        self.vk_token = os.getenv('vk_token')

    def get_photos(self, id, count='5'):
        self.id = id
        self.count = count
        url_vk = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': id, 
                  'access_token': {self.vk_token}, 
                  'v': '5.131', 
                  'album_id': 'profile',
                  'rev': '1',
                  'extended': '1',
                  'photo_sizes': '1',
                  'count': count
                  }
        response = requests.get(url=url_vk, params=params)
        data = response.json()
        return data

class SendPhotosToYandex:
    def get_headers(self, yandex_token):
        self.yandex_token = yandex_token
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.yandex_token}'
        }
    
    def upload_photos(self, yandex_token, data):
        self.yandex_token = yandex_token
        self.data = data
        url_yandex = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers(f'{self.yandex_token}')
        with open('new_file.json', 'w') as f:
            json.dump(data, f, indent=2)
        file_names = []
        files_info = []
        res_data = {'files_info': files_info}
        with open('new_file.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            index = 0
            for obj in json_data['response']['items']:
                index += 1
                for photo in obj['sizes']:
                    if photo['type'] == 'w':
                        photo_url = photo['url']
                        photo_type = 'w'
                        break
                likes_count = obj['likes']['count']
                date_unix = int(obj['date'])
                date = datetime.utcfromtimestamp(date_unix).strftime('%Y-%m-%d %H:%M:%S')
                dict = {
                    'url': photo_url, 'likes_count': likes_count, 'date': date
                }
                file_name = likes_count
                if file_name not in file_names:
                    file_names.append(file_name)
                else:
                    file_name = f'{likes_count}-{date[:10]}'
                    file_names.append(file_name)
                with open(f'user_photo{index}', 'w') as photo:
                    json.dump(dict, photo, indent=2)
                file_path = f'Фото из ВК/{file_name}.jpg'
                params = {'path': file_path, 'overwrite': 'true'}
                response = requests.get(url=url_yandex, headers=headers, params=params)
                params = {'path': file_path, 'url': photo_url}
                response = requests.post(url=url_yandex, headers=headers, params=params)
                if response.status_code == 202:
                    print('Фото загружено')
                    data = {'file_name': f'{file_name}.jpg', 'size': photo_type}
                    files_info.append(data)
                else:
                    print(f'Ошибка {response.status_code}')
        with open('uploaded_files_info.json', 'w') as res:
            json.dump(res_data, res, indent=2)




copy_test = CopyVkPhotos()
id = input('Введите id пользователя vk: ')
data = copy_test.get_photos(id)
yandex_token = os.getenv('yandex_token')
send_test = SendPhotosToYandex()
send_test.upload_photos(yandex_token, data)