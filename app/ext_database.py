import ibm_db_dbi
from flask import current_app
import json
from .ext_databases.db_queries import *
import sys


class Database:
    """
    Класс для работы с внешними базами данных DB2.

    Attributes:
        hostname (str): Ip-адрес БД или алиас.
        username (str): Имя пользователя-логин.
        password (str): Пароль.
    """

    def __init__(self, hostname: str, username: str, password: str):
        """
        Инициализация подключения к БД.

        Parameters:
            hostname (str): Ip-адрес БД или алиас.
            username (str): Имя пользователя-логин.
            password (str): Пароль.
        """
        self.hostname = hostname
        self.username = username
        self.password = password

    def __enter__(self):
        self.connection = ibm_db_dbi.connect(
            self.hostname, self.username, self.password
        )
        current_app.logger.debug("Открыто подкючение к БД")
        return self

    def get_db_data(self, query, id=None, json_data=None):
        """
        Получение данных из БД

        Parameters:
            query (str): SQL-запрос к БД.


        Returns:
            list: Список словарей.
            str: В виде json.
        """
        self.cursor = self.connection.cursor()
        current_app.logger.debug("Открыт курсор")
        try:
            if id is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, (id,))
            fields = [field_md[0].lower() for field_md in self.cursor.description]
            if json_data is None:
                db_data = [dict(zip(fields, row)) for row in self.cursor.fetchall()]
            else:
                db_data = json.dumps([dict(zip(fields, row)) for row in self.cursor.fetchall()], indent=4, default=str)
        except:
            current_app.logger.debug("Ошибка при получении данных из БД")
            db_data = None
        finally:
            self.cursor.close()
            current_app.logger.debug("Закрыт курсор")
            return db_data

    def get_data_document(self, id, fields=None):
        db_data = self.get_db_data(query_document_fiedls, id)
        data_document = self.get_data_document_from_db_data(db_data, fields)
        return data_document

    def get_attributes(self, id):
        db_data = self.get_db_data(query_atrributes, id)
        data_attributes = self.get_attributes_from_db_data(db_data)
        return data_attributes

    def get_linked_document_id(self, id, typ):
        db_data = self.get_db_data(query_linked_docs, id)
        linked_document_id = self.get_linked_document_id_from_db_data(db_data, typ)
        return linked_document_id

    def get_linked_documents(self, id):
        db_data = self.get_db_data(query_linked_docs, id)
        return db_data

    def get_attached_documents(self, id):
        db_data = self.get_db_data(query_attached_docs, id)
        data_attached_documnets = self.get_attached_documents_from_db_data(db_data)
        return data_attached_documnets

    def get_linked_parent_document_id(self, id):
        db_data = self.get_db_data(query_linked_parent_docs, id)
        linked_parent_document_id = self.get_data_document_from_db_data(
            db_data, ["parent_doc_id"]
        )
        return linked_parent_document_id["parent_doc_id"]

    def get_content_xml(self, id):
        db_data = self.get_db_data(query_content_body_xml, id)
        content_xml = self.get_data_document_from_db_data(db_data, ["body_xml"])
        return content_xml["body_xml"]

    def get_szv_zapros_data(self, id):
        db_data = self.get_db_data(query_szv_zapros, id)
        return db_data

    def get_szi_sv_data(self, id):
        db_data = self.get_db_data(query_szi_sv, id)
        return db_data

    @staticmethod
    def get_attributes_from_db_data(db_data):
        attributes = {}
        for item in db_data:
            if item["name"] == "process-code":
                attributes.update({"process-code": item["val"]})
            elif item["name"] == "process-id":
                attributes.update({"process-id": item["val"]})
        return attributes

    @staticmethod
    def get_linked_document_id_from_db_data(db_data, typ):
        if db_data[0]["typ"] == typ:
            return {key: value for (key, value) in db_data[0].items() if key == "doc_id"}

    @staticmethod
    def get_data_document_from_db_data(db_data, fields=None):
        return {key: value for (key, value) in db_data[0].items() if key in fields}

    @staticmethod
    def get_attached_documents_from_db_data(db_data):
        if db_data:
            data_attached_docs = ""
            for item in db_data:
                data_attached_docs += (
                    f"<DocumentRef id=\"{item['doc_id']}\" nsiType=\"{item['typ']}\"/> "
                )
            attached_docs = f"<AttachedDocuments>{data_attached_docs}</AttachedDocuments>"
            return {"attached_docs": attached_docs}
        else:
            return {"attached_docs": ""}

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            current_app.logger.error(f"{sys.exc_info()}")

        self.connection.close()
        current_app.logger.debug("Закрыто подкючение к БД")

