import json
import datetime


"""
Перевод указанной пользователем даты в миллисекунды.
По умолчанию указана дата 1970-1-3 00:00:00
"""


def convert_time(year=1970, month=1, day=3, hour=0, min=0, sec=0):
    milliseconds = int(
        datetime.datetime(year, month, day, hour, min, sec).timestamp() * 1000
    )
    return milliseconds


def write_file():
    with open(doc_title, "w", encoding="utf-8") as output_file:
        output_file.write(citations)


def main():
    with open("library.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data_string = data["docs"]
    for item in data_string:
        citations = ""
        if item["citations"] != []:
            doc_title = f'{item["data"]["doc_title"]}.md'
            for citation in item["citations"]:
                if convert_time() < citation["note_insert_time"]:
                    citations += f'>{citation["note_body"]}\n'


if __name__ == "__main__":
    main()
