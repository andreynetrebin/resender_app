import uuid


def get_npf_doc_uspn_prepare_data(id, data_message):
    if data_message["TO"] == "urn:region:777000:USPN":
        request_id = data_message["NAME"][18:54].replace("-", "")
        prepare_data = {
            "message_id": uuid.uuid4().hex,
            "request_id": request_id,
            "id": id,
            "process_code": data_message["process-code"],
            "upp_id": data_message["DOC_ID"],
        }
        return prepare_data
