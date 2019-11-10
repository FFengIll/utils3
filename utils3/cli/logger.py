import logging
import sys


def get_logbook_logger():
    from logbook import Logger, StreamHandler

    # use string level
    handler = StreamHandler(sys.stdout, level='INFO')
    handler.push_application()
    logger = Logger('cutwhite')


def get_color_logger(name, level=logging.NOTSET):
    try:
        import colorlog, logging
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
    coloredlogs.install(level=level)

    # If you don't want to see log messages from libraries, you can pass a
    # specific logger object to the install() function. In this case only log
    # messages originating from that logger will show up on the terminal.
    coloredlogs.install(level=level, logger=logger)

    # Some examples.
    logger.debug("this is a debugging message")
    logger.info("this is an informational message")
    logger.warning("this is a warning message")
    logger.error("this is an error message")
    logger.critical("this is a critical message")

    return logger


def get_logger(name, level=logging.NOTSET, file=None):
    try:
        if isinstance(level, str):
            level = getattr(logging, level.upper())

        # logger object
        app_log = logging.getLogger(name)

        # set format        
        format_str = logging.Formatter("%(asctime)s %(filename)s[%(lineno)d] %(levelname)s %(message)s")

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
    get_colored_logger(__file__, 'Debug')


if __name__ == '__main__':
    test_get_colored_logger()
