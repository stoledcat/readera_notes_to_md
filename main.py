import json
import datetime
import os
import zipfile


"""
Перевод указанной пользователем даты в миллисекунды.
По умолчанию указана дата 1970-1-3 00:00:00
"""


# конвертировать указанное время в миллисекунды
def convert_time(year=1970, month=1, day=3, hour=0, min=0, sec=0):
    milliseconds = int(
        datetime.datetime(year, month, day, hour, min, sec).timestamp() * 1000
    )
    return milliseconds


# # запросить начальную дату экспорта цитат
# def enter_date():
#     print("Укажите, с какой даты экспортировать цитаты.")
#     choose = input("Либо введите '0', чтобы экспортировать все: ")
#     if int(choose) != 0:
#         year = int(input("Введите год: "))
#         month = input("Введите месяц: ")
#         month = int(month.lstrip("0"))
#         day = input("Введите день: ")
#         day = int(day.lstrip("0"))
#     return convert_time(year, month, day)


# подготовить бэкап, изменить расширение bak на zip
def prepare_file():
    for filename in os.listdir("."):
        infilename = os.path.join(".", filename)
        if not os.path.isfile(infilename):
            continue
        os.path.splitext(filename)
        new_name = infilename.replace(".bak", ".zip")
        os.rename(infilename, new_name)
        if new_name.endswith(".zip"):
            zip_file = new_name
    return zip_file[2:]


# получить данные из файла library
def extract_from_zip():
    input_file = prepare_file()
    with zipfile.ZipFile(input_file, "r") as archive:
        file_list = archive.namelist()
        for file_name in file_list:
            if file_name == "library.json":
                with archive.open(file_name) as json_file:
                    json_data = json_file.read().decode("utf-8")
                    data = json.loads(json_data)
    return data


# создать словарь {'код книги(sha-1)': 'название коллекции в ReadEra'}
def create_coll_dict(data_colls):
    coll_dict = {}
    for item in data_colls["colls"]:
        if item["data"]["coll_title"] != []:
            for docs in item["docs"]:
                new_key = {docs: item["data"]["coll_title"]}
                coll_dict.update(new_key)
    return coll_dict


# проверить существования отдельного каталога для цитат
# если он отсутствует, создать
def write_file_with_collection(doc_title, collection, citations):
    if os.path.isdir("Books") is False:
        os.mkdir("Books")
    with open(f"Books/{doc_title}", "w", encoding="utf-8") as output_file:
        output_file.write(f"[[{collection}]]\n[[Цитаты]]\n\n" + citations)


def write_file_without_collection(doc_title, citations):
    if os.path.isdir("Books") is False:
        os.mkdir("Books")
    with open(f"Books/{doc_title}", "w", encoding="utf-8") as output_file:
        output_file.write("[[Цитаты]]\n\n" + citations)


# заменить в названии файлов запрещенные символы
def replace_symbols(item):
    doc_title = f'{item["data"]["doc_title"]}.md'
    doc_title = doc_title.replace(":", ";")
    doc_title = doc_title.replace("/", "-")
    doc_title = doc_title.replace("?", ".")
    return doc_title


# создать хранилище с цитатами
def make_citations(item):
    count = 0
    citations = ""
    for citation in item["citations"]:
        if convert_time() < citation["note_insert_time"]:
            count += 1
            citations += f'>{citation["note_body"]}\n\n'
    if count >= 1:
        citations = ""
        for citation in item["citations"]:
            citations += f'>{citation["note_body"]}\n\n'
    return citations


def make_books(book_key, doc_title, collection, citations):
    if citations != "":
        if book_key in collection:
            write_file_with_collection(
                doc_title, collection[book_key], citations
                )
        elif book_key not in collection:
            write_file_without_collection(doc_title, citations)


def main():
    # enter_date()
    data_docs = extract_from_zip()["docs"]  # получить данные файлов
    data_colls = extract_from_zip()  # получить данные коллекций
    collection = create_coll_dict(data_colls)
    for item in data_docs:
        book_key = item["uri"]
        if item["data"]["doc_format"] in ("FB2", "EPUB", "MOBI"):
            if item["citations"] != []:
                doc_title = replace_symbols(item)
                citations = make_citations(item)
                make_books(book_key, doc_title, collection, citations)


if __name__ == "__main__":
    main()
