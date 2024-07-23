import uuid


def rnpp_prepare_data(**item):
    message_dict = {
        "MESSAGE_ID": uuid.uuid4().hex,
        "REGION": item["REGION"],
        "REQUEST_ID": item["REQUEST_ID"],
        "EHD_ID_RNPP": item["EHD_ID_RNPP"],
        "EHD_ID_ZNP": item["EHD_ID_ZNP"],
        "EXD_ID": item["EXD_ID"],
        "EHD_ID_TRRAS": item["EHD_ID_TRRAS"],
        "EHD_ID_SNPAR": item["EHD_ID_SNPAR"],
    }

    return (item["EHD_ID_ZNP"], message_dict)
