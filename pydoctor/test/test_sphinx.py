"""
Tests for Sphinx integration.
"""
import zlib

from pydoctor.sphinx import SphinxInventory


def make_SphinxInventory():
    """
    Return a SphinxInventory.
    """
    return SphinxInventory(logger=object(), project_name='project_name')


def make_SphinxInventoryWithLog():
    """
    Return a SphinxInventory with patched log.
    """
    inventory = make_SphinxInventory()
    log = []
    inventory.msg = lambda part, msg: log.append((part, msg))
    return (inventory, log)


def test_getPayload_empty():
    """
    Return empty string.
    """
    sut = make_SphinxInventory()
    content = """# Sphinx inventory version 2
# Project: some-name
# Version: 2.0
# The rest of this file is compressed with zlib.
x\x9c\x03\x00\x00\x00\x00\x01"""

    result = sut._getPayload(content)

    assert '' == result


def test_getPayload_content():
    """
    Return content as string.
    """
    payload = 'first_line\nsecond line'
    sut = make_SphinxInventory()
    content = """# Ignored line
# Project: some-name
# Version: 2.0
# commented line.
%s""" % (zlib.compress(payload),)

    result = sut._getPayload(content)

    assert payload == result


def test_getPayload_invalid():
    """
    Return empty string and log an error when failing to uncompress data.
    """
    sut, log = make_SphinxInventoryWithLog()
    sut._base_url = 'http://tm.tld'
    content = """# Project: some-name
# Version: 2.0
not-valid-zlib-content"""

    result = sut._getPayload(content)

    assert '' == result
    assert [(
        'sphinx', 'Failed to uncompress inventory from http://tm.tld',
        )] == log


def test_getLink_not_found():
    """
    Return None if link does not exists.
    """
    sut = make_SphinxInventory()

    assert None is sut.getLink('no.such.name')


def test_getLink_found():
    """
    Return the link from internal state.
    """
    sut = make_SphinxInventory()
    sut._base_url = 'http://base.tld'
    sut._links['some.name'] = 'some/url.php'

    assert 'http://base.tld/some/url.php' == sut.getLink('some.name')


def test_getLink_self_anchor():
    """
    Return the link with anchor as target name when link end with $.
    """
    sut = make_SphinxInventory()
    sut._base_url = 'http://base.tld'
    sut._links['some.name'] = 'some/url.php#$'

    assert 'http://base.tld/some/url.php#some.name' == sut.getLink('some.name')


def test_load_functional():
    """
    Functional test for loading an empty inventory.
    """
    payload = (
        'some.module1 py:module -1 module1.html -\n'
        'other.module2 py:module 0 module2.html Other description\n'
        )
    sut = make_SphinxInventory()
    # Patch URL loader to avoid hitting the system.
    content = """# Sphinx inventory version 2
# Project: some-name
# Version: 2.0
# The rest of this file is compressed with zlib.
%s""" % (zlib.compress(payload),)
    sut._getURL = lambda _: content

    sut.load('http://some.url/api/objects.inv')

    assert 'http://some.url/api/module1.html' == sut.getLink('some.module1')
    assert 'http://some.url/api/module2.html' == sut.getLink('other.module2')


def test_load_bad_url():
    """
    Log an error when failing to get base url from url.
    """
    sut, log = make_SphinxInventoryWithLog()

    sut.load('really.bad.url')

    assert sut._links == {}
    expected_log = [(
        'sphinx', 'Failed to get remote base url for really.bad.url'
        )]
    assert expected_log == log


def test_load_fail():
    """
    Log an error when failing to get content from url.
    """
    sut, log = make_SphinxInventoryWithLog()
    sut._getURL = lambda _: None

    sut.load('http://some.tld/o.inv')

    assert sut._links == {}
    expected_log = [(
        'sphinx', 'Failed to get object inventory from http://some.tld/o.inv'
        )]
    assert expected_log == log


def test_parseInventory_empty():
    """
    Return empty dict for empty input.
    """
    sut = make_SphinxInventory()

    result = sut._parseInventory('')

    assert {} == result


def test_parseInventory_single_line():
    """
    Return a dict with a single member.
    """
    sut = make_SphinxInventory()

    result = sut._parseInventory('some.attr py:attr -1 some.html De scription')

    assert {'some.attr': 'some.html'} == result


def test_parseInventory_invalid_lines():
    """
    Skip line and log an error.
    """
    sut, log = make_SphinxInventoryWithLog()
    sut._base_url = 'http://tm.tld'
    content = (
        'good.attr py:attribute -1 some.html -\n'
        'bad.attr bad format\n'
        'very.bad\n'
        '\n'
        'good.again py:module 0 again.html -\n'
        )

    result = sut._parseInventory(content)

    assert {
        'good.attr': 'some.html',
        'good.again': 'again.html'
        } == result
    assert [
        (
            'sphinx',
            'Failed to parse line "bad.attr bad format" for http://tm.tld'
            ),
        ('sphinx', 'Failed to parse line "very.bad" for http://tm.tld'),
        ('sphinx', 'Failed to parse line "" for http://tm.tld'),
        ] == log
