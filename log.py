import logging


def init_custom_logger(custom_name):
    """initializes a custom logger

    all modules and submodules should use this via
        import logging
        logger = logging.getLogger(custom_name)
    
    """
    handler = logging.FileHandler('monitor.log', 'a')
   
    # include 'module' so that it is clear where the message came from 
    format = logging.Formatter('%(asctime)s %(levelname)s - %(module)s: %(message)s')
    handler.setFormatter(format)

    logger = logging.getLogger(custom_name)
    logger.addHandler(handler)
    
    return logger

