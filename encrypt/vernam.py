from random import randint

class Vernam:    
    def genetate_key(self, length: int) -> str:     
        alphabet = 'qwertyuiopasdfghjklzxcvbnm'
        length = 10 if length >= 10 else length
        key = [alphabet[randint(0, len(alphabet) - 1)] for i in range(length)]
        return ''.join(key)
    
    def __correct_key(self, key: str, length: int) -> str:
        return key * (length // len(key)) + key[:length%len(key)]
    
    def __int_key(self, key: str) -> int:
        return ord(key) % self.dim_max
    
    def encrypt(self, text: str, key: str) -> str:
        self.dim_max = ord(max(list(text)))
        new_data_array = [0 for i in range(len(text))]
        key = self.__correct_key(key, len(text))
        for i, symbol in enumerate(text):
            new_data_array[i] = chr(self.__int_key(key[i]) ^ ord(symbol))
        return ''.join(new_data_array)

    def decrypt(self, text: str, key: str) -> str:
        return self.encrypt(text, key)
