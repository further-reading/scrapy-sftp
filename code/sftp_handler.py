from io import BytesIO

import paramiko
import yarl
from scrapy.responsetypes import responsetypes
from scrapy.utils.decorators import defers


class SFTPHandler:
    lazy = False

    @classmethod
    def from_crawler(cls, crawler):
        username = crawler.settings.get("SFTP_USER")
        password = crawler.settings.get("SFTP_PASSWORD")
        port = crawler.settings.get("SFTP_PORT", 22)
        host = crawler.settings.get("SFTP_HOST")
        return cls(username, password, port, host)

    def __init__(self, username, password, port, host):
        self.sftp = self.make_sftp_connection(
            username,
            password,
            port,
            host,
        )

    @defers
    def download_request(self, request, spider):
        url = yarl.URL(request.url)
        path = url.path
        with BytesIO() as stream:
            self.sftp.getfo(path, stream)
            stream.seek(0)
            body = stream.getvalue()

        respcls = responsetypes.from_args(filename=path, body=body)
        return respcls(url=request.url, body=body)

    def make_sftp_connection(self, username, password, port, host):
        t = paramiko.Transport((host, port))
        t.banner_timeout = 60
        t.connect(username=username, password=password)
        return paramiko.SFTPClient.from_transport(t)
