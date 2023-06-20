import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from tokens import comunity_token, access_token, DSN
from backend import VkTools
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import base

Base = declarative_base()

engine = create_engine(DSN)
Base.metadata.create_all(engine)


class Botinterface:

    def __init__(self, comunity_token, access_token):
        self.bot = vk_api.VkApi(token=comunity_token)
        self.vk_tools = VkTools(access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0

    def write_msg(self, user_id, message=None, attachment=None):
        self.bot.method('messages.send', {'user_id': user_id,
                                          'message': message,
                                          'attachment': attachment,
                                          'random_id': get_random_id()})

    def handler(self):
        longpoll = VkLongPoll(self.bot)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == "привет":
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.write_msg(event.user_id, f'Хай, {self.params["name"]}')
                    if self.params["city"] == None:
                        self.write_msg(event.user_id, f'введите ваш город для поиска')
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                self.params["city"] = event.text.replace('-', ' ').title()
                                self.write_msg(event.user_id, f'город добавлен, {self.params["name"]}, {self.params["city"]}')
                                break
                    if self.params["bdate"] == None:
                        self.write_msg(event.user_id, f'введите ваш возраст для поиска')
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                if event.text.isdigit():
                                    self.params["bdate"] = int(event.text.title())
                                    self.write_msg(event.user_id, f'возраст добавлен, {self.params["name"]}, {self.params["city"]}, {self.params["bdate"]}')
                                    break
                elif event.text.lower() == "поиск":
                    self.write_msg(event.user_id, "начнем поиск")
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        while base.check_user(engine, profile_id=event.user_id, worksheet_id=worksheet["id"]) == True:
                            worksheet = self.worksheets.pop()
                        photos = self.vk_tools.photos_get(worksheet["id"])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.worksheets = self.vk_tools.user_serch(self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.photos_get(worksheet["id"])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                            self.offset += 30
                    self.write_msg(event.user_id, f'имя: {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}', attachment=photo_string)
                    base.add_user(engine=engine, profile_id=event.user_id, worksheet_id=worksheet["id"])
                elif event.text.lower() == "пока":
                    self.write_msg(event.user_id, "Пока((")
                else:
                    self.write_msg(event.user_id, "Не поняла вашего ответа...")



if __name__ == '__main__':
    bot = Botinterface(comunity_token, access_token)
    bot.handler()
