from pydub import AudioSegment
import speech_recognition as sr

import os

class SpeechRecognizer:
    def __init__(self) -> None:
        self.audio_format = 'wav'
        self.recognizer = sr.Recognizer()
    
    def __convert(self, path: str) -> None:
        ogg_version = AudioSegment.from_ogg(path)
        ogg_version.export('media/audio.'+self.audio_format,
                            format=self.audio_format)

    def recognize(self, path: str) -> str:
        self.__convert(path)
        
        with sr.AudioFile('media/audio.'+self.audio_format) as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.record(source)
        
        result = self.recognizer.recognize_vosk(audio, language="ru")
        return result[14:-3]

    def delete(self) -> None:
        os.remove('media/audio.ogg')
        os.remove('media/audio.wav')
