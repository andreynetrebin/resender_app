import csv


def read_txt(filename, encoding=None):
    with open(filename, encoding=encoding) as txt_file:
        return txt_file.read()


def read_txt_lines(filename, encoding=None):
    with open(filename, encoding=encoding) as txt_file:
        return txt_file.readlines()


def append_to_csv(csv_filename, data, encoding=None):
    with open(csv_filename, 'a', encoding=encoding) as csv_file:
        csv_file.write(data + '\n')


def get_delimiter(filename, encoding=None):
    sniffer = csv.Sniffer()
    with open(filename, encoding=encoding) as fp:
        delimiter = sniffer.sniff(fp.read(5000)).delimiter
    return delimiter


def get_dict_from_csv(filename, delimiter, encoding=None):
    with open(filename, encoding=encoding) as csvFile:
        reader = csv.DictReader(csvFile, delimiter=delimiter)
        for row in reader:
            yield dict(row)


def write_txt(filename, text, mode, encoding=None):
    with open(filename, mode, encoding=encoding) as txt_file:
        txt_file.write(text)


def export_to_csv(filename, data, fieldnames, mode='w'):
    try:
        with open(filename, mode, encoding='cp1251') as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
                extrasaction='ignore',
                delimiter=';'
            )
            for row in data:
                writer.writerow(row)
    except IOError:
        pass


def get_fieldnames(data):
    for row in data:
        return [*row]
