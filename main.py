import json
import datetime
import os


"""
Перевод указанной пользователем даты в миллисекунды.
По умолчанию указана дата 1970-1-3 00:00:00
"""


def convert_time(year=1970, month=1, day=3, hour=0, min=0, sec=0):
    milliseconds = int(
        datetime.datetime(year, month, day, hour, min, sec).timestamp() * 1000
    )
    return milliseconds


def open_file():
    with open("library.json", "r", encoding="utf-8") as input_file:
        data = json.load(input_file)
        return data


def write_file(doc_title, citations):
    os.mkdir('Books')
    with open(doc_title, "w", encoding="utf-8") as output_file:
        output_file.write(citations)


def main():
    data_string = open_file()["docs"]  # открыть исходный файл
    for item in data_string:
        citations = ""
        if item["citations"] != []:
            doc_title = f'{item["data"]["doc_title"]}.md'  # название книги => имя выходного файла
            for citation in item["citations"]:
                if convert_time() < citation["note_insert_time"]:
                    citations += f'>{citation["note_body"]}\n'
            write_file(doc_title, citations)


if __name__ == "__main__":
    main()
