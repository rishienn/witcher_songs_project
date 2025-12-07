import re
from collections import Counter
import pymorphy3

morph = pymorphy3.MorphAnalyzer()

def tokenize(text: str):
    """
    Разбивает текст на слова, оставляя только буквы (русские и латинские), и возвращает список слов в нижнем регистре.
    """
    text = text.lower()
    words = []
    current_word = ""
    for char in text:
        if ('а' <= char <= 'я') or ('a' <= char <= 'z') or char == 'ё':
            current_word += char
        else:
            if current_word != "":
                words.append(current_word)
                current_word = ""
    if current_word != "":
        words.append(current_word)
    return words

def lemmatize_text(text: str):
    """
    Преобразует слова текста в их нормальные формы (леммы) и возвращает их список.
    """
    words = tokenize(text)
    lemmas = [morph.parse(w)[0].normal_form for w in words]
    return lemmas

def count_words(text: str):
    """
    Считает количество слов в тексте.
    """
    return len(tokenize(text))

def count_unique_lemmas(text: str):
    """
    Считает количество уникальных лемм в тексте.
    """
    return len(set(lemmatize_text(text)))

def calculate_ttr(text: str):
    """
    Вычисляет Type-Token Ratio (TTR) текста.
    """
    words = tokenize(text)
    return len(set(words)) / len(words) if words else 0

def find_longest_word(text: str):
    """
    Находит самое длинное слово в тексте.
    """
    words = tokenize(text)
    return max(words, key=len) if words else ""

def get_pos_statistics(text: str):
    """
    Считает количество слов каждой части речи в тексте.
    """
    pos_counts = Counter()
    for word in tokenize(text):
        p = morph.parse(word)[0]
        if p.tag.POS:
            pos_counts[p.tag.POS] += 1
    return dict(pos_counts)

def get_most_common_lemmas(text: str, n=10):
    """
    Находит n самых частых лемм в тексте.
    """
    lemmas = lemmatize_text(text)
    return Counter(lemmas).most_common(n)

def get_verbs(text: str):
    """
    Извлекает все глаголы текста в нормальной форме.
    """
    verbs = []
    for word in tokenize(text):
        p = morph.parse(word)[0]
        if p.tag.POS == "VERB":
            verbs.append(p.normal_form)
    return verbs

def count_specific_lemmas_unique(text: str, target_words: list):
    """
    Считает упоминания заданных слов/персонажей один раз на текст.
    """
    lemmas_set = set(lemmatize_text(text))
    return {word: int(word in lemmas_set) for word in target_words}

def lexical_density(text: str):
    """
    Вычисляет лексическую плотность текста (доля уникальных лемм).
    """
    lemmas = lemmatize_text(text)
    return len(set(lemmas)) / len(lemmas) if lemmas else 0