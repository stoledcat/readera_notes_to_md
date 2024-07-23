import json
import datetime
import os
import zipfile


"""
Перевод указанной пользователем даты в миллисекунды.
По умолчанию указана дата 1970-1-3 00:00:00
"""


# указать название метафайла
def select_metafile():
    # print("Выберите название метафайла,")
    metafile = input("Выберите название метафайла,\
на который будут ссылаться все цитаты: ")
    return metafile


# запросить начальную дату экспорта цитат
def enter_date():
    print("Экспортировать все цитаты - 0")
    print("Экспортировать начиная с указанной даты - 1")
    choose = input("Выбор: ")
    while choose not in ("0", "1") or choose.isalpha():
        choose = input("Неверный вариант. Повторите выбор: ")
    if choose == "1":
        year = input("Введите год: ")
        while not year.isdigit():
            year = input("Некорректное значение. Укажите год: ")
        year = int(year)
        month = input("Введите месяц: ")
        while not month.isdigit() or int(month) > 12:
            month = input("Некорректное значение. Укажите месяц: ")
        month = int(month.lstrip("0"))
        day = input("Введите день: ")
        while not day.isdigit() or int(day) > 31:
            day = input("Некорректное значение. Укажите день: ")
        day = int(day.lstrip("0"))
        check_value = int(year) + int(month) + int(day)
        if not str(check_value).isdigit():
            print("Введены некорретные данные.")
    elif choose == "0":
        year = 1970
        month = 1
        day = 3
    return convert_time(year, month, day)


# конвертировать указанное время в миллисекунды
def convert_time(year=1970, month=1, day=3):
    milliseconds = int(
        datetime.datetime(year, month, day).timestamp() * 1000
    )
    return milliseconds


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
def write_file_with_collection(doc_title, collection, citations, metafile):
    if os.path.isdir("Books") is False:
        os.mkdir("Books")
    with open(f"Books/{doc_title}", "w", encoding="utf-8") as output_file:
        output_file.write(f"[[{collection}]]\n[[{metafile}]]\n\n" + citations)


def write_file_without_collection(doc_title, citations, metafile):
    if os.path.isdir("Books") is False:
        os.mkdir("Books")
    with open(f"Books/{doc_title}", "w", encoding="utf-8") as output_file:
        output_file.write(f"[[{metafile}]]\n\n" + citations)


# заменить в названии файлов запрещенные символы
def replace_symbols(item):
    doc_title = f'{item["data"]["doc_title"]}.md'
    doc_title = doc_title.replace(":", ";")
    doc_title = doc_title.replace("/", "-")
    doc_title = doc_title.replace("?", ".")
    return doc_title


# создать хранилище с цитатами
def make_citations(item, timestamp):
    count = 0
    citations = ""
    for citation in item["citations"]:
        if timestamp < citation["note_insert_time"]:
            count += 1
            citations += f'>{citation["note_body"]}\n\n'
    if count >= 1:
        citations = ""
        for citation in item["citations"]:
            citations += f'>{citation["note_body"]}\n\n'
    return citations


def make_books(book_key, doc_title, collection, citations, metafile):
    if citations != "":
        if book_key in collection:
            write_file_with_collection(
                doc_title, collection[book_key], citations,
                metafile)
        elif book_key not in collection:
            write_file_without_collection(doc_title, citations, metafile)


def main():
    timestamp = enter_date()
    metafile = select_metafile()
    data_docs = extract_from_zip()["docs"]  # получить данные файлов
    data_colls = extract_from_zip()  # получить данные коллекций
    collection = create_coll_dict(data_colls)
    for item in data_docs:
        book_key = item["uri"]
        if item["data"]["doc_format"] in ("FB2", "EPUB", "MOBI"):
            if item["citations"] != []:
                doc_title = replace_symbols(item)
                citations = make_citations(item, timestamp)
                make_books(book_key, doc_title, collection, citations,
                           metafile)


if __name__ == "__main__":
    main()
