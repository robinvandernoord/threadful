from src.threadful.__about__ import __version__


def test_version():
    assert __version__
    assert isinstance(__version__, str)
