import json
import datetime
import os
import zipfile


"""
Перевод указанной пользователем даты в миллисекунды.
По умолчанию указана дата 1970-1-3 00:00:00
"""


def convert_time(year=1970, month=1, day=3, hour=0, min=0, sec=0):
    milliseconds = int(
        datetime.datetime(year, month, day, hour, min, sec).timestamp() * 1000
    )
    return milliseconds


def enter_date():
    print("Укажите, с какой даты экспортировать цитаты.")
    choose = input("Либо введите '0', чтобы экспортировать все: ")
    if int(choose) != 0:
        year = int(input("Введите год: "))
        month = input("Введите месяц: ")
        month = int(month.lstrip('0'))
        day = input("Введите день: ")
        day = int(day.lstrip('0'))
        return convert_time(year, month, day)


# подготовка бэкапа, изменение расширения bak на zip
def prepare_file():
    for filename in os.listdir('.'):
        infilename = os.path.join('.', filename)
        if not os.path.isfile(infilename): continue
        os.path.splitext(filename)
        new_name = infilename.replace('.bak', '.zip')
        os.rename(infilename, new_name)
    return new_name[2:]


# получение данных из файла library
def extract_from_zip():
    input_file = prepare_file()
    with zipfile.ZipFile(input_file, 'r') as archive:
        file_list = archive.namelist()
        for file_name in file_list:
            if file_name == 'library.json':
                with archive.open(file_name) as json_file:
                    json_data = json_file.read().decode('utf-8')
                    data = json.loads(json_data)
    return data


# проверка существования отдельного каталога для цитат
# если он отсутствует, создается
def write_file(doc_title, citations):
    if os.path.isdir("Books") is False:
        os.mkdir("Books")
    with open(f"Books/{doc_title}", "w", encoding="utf-8") as output_file:
        output_file.write("[[Цитаты]]\n\n" + citations)


def replace_symbols(item):
    doc_title = f'{item["data"]["doc_title"]}.md'
    doc_title = doc_title.replace(":", ";")
    doc_title = doc_title.replace("/", "-")
    doc_title = doc_title.replace("?", ".")
    return doc_title


def main():
    # enter_date()
    data_string = extract_from_zip()["docs"]  # открыть исходный файл
    for item in data_string:
        citations = ""
        if item["citations"] != [] and item["data"]["doc_format"] in ("FB2", "EPUB", "MOBI"):
            # название книги => имя выходного файла
            doc_title = replace_symbols(item)
            for citation in item["citations"]:
                if convert_time() < citation["note_insert_time"]:
                    citations += f'>{citation["note_body"]}\n\n'
            write_file(doc_title, citations)


if __name__ == "__main__":
    main()
