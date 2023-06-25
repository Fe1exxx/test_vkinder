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
                    """БЕРЁМ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ"""
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.write_msg(event.user_id, f'Хай, {self.params["name"]}, {self.params["year"]}')
                    """ПРОВЕРКА НАЛИЧИЯ ГОРОДА"""
                    if self.params["city"] == None:
                        self.write_msg(event.user_id, f'введите ваш город для поиска')
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                self.params["city"] = event.text.replace('-', ' ').title()
                                self.write_msg(event.user_id, f'город добавлен, {self.params["name"]}, {self.params["city"]}')
                                break
                    """ПРОВЕРКА НАЛИЧИЯ ВОЗРАСТА"""
                    if self.params["year"] == None:
                        self.write_msg(event.user_id, f'введите ваш год рождения для поиска')
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                if event.text.isdigit():
                                    self.params["year"] = int(event.text.title())
                                    self.write_msg(event.user_id, f'возраст добавлен, {self.params["name"]}, {self.params["city"]}, {self.params["year"]}')
                                    break
                elif event.text.lower() == "поиск":
                    self.write_msg(event.user_id, "начнем поиск")
                    """БОТ ИЩЕТ АНКЕТЫ ПО ДАННЫМ ПОЛЬЗОВАТЕЛЯ"""
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        while base.check_user(engine, profile_id=event.user_id, worksheet_id=worksheet["id"]) == True:
                            worksheet = self.worksheets.pop()
                        """БЕРЁМ 3 ФОТО ИЗ ВЫБРАННОЙ АНКЕТЫ"""
                        photos = self.vk_tools.photos_get(worksheet["id"])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.worksheets = self.vk_tools.user_serch(self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        while base.check_user(engine, profile_id=event.user_id, worksheet_id=worksheet["id"]) == True:
                            if len(self.worksheets):
                                worksheet = self.worksheets.pop()
                            photos = self.vk_tools.photos_get(worksheet["id"])
                            photo_string = ''
                            for photo in photos:
                                photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                            self.offset += 30
                        """ЗАПИСЬ АНКЕТЫ В БАЗУ ДАННЫХ"""
                    self.write_msg(event.user_id, f'имя: {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}', attachment=photo_string)
                    self.write_msg(event.user_id, base.check_user(engine, profile_id=event.user_id, worksheet_id=worksheet["id"]))
                    if base.check_user(engine, profile_id=event.user_id, worksheet_id=worksheet["id"]) == False:
                        base.add_user(engine=engine, profile_id=event.user_id, worksheet_id=worksheet["id"])
                    # elif event.text.lower() == "в избранное":
                    #     base.add_favorites(engine=engine, profile_id=event.user_id, worksheet_id=worksheet["id"])
                    # elif event.text.lower() == "в черный список":
                    #     base.add_black_list(engine=engine, profile_id=event.user_id, worksheet_id=worksheet["id"])
                elif event.text.lower() == "пока":
                    self.write_msg(event.user_id, "Пока((")
                else:
                    self.write_msg(event.user_id, "Не поняла вашего ответа...")



if __name__ == '__main__':
    bot = Botinterface(comunity_token, access_token)
    bot.handler()

