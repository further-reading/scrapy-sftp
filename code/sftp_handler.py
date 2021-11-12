from io import BytesIO

import paramiko
import yarl
from scrapy.responsetypes import responsetypes
from scrapy.utils.decorators import defers


class SFTPHandler:
    lazy = False

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.username = crawler.settings.get("SFTP_USER")
        self.password = crawler.settings.get("SFTP_PASSWORD")
        self.port = crawler.settings.get("SFTP_PORT", 22)
        self.host = crawler.settings.get("SFTP_HOST")
        self.tries = crawler.settings.get("SFTP_TRIES", 3)
        self.sftp = self.make_sftp_connection()

    @defers
    def download_request(self, request, spider):
        url = yarl.URL(request.url)
        path = url.path
        try:
            body = self.sftp_get_data(path)
            status = 200
        except FileNotFoundError:
            body = None
            status = 404

        respcls = responsetypes.from_args(filename=path, body=body)
        return respcls(url=request.url, body=body, status=status)

    def sftp_get_data(self, path):
        tries = 0
        while tries < self.tries:
            with BytesIO() as stream:
                try:
                    self.sftp.getfo(path, stream)
                    stream.seek(0)
                    return stream.getvalue()
                except OSError as e:
                    if "OSError: Socket is closed" in str(e):
                        # likely timed out, reopen connection
                        tries += 1
                        self.sftp = self.make_sftp_connection()
                    else:
                        raise e

    def make_sftp_connection(self):
        t = paramiko.Transport((self.host, self.port))
        t.banner_timeout = 60
        t.connect(username=self.username, password=self.password)
        return paramiko.SFTPClient.from_transport(t)

    def close(self):
        self.sftp.close()
