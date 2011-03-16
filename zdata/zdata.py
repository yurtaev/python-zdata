# -*- coding:utf-8 -*-

import urllib
import re

try:
    import simplejson as json
except ImportError:
    import json

class zdata:
    def __init__(self, username, password, api_key):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.ticket = {
            "ZohoWriter": None,
            "ZohoSheet": None,
            "ZohoShow": None,
            "ZohoCRM": None,
            "ZohoProjects": None
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
        self.services = ["ZohoWriter", "ZohoSheet", "ZohoShow", "ZohoCRM", "ZohoProjects"]
        self.URL_TICKET = "https://accounts.zoho.com/login?servicename=%s&FROM_AGENT=true&LOGIN_ID=%s&PASSWORD=%s"

    def _check_servicename(self, servicename):
        if not servicename in self.services:
            msg = '%s is not servicename %s' % (servicename, str(self.services))
            raise Exception(msg)

    def _check_format(self, format, servicename=None):
        if servicename:
            if not format in self.formats[servicename]:
                msg = '%s is not format %s %s' % (format, servicename, str(self.formats[servicename]))
                raise Exception(msg)
        else:
            if not format in self.formats["get"]:
                msg = '%s is not GET format %s' % (format, str(self.formats["get"]))
                raise Exception(msg)

    def _check_access(self, access):
        if not access in self.formats["access"]:
            msg = '%s is not access %s' % (access, str(self.formats["access"]))
            raise Exception(msg)

    def get_ticket (self, servicename):
        self._check_servicename(servicename)

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

    def get_list(self, servicename, format="json", dic=False):
        self._check_servicename(servicename)
        self._check_format(format)

        args = (format, self.api_key, self.get_ticket(servicename))

        url = self.urls[servicename]["list"] % args

        data = urllib.urlopen(url)
        data = data.read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def get_content(self, access, servicename, id, format="json", dic=False):
        self._check_servicename(servicename)
        self._check_format(format)
        self._check_access(access)

        args = (access, format, id, self.api_key, self.get_ticket(servicename))

        url = self.urls[servicename]["content"] % args

        data = urllib.urlopen(url)
        data = data.read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def get_url_download(self, access, servicename, format, id):
        self._check_access(access)
        self._check_servicename(servicename)
        self._check_format(format, servicename=servicename)

        args = (access, format, id, self.api_key, self.get_ticket(servicename))

        url = self.urls[servicename]["download"] % args

        return url

class CRM:
    def __init__(self, username, password, api_key):
        self.zdata = zdata(username, password, api_key)
        self.ticket = self.zdata.get_ticket("ZohoCRM")
        self.api_key = api_key
        self.methods = ["getMyRecords", "getRecords", "getRecordById", "getCVRecords", "getSearchRecords",
                        "getSearchRecordsByPDC", "insertRecords", "updateRecords", "deleteRecords", "convertLead"]

    def _check_method(self, method):
        if not method in self.methods:
            msg = '%s is not method %s' % (method, str(self.methods))
            raise Exception(msg)

    def request(self, method, format="json", newFormat="1", dic=False, **kwargs):
        self._check_method(method)
        url = "http://crm.zoho.com/crm/private/%s/Leads/%s" % (format, method)
        if not "apikey" in kwargs:
            kwargs["apikey"] = self.api_key
        if not "ticket" in kwargs:
            kwargs["ticket"] = self.ticket
        kwargs["newFormat"] = newFormat
        args = urllib.urlencode(kwargs)
        data = urllib.urlopen(url, args)
        data = data.read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

class Projects:
    def __init__(self, username, password, api_key):
        self.zdata = zdata(username, password, api_key)
        self.ticket = self.zdata.get_ticket("ZohoProjects")
        self.api_key = api_key
        self.methods = ["getportals", "getlogin", "getphotourl", "content", "add", "delete", "update", ""]

    def _check_method(self, method):
        if not method in self.methods:
            msg = '%s is not method %s' % (method, str(self.methods))
            raise Exception(msg)

    def my_info(self, method, format="json", dic=False, **kwargs):
        self._check_method(method)
        if "getphotourl" in method:
            url = "http://projects.zoho.com/api/private/%s/user/%s" % (format, method)
        else:
            url = "http://projects.zoho.com/api/private/%s/dashbs/%s" % (format, method)
        if not "apikey" in kwargs:
            kwargs["apikey"] = self.api_key
        if not "ticket" in kwargs:
            kwargs["ticket"] = self.ticket
        args = urllib.urlencode(kwargs)
        data = urllib.urlopen(url, args)
        data = data.read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def request(self, method, portal_name, format="json", dic=False, **kwargs):
        self._check_method(method)
        if method == "":
            url = "http://projects.zoho.com/portal/%s/api/private/%s/projects" % (portal_name, format)
        else:
            url = "http://projects.zoho.com/portal/%s/api/private/%s/project/%s" % (portal_name, format, method)
        if not "apikey" in kwargs:
            kwargs["apikey"] = self.api_key
        if not "ticket" in kwargs:
            kwargs["ticket"] = self.ticket
        args = urllib.urlencode(kwargs)
        data = urllib.urlopen(url, args)
        data = data.read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def users(self, portal_name, projid, format="json", dic=False):
        url = "http://projects.zoho.com/portal/%s/api/private/%s/users?apikey=%s&ticket=%s"
        url = url % (portal_name, format, self.api_key, self.ticket)
        args = dict(projId=projid)
        data = urllib.urlopen(url, urllib.urlencode(args))
        data = data.read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def tasks(self, portal_name, projid, format="json", dic=False):
        url = "http://projects.zoho.com/portal/%s/api/private/%s/tasks?apikey=%s&ticket=%s"
        url = url % (portal_name, format, self.api_key, self.ticket)
        args = dict(projId=projid,
                    flag="allflag",
                    uname="all",
                    mstatus="notcompleted",
                    dispType="upcoming")
        data = urllib.urlopen(url, urllib.urlencode(args))
        data = data.read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def milestones(self, portal_name, projid, format="json", dic=False):
        url = "http://projects.zoho.com/portal/%s/api/private/%s/mss?apikey=%s&ticket=%s"
        url = url % (portal_name, format, self.api_key, self.ticket)
        args = dict(projId=projid,
                    flag="allflag",
                    status="notcompleted",
                    matchcrit="upcoming")
        data = urllib.urlopen(url, urllib.urlencode(args))
        data = data.read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format is "xml":
            return data

    def meetings(self, portal_name, projid, format="json", dic=False):
        url = "http://projects.zoho.com/portal/%s/api/private/%s/meetings?apikey=%s&ticket=%s"
        url = url % (portal_name, format, self.api_key, self.ticket)
        args = dict(projId=projid,
                    state="open")
        data = urllib.urlopen(url, urllib.urlencode(args)).read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def documents(self, portal_name, projid, format="json", dic=False):
        url = "http://projects.zoho.com/portal/%s/api/private/%s/docs?apikey=%s&ticket=%s"
        url = url % (portal_name, format, self.api_key, self.ticket)
        args = dict(projId=projid)
        data = urllib.urlopen(url, urllib.urlencode(args)).read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data

    def get_user_status(self, portal_name, projid, format="json", dic=False):
        url = "http://projects.zoho.com/portal/%s/api/private/%s/dashbs/getstatmesg?apikey=%s&ticket=%s"
        url = url % (portal_name, format, self.api_key, self.ticket)
        args = dict(projId=projid)
        data = urllib.urlopen(url, urllib.urlencode(args)).read()

        if format in "json":
            if dic:
                return json.loads(data)
            else:
                return data
        elif format in "xml":
            return data