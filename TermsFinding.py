import math
import re

import plotly.graph_objects as go
import pymorphy2


def PrepareText(filename):
    """Предобработка текста"""
    with open(filename, 'r') as file:
        text = file.read().replace(',', ' ').replace('.', ' ').replace('-', ' ').replace('\n', ' ')
    text = re.sub(r'[a-z]([A-Z])', r'-\1', text).lower()
    return re.compile('\w+').findall(text)


def nGramsVocab(words, n):
    """Построение частотного словаря"""
    vocab = dict()
    for i in range(len(words) - n + 1):
        if " ".join(words[i:i + n]) in vocab:
            vocab[" ".join(words[i:i + n])] += 1
        else:
            vocab[" ".join(words[i:i + n])] = 1
    return vocab


def VisualizeVocab(vocab, metrics, topElems):
    """Визуализация частотного словаря"""
    sortedVocab = sorted(vocab.items(), key=lambda pair: pair[1], reverse=True)
    vocabKeys, vocabValues = zip(*sortedVocab)

    if metrics == 'qnt':
        fig = go.Figure(data=[go.Table(header=dict(values=['Словосочетание', 'Количество']),
                                       cells=dict(values=[vocabKeys[:topElems], vocabValues[:topElems]]))])
        fig.update_layout(width=500, height=3000)
        fig.show()

    if metrics == 'prob':
        vocabProb = list(vocabValues)
        length = sum(vocabValues)
        for i in range(len(vocabProb)):
            vocabProb[i] = round(vocabProb[i] / length, 3)
        fig = go.Figure(data=[go.Table(header=dict(values=['Словосочетание', 'Вероятность']),
                                       cells=dict(values=[vocabKeys, vocabProb]))])
        fig.update_layout(width=500, height=3000)
        fig.show()

    if metrics == 'qntprob':
        vocabProb = list(vocabValues)
        length = sum(vocabValues)
        for i in range(len(vocabProb)):
            vocabProb[i] = round(vocabProb[i] / length, 3)
        fig = go.Figure(data=[go.Table(header=dict(values=['Словосочетание', 'Количество', 'Вероятность']),
                                       cells=dict(values=[vocabKeys[:topElems], vocabValues[:topElems],
                                                          vocabProb[:topElems]]))])
        fig.update_layout(width=500, height=3000)
        fig.show()


def FrequencySort(words):
    """Упорядочивание по мере частотности"""
    terms = dict()
    for i in range(len(words)):
        words[i] = morph.parse(words[i])[0].normal_form

    for i in range(len(words)):
        if morph.parse(words[i])[0].tag.POS == 'ADJF' and morph.parse(words[i + 1])[0].tag.POS == 'NOUN':
            if " ".join(words[i:i + 2]) in terms:
                terms[" ".join(words[i:i + 2])] += 1
            else:
                terms[" ".join(words[i:i + 2])] = 1

    VisualizeVocab(terms, 'qntprob', 20)
    return terms


def MutualInfoSort(words):
    """Упорядочивание по мере взаимной информации"""
    for i in range(len(words)):
        words[i] = morph.parse(words[i])[0]
        words[i] = words[i].normal_form
        terms = dict ()

    vocab1 = nGramsVocab(words, 1)

    for i in range(len(words)):
        if morph.parse(words[i])[0].tag.POS == 'ADJF' and morph.parse(words[i + 1])[0].tag.POS == 'NOUN':
            if " ".join(words[i:i + 2]) in terms:
                terms[" ".join(words[i:i + 2])] += 1
            else:
                terms[" ".join(words[i:i + 2])] = 1

    for key in terms:
        terms[key] = round(math.log((terms[key] * len(words)) / (
                vocab1[re.compile('\w+').findall(key)[0]] * vocab1[re.compile('\w+').findall(key)[1]]), 2), 3)

    sortedTerms = sorted(terms.items(), key=lambda pair: pair[1], reverse=True)
    termsKeys, termsValues = zip(*sortedTerms)
    fig = go.Figure(data=[go.Table(header=dict(values=['Словосочетание', 'Взаимная информация']),
                                   cells=dict(values=[termsKeys[:20], termsValues[:20]]))])
    fig.update_layout(width=500, height=3000)
    fig.show()
    return terms


# подготовка данных
words = PrepareText('polit.txt')
morph = pymorphy2.MorphAnalyzer()

# топ конструкций по частотности
vocab = FrequencySort(words)

# топ конструкций по взаимной информации
vocab = MutualInfoSort(words)
