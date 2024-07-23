query_document_fiedls = "select * from document where id = (?)"
query_atrributes = "select name, val from document_attribute where r_doc = (?)"
query_attached_docs = "select l.r_obj2_id doc_id, docs.typ from links as l join document as docs on l.r_obj2_id = docs.id where l.up = 410 and l.r_obj1_id in (?) and upper(l.val) = 'СОДЕРЖИТ'"
query_linked_docs = "select l.r_obj2_id doc_id, docs.typ from links as l join document as docs on l.r_obj2_id = docs.id where l.up = 410 and l.r_obj1_id in (?) and upper(l.val) = 'ИМЕЕТ'"
query_linked_parent_docs = "select l.r_obj1_id parent_doc_id from links as l where l.up = 410 and l.r_obj2_id in (?)"
query_content_body_xml = "select files.body_xml from document_content as doc_cont join files on doc_cont.r_file = files.id where doc_cont.r_doc in (?)"
query_content_body = "select files.body from document_content as doc_cont join files on doc_cont.r_file = files.id where doc_cont.r_doc in (?)"
query_szv_zapros = """
with prbz as
(
select 
	doc.id prbz_id
	,doc.status
	,doc.sender
	,doc.reg_date
from
	document as doc
where
	doc.id = (?)
)
,szi_sv as
(
select
    prbz.prbz_id
    ,doc.id id_szi_sv
    ,doc.status
    ,doc.reg_date
from
	prbz
	join links as links on prbz.prbz_id = links.r_obj1_id 
	join document as doc on links.r_obj2_id = doc.id
where
	links.up = 410
and
    doc.typ = 10004	
)
select 
    (select clsf.term status_szv_zapros from cls_item as clsf where clsf.up = 300 and clsf.term_num = 1 and clsf.num = prbz.status)
    ,prbz.sender
    ,prbz.reg_date reg_date_szv_zapros
    ,szi_sv.id_szi_sv id_szi_sv
    ,(select clsf.term status_szi_sv from cls_item as clsf where clsf.up = 300 and clsf.term_num = 1 and clsf.num = szi_sv.status)
    ,szi_sv.reg_date reg_date_szi_sv
from
	prbz
	left join szi_sv on prbz.prbz_id = szi_sv.prbz_id
 

"""
query_szi_sv_ = """
with prepare_data as
(  	
select
	vio_xml_msg_id
	,vio_xml_from
	,vio_xml_doc_xml
from
	spumst.spu_msg_vio_xml
where
	vio_xml_pr_ref = (?)
and
	vio_xml_stat = 5
and
	vio_xml_end_ts > (?)
)
select
	prepare_data.vio_xml_msg_id
	,prepare_data.vio_xml_from
from
	prepare_data
	,xmltable(
            '$d/*:Envelope/*:Body' passing xmlparse(prepare_data.vio_xml_doc_xml) as "d"
            columns exd_id  bigint
            path 'Message/BussinessData/Notification/Documents/Document/@id'
            ) as doc_xml
where
	doc_xml.exd_id = (?)
;	
"""

query_szi_sv = """
with prepare_data as
(  	
select distinct
	doc.exd_id as id
	,doc2.request_id as requestid 
	,doc2.exd_id as parentdocid
from
	spumst.spu_doc doc
	join spumst.spu_doc doc2 on doc.doc_lnk_id = doc2.op_uni
where
	doc.exd_id = (?)
)
select
	prepare_data.*
	,vio_xml.vio_xml_msg_id as correlationid
    ,vio_xml.vio_xml_from as recipient
    ,vio_xml.vio_xml_beg_ts
    ,vio_xml.vio_xml_end_ts
    ,vio_xml.vio_xml_stat
from
	prepare_data
	join spumst.spu_msg_vio_xml as vio_xml on prepare_data.requestid = vio_xml.vio_xml_pr_ref 
	join xmltable(
            '$d/*:Envelope/*:Body' passing xmlparse(vio_xml.vio_xml_doc_xml) as "d"
            columns exd_id  bigint
            path 'Message/BussinessData/Notification/Documents/Document/@id'
            ) as doc_xml on prepare_data.parentdocid = doc_xml.exd_id
where
vio_xml.vio_xml_stat = 5
;	   
"""
