import uuid


def get_action_queue(process_code):
    if process_code == "SPU_Application_PersonADV_Processing":
        action = "http://vio.pfr.ru/person/Application/SPU_Application_PersonADV_Processing/ApplyApplicationRequest"
        queue = "SPU.APPSPU.IN"
        return (action, queue)
    elif process_code == "ApplicationProccessingMSK":
        action = "http://vio.pfr.ru/person/Application/MSKApplicationPortType/ApplyApplicationRequest"
        queue = "MSK.APPMSK.IN"
        return (action, queue)
    elif process_code == "ApplicationProccessingKSP":
        action = "http://vio.pfr.ru/person/Application/KSPApplicationPortType/ApplyApplicationRequest"
        queue = "KSP.APPKSP.IN"
        return (action, queue)
    elif process_code == "ApplicationProccessingSPU":
        action = "http://vio.pfr.ru/person/Application/SPUApplicationPortType/ApplyApplicationRequest"
        queue = "SPU.APPSPU.IN"
        return (action, queue)
    elif process_code == "ApplicationProccessingASV":
        action = "http://vio.pfr.ru/person/Application/ASV_ApplicationPortType/ApplyApplicationRequest"
        queue = "ASV.APPASV.IN"
        return (action, queue)
    elif process_code == "ApplicationProccessingNVPSV":
        action = "http://vio.pfr.ru/person/Application/NVPSV_ApplicationPortType/ApplyApplicationRequest"
        queue = "NVPSV.APPNVPSV.IN"
        return (action, queue)
    elif process_code == "ApplicationProccessingUSPN":
        action = "http://vio.pfr.ru/person/Application/USPN_ApplicationPortType/ApplyApplicationRequest"
        queue = "USPN.APPUSPN.IN"
        return (action, queue)
    elif process_code == "ApplicationProccessingUSPNNoWait":
        action = "http://vio.pfr.ru/person/Application/USPN_Application_Unified_ProccessingNoWait/ApplyApplicationRequest"
        queue = "USPN.APPUSPN.IN"
        return (action, queue)
    elif process_code == "ApplicationProccessingNVPSVNoWait":
        action = "http://vio.pfr.ru/person/Application/NVPSV_Application_Unified_ProccessingNoWait/ApplyApplicationRequest"
        queue = "NVPSV.APPNVPSV.IN"
        return (action, queue)
    else:
        return (None, None)


def get_person_app_prepare_data(id, data_message):
    if data_message["DOC_ID"] and data_message["action"] is not None:
        prepare_data = {
            "message_id": uuid.uuid4().hex,
            "action": data_message["action"],
            "guid": data_message["process-id"],
            "sender": data_message["SENDER"],
            "doc_id": id,
            "typ": data_message["TYP"],
            "attached_docs": data_message["attached_docs"],
            "upp_id": data_message["DOC_ID"],
        }
        return prepare_data
