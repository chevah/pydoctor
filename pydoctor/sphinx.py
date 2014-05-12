"""
Support for Sphinx compatibility.
"""
from __future__ import absolute_import
import urllib2
import zlib


class SphinxInventory(object):
    """
    Sphinx inventory handler.
    """

    version = (2, 0)

    def __init__(self, logger, project_name):
        self.project_name = project_name
        self.msg = logger
        self._base_url = ''
        self._links = {}

    def load(self, url):
        """
        Load inventory from URL.
        """
        parts = url.rsplit('/', 1)
        if len(parts) != 2:
            self.msg(
                'sphinx', 'Failed to get remote base url for %s' % (url,))
            return

        self._base_url = parts[0]

        data = self._getURL(url)

        if not data:
            self.msg(
                'sphinx', 'Failed to get object inventory from %s' % (url, ))
            return

        payload = self._getPayload(data)
        self._links = self._parseInventory(payload)

    def _getURL(self, url):
        """
        Get content of URL.

        This is a helper for testing.
        """
        try:
            response = urllib2.urlopen(url)
            return response.read()
        except:
            return None

    def _getPayload(self, data):
        """
        Parse inventory and return clear text payload without comments.
        """
        payload = ''
        while True:
            parts = data.split('\n', 1)
            if len(parts) != 2:
                payload = data
                break
            if not parts[0].startswith('#'):
                payload = data
                break
            data = parts[1]
        try:
            return zlib.decompress(payload)
        except:
            self.msg(
                'sphinx',
                'Failed to uncompress inventory from %s' % (self._base_url, ),
                )
            return ''

    def _parseInventory(self, payload):
        """
        Parse clear text payload and load it into internal links database.
        """
        result = {}
        for line in payload.splitlines():
            parts = line.split(' ', 4)
            if len(parts) != 5:
                self.msg(
                    'sphinx',
                    'Failed to parse line "%s" for %s' % (line, self._base_url),
                    )
                continue
            result[parts[0]] = parts[3]
        return result

    def getLink(self, name):
        """
        Return link for `name` or None if no link is found.
        """
        relative_link = self._links.get(name, None)
        if not relative_link:
            return None

        # For links ending with $, replace it with full name.
        if relative_link.endswith('$'):
            relative_link = relative_link[:-1] + name

        return '%s/%s' % (self._base_url, relative_link)
