import os
import sys
import requests
import zulip

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tg_bot_admin.settings")
import django
django.setup()
from django.conf import settings

from logger import create_logger
logger = create_logger(logger_name=__name__)

class ZulipException(Exception):
    pass

class ZulipClient():
    def __init__(self):
        self.is_active = False
        self._create_client()

    def _create_client(self):
        try:
            self.client = zulip.Client(
                api_key=settings.ZULIP_API_KEY,
                email=settings.ZULIP_EMAIL,
                site=settings.ZULIP_SITE,
                insecure=settings.ZULIP_ALLOW_INSECURE
            )
            self.is_active = True
            logger.info("ZulipClient настроен.")

        except Exception as e:
            self.is_active = False
            logger.fatal(e)
            # raise ZulipException(e)

    def send_msg_to_channel(self, channel_name: str, topic: str, msg: str) -> str:
        request = {
            "type": "channel",
            "to": channel_name,
            "topic": topic,
            "content": msg,
        }
        result = self.client.send_message(request)

        # {'result': 'error', 'msg': "Channel with ID '79219376763' does not exist", 'stream_id': 79219376763,
        # 'code': 'STREAM_DOES_NOT_EXIST'}

        if result["result"] == "success":
            logger.info(f"Отправлено сообщение в канал '{channel_name}'")
        else:
            err_msg = f"Ошибка при отправлении сообщения в канал'{channel_name}' - {result.get('msg', '')}"
            logger.warning(err_msg)
            #raise ZulipException(err_msg)

    def get_channel_id(self, channel_name: str) -> int:
        # по названию канала возвращает его ID, или 0, если канала нет
        #
        # {'result': 'error', 'msg': "Invalid channel name 'tg_bot'", 'code': 'BAD_REQUEST'}
        # {'result': 'success', 'msg': '', 'stream_id': 6}

        # if not channel_name:
        #     raise ValueError("Не указано название канала.")

        result = self.client.get_stream_id(channel_name)

        if result["result"] == 'success':
            return result["stream_id"]
        elif (result["result"] == 'error' and "Invalid channel name" in result["msg"]):  # todo
            return 0
        else:
            err_msg = f"Ошибка при обращении к каналу (get_channel_id) '{channel_name}' - {result.get('msg', '')}"
            logger.warning(err_msg)
            # raise ZulipException(err_msg)

    def is_channel_exists(self, channel_name: str) -> bool:
        channel_id = self.get_channel_id(channel_name)
        return channel_id > 0

    def subscribe_to_channel(self, channel_name: str, principals: [int]=[]) -> int:
        # Create and subscribe to channel.
        # в параметр principals можно передать список [user_id] , которые будут подписаны на канал
        # {'result': 'success', 'msg': '', 'subscribed': {'8': ['канал про все']}, 'already_subscribed': {}} - если канал создали
        # {'result': 'success', 'msg': '', 'subscribed': {}, 'already_subscribed': {'8': ['Zulip']}} - если канал уже был
        # if not channel_name:
        #     raise ValueError("Не указано название канала.")

        result = self.client.add_subscriptions(
            streams=[
                {
                    "name": channel_name,
                    "description": "Описание канала",
                },

            ],
            principals=principals,
        )

        if result["result"] == "success":
            if not principals:
                logger.info(f"Создан канал '{channel_name}'")
            else:
                logger.info(f"Создан канал '{channel_name}'. Пользователи {principals} подписаны на канал.")

            return channel_name
        else:
            err_msg = f"Ошибка при подписании на канал '{channel_name}' - {result.get('msg', '')}"
            logger.warning(err_msg)
            # raise ZulipException(err_msg)

    def get_group_members(self, group_id: int):
        # возвращает массив [user_ids]
        try:
            group_id = int(group_id)
        except ValueError:
            logger.warning(f"Неправильный номер группы Zulip - {group_id}")
            return []

        params = {
            'direct_member_only': 'false',
        }

        response = requests.get(
            f'{settings.ZULIP_SITE}/api/v1/user_groups/{group_id}/members',
            params=params,
            auth=(settings.ZULIP_EMAIL, settings.ZULIP_API_KEY),
        )

        response = response.json()
        if response["result"] == "success":
            return response["members"]

        return []


if __name__ == '__main__':
    try:
        client = ZulipClient()
    except ZulipException:
        sys.exit("Фатальная ошибка! Выполнение программы прекращено!")
        
        
    # add channel / subscribe_to_channel
    #
    # print(client.subscribe_to_channel("+79219376763"))

    # send_msg_to_channel
    #
    # client.send_msg_to_channel(
    #     "+79219376763",
    #     "tg_bot",
    #     "Тестовое сообщение 5"
    # )

    # get_channel_id
    #
    # try:
    #     ch_name = "Zulip"
    #     print(f"ID of channel '{ch_name}' is: {client.get_channel_id(ch_name)}")
    #     ch_name = "not_exist"
    #     print(f"ID of channel '{ch_name}' is: {client.get_channel_id(ch_name)}")
    # except ZulipException as e:
    #     print(e)

    # get_
    group_id = 47 # ТехОтдел
    print(client.get_group_members(group_id))
