from flask import (
    Blueprint,
    current_app,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
    abort,
    send_from_directory,
)
from flask_login import login_required, current_user
# from flask_paginate import Pagination, get_page_parameter
from werkzeug.utils import secure_filename
from os import path, makedirs, listdir, remove
from os.path import basename
from string import Template
import time
import glob
import calendar
import zipfile
import shutil
import requests
import subprocess
import configparser
import datetime
import re
import json
from ..ext_database import Database
# from .mq import ManagerQueue
from app.db import get_db
from .utils import (
    get_delimiter,
    get_dict_from_csv,
    read_txt,
    read_txt_lines,
    write_txt,
    export_to_csv,
    append_to_csv,

)
from .prepare_data.person_apply_application_request import (
    get_action_queue,
    get_person_app_prepare_data,
)
from .prepare_data.vmse_proactive import get_vmse_proactive_prepare_data
from .prepare_data.upp_efs import upp_efs_prepare_data
from .prepare_data.upp_is import upp_is_prepare_data
from .prepare_data.upp_szvm import upp_szvm_prepare_data
from .prepare_data.poszn import poszn_prepare_data
from .prepare_data.rnpp import rnpp_prepare_data
from .prepare_data.egrn_egrul_egrip_prepare_data import (
    get_egrn_egrul_egrip_prepare_data,
)
from .prepare_data.vmse_zapros import (
    get_vmse_zapros_prepare_data,
    get_vmse_data_from_packet_xml,
)
from .prepare_data.npf_doc_uspn import get_npf_doc_uspn_prepare_data
from .prepare_data.adv_adi_prepare_data import get_adv_adi_prepare_data
from .prepare_data.szi_sv_to_nvp_prepare_data import get_szi_sv_to_nvp_prepare_data
from .prepare_data.szi_km_to_fbdp_prepare_data import get_szi_km_to_fbdp_prepare_data

resend = Blueprint(
    "resend", __name__, template_folder="templates", static_folder="static"
)

ALLOWED_EXTENSIONS = {"txt", "csv", "xml", "json"}

resend_dir = path.abspath(path.dirname(__file__))

utilities_dir = path.join(resend_dir, "utilities")
if not path.exists(utilities_dir):
    makedirs(utilities_dir)

uploads_dir = path.join(resend_dir, "uploads")
if not path.exists(uploads_dir):
    makedirs(uploads_dir)

downloads_dir = path.join(resend_dir, "downloads")
if not path.exists(downloads_dir):
    makedirs(downloads_dir)

cls_regions_file = path.join(resend_dir, "cls_files", "regions.csv")

config = configparser.ConfigParser()
config.read(path.join(resend_dir, "settings.ini"), encoding="utf-8")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_message(work_name, prepare_data):
    cursor = get_db().cursor()
    cursor.execute(
        """SELECT template_message FROM
        template_messages tm
        JOIN works on tm.work_id = works.id
        WHERE works.name = ?""", (work_name,))
    template_message = Template(cursor.fetchone()[0])
    message = template_message.safe_substitute(prepare_data)

    return message


def get_data_to_sent(id, message, data_message):
    message_bytes = bytes(message, "utf-8")
    if "process-code" in data_message:
        process_code = data_message["process-code"]
    else:
        process_code = ""
    if "TYP" in data_message:
        doc_typ = data_message["typ"]
    else:
        doc_typ = ""

    return {
        id: {
            "message": message_bytes,
            "queue_name": data_message["queue_name"],
            "process_code": process_code,
            "doc_typ": doc_typ,
        }
    }


def convert(date_time):
    format = "%Y-%m-%d"
    datetime_str = datetime.datetime.strptime(date_time, format)
    return datetime_str


def request_to_elastik(id, search_date):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}
    elk_host = config.get("ELK", "host")
    elk_port = config.get("ELK", "port")
    response = requests.get(
        f"http://{elk_host}:{elk_port}/vioup_{search_date}/_search?q={id}", headers=headers)

    return response


def add_to_journal(request, work_name, journal_msg_report):
    url = request.base_url
    cursor = get_db().cursor()
    cursor.execute(
        "INSERT INTO journal_resend (name, result, url, user_id) VALUES (?,?,?,?)",
        (
            work_name,
            journal_msg_report,
            url,
            current_user.id,
        ),
    )
    cursor.connection.commit()


@resend.route("/")
def index():
    cursor = get_db().cursor()
    tech_prosesses = cursor.execute("SELECT id, name from techprocesses").fetchall()
    works = cursor.execute("SELECT name, url, techprocess_id from works").fetchall()
    return render_template("resend/index.html", tech_prosesses=tech_prosesses, works=works)


@resend.route("/get_szv_zapros", methods=["POST", "GET"])
@login_required
def get_szv_zapros():
    if "prbz" in current_user.roles or "all" in current_user.roles:
        work_name = "Поиск СЗВ-Запроса по messageID"
        current_date = datetime.date.today()
        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()

            start_date = request.form["start_date"]
            end_date = request.form["end_date"]

            if start_date > end_date:
                flash("Конечная дата не может быть раньше начальной", "danger")
                return redirect(url_for("resend.get_szv_zapros"))

            delta = convert(end_date) - convert(start_date)

            if delta.days > 7:
                flash("Период не должен быть более 7 дней", "danger")
                return redirect(url_for("resend.get_szv_zapros"))

            result = []
            result_finded = []
            result_not_finded = []

            for id in list_ids:
                record = {}
                for i in range(delta.days + 1):
                    day = (convert(start_date) + datetime.timedelta(days=i)).date()
                    current_app.logger.debug("ищем даннные в базе ELK")
                    response_data = request_to_elastik(id, day)
                    json_data = json.loads(response_data.text)
                    hits = json_data["hits"]["hits"]
                    if len(hits) > 0:
                        pattern_id = r'id="(\d+)"'
                        for hit in hits:
                            if hit["_source"]["source"] == "REGISTRATORRESPONSEFORSYS":
                                content = hit["_source"]["business_data"]
                                regex_id = re.compile(pattern_id)
                                try:
                                    id = regex_id.search(content).group(1).strip()
                                    request_id = hit["_source"][
                                        "globalTransactionId"
                                    ].strip()
                                    message_id = hit["_source"][
                                        "localTransactionId"
                                    ].strip()
                                    data = {
                                        "request_id": request_id,
                                        "message_id": message_id,
                                        "id_szv_zapros": id,
                                    }
                                    record.update(data)
                                    current_app.logger.debug("ищем даннные в базе ВИО")
                                    with Database(config.get("VIO_DATABASE", "alias"),
                                                  config.get("VIO_DATABASE", "login"),
                                                  config.get("VIO_DATABASE", "password")) as db:
                                        szv_zapros_data = db.get_szv_zapros_data(id)
                                        record.update(szv_zapros_data[0])
                                    result_finded.append(id)
                                except AttributeError:
                                    current_app.logger.debug("Среди полученных данных не было ID-шника СЗВ-Запроса")
                                    continue
                    else:
                        continue
                    if record:
                        break
                # Проверяем был ли найден ID СЗВ-Запроса
                if not record:
                    data = {
                        "request_id": "-",
                        "message_id": id.strip(),
                        "id_szv_zapros": "-",
                        "status_szv_zapros": "-",
                        "sender": "-",
                        "reg_date_szv_zapros": "-",
                        "id_szi_sv": "-",
                        "status_szi_sv": "-",
                        "reg_date_szi_sv": "-",
                    }
                    record.update(data)
                    result_not_finded.append(id)
                result.append(record)

            ts = calendar.timegm(time.gmtime())
            fieldnames = get_fieldnames(result)
            header = "request_id;message_id;ID в ЕХД СЗВ-Запроса;Статус СЗВ-Запроса;Регион;Дата регистрации СЗВ-Запроса;ID в ЕХД СЗИ-СВ;Статус СЗИ-СВ;Дата регистрации СЗИ-СВ"
            result_csv_filename = None
            if result_finded:
                prepare_csv_file = path.join(downloads_dir, f"{ts}.csv")
                export_to_csv(prepare_csv_file, result, fieldnames)
                content_csv = read_txt(prepare_csv_file, encoding="cp1251")
                remove(prepare_csv_file)
                result_csv_filename = f"{start_date}_{end_date}_{ts}.csv"
                result_csv_file = path.join(downloads_dir, result_csv_filename)
                append_to_csv(result_csv_file, header, encoding="cp1251")
                append_to_csv(result_csv_file, content_csv, encoding="1251")

            info_to_log = f"user:{current_user.username},запуск нахождения ID СЗВ-Запроса по messageID"
            current_app.logger.info(info_to_log)

            resend_result = len(result_finded)
            resend_bad_result = len(result_not_finded)
            journal_msg_report = (
                f"Найдено {resend_result} ID СЗВ-Запроса, не найдено {resend_bad_result}"
            )
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/search_szv_zapros.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=result_not_finded,
                download_filename=result_csv_filename,
            )

        return render_template(
            "resend/get_szv_zapros.html",
            current_date=current_date,
            resend_title=work_name,
            comment='Указываем в столбик именно messageID'
        )

    else:
        abort(403, "Отсутствует доступ")


@resend.route("/szi_sv_to_nvp", methods=["POST", "GET"])
@login_required
def szi_sv_to_nvp():
    if "prbz" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка СЗИ-СВ в НВП"

        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()

            messages = {}
            bad_list = []
            with Database(config.get("VIO_DATABASE", "alias"), config.get("VIO_DATABASE", "login"),
                          config.get("VIO_DATABASE", "password")) as db:
                with Database(config.get("SPU_DATABASE", "alias"), config.get("SPU_DATABASE", "login"),
                              config.get("SPU_DATABASE", "password")) as db2:
                    for id in list_ids:
                        data_message = {}

                        szv_zapros_data = db.get_szv_zapros_data(id)
                        id_szi_sv = szv_zapros_data[0]['id_szi_sv']
                        if id_szi_sv is not None:
                            data_message.update(szv_zapros_data[0])

                            spu_szi_sv_data = db2.get_szi_sv_data(id_szi_sv)[0]

                            if spu_szi_sv_data:
                                data_message.update(spu_szi_sv_data)
                                data_message.update({"queue_name": config.get("MqSpuOut", "queue_name")})
                                prepare_data = get_szi_sv_to_nvp_prepare_data(data_message)

                                if prepare_data:
                                    message = get_message(work_name, prepare_data)
                                    data_to_sent = get_data_to_sent(
                                        id, message, data_message
                                    )
                                    messages.update(data_to_sent)

                            else:
                                bad_list.append(id)

                        else:
                            bad_list.append(id)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
            add_to_journal(request, work_name, journal_msg_report)
            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )

        return render_template(
            "resend/list_input.html",
            resend_title=work_name,
            comment="Указываем в столбик ID в ЕХД СЗВ-Запроса"
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/journal")
@login_required
def journal():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    limit = 10
    offset = page * limit - limit
    cursor = get_db().cursor()
    journal_data = cursor.execute(
        "SELECT * from journal_resend WHERE user_id = ?", (current_user.id,)
    ).fetchall()
    total = len(journal_data)

    cursor.execute(
        "select * from journal_resend WHERE user_id = ? order by created desc limit ? offset ?",
        (
            current_user.id,
            limit,
            offset,
        ),
    )
    data = cursor.fetchall()
    pagination = Pagination(page=page, page_per=limit, total=total)

    return render_template("resend/journal.html", pagination=pagination, data=data)


@resend.route("/change_status", methods=["GET", "POST"])
@login_required
def change_status():
    if "change_status" in current_user.roles or "all" in current_user.roles:
        work_name = "Смена статуса"
        if request.method == "POST":
            params = request.form.getlist("flexRadioDefault")
            selected_status = params[0]
            text = request.form["text"]
            list_ids = text.splitlines()
            bad_list = []
            good_list = []
            for id in set(list_ids):
                try:
                    ehd_host_api = config.get("EHD_API_DOC_STATUS", "host")
                    request_check = requests.get(
                        f"http://{ehd_host_api}/udsapi/v1/documents/statuses",
                        params={"documentId": id},
                    )
                    if request_check.json()["errors"] != ["Document not found"]:
                        current_status = request_check.json()["payload"]["value"]
                        if current_status != int(selected_status):
                            req_change = requests.post(
                                f"http://{ehd_host_api}/udsapi/v1/documents/statuses/conditional",
                                params={
                                    "documentId": id,
                                    "newStatus": selected_status,
                                    "strategy": "NONE",
                                },
                            )
                            if req_change.status_code == 200:
                                good_list.append(id)
                                current_app.logger.info(
                                    f"user:{current_user.username},сменен статус документа:{id},старый статус:{current_status},новый статус: {selected_status}"
                                )
                            else:
                                bad_list.append(id)
                                current_app.logger.error(
                                    f"user:{current_user.username}, произошла ошибка при смене статуса документу:{id}"
                                )
                        else:
                            bad_list.append(id)
                            current_app.logger.info(
                                f"user:{current_user.username},текущий статус документа:{id} = выбранному"
                            )
                    else:
                        bad_list.append(id)
                        current_app.logger.error(
                            f"user:{current_user.username},документ:{id} не найден"
                        )
                except:
                    bad_list.append(id)
                    current_app.logger.error(
                        f"Произошла ошибка при получении статуса документа - {id}"
                    )
            journal_msg_report = f"Сменён статус по {len(good_list)} документам, смена статуса не прошла по {len(bad_list)} документам"
            add_to_journal(request, work_name, journal_msg_report)
            return render_template(
                "resend/resend_result.html",
                resend_result=len(good_list),
                resend_bad_result=len(bad_list),
                bad_list=bad_list,
            )

        return render_template(
            "resend/change_status.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


# Сервис заявлений (PersonApplication)
# От ВИО в ФП (НВПиСВ, КСП, АСВ, УСПН, МСК, СПУ)
@resend.route("/person_apply_application_request", methods=["GET", "POST"])
@login_required
def person_apply_application_request():
    if "persons" in current_user.roles or "all" in current_user.roles:
        work_name = "От ВИО в ФП (НВПиСВ, КСП, АСВ, УСПН, МСК, СПУ)"

        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()

            messages = {}
            bad_list = []

            with Database(config.get("VIO_DATABASE", "alias"), config.get("VIO_DATABASE", "login"),
                          config.get("VIO_DATABASE", "password")) as db:
                for id in list_ids:
                    data_message = {}

                    data_document = db.get_data_document(id, fields=["SENDER", "TYP"])
                    data_message.update(data_document)

                    data_attributes = db.get_attributes(id)
                    data_message.update(data_attributes)

                    data_linked_docs = db.get_linked_document_id(id, 14)
                    data_message.update(data_linked_docs)

                    data_attached_docs = db.get_attached_documents(id)
                    data_message.update(data_attached_docs)

                    action, queue_name = get_action_queue(data_message["process-code"])
                    data_message.update({"action": action, "queue_name": queue_name})
                    prepare_data = get_person_app_prepare_data(id, data_message)
                    if prepare_data:
                        template = path.join(
                            templates_dir, "person_apply_application_request.txt"
                        )
                        message = get_message(work_name, prepare_data)
                        # print(message)
                        data_to_sent = get_data_to_sent(
                            id, message.replace("\n", ""), data_message
                        )
                        messages.update(data_to_sent)
                    else:
                        bad_list.append(id)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
            add_to_journal(request, work_name, journal_msg_report)
            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )

        return render_template(
            "resend/list_input.html",
            resend_title=work_name,
        )
    else:
        abort(403, "Отсутствует доступ")


# Выписки МСЭ от ФГИС ФРИ
# Переотправка в НВП (По инициативке)
@resend.route("/vmse_proactive", methods=["GET", "POST"])
@login_required
def vmse_proactive():
    if "fri_vmse" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка в НВП (По инициативке)"
        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()

            messages = {}
            bad_list = []
            with Database(config.get("VIO_DATABASE", "alias"), config.get("VIO_DATABASE", "login"),
                          config.get("VIO_DATABASE", "password")) as db:
                for id in list_ids:
                    data_message = {}

                    data_document = db.get_data_document(id, fields=["FROM", "TYP"])
                    data_message.update(data_document)

                    data_message.update(
                        {
                            "process_code": "urn:process:4:6.0",
                            "queue_name": config.get("MqVioRoute", "queue_name"),
                        }
                    )
                    prepare_data = get_vmse_proactive_prepare_data(id, data_message)
                    if prepare_data:
                        message = get_message(work_name, prepare_data)
                        data_to_sent = get_data_to_sent(
                            id, message.strip(), data_message
                        )
                        messages.update(data_to_sent)
                    else:
                        bad_list.append(id)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
            add_to_journal(request, work_name, journal_msg_report)
            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )
        return render_template(
            "resend/list_input.html",
            resend_title=work_name,
        )
    else:
        abort(403, "Отсутствует доступ")


# Сервис страхователей (InsurerReport)
# Переотправка в АСВ по пакетам ЕФС-1
@resend.route("/upp_efs", methods=["GET", "POST"])
@login_required
def upp_efs():
    if "insurers" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка в АСВ по пакетам ЕФС-1"
        if request.method == "POST":
            file = request.files["file"]
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                delimiter = get_delimiter(filepath)
                template = path.join(templates_dir, "efs_upp.txt")

                messages = {}
                bad_list = []

                for item in get_dict_from_csv(filepath, delimiter):
                    data_message = {}
                    data_message.update(
                        {
                            "process_code": "InsurerReportProcessingEFS",
                            "queue_name": config.get("MqAsvEfsIn", "queue_name"),
                            "TYP": 80291,
                        }
                    )
                    id, message_dict = upp_efs_prepare_data(**item)
                    message = get_message(work_name, prepare_data)
                    data_to_sent = get_data_to_sent(id, message, data_message)
                    messages.update(data_to_sent)

                with ManagerQueue(
                        config.get("Mq", "queue_manager"),
                        config.get("Mq", "channel"),
                        config.get("Mq", "conn_info"),
                ) as qmgr:
                    for key, val in messages.items():
                        qmgr.send_message(val["queue_name"], val["message"])
                        info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                        current_app.logger.info(info_to_log)

                resend_result = len(messages)
                resend_bad_result = len(bad_list)

                journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
                add_to_journal(request, work_name, journal_msg_report)
                return render_template(
                    "resend/resend_result.html",
                    resend_result=resend_result,
                    resend_bad_result=resend_bad_result,
                    bad_list=bad_list,
                )
        return render_template(
            "resend/file_input.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


# Сервис страхователей (InsurerReport)
# Переотправка в АСВ по пакетам ИС
@resend.route("/upp_is", methods=["GET", "POST"])
@login_required
def upp_is():
    if "insurers" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка в АСВ по пакетам ИС"
        if request.method == "POST":
            file = request.files["file"]
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                delimiter = get_delimiter(filepath)

                messages = {}
                bad_list = []

                for item in get_dict_from_csv(filepath, delimiter):
                    data_message = {}
                    data_message.update(
                        {
                            "process_code": "InsurerReportProcessingIS",
                            "queue_name": config.get("MqAsvIsIn", "queue_name"),
                            "TYP": 424,
                        }
                    )
                    id, message_dict = upp_is_prepare_data(**item)
                    message = get_message(work_name, prepare_data)
                    data_to_sent = get_data_to_sent(id, message, data_message)
                    messages.update(data_to_sent)

                with ManagerQueue(
                        config.get("Mq", "queue_manager"),
                        config.get("Mq", "channel"),
                        config.get("Mq", "conn_info"),
                ) as qmgr:
                    for key, val in messages.items():
                        qmgr.send_message(val["queue_name"], val["message"])
                        info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                        current_app.logger.info(info_to_log)

                resend_result = len(messages)
                resend_bad_result = len(bad_list)

                journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
                add_to_journal(request, work_name, journal_msg_report)
                return render_template(
                    "resend/resend_result.html",
                    resend_result=resend_result,
                    resend_bad_result=resend_bad_result,
                    bad_list=bad_list,
                )
        return render_template(
            "resend/file_input.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


# Сервис страхователей (InsurerReport)
# Переотправка в АСВ по пакетам СЗВ-М
@resend.route("/upp_szvm", methods=["GET", "POST"])
@login_required
def upp_szvm():
    if "insurers" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка в АСВ по пакетам СЗВ-М"
        if request.method == "POST":
            file = request.files["file"]
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                delimiter = get_delimiter(filepath)

                messages = {}
                bad_list = []

                for item in get_dict_from_csv(filepath, delimiter):
                    data_message = {}
                    data_message.update(
                        {
                            "process_code": "InsurerReportProcessingSZVM",
                            "queue_name": config.get("MqAsvSzvmIn", "queue_name"),
                            "TYP": 22,
                        }
                    )

                    id, message_dict = upp_szvm_prepare_data(**item)
                    message = get_message(work_name, prepare_data)
                    data_to_sent = get_data_to_sent(id, message, data_message)
                    messages.update(data_to_sent)

                with ManagerQueue(
                        config.get("Mq", "queue_manager"),
                        config.get("Mq", "channel"),
                        config.get("Mq", "conn_info"),
                ) as qmgr:
                    for key, val in messages.items():
                        qmgr.send_message(val["queue_name"], val["message"])
                        info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                        current_app.logger.info(info_to_log)

                resend_result = len(messages)
                resend_bad_result = len(bad_list)

                journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
                add_to_journal(request, work_name, journal_msg_report)

                return render_template(
                    "resend/resend_result.html",
                    resend_result=resend_result,
                    resend_bad_result=resend_bad_result,
                    bad_list=bad_list,
                )
        return render_template(
            "resend/file_input.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/resend_files", methods=["GET", "POST"])
@login_required
def resend_files():
    if "resend_files" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка файлов"
        if request.method == "POST":
            files = request.files.getlist("files")
            params = request.form.getlist("flexRadioDefault")
            queue_name = params[0]
            messages = {}
            bad_list = []
            for file in files:
                data_message = {}
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                data_message.update({"queue_name": queue_name})
                message = read_txt(filepath)
                data_to_sent = get_data_to_sent(filename, message, data_message)
                messages.update(data_to_sent)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} файлам, отправка не прошла по {resend_bad_result} файлам"
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )
        return render_template(
            "resend/files_input.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/egrn_egrul_egrip", methods=["GET", "POST"])
@login_required
def egrn_egrul_egrip():
    if "egrn_egrul_egrip" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка в АСВ по пакетам ЕГРН/ЕГРЮЛ/ЕГРИП"
        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()

            messages = {}
            bad_list = []
            with Database(config.get("VIO_DATABASE", "alias"), config.get("VIO_DATABASE", "login"),
                          config.get("VIO_DATABASE", "password")) as db:
                for id in list_ids:
                    data_message = {}

                    data_document = db.get_data_document(id, fields=["TYP"])
                    data_message.update(data_document)

                    data_attributes = db.get_attributes(id)
                    data_message.update(data_attributes)

                    data_message.update({"queue_name": config.get("MqUvkipOut", "queue_name")})

                    prepare_data = get_egrn_egrul_egrip_prepare_data(id, data_message)
                    if prepare_data:
                        message = get_message(work_name, prepare_data)
                        #                        print(message)
                        data_to_sent = get_data_to_sent(id, message, data_message)
                        messages.update(data_to_sent)
                    else:
                        bad_list.append(id)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )
        return render_template(
            "resend/list_input.html",
            resend_title=work_name,
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/resend_files_egrn_egrip_egrul", methods=["GET", "POST"])
@login_required
def resend_files_egrn_egrip_egrul():
    if "egrn_egrul_egrip" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка пакетов ЕГРН/ЕГРЮЛ/ЕГРИП в ЕХД"
        if request.method == "POST":
            files = request.files.getlist("files")
            messages = {}
            bad_list = []
            for file in files:
                data_message = {}
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                data_message.update({"queue_name": config.get("MqUvkipRq", "queue_name")})
                message = read_txt(filepath)
                data_to_sent = get_data_to_sent(filename, message, data_message)
                messages.update(data_to_sent)

            list_md = [
                {"param": config.get("MqUvkipRq", "param_to_q"), "value": config.get("MqUvkipRq", "value_to_q")},
                {"param": config.get("MqUvkipRq", "param_to_qmgr"), "value": config.get("MqUvkipRq", "value_to_qmgr")},
            ]

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(
                        val["queue_name"], val["message"], list_md=list_md
                    )
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} файлам, отправка не прошла по {resend_bad_result} файлам"
            add_to_journal(request, work_name, journal_msg_report)
            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )
        return render_template(
            "resend/files_egrn_egrip_egrul_input.html",
            resend_title=work_name,
        )
    else:
        abort(403, "Отсутствует доступ")


# Выписки МСЭ от ФГИС ФРИ
# Переотправка в НВП (По запросу)
@resend.route("/vmse_zapros", methods=["GET", "POST"])
@login_required
def vmse_zapros():
    if "fri_vmse" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка в НВП (По запросу)"
        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()

            messages = {}
            bad_list = []
            with Database(config.get("VIO_DATABASE", "alias"), config.get("VIO_DATABASE", "login"),
                          config.get("VIO_DATABASE", "password")) as db:
                for id in list_ids:
                    data_message = {}

                    data_document = db.get_data_document(
                        id,
                        fields=[
                            "FROM",
                            "TO",
                            "TYP",
                            "REG_NUM",
                            "REG_DATE",
                            "NAME",
                            "DOC_NUM",
                            "DOC_DATE",
                            "ADM_DATE",
                            "SENDER",
                            "RECEIVER",
                        ],
                    )
                    data_message.update(data_document)

                    queue_name = f"{data_message['TO'].split(':')[2]}.NVP.FTE.IN"

                    data_message.update(
                        {"process_code": "urn:process:4:3.0", "queue_name": queue_name}
                    )
                    parent_id_document = db.get_linked_parent_document_id(id)
                    content_xml = db.get_content_xml(parent_id_document)

                    data_message.update(
                        {"data": get_vmse_data_from_packet_xml(content_xml)}
                    )
                    prepare_data = get_vmse_zapros_prepare_data(id, data_message)
                    if prepare_data:
                        message = get_message(work_name, prepare_data)
                        #                        print(message)
                        data_to_sent = get_data_to_sent(
                            id, message.strip(), data_message
                        )
                        messages.update(data_to_sent)
                    else:
                        bad_list.append(id)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"], rfh2=True)
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
            add_to_journal(request, work_name, journal_msg_report)
            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )
        return render_template(
            "resend/list_input.html",
            resend_title=work_name,
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/npf_doc_uspn", methods=["GET", "POST"])
@login_required
def npf_doc_uspn():
    if "npf_uspn" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка документов НПФ в УСПН"
        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()
            params = request.form.getlist("flexRadioDefault")
            try:
                process_code = params[0]
            except IndexError:
                process_code = "urn:process:5:1.0"
            messages = {}
            messages_additional = {}
            bad_list = []

            with Database(config.get("VIO_DATABASE", "alias"), config.get("VIO_DATABASE", "login"),
                          config.get("VIO_DATABASE", "password")) as db:
                for id in list_ids:
                    data_message = {}

                    data_document = db.get_data_document(id, fields=["TYP", "TO"])
                    data_message.update(data_document)

                    data_linked_docs = db.get_linked_document_id(id, 14)
                    data_message.update(data_linked_docs)

                    upp_name = db.get_data_document(
                        data_message["DOC_ID"], fields=["NAME"]
                    )
                    data_message.update(upp_name)

                    data_message.update(
                        {"process-code": process_code, "queue_name": config.get("MqUspnUpp", "queue_name")}
                    )

                    prepare_data = get_npf_doc_uspn_prepare_data(id, data_message)
                    if prepare_data:
                        message_uspn = get_message(template_uspn, id, prepare_data)
                        data_to_sent_uspn = get_data_to_sent(
                            id, message_uspn, data_message
                        )
                        messages.update(data_to_sent_uspn)
                        message_uvkip = get_message(template_uvkip, id, prepare_data)
                        data_message["queue_name"] = config.get("MqUvkipUpp", "queue_name")
                        data_to_sent_uvkip = get_data_to_sent(
                            id, message_uvkip, data_message
                        )
                        messages_additional.update(data_to_sent_uvkip)
                    else:
                        bad_list.append(id)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

                for key, val in messages_additional.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )

        return render_template(
            "resend/uspn_input.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


# Сервис страхователей (InsurerReport)
# Переотправка атомарок
@resend.route("/efs_atom_retry_tool", methods=["GET", "POST"])
@login_required
def efs_atom_retry_tool():
    if "insurers" in current_user.roles or "all" in current_user.roles:

        work_name = "Переотправка атомарок"
        if request.method == "POST":
            text = request.form["text"]
            ts = calendar.timegm(time.gmtime())
            cur_utilities_dir = path.join(utilities_dir, f"efs_atom_retry_tool_{ts}")
            shutil.copytree(
                path.join(utilities_dir, "efs-atom-retry-tool_etalon"),
                cur_utilities_dir,
            )

            write_txt(
                path.join(cur_utilities_dir, "atomsResend.txt"),
                text,
                "w",
                encoding="utf-8",
            )

            subprocess.call(
                [
                    "java",
                    "-jar",
                    path.join(cur_utilities_dir, "efs-atom-retry-tool-2.5.2.jar"),
                ]
            )

            for filename in listdir(cur_utilities_dir):
                if filename.startswith("reportFile"):
                    log_report = read_txt_lines(path.join(cur_utilities_dir, filename))

            zip_filename = f"efs_atom_retry_tool_{ts}.zip"
            files_to_zip = glob.glob(path.join(cur_utilities_dir, "*.txt"))

            with zipfile.ZipFile(path.join(downloads_dir, zip_filename), "w") as zf:

                for util_filename in files_to_zip:
                    filename_zip = basename(util_filename)
                    zf.write(util_filename, filename_zip)
            shutil.rmtree(cur_utilities_dir)

            info_to_log = (
                f"user:{current_user.username},запуск утиллиты: efs_atom_retry_tool"
            )
            current_app.logger.info(info_to_log)

            journal_msg_report = f"{log_report[-2]} {log_report[-1]}"
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/resend_log_report.html",
                log_report=log_report,
                download_filename=zip_filename,
            )

        return render_template(
            "resend/list_input.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/resend_files_soe", methods=["GET", "POST"])
@login_required
def resend_files_soe():
    if "resend_files" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка файлов в СОЭ"
        if request.method == "POST":
            files = request.files.getlist("files")
            params = request.form.getlist("flexRadioDefault")
            queue_name = params[0]
            messages = {}
            bad_list = []
            for file in files:
                data_message = {}
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                data_message.update({"queue_name": queue_name})
                message = read_txt(filepath)
                data_to_sent = get_data_to_sent(filename, message, data_message)
                messages.update(data_to_sent)

            with ManagerQueue(
                    config.get("MqSOE", "queue_manager"),
                    config.get("MqSOE", "channel"),
                    config.get("MqSOE", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} файлам, отправка не прошла по {resend_bad_result} файлам"
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )
        return render_template(
            "resend/files_input_soe.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/downloads/<path:download_filename>", methods=["GET", "POST"])
@login_required
def downloads(download_filename):
    # print("test")
    return send_from_directory(downloads_dir, download_filename)


@resend.route("/resend_poszn", methods=["GET", "POST"])
@login_required
def resend_poszn():
    if "nazn_pens" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка ПОСЗН в НВП"
        if request.method == "POST":
            file = request.files["file"]
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                delimiter = get_delimiter(filepath)

                delimiter_cls_regions_file = get_delimiter(
                    cls_regions_file, encoding="utf-8"
                )
                regions = [
                    region["QMREG"]
                    for region in get_dict_from_csv(
                        cls_regions_file, delimiter_cls_regions_file, encoding="utf-8"
                    )
                ]

                messages = {}
                bad_list = []

                for item in get_dict_from_csv(filepath, delimiter):
                    data_message = {}
                    data_message.update(
                        {
                            "process_code": "ApplicationProccessingNVPSV",
                            "queue_name": config.get("MqNvpsvOut", "queue_name"),
                            "TYP": 80248,
                        }
                    )

                    if item["RECEIVER"] in regions:
                        id, message_dict = poszn_prepare_data(**item)
                        message = get_message(work_name, prepare_data)
                        data_to_sent = get_data_to_sent(id, message, data_message)
                        messages.update(data_to_sent)
                    else:
                        bad_list.append(id)

                with ManagerQueue(
                        config.get("Mq", "queue_manager"),
                        config.get("Mq", "channel"),
                        config.get("Mq", "conn_info"),
                ) as qmgr:
                    for key, val in messages.items():
                        qmgr.send_message(val["queue_name"], val["message"])
                        info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                        current_app.logger.info(info_to_log)

                resend_result = len(messages)
                resend_bad_result = len(bad_list)

                journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
                add_to_journal(request, work_name, journal_msg_report)

                return render_template(
                    "resend/resend_result.html",
                    resend_result=resend_result,
                    resend_bad_result=resend_bad_result,
                    bad_list=bad_list,
                )
        return render_template(
            "resend/file_input.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/resend_rnpp", methods=["GET", "POST"])
@login_required
def resend_rnpp():
    if "nazn_pens" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка РНПП в НВП"
        if request.method == "POST":
            file = request.files["file"]
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                delimiter = get_delimiter(filepath)
                delimiter_cls_regions_file = get_delimiter(
                    cls_regions_file, encoding="utf-8"
                )
                regions = [
                    region["QMREG"]
                    for region in get_dict_from_csv(
                        cls_regions_file, delimiter_cls_regions_file, encoding="utf-8"
                    )
                ]

                messages = {}
                bad_list = []

                for item in get_dict_from_csv(filepath, delimiter):
                    data_message = {}
                    data_message.update(
                        {
                            "process_code": "ApplicationProccessingNVPSV",
                            "queue_name": config.get("MqNvpsvOut", "queue_name"),
                            "TYP": 4001,
                        }
                    )
                    if item["REGION"] in regions:
                        id, message_dict = rnpp_prepare_data(**item)
                        message = get_message(work_name, prepare_data)
                        data_to_sent = get_data_to_sent(id, message, data_message)
                        messages.update(data_to_sent)
                    else:
                        bad_list.append(id)

                with ManagerQueue(
                        config.get("Mq", "queue_manager"),
                        config.get("Mq", "channel"),
                        config.get("Mq", "conn_info"),
                ) as qmgr:
                    for key, val in messages.items():
                        qmgr.send_message(val["queue_name"], val["message"])
                        info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                        current_app.logger.info(info_to_log)

                resend_result = len(messages)
                resend_bad_result = len(bad_list)

                journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
                add_to_journal(request, work_name, journal_msg_report)

                return render_template(
                    "resend/resend_result.html",
                    resend_result=resend_result,
                    resend_bad_result=resend_bad_result,
                    bad_list=bad_list,
                )
        return render_template(
            "resend/file_input.html", resend_title=work_name
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/resend_adv_adi", methods=["GET", "POST"])
@login_required
def resend_adv_adi():
    if "adv_123" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка АДИ-Рег/АДИ-8"
        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()

            messages = {}
            bad_list = []
            with Database(config.get("VIO_DATABASE", "alias"), config.get("VIO_DATABASE", "login"),
                          config.get("VIO_DATABASE", "password")) as db:
                for id in list_ids:
                    data_message = {}

                    data_document = db.get_data_document(id, fields=["SENDER", "TYP"])
                    data_message.update(data_document)

                    data_attributes = db.get_attributes(id)
                    data_message.update(data_attributes)

                    data_linked_docs = db.get_linked_documents(id)

                    for item in data_linked_docs:
                        if item["TYP"] == 14:
                            data_message.update({"upp_id": item["DOC_ID"]})
                        elif item["TYP"] == 80097:
                            data_message.update(
                                {"adi_id": item["DOC_ID"], "adi_typ": item["TYP"]}
                            )
                        elif item["TYP"] == 606:
                            data_message.update(
                                {"adi_id": item["DOC_ID"], "adi_typ": item["TYP"]}
                            )

                    data_adi_document = db.get_data_document(
                        data_message["adi_id"], fields=["REG_DATE"]
                    )
                    data_message.update(data_adi_document)

                    if data_message["adi_typ"] == 80097:
                        adi_xml = db.get_content_xml(data_message["adi_id"])
                        data_message.update({"adi_xml": adi_xml})
                    data_message.update({"queue_name": config.get("MqAppSpuOut", "queue_name")})
                    prepare_data = get_adv_adi_prepare_data(id, data_message)
                    if prepare_data:
                        message = get_message(work_name, prepare_data)
                        data_to_sent = get_data_to_sent(id, message, data_message)
                        messages.update(data_to_sent)
                    else:
                        bad_list.append(id)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )

        return render_template(
            "resend/list_input.html",
            resend_title=work_name,
        )
    else:
        abort(403, "Отсутствует доступ")


@resend.route("/efs_to_spu", methods=["GET", "POST"])
@login_required
def resend_files_efs_to_spu():
    if "insurers" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка в СПУ"
        if request.method == "POST":
            files = request.files.getlist("files")
            params = request.form.getlist("flexRadioDefault")
            queue_name = params[0]
            messages = {}
            bad_list = []
            for file in files:
                data_message = {}
                filename = secure_filename(file.filename)
                filepath = path.join(uploads_dir, filename)
                file.save(filepath)
                data_message.update({"queue_name": queue_name})
                message = read_txt(filepath)
                data_to_sent = get_data_to_sent(filename, message, data_message)
                messages.update(data_to_sent)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} файлам, отправка не прошла по {resend_bad_result} файлам"
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )
        return render_template(
            "resend/files_input_efs_to_spu.html", resend_title=work_name
        )
    else:
        abort(403)


@resend.route("/szi_km_to_fbdp", methods=["GET", "POST"])
@login_required
def szi_km_to_fbdp():
    if "insurers" in current_user.roles or "all" in current_user.roles:
        work_name = "Переотправка СЗИ-КМ в ФБДП"
        if request.method == "POST":
            text = request.form["text"]
            list_ids = text.splitlines()

            messages = {}
            bad_list = []
            with Database(config.get("VIO_DATABASE", "alias"), config.get("VIO_DATABASE", "login"),
                          config.get("VIO_DATABASE", "password")) as db:
                for id in list_ids:
                    data_message = {}

                    data_document = db.get_data_document(id, fields=["TYP"])
                    data_message.update(data_document)

                    data_attributes = db.get_attributes(id)
                    data_message.update(data_attributes)

                    data_message.update({"queue_name": config.get("MqSpuOut", "queue_name")})

                    prepare_data = get_szi_km_to_fbdp_prepare_data(id, data_message)
                    if prepare_data:
                        message = get_message(work_name, prepare_data)
                        #                        print(message)
                        data_to_sent = get_data_to_sent(id, message, data_message)
                        messages.update(data_to_sent)
                    else:
                        bad_list.append(id)

            with ManagerQueue(
                    config.get("Mq", "queue_manager"),
                    config.get("Mq", "channel"),
                    config.get("Mq", "conn_info"),
            ) as qmgr:
                for key, val in messages.items():
                    qmgr.send_message(val["queue_name"], val["message"])
                    info_to_log = f"user:{current_user.username},сообщение отправлено в очередь:{val['queue_name']},код процесса:{val['process_code']},id документа:{key},тип документа:{val['doc_typ']}"
                    current_app.logger.info(info_to_log)

            resend_result = len(messages)
            resend_bad_result = len(bad_list)

            journal_msg_report = f"Выполнена отправка по {resend_result} документам, отправка не прошла по {resend_bad_result} документам"
            add_to_journal(request, work_name, journal_msg_report)

            return render_template(
                "resend/resend_result.html",
                resend_result=resend_result,
                resend_bad_result=resend_bad_result,
                bad_list=bad_list,
            )
        return render_template(
            "resend/list_input.html",
            resend_title=work_name,
        )
    else:
        abort(403, "Отсутствует доступ")
