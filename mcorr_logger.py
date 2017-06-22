import logging
import sys
import os

#logger.debug('Debug error')
#logger.info('INFO ERROR')
#logger.critical('INFO ERROR2')

def init_logger():
    main_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    #print("PATH :\n"+main_path)
    formatter = logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")
    handler_critic = logging.FileHandler(main_path+"/logs/error.log", mode="a", encoding="utf-8")
    handler_info = logging.FileHandler(main_path+"/logs/info.log", mode="a", encoding="utf-8")
    handler_critic.setFormatter(formatter)
    handler_info.setFormatter(formatter)
    handler_info.setLevel(logging.INFO)
    handler_critic.setLevel(logging.CRITICAL)
    logger = logging.getLogger("m_corr")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler_critic)
    logger.addHandler(handler_info)
    return logger
