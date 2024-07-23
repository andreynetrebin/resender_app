import uuid


def poszn_prepare_data(**item):
    message_dict = {
        "message_id": uuid.uuid4().hex,
        "receiver": item["RECEIVER"],
        "request_id": item["globalProcessID"],
        "app_id": item["app_id"],
    }

    return (item["app_id"], message_dict)
