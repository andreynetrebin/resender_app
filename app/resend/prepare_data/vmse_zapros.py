import uuid
import xml.etree.ElementTree as ET


def get_vmse_data_from_packet_xml(packet_xml):
    tree = ET.fromstring(packet_xml)
    for body in tree.findall("{http://www.w3.org/2003/05/soap-envelope}Body"):
        data = body[0][0].text
        return data


def get_vmse_zapros_prepare_data(id, data_message):
    if (
            data_message["TYP"] == 30002
            and data_message["FROM"] == "urn:region:777000:UVKiP"
    ):
        print(type(data_message["DOC_DATE"]))
        prepare_data = {
            "message_id": uuid.uuid4().hex,
            "request_id": uuid.uuid4().hex,
            "document_id": id,
            "document_number": data_message["DOC_NUM"],
            "document_date": data_message["DOC_DATE"]
            .astimezone()
            .replace()
            .isoformat(sep="T", timespec="milliseconds"),
            "reg_number": data_message["REG_NUM"],
            "reg_date": data_message["REG_DATE"]
            .astimezone()
            .replace()
            .isoformat(sep="T", timespec="milliseconds"),
            "receive_date": data_message["ADM_DATE"]
            .astimezone()
            .replace()
            .isoformat(sep="T", timespec="milliseconds"),
            "submitter": data_message["SENDER"],
            "recipient": data_message["RECEIVER"],
            "to": data_message["TO"],
            "data": data_message["data"],
        }
        return prepare_data
