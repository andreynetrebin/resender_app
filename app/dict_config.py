def get_dict_config(log_level, log_filename):
    dict_config = {
        'version': 1,
        'formatters': {'default': {
            'format': '%(levelname)-8s - %(module)s - [%(asctime)s] - %(message)s',
        }},
        'handlers': {
            'time-rotate': {
                'level': 'INFO',
                'formatter': 'default',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': log_filename,
                'when': "D",
                'interval': 1,
                'backupCount': 10
            }},
        'root': {
            'level': log_level,
            'handlers': ['time-rotate']
        },
    }

    return dict_config
