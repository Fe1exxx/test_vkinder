import requests
from pprint import pprint
from datetime import datetime
import vk_api
from tokens import access_token, comunity_token
from vk_api.exceptions import ApiError

class VkTools:
    def __init__(self, access_token):
        self.exp_api = vk_api.VkApi(token=access_token)

    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)


    def get_profile_info(self, user_id):

        try:
            info, = self.exp_api.method('users.get',
                                       {'user_id': user_id,
                                        'fields': 'city, sex, relation, bdate'
                                        }
                                       )
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if 'first_name' in info and 'last_name' in info else None,
                   'sex': info.get('sex'),
                   'city': info.get('city')['title'] if info.get('city') is not None else None,
                   'year': self._bdate_toyear(info.get('bdate'))
                   }


        return result

    def user_serch(self, profile, offset):

        try:
            profiles = self.exp_api.method('users.search',
                                           {'count': 30,
                                            'offset': offset,
                                            'hometown': profile['city'],
                                            'age_from': profile['year'] - 3,
                                            'age_to': profile['year'] + 3,
                                            'sex': 1 if profile['sex'] == 2 else 2,
                                            'has_foto': True
                                            })

        except ApiError as e:
            profiles = {}
            print(f'error = {e}')

        result = [{'name': item['first_name'] + ' ' + item['last_name'],
                   'id': item['id']
                   } for item in profiles['items'] if item['is_closed'] is False
                  ]

        return result

    def photos_get(self, id):

        try:
            photos = self.exp_api.method('photos.get',
                                          {'owner_id': id,
                                           'album_id': 'profile',
                                           'extended': 1
                                           })

        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        results = [{'owner_id': item['owner_id'],
                    'id': item['id'],
                    'likes': item['likes']['count'],
                    'comments': item['comments']['count']
                    } for item in photos['items']
                   ]

        results.sort(
            key=lambda item: item['comments'] + item['likes'],
            reverse=True
        )

        return results[0:3]



if __name__ == '__main__':
    tools = VkTools(comunity_token)
    user_id = 40507711
    profile = tools.get_profile_info(user_id)
    print(profile)
    
