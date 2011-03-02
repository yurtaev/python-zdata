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
        self.URL_TICKET = "https://accounts.zoho.com/login?servicename=%s&FROM_AGENT=true&LOGIN_ID=%s&PASSWORD=%s"

    def __check_servicename(self, servicename):
        if not servicename in ["ZohoWriter", "ZohoSheet", "ZohoShow"]:
            msg = '%s is not servicename ["ZohoWriter", "ZohoSheet", "ZohoShow"]' % servicename
            raise Exception(msg)

    def __check_format(self, format, servicename=None):
        if servicename:
            if servicename in "ZohoWriter":
                if not format in ["doc", "docx", "pdf", "html", "sxw", "odt", "rtf"]:
                    msg = '%s not format %s ["doc", "docx", "pdf", "html", "sxw", "odt", "rtf"]' % (format, servicename)
                    raise Exception(msg)
            elif servicename in "ZohoSheet":
                if not format in ["xls", "xlsx", "ods", "sxc", "pdf", "html", "csv", "tsv"]:
                    msg = '%s not format %s ["xls", "xlsx", "ods", "sxc", "pdf", "html", "csv", "tsv"]' % (format, servicename)
                    raise Exception(msg)
            elif servicename in "ZohoShow":
                if not format in ["ppt", "pps", "odp", "pdf"]:
                    msg = '%s not format %s ["ppt", "pps", "odp", "pdf"]' % (format, servicename)
                    raise Exception(msg)
        if not format in ["xml", "json"]:
            msg = '%s not format ["xml", "json"]' % format
            raise Exception(msg)

    def __check_access(self, access):
        if not access in ["private", "public"]:
            msg = '%s is not access ["private", "public"]' % access
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
        url = None

        if servicename in "ZohoWriter":
            url = "https://export.writer.zoho.com/api/private/%s/documents?apikey=%s&ticket=%s" % args
        elif servicename in "ZohoSheet":
            url = "https://sheet.zoho.com/api/private/%s/books?apikey=%s&ticket=%s" % args
        elif servicename in "ZohoShow":
            url = "http://show.zoho.com/api/private/%s/presentations?apikey=%s&ticket=%s" % args

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
        url = None

        if servicename in "ZohoWriter":
            url = "https://export.writer.zoho.com/api/%s/%s/content/%s?apikey=%s&ticket=%s" % args
        elif servicename in "ZohoSheet":
            url = "https://sheet.zoho.com/api/%s/%s/content/%s?apikey=%s&ticket=%s" % args
        elif servicename in "ZohoShow":
            url = "https://show.zoho.com/api/%s/%s/content/%s?apikey=%s&ticket=%s" % args

        data = urllib.urlopen(url)
        data = data.read()

        if format in "json":
            if dict:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data