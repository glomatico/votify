import logging

from votify.cli.utils import CustomLoggerFormatter


def make_record(levelno):
    return logging.LogRecord("votify", levelno, __file__, 1, "hello", None, None)


def test_format_unknown_level_does_not_crash():
    formatted = CustomLoggerFormatter(use_colors=True).format(make_record(15))
    assert "hello" in formatted


def test_format_known_levels():
    for levelno in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL):
        formatted = CustomLoggerFormatter(use_colors=True).format(make_record(levelno))
        assert "hello" in formatted
    plain = CustomLoggerFormatter(use_colors=False).format(make_record(15))
    assert "hello" in plain
