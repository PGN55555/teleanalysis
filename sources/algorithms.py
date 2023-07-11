import spacy
from spacy.lang.ru.stop_words import STOP_WORDS

import matplotlib.pyplot as plt
from wordcloud import WordCloud

from string import punctuation
from collections import Counter
from heapq import nlargest

import pandas as pd
from random import randint
import os

class TextPrepare:
    def __init__(self) -> None:
        self.nlp = spacy.load("ru_core_news_sm")
    

    def config(self, df) -> None:
        self.df = df
        self.text = ''
        self.text_with_audio = ''
        for i, msg in self.df.iterrows():
            if msg['text'] != None and not msg['is_audio']:
                self.text += msg['text'] + ' '
            elif msg['is_audio']:
                self.text_with_audio += msg['text'] + ' '
        self.text_with_audio += self.text
    
    def prepare(self) -> None:
        self.doc = self.nlp(self.text)
        self.doc_with_audio = self.nlp(self.text_with_audio)
        
        self.keyword = []
        self.keyword_with_audio = []
        stopwords = list(STOP_WORDS)
        pos_tag = ['PROPN', 'ADJ', 'NOUN', 'VERB']
        for token in self.doc:
            if token.text in stopwords or token.text in punctuation:
                continue
            if token.pos_ in pos_tag:
                self.keyword.append(token.text)
        
        for token in self.doc_with_audio:
            if token.text in stopwords or token.text in punctuation:
                continue
            if token.pos_ in pos_tag:
                self.keyword_with_audio.append(token.lemma_)


class Wordcloud:
    def create(self, keyword: list) -> None:
        text = ' '.join(keyword)
        colors = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
        index_color = randint(0, 4)
        cloud_obj = WordCloud(max_words=100,
                        background_color='white',
                        colormap=colors[index_color],
                        font_path='fonts/FuturaBookC.ttf',
                        width=2000,
                        height=1500)
        cloud = cloud_obj.generate(text)
        plt.imshow(cloud)
        plt.axis('off')
        plt.savefig('media/cloud.png', dpi=300, bbox_inches='tight')
        plt.cla()
        plt.clf()
    
    def delete(self) -> None:
        os.remove('media/cloud.png')


class Summary:
    def create(self, doc, keyword: list) -> str:
        freq_word = Counter(keyword)

        max_freq = Counter(keyword).most_common(1)[0][1]
        for word in freq_word.keys():
            freq_word[word] /= max_freq

        sent_strength = dict()
        for sent in doc.sents:
            for word in sent:
                if word.text in freq_word.keys():
                    if sent in sent_strength.keys():
                        sent_strength[sent] += freq_word[word.text]
                    else:
                        sent_strength[sent] = freq_word[word.text]

        result = nlargest(5, sent_strength, key=sent_strength.get)
        final = ' '.join([w.text for w in result])

        return final

class Morphemes:
    def create(self, doc) -> None:
        morphemes = [w.pos_ for w in doc]
        morphemes_count = Counter(morphemes)
        morphemes_count = dict(sorted(morphemes_count.items(),
                                      key=lambda item: item[1]))
        
        colors = ['indianred', 'seagreen', 'teal', 'steelblue', 'indigo']
        color_index = randint(0, 4)
        
        plt.bar(morphemes_count.keys(),
                morphemes_count.values(),
                color=colors[color_index])
        plt.ylabel('Количество появлений')
        plt.xlabel('Части речи')
        plt.xticks(rotation=45)
        plt.savefig('media/morphemes.png', dpi=300, bbox_inches='tight')
        plt.cla()
        plt.clf()

    def delete(self) -> None:
        os.remove('media/morphemes.png')

class MessagesCount:
    def create(self, df) -> None:
        dates_count = Counter(df['date'])
        dates_count = dict(sorted(dates_count.items()))
        
        colors = ['indianred', 'seagreen', 'teal', 'steelblue', 'indigo']
        color_index = randint(0, 4)
        
        plt.bar(dates_count.keys(),
                dates_count.values(),
                color=colors[color_index])
        plt.ylabel('Количество сообщений')
        plt.xlabel('Дата')
        plt.xticks(rotation=45)
        plt.savefig('media/dates.png', dpi=300, bbox_inches='tight')
        plt.cla()
        plt.clf()

    def delete(self) -> None:
        os.remove('media/dates.png')