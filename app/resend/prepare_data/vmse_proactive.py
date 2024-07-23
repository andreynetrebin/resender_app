import uuid


def get_vmse_proactive_prepare_data(id, data_message):
    if (
            data_message["TYP"] == 30002
            and data_message["FROM"] == "urn:region:777000:NVPSV"
    ):
        prepare_data = {
            "message_id": uuid.uuid4().hex,
            "request_id": uuid.uuid4().hex,
            "id": id,
        }
        return prepare_data
