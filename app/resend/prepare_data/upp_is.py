import uuid


def upp_is_prepare_data(**item):
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
        "doc_typ": item["doc_typ"],
        "uppid": item["uppid"],
        "uppstatus": item["uppstatus"],
    }
    return (item["packageId"], message_dict)
