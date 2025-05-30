import string
import nltk
import pymorphy3
from nltk.corpus import stopwords
import math

nltk.download("stopwords")

def text_prepare(f):

    with open(f, 'r', encoding="utf-8") as file:

        text = file.read().lower()
        text = ''.join([ch for ch in text if ch not in string.punctuation and ch not in ".«»…—–"]) # удаление знаков пунктуации
        text = ''.join([i if not i.isdigit() else ' ' for i in text]) # удаление чисел
        documents = text.split("\n\n")

        tokens = text.split()

        stop_words = set(stopwords.words('russian'))
        my_stop = ["я", "мой", "твой", "ты", "ваш", "вы", "мы", "ах", "ох", "ой", "ль", "б", "бы", "сам", "тот", "о", "к", "это", "ай", "эй", "этот", "тот", "те", "пpи", "от"]

        filtered_tokens = [word for word in tokens if word not in stop_words] # удаление стоп слов

        morph = pymorphy3.MorphAnalyzer()
        lemmed_words = [morph.parse(word)[0].normal_form for word in filtered_tokens] # приводим слова к их начальной форме
        lemmed_words = [word for word in lemmed_words if
               word not in my_stop]

        docs = []
        for doc in documents:
            doc = ''.join([ch for ch in doc if ch not in string.punctuation and ch not in ".«»…—–"])
            doc = ''.join([i if not i.isdigit() else ' ' for i in doc])
            doc = doc.split()
            doc = [word for word in doc if word not in stop_words]
            doc = [morph.parse(word)[0].normal_form for word in doc]
            doc = [word for word in doc if word not in my_stop]
            docs.append(set(doc))

    return lemmed_words, docs

def get_tf(words):

    dct = {}
    for word in words:
        dct[word] = dct.get(word, 0) + 1
    dct = dict(map(lambda x: (x[0], x[1]/len(words)), dct.items()))
    dct = sorted(dct.items(), key=lambda x: x[0])
    return sorted(dct, key=lambda x: x[1], reverse=True)

def get_idf(words, docs):
    dct = {}
    for word in set(words):
        dct[word] = math.log( len(words) / (sum(1 for doc in docs if word in doc) + 0.000000000000001) )
    return sorted(dct.items(), key=lambda x: x[0])

