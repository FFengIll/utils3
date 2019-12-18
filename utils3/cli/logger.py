import logging
import sys
import os


def get_logbook(name, level=logging.INFO, file=None):
    import logbook
    from logbook import StreamHandler
    from logbook.more import ColorizedStderrHandler

    def log_type(record, handler):
        log = "[{date}] [{level}] [{filename}] [{func_name}] [{lineno}] {msg}".format(
            date=record.time,  # 日志时间
            level=record.level_name,  # 日志等级
            filename=os.path.split(record.filename)[-1],  # 文件名
            func_name=record.func_name,  # 函数名
            lineno=record.lineno,  # 行号
            msg=record.message  # 日志内容
        )
        return log

    if isinstance(level, str):
        # logbook use different define
        level = getattr(logbook, level.upper())

    handler = logbook.StreamHandler(sys.stdout)
    handler.formatter = log_type
    handler.push_application()

    logger = logbook.Logger(name)
    logger.handlers = []
    logger.handlers.append(handler)
    # set level on logger is enough
    logger.level = level
    return logger


def get_color_logger(name, level=logging.NOTSET):
    try:
        import colorlog
        import logging
        pass
    except:
        return get_logger(name, level)


def get_colored_logger(name, level=logging.NOTSET):
    import coloredlogs

    # Create a logger object.
    logger = get_logger(name, level)

    # By default the install() function installs a handler on the root logger,
    # this means that log messages from your code and log messages from the
    # libraries that you use will all show up on the terminal.
    # coloredlogs.install(level=level)

    # If you don't want to see log messages from libraries, you can pass a
    # specific logger object to the install() function. In this case only log
    # messages originating from that logger will show up on the terminal.
    coloredlogs.install(level=level, logger=logger)

    return logger


def get_logger(name, level=logging.NOTSET, file=None):
    try:
        if isinstance(level, str):
            level = getattr(logging, level.upper())

        # logger object
        app_log = logging.getLogger(name)

        # set format        
        format_str = logging.Formatter(
            "%(asctime)s %(filename)s[%(lineno)d] %(levelname)s %(message)s")

        if len(app_log.handlers) <= 0:

            # create stander output handler
            crit_hand = logging.StreamHandler(sys.stderr)
            crit_hand.setFormatter(format_str)
            app_log.addHandler(crit_hand)

            # create file handler
            if file:
                file_hand = logging.FileHandler(file, 'a')
                file_hand.setFormatter(format_str)
                app_log.addHandler(file_hand)

        # 必须设置，否则无法输出
        app_log.setLevel(level)
        app_log.propagate = False

        return app_log
    except Exception as e:
        logging.shutdown()
        raise e


def test_get_colored_logger():
    logger = get_colored_logger(__file__, 'Debug')

    # Some examples.
    logger.debug("this is a debugging message")
    logger.info("this is an informational message")
    logger.warning("this is a warning message")
    logger.error("this is an error message")
    logger.critical("this is a critical message")


if __name__ == '__main__':
    test_get_colored_logger()
