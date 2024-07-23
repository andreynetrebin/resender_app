import pymqi
from flask import current_app


class ManagerQueue:

    def __init__(self, queue_manager: str, channel: str, conn_info: str):
        self.queue_manager = queue_manager
        self.channel = channel
        self.conn_info = conn_info
        self.queue = None
        self.connection = None

    def __enter__(self):
        try:
            self.connection = pymqi.connect(
                self.queue_manager, self.channel, self.conn_info
            )
            current_app.logger.debug("Открыто подкючение к MQ")
            return self
        except:
            logger.critical("Не удалось подключиться к MQ")

    def send_message(self, queue_name, message, list_md=None, rfh2=None):
        self.queue = pymqi.Queue(self.connection, queue_name)
        if list_md is None and rfh2 is None:
            self.queue.put(message)
        elif list_md is not None:
            put_mqmd = self.get_put_mqmd(list_md)
            self.queue.put(message, put_mqmd)
        elif rfh2 is not None:
            md = pymqi.MD()
            md.Format = pymqi.CMQC.MQFMT_RF_HEADER_2
            opts = pymqi.pmo()
            rfh2 = pymqi.RFH2()
            rfh2["CodedCharSetId"] = 1208
            rfh2["NameValueCCSID"] = 1208
            rfh2.add_folder(bytes("<mcd><Msd>xmlnsc</Msd></mcd>", "utf-8"))
            self.queue.put_rfh2(message, md, opts, [rfh2])

    @staticmethod
    def get_put_mqmd(self, list_md):
        put_mqmd = pymqi.MD()
        for md in list_md:
            put_mqmd[md["param"]] = bytes(md["value"], "utf-8")
        return put_mqmd

    def close(self):
        self.connection.disconnect()
        self.connection = None
        current_app.logger.debug("Закрыто подкючение к MQ")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
