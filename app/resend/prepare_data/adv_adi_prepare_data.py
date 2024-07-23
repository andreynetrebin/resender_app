import uuid
import re


def get_adv_adi_prepare_data(id, data_message):
    if (
            data_message["TYP"] in [101, 102, 103]
            and data_message["process-code"] == "SPU_Application_PersonADV_Processing"
    ):

        if data_message["adi_typ"] == 80097:
            pattern_snils = "<СНИЛС>(\d{3}-\d{3}-\d{3}\s\d{2})</СНИЛС>"
            snils = re.findall(pattern_snils, data_message["adi_xml"])[0]
            status = 17
            status_name = "Учтено"
            comment = "Ваше заявление учтено."
        elif data_message["adi_typ"] == 606:
            snils = data_message["SENDER"]
            status = 20
            status_name = "Отклонено"
            comment = "Ваше заявление отклонено. Найдены похожие ЗЛ. Просим обратиться в СФР для уточнения."

        prepare_data = {
            "message_id": uuid.uuid4().hex,
            "GUID": data_message["process-id"],
            "ADV_ID": id,
            "ADV_TYP": data_message["TYP"],
            "SNILS": snils,
            "change_date": data_message["REG_DATE"]
            .astimezone()
            .replace()
            .isoformat(sep="T", timespec="milliseconds"),
            "ADI_ID": data_message["adi_id"],
            "status": status,
            "status_name": status_name,
            "comment": comment,
            "adi_typ": data_message["adi_typ"],
        }
        return prepare_data
