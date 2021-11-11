# scrapy-sftp

A simpler handler to help enable scraping SFTP files with scrapy. This is a quick thing I hacked together that uses paramiko 
to make the sftp connection and return the file's body as a Response object.

## Installation

Download the sftp_handler file to an appropriate part of your project. Update your project requirements with the requirements on requirements.txt.

## Usage

This file can be added as a download handler for sftp uris by adding the following to your project settings.

```python

DOWNLOAD_HANDLERS = {
    "sftp": "Path.to.sftp_handler.SFTPHandler",
}

SFTP_USER = "login username"
SFTP_PASSWORD = "login password"
SFTP_HOST = "SFTP domain/ip address"
```

After you do this, any sftp url will be passed through the handler and the body attribute of the response will be the file in bytes format.

## Caveats

This is a very quick proof of concept hack. It may not suit if you are scraping large numbers of large files.
