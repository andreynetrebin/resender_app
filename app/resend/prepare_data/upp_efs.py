import uuid


def upp_efs_prepare_data(**item):
    message_dict = {
        "messageID": uuid.uuid4().hex,
        "GlobalProcessId": item["GlobalProcessId"],
        "GlobalProcessType": item["GlobalProcessType"],
        "insurerRegNum": item["insurerRegNum"],
        "packageId": item["packageId"],
        "channel": item["channel"],
        "AcceptDate": item["AcceptDate"],
        "Code": item["Code"],
        "Branch": item["Branch"],
        "ExternalNumber": item["ExternalNumber"],
        "docid": item["docid"],
        "uppid": item["uppid"],
        "uppstatus": item["uppstatus"],
    }

    return (item["packageId"], message_dict)
