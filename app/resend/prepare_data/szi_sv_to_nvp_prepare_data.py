import uuid


def get_szi_sv_to_nvp_prepare_data(data_message):
    message_dict = {
        "message_id": uuid.uuid4().hex,
        "REQUESTID": data_message["REQUESTID"],
        "PARENTDOCID": data_message["PARENTDOCID"],
        "ID": data_message["ID"],
        "CORRELATIONID": data_message["CORRELATIONID"],
        "RECIPIENT": data_message["RECIPIENT"]
    }

    return message_dict
