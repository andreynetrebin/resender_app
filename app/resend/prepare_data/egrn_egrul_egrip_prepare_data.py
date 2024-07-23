import uuid


def get_egrn_egrul_egrip_prepare_data(id, data_message):
    if data_message["TYP"] == 123:
        task_code = "FNS.ASV.EGRUL.Processing"
        input_message_name = "FNS.ASV.EGRUL.RQ"
        process_ref_code = "FNS.ASV.EGRUL"

    elif data_message["TYP"] == 124:
        task_code = "FNS.ASV.EGRIP.Processing"
        input_message_name = "FNS.ASV.EGRIP.RQ"
        process_ref_code = "FNS.ASV.EGRIP"

    elif data_message["TYP"] == 125:
        task_code = "FNS.ASV.EGRN.Processing"
        input_message_name = "FNS.ASV.EGRN.RQ"
        process_ref_code = "FNS.ASV.EGRN"

    else:
        return False

    prepare_data = {
        "message_id": uuid.uuid4().hex,
        "task_code": task_code,
        "input_message_name": input_message_name,
        "process_ref_code": process_ref_code,
        "guid": data_message["process-id"],
        "id": id,
        "typ": data_message["TYP"],
    }
    return prepare_data
