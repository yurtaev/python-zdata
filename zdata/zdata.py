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

    def get_ticket (self, servicename):
        if not servicename in ["ZohoWriter", "ZohoSheet", "ZohoShow"]:
            raise Exception('not servicename in ["ZohoWriter", "ZohoSheet", "ZohoShow"]')

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
        if not servicename in ["ZohoWriter", "ZohoSheet", "ZohoShow"]:
            raise Exception('not servicename in ["ZohoWriter", "ZohoSheet", "ZohoShow"]')
        if not format in ["xml", "json"]:
            raise Exception('not format in ["xml", "json"]')

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
        if not servicename in ["ZohoWriter", "ZohoSheet", "ZohoShow"]:
            raise Exception('not servicename in ["ZohoWriter", "ZohoSheet", "ZohoShow"]')
        if not format in ["xml", "json"]:
            raise Exception('not format in ["xml", "json"]')
        if not access in ["private", "public"]:
            raise Exception('not public in ["private", "public"]')

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