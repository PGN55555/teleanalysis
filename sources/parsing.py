import configparser
from datetime import datetime, timedelta
import pandas as pd

from sources.speech_recognition import SpeechRecognizer

from telethon.sync import TelegramClient

class Parsing:
    def __init__(self) -> None:
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.client = TelegramClient('parsing_session', 
                                config['PARSER']['api_id'], 
                                config['PARSER']['api_hash'])
        self.client.start()

        self.sr = SpeechRecognizer()


    async def chat_exist(self, chat_name: str) -> bool:
        try:
            result = await self.client.get_messages(chat_name, limit=1)
            return len(result) != 0
        except:
            return False
    
    def __get_data(self, data: str):
        return datetime.strptime(data, '%d.%m.%Y').date()

    def check_format_data(self, data: str) -> bool:
        try:
            self.__get_data(data)
            return True
        except:
            return False
    
    def get_df(self):
        return self.df
    
    async def parse(self, chat_info: dict) -> None:
        self.df = pd.DataFrame(columns=['date', 'sender',
                                         'text', 'is_audio'])
        chat_name = chat_info['chat_name']
        date_min = self.__get_data(chat_info['date_min'])
        date_max = self.__get_data(chat_info['date_max']) + timedelta(days=1)
        pre_first_msg = await self.client.get_messages(chat_name, 
                                                 offset_date=date_min,
                                                 limit=1)
        last_msg = await self.client.get_messages(chat_name,
                                             offset_date=date_max,
                                             limit=1, reverse=True)
        
        if len(pre_first_msg) == 0:
            pre_first_msg = await self.client.get_messages(chat_name, 
                                             limit=1, reverse=True)
        if len(last_msg) == 0:
            last_msg = await self.client.get_messages(chat_name,
                                             limit=1)
            
        result_all = await self.client.get_messages(chat_name,
                                          min_id=pre_first_msg[0].id,
                                          max_id=last_msg[0].id)

        for i, message in enumerate(result_all):
            if message.voice == None:
                self.df.loc[i] = [message.date.date(), await message.get_sender(),
                                  message.text, 0]
            else:
                path = 'media/audio.ogg'
                await self.client.download_media(message=message, file=path)
                message_text = self.sr.recognize(path)
                self.sr.delete()
                self.df.loc[i] = [message.date.date(), await message.get_sender(),
                                  message_text, 1]
        
    