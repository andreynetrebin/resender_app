DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(128) NOT NULL
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username varchar(128) NOT NULL,
    password varchar(64) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    department_id INTEGER NOT NULL,
    FOREIGN KEY(department_id) REFERENCES departments(id)
);

DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(64) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS links;
CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(role_id) REFERENCES roles(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS journal_resend;
CREATE TABLE journal_resend (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(64) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')),
    result TEXT NOT NULL, 
    description varchar(128),
    url varchar(128) NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS techprocesses;
CREATE TABLE techprocesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(128) NOT NULL
);

DROP TABLE IF EXISTS works;
CREATE TABLE works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(128) NOT NULL,
    url varchar(128) NOT NULL,
    techprocess_id INTEGER NOT NULL,
    FOREIGN KEY(techprocess_id) REFERENCES techprocesses(id)
);

DROP TABLE IF EXISTS template_messages;
CREATE TABLE template_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(128) NOT NULL,
    template_message text NOT NULL,
    work_id INTEGER NOT NULL,
    FOREIGN KEY(work_id) REFERENCES works(id)
);

DROP TABLE IF EXISTS settings_type;
CREATE TABLE settings_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(128) NOT NULL
);


DROP TABLE IF EXISTS settings;
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name varchar(128) NOT NULL,
    value varchar(128) NOT NULL,
    setting_type_id INTEGER NOT NULL,
    FOREIGN KEY(setting_type_id) REFERENCES settings_type(id)
);



INSERT INTO departments (name) VALUES ('Отдел эксплуатации');  
INSERT INTO departments (name) VALUES ('Отдел ПУ');  
INSERT INTO departments (name) VALUES ('Отдел НСИ');  
INSERT INTO departments (name) VALUES ('Руководство');  

INSERT INTO users (username, password, department_id) VALUES ('admin', 'sha256$CPXnQtsB6cUyHFLb$7ad79b9287be36affbb793d6e3ff1f3dfe59342eef9bcee5e6f7d78fcfa600b3', 1);
INSERT INTO users (username, password, department_id) VALUES ('netrebin', 'sha256$kXZW4MokYwgxLRjt$196001b3092215636c5db3d7bfd94521c3d4114e2a04b278c94ca0fdd5172f96', 1);
INSERT INTO users (username, password, department_id) VALUES ('test_user', 'sha256$kXZW4MokYwgxLRjt$196001b3092215636c5db3d7bfd94521c3d4114e2a04b278c94ca0fdd5172f96', 1);

INSERT INTO roles (name) VALUES ('admin');  
INSERT INTO roles (name) VALUES ('all');
INSERT INTO roles (name) VALUES ('fri_vmse');
INSERT INTO roles (name) VALUES ('insurers');
INSERT INTO roles (name) VALUES ('npf_uspn');            
INSERT INTO roles (name) VALUES ('persons');            

INSERT INTO links (role_id, user_id) VALUES (1, 1);
INSERT INTO links (role_id, user_id) VALUES (2, 2);
INSERT INTO links (role_id, user_id) VALUES (3, 3);
INSERT INTO links (role_id, user_id) VALUES (4, 3);

INSERT INTO techprocesses (name) VALUES ('Сервис заявлений (PersonApplication)');  
INSERT INTO techprocesses (name) VALUES ('Сервис страхователей (InsurerReport)');  
INSERT INTO techprocesses (name) VALUES ('Выписки МСЭ от ФГИС ФРИ');  
INSERT INTO techprocesses (name) VALUES ('Выписки ЕГРН/ЕГРИП/ЕГРЮЛ');  
INSERT INTO techprocesses (name) VALUES ('Документы НПФ');  
INSERT INTO techprocesses (name) VALUES ('Назначение пенсии');  
INSERT INTO techprocesses (name) VALUES ('АДВ-1,2,3');  
INSERT INTO techprocesses (name) VALUES ('Переотправка файлов');  
INSERT INTO techprocesses (name) VALUES ('Смена статуса в ЕХД');  
INSERT INTO techprocesses (name) VALUES ('Перерасчёт пенсии (ПРБЗ)');  

INSERT INTO works (name, url, techprocess_id) VALUES ('От ВИО в ФП (НВПиСВ, КСП, АСВ, УСПН, МСК, СПУ)', 'http://127.0.0.1:5000/resend/person_apply_application_request', 1);

INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в АСВ по пакетам ЕФС-1', 'http://127.0.0.1:5000/resend/upp_efs', 2);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в АСВ по пакетам ИС', 'http://127.0.0.1:5000/resend/upp_is', 2);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в АСВ по пакетам СЗВ-М', 'http://127.0.0.1:5000/resend/upp_szvm', 2);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка атомарок', 'http://127.0.0.1:5000/resend/efs_atom_retry_tool', 2);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в СПУ', 'http://127.0.0.1:5000/resend/upp_resend_files_efs_to_spuefs', 2);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка СЗИ-КМ в ФБДП', 'http://127.0.0.1:5000/resend/szi_km_to_fbdp', 2);

INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в НВП (По инициативке)', 'http://127.0.0.1:5000/resend/vmse_proactive', 3);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в НВП (По запросу)', 'http://127.0.0.1:5000/resend/vmse_zapros', 3);

INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в АСВ', 'http://127.0.0.1:5000/resend/egrn_egrul_egrip', 4);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в ЕХД', 'http://127.0.0.1:5000/resend/resend_files_egrn_egrip_egrul', 4);

INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка в УСПН', 'http://127.0.0.1:5000/resend/npf_doc_uspn', 5);

INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка РНПП в НВП', 'http://127.0.0.1:5000/resend/resend_rnpp', 6);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка ПОСЗН в НВП', 'http://127.0.0.1:5000/resend/resend_poszn', 6);

INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка АДИ-Рег/АДИ-8', 'http://127.0.0.1:5000/resend/resend_adv_adi', 7);

INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка файлов', 'http://127.0.0.1:5000/resend/resend_files', 8);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка файлов в СОЭ', 'http://127.0.0.1:5000/resend/resend_files_soe', 8);

INSERT INTO works (name, url, techprocess_id) VALUES ('Смена статуса', 'http://127.0.0.1:5000/resend/change_status', 9);

INSERT INTO works (name, url, techprocess_id) VALUES ('Поиск СЗВ-Запроса по messageID', 'http://127.0.0.1:5000/resend/get_szv_zapros', 10);
INSERT INTO works (name, url, techprocess_id) VALUES ('Переотправка СЗИ-СВ в НВП', 'http://127.0.0.1:5000/resend/szi_sv_to_nvp', 10);

INSERT INTO template_messages (name, template_message, work_id) VALUES ('apply_application_request', 
'<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:aa="http://vio.pfr.ru/Statements/ApplyApplication/1.0">
    <soap:Header>
        <wsa:MessageID>$message_id</wsa:MessageID>
        <wsa:Action>$action</wsa:Action>
        <GlobalProcessID>$guid</GlobalProcessID>
    </soap:Header>
    <soap:Body>
        <aa:ApplyApplicationRequest>
            <PersonApplication>
                <Applicant>
                    <SNILS>$sender</SNILS>
                </Applicant>
                <ApplicationForm nsiType="$typ" applicationId="$doc_id"/>
                    $attached_docs
                <RelatedDocuments>
                    <DocumentRef id="$upp_id" nsiType="14"/>
                </RelatedDocuments>
            </PersonApplication>
        </aa:ApplyApplicationRequest>
    </soap:Body>
</soap:Envelope>', 1);
