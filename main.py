import os
from collections import Counter
from file_utils import read_text_file, write_text_file, read_csv_file, write_csv_file, get_files_in_folder
from text_utils import (
    lemmatize_text, count_words, count_unique_lemmas, calculate_ttr, find_longest_word,
    get_pos_statistics, get_most_common_lemmas, get_verbs, count_specific_lemmas_unique, lexical_density
)

import nltk
nltk.download('punkt')           # Токенизация
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng') # POS-tagging
nltk.download('wordnet')         # Лемматизация
nltk.download('stopwords')       # Стоп-слова

# Анализ одного текста
from nltk.corpus import stopwords
russian_stopwords = set(stopwords.words('russian'))

def analyze_single_text(filepath, filename):
    """
    Производит анализ каждого текста в корпусе.
    """
    text = read_text_file(filepath)
    if text.startswith("Ошибка"):
        return {"filename": filename, "error": text}

    lemmas = lemmatize_text(text)
    pos_stats = get_pos_statistics(text)

    filtered_lemmas = [l for l in lemmas if l not in russian_stopwords]
    top_lemmas = Counter(filtered_lemmas).most_common(10)

    verbs = get_verbs(text)

    return {
        "filename": filename,
        "text": text,
        "words_count": count_words(text),
        "lemmas": lemmas,
        "unique_lemmas": count_unique_lemmas(text),
        "ttr": round(calculate_ttr(text),4),
        "lexical_density": round(lexical_density(text),4),
        "longest_word": find_longest_word(text),
        "lines_count": text.count("\n")+1,
        "pos_stats": pos_stats,
        "top_lemmas": top_lemmas,
        "verbs": verbs
    }


# Анализ всего корпуса
def analyze_corpus(corpus_folder):
    results = []
    files = get_files_in_folder(corpus_folder, ".txt")
    print(f"Найдено {len(files)} файлов.\n")
    for i, fname in enumerate(files,1):
        print(f"[{i}/{len(files)}] Анализ: {fname}")
        filepath = os.path.join(corpus_folder, fname)
        results.append(analyze_single_text(filepath,fname))
    print("Анализ завершён.\n")
    return results

def generate_report(results, metadata, character_groups, color_words):
    """
    Выводит отчет.
    """
    report_lines = []
    report_lines.append("="*60)
    report_lines.append("ОТЧЁТ ПО АНАЛИЗУ КОРПУСА")
    report_lines.append("="*60+"\n")

    # Общая статистика
    total_texts = len([r for r in results if "error" not in r])
    total_words = sum(r["words_count"] for r in results if "error" not in r)
    all_lemmas = []
    for r in results:
        if "error" not in r:
            all_lemmas.extend(r["lemmas"])
    total_unique_lemmas = len(set(all_lemmas))
    avg_ttr = round(sum(r["ttr"] for r in results if "error" not in r)/total_texts,4) if total_texts else 0

    report_lines.append("ОБЩАЯ СТАТИСТИКА:")
    report_lines.append(f"  Всего текстов: {total_texts}")
    report_lines.append(f"  Всего слов: {total_words}")
    report_lines.append(f"  Всего уникальных слов: {total_unique_lemmas}")
    report_lines.append(f"  Средний TTR: {avg_ttr}\n")

    # Статистика по каждому тексту
    report_lines.append("ДЕТАЛЬНАЯ СТАТИСТИКА ПО ФАЙЛАМ:")
    report_lines.append("-"*50)
    metadata_map = {row["filename"]: row for row in metadata}

    for r in results:
        fname = r["filename"]
        meta = metadata_map.get(fname,{})
        title = meta.get("title",fname)
        report_lines.append(f"\n📄 {title}")
        report_lines.append(f"   Автор: {meta.get('author','?')}")
        report_lines.append(f"   Год: {meta.get('year','?')}")
        if "error" in r:
            report_lines.append(f"   Ошибка: {r['error']}")
            continue
        report_lines.append(f"   Слов: {r['words_count']}")
        report_lines.append(f"   Уникальных лемм: {r['unique_lemmas']}")
        report_lines.append(f"   TTR: {r['ttr']}")
        report_lines.append(f"   Лексическая плотность: {r['lexical_density']}")
        report_lines.append(f"   Самое длинное слово: {r['longest_word']}")
        report_lines.append(f"   Строк: {r['lines_count']}")
        report_lines.append("   Топ-10 лемм: " + ", ".join([f"{l}:{c}" for l,c in r["top_lemmas"]]))
        report_lines.append("   Части речи: " + ", ".join([f"{k}:{v}" for k,v in r["pos_stats"].items()]))
        report_lines.append("   5 самых употребляемых глаголов: " + ", ".join(r["verbs"][:5]))

    # Выводы по статистике
    report_lines.append("\nВЫВОДЫ И ИНТЕРПРЕТАЦИЯ:")

    # Подсчет персонажей
    report_lines.append("\nУпоминания персонажей (по текстам, один раз на текст):")
    for char, words in character_groups.items():
        count = sum(max(count_specific_lemmas_unique(r["text"], words).values()) for r in results if "error" not in r)
        report_lines.append(f"  {char}: {count}")

    # Поиск самого лексически разнообразного текста
    valid_results = [r for r in results if "error" not in r]
    if valid_results:
        metadata_map = {row["filename"]: row for row in metadata}
        lex_diverse = max(valid_results, key=lambda x: x["ttr"])
        title = metadata_map.get(lex_diverse["filename"], {}).get("title", lex_diverse["filename"])
        report_lines.append(f"\nСамый лексически разнообразный текст: {title} (TTR={lex_diverse['ttr']})")

    # Поиск автора с наибольшим количеством текстов
    authors = [metadata_map.get(r["filename"],{}).get("author","?") for r in results if "error" not in r]
    if authors:
        most_author = Counter(authors).most_common(1)[0]
        report_lines.append(f"Автор с наибольшим количеством текстов: {most_author[0]} ({most_author[1]})")

    #Поиск самого длинного слова
    all_longest = [r["longest_word"] for r in results if "error" not in r]
    report_lines.append(f"Самое длинное слово по корпусу: {max(all_longest, key=len) if all_longest else ''}")

    # Цветовая статистика по корпусу (с учетом форм слова и синонимов)
    color_variants = {
        "черный": ["черный","чёрный","чернота"],
        "белый": ["белый","беловатый","белизна","белоголовый","беловолосый"],
        "красный": ["красный","краснота","красноватый","кровь","кровавый"],
        "серый": ["пепельный","пепел","серебро","серебряный", "серый","сталь","стальной"],
        "желтый": ["желтый","золотой","золото"],
        "зеленый": ["изумрудный","изумруд","зелень","зеленый"],
        "фиолетовый": ["фиолетовый","фиалковый","фиалка","сирень"],
    }

    color_counts = {color: 0 for color in color_words}

    for r in results:
        if "error" in r:
            continue
        lemmas_set = set(r["lemmas"])
        for color, variants in color_variants.items():
            # если любая лемма текста совпадает с любым вариантом цвета, учитываем
            if any(var in lemmas_set for var in variants):
                color_counts[color] += 1

    report_lines.append("\nЦветограмма:")
    max_val = max(color_counts.values()) if color_counts else 1
    for color, val in color_counts.items():
        bar = "█" * int(40*val/max_val) if val > 0 else ""
        report_lines.append(f"{color:12}: {bar} ({val})")

    # Подсчет топ-10 лемм
    counter = Counter()
    for r in valid_results:
        filtered_lemmas = [l for l in r["lemmas"] if l not in russian_stopwords]
        counter.update(filtered_lemmas)

    report_lines.append("\n10 самых частотных лемм:")
    for l,c in counter.most_common(10):
        report_lines.append(f"  {l}: {c}")


    # Подсчет средней длины текста
    avg_words = round(sum(r["words_count"] for r in valid_results)/len(valid_results),2) if valid_results else 0
    avg_lines = round(sum(r["lines_count"] for r in valid_results)/len(valid_results),2) if valid_results else 0
    report_lines.append(f"\nСредняя длина текста (слов): {avg_words}")
    report_lines.append(f"Средняя длина текста (строк): {avg_lines}")

    # Подсчет самых частотных глаголов (топ-5)
    verbs_counter = Counter()
    for r in valid_results:
        verbs_counter.update(r["verbs"])
    report_lines.append("\n5 самых употребляемых глаголов:")
    for v,c in verbs_counter.most_common(5):
        report_lines.append(f"  {v}: {c}")

    # Самая частотная часть речи
    pos_counter = Counter()
    for r in valid_results:
        pos_counter.update(r["pos_stats"])
    if pos_counter:
        most_pos = pos_counter.most_common(1)[0]
        report_lines.append(f"\nСамая частотная часть речи: {most_pos[0]} ({most_pos[1]})")

    return "\n".join(report_lines)

def main():
    """
    Создает CSV-файл и вызывает предыдущие функции
    """
    corpus_folder = "corpus"
    metadata_file = "data/metadata.csv"

    metadata = read_csv_file(metadata_file)
    results = analyze_corpus(corpus_folder)

    character_groups = {
        "Геральт": ["волк","белый","геральт","белоголовый","беловолосый","ведьмак","охотник","сталь","меч"],
        "Цири": ["ласточка","дитя","девочка","цири","цирилла","фалька","пепельный","зеленый","башня"],
        "Йеннифэр": ["йеннифэр","йеннифер","йен","чародейка","сирень","крыжовник","ночь"]
    }

    color_words = ["черный","белый","красный","желтый","зеленый","серый","фиолетовый"]

    # CSV
    headers = ["filename","author","year","title","words_count","unique_lemmas","ttr","lexical_density","longest_word","lines_count"]
    csv_rows = []
    meta_map = {row["filename"]: row for row in metadata}
    for r in results:
        m = meta_map.get(r["filename"],{})
        csv_rows.append([
            r["filename"],
            m.get("author",""),
            m.get("year",""),
            m.get("title",""),
            r.get("words_count",""),
            r.get("unique_lemmas",""),
            r.get("ttr",""),
            r.get("lexical_density",""),
            r.get("longest_word",""),
            r.get("lines_count","")
        ])
    os.makedirs("results", exist_ok=True)
    write_csv_file("results/statistics.csv", csv_rows, headers)

    # TXT
    report = generate_report(results, metadata, character_groups, color_words)
    write_text_file("results/report.txt", report)
    print("\nВсе результаты сохранены в папке results.\n")

if __name__ == "__main__":
    main()