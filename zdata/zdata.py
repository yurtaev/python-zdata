# -*- coding:utf-8 -*-

import urllib
import re

try:
    import simplejson as json
except ImportError:
    import json

class zdata():
    def __init__(self, username, password, api_key):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.ticket = {
            "ZohoWriter": None,
            "ZohoSheet": None,
            "ZohoShow": None
        }
        self.formats = {
            "ZohoWriter": ["doc", "docx", "pdf", "html", "sxw", "odt", "rtf"],
            "ZohoSheet": ["xls", "xlsx", "ods", "sxc", "pdf", "html", "csv", "tsv"],
            "ZohoShow": ["ppt", "pps", "odp", "pdf"],
            "get": ["xml", "json"],
            "access": ["private", "public"]
        }
        self.urls = {
            "ZohoWriter": {
                "list": "https://export.writer.zoho.com/api/private/%s/documents?apikey=%s&ticket=%s",
                "content": "https://export.writer.zoho.com/api/%s/%s/content/%s?apikey=%s&ticket=%s",
                "download": "https://export.writer.zoho.com/api/%s/%s/download/%s?apikey=%s&ticket=%s"
            },
            "ZohoSheet": {
                "list": "https://sheet.zoho.com/api/private/%s/books?apikey=%s&ticket=%s",
                "content": "https://sheet.zoho.com/api/%s/%s/content/%s?apikey=%s&ticket=%s",
                "download": "https://sheet.zoho.com/api/%s/%s/download/%s?apikey=%s&ticket=%s"
            },
            "ZohoShow": {
                "list": "http://show.zoho.com/api/private/%s/presentations?apikey=%s&ticket=%s",
                "content": "https://show.zoho.com/api/%s/%s/content/%s?apikey=%s&ticket=%s",
                "download": "https://show.zoho.com/api/%s/%s/download/%s?apikey=%s&ticket=%s"
            }
        }
        self.URL_TICKET = "https://accounts.zoho.com/login?servicename=%s&FROM_AGENT=true&LOGIN_ID=%s&PASSWORD=%s"

    def __check_servicename(self, servicename):
        if not servicename in ["ZohoWriter", "ZohoSheet", "ZohoShow"]:
            msg = '%s is not servicename ["ZohoWriter", "ZohoSheet",     "ZohoShow"]' % servicename
            raise Exception(msg)

    def __check_format(self, format, servicename=None):
        if servicename:
            if not format in self.formats[servicename]:
                msg = '%s is not format %s %s' % (format, servicename, str(self.formats[servicename]))
                raise Exception(msg)
        else:
            if not format in self.formats["get"]:
                msg = '%s is not GET format %s' % (format, str(self.formats["get"]))
                raise Exception(msg)

    def __check_access(self, access):
        if not access in self.formats["access"]:
            msg = '%s is not access %s' % (access, str(self.formats["access"]))
            raise Exception(msg)

    def get_ticket (self, servicename):
        self.__check_servicename(servicename)

        if self.ticket[servicename]:
            return self.ticket[servicename]

        url = self.URL_TICKET % (servicename, self.username, self.password)

        data = urllib.urlopen(url)
        data = data.read()

        result = re.findall("(?:RESULT=)(.*)", data)[0]
        if result == "FALSE":
            warning = re.findall("(?:CAUSE=)(.*)", data)[0]
            raise Exception(warning)

        self.ticket[servicename] = re.findall("(?:TICKET=)(.*)", data)[0]

        return self.ticket[servicename]

    def get_list(self, servicename, format="json", dict=False):
        self.__check_servicename(servicename)
        self.__check_format(format)

        args = (format, self.api_key, self.get_ticket(servicename))

        url = self.urls[servicename]["list"] % args

        data = urllib.urlopen(url)
        data = data.read()

        if format in "json":
            if dict:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def get_content(self, access, servicename, id, format="json", dict=False):
        self.__check_servicename(servicename)
        self.__check_format(format)
        self.__check_access(access)

        args = (access, format, id, self.api_key, self.get_ticket(servicename))

        url = self.urls[servicename]["content"] % args

        data = urllib.urlopen(url)
        data = data.read()

        if format in "json":
            if dict:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def get_url_download(self, access, servicename, format, id):
        self.__check_access(access)
        self.__check_servicename(servicename)
        self.__check_format(format, servicename=servicename)

        args = (access, format, id, self.api_key, self.get_ticket(servicename))

        url = self.urls[servicename]["download"] % args

        return url