import uuid


def get_szi_km_to_fbdp_prepare_data(id, data_message):
    if data_message["TYP"] == 80237:
        prepare_data = {
            "message_id": uuid.uuid4().hex,
            "request_id": data_message["process-id"],
            "id": id,
        }
        return prepare_data
