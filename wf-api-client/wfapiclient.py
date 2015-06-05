""" wfapiclient - WebFaction API Client module
    
    A local client for interfacing to the WebFaction web hosting server API.
    It provides class-based organization, convenience methods, script execution,
    and run reporting.
    
    Can be used as standalone module to execute a supplied script file or as an 
    imported module within individual script files.
    
    Provides HTML-formatted results reports.
"""

from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import os.path
import inspect
import argparse
from io import open
from datetime import datetime
from collections import OrderedDict

try:
    import xmlrpclib as _xmlrpc
except ImportError:
    import xmlrpc.client as _xmlrpc

if sys.version_info < (3,):
    #define python2-compatible string function
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
    
    #define python2-compatible string comparators
    text_type = unicode
    binary_type = str
else:
    #define python3-compatible string function
    def u(x):
        return x
    
    #define python3-compatible string comparators
    text_type = str
    binary_type = bytes
#/python version checks


BLANK_STR = u("")
COMMA_SEP = u(", ")
SUCCESS = u("success")
FAILURE = u("failure")

API_URL = u("https://api.webfaction.com/")

HTML_START = u("""
<!DOCTYPE html>
<html>
  <head>
    <title>WebFaction API Run Results</title>
    <style>ul#results {border: 2px ridge maroon; background-color: #ffffcc; padding: 0.25em 1.5em; margin-left: 0;}
           li.success {color: #006400;}
           li.failure {color: #dc143c; text-decoration: line-through;}
    </style>
  </head>
  <body>
    <h1>WebFaction API Run Results</h1>
    <ul id="results">
""")

HTML_END = u("""    
    </ul>
  </body>
</html>
""")



def already_exists(key, value, items):
    """
    Checks for existence of `value` for `key` in dictionary `items`.
    """
    _exists = False
    for item in items:
        if (key in item and item[key] == value):
            _exists = True
    return _exists
#/already_exists


class Mailbox(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_mailboxes(self):
        return self._server.list_mailboxes(self._session_id)
    #/list_mailboxes
    
    
    def create_mailbox(self,
                       mailbox=BLANK_STR,
                       enable_spam_protection=True,
                       discard_spam=False,
                       spam_redirect_folder=BLANK_STR,
                       use_manual_procmailrc=False,
                       manual_procmailrc=BLANK_STR,
                       inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_mailboxes = self.list_mailboxes()
        if not already_exists(u('name'), mailbox, _existing_mailboxes):
            try:
                self._result = self._server.create_mailbox(self._session_id, 
                                                           mailbox, 
                                                           enable_spam_protection, 
                                                           discard_spam, 
                                                           spam_redirect_folder, 
                                                           use_manual_procmailrc, 
                                                           manual_procmail)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #mailbox already in _existing_mailboxes
            _msg = u("Can't create Mailbox '{}' that already exists.").format(mailbox)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_mailbox
    
    
    def delete_mailbox(self,
                       mailbox=BLANK_STR,
                       inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_mailboxes = self.list_mailboxes()
        if already_exists(u('name'), mailbox, _existing_mailboxes):
            try:
                self._result = self._server.delete_mailbox(self._session_id, 
                                                           mailbox)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #mailbox not already in _existing_mailboxes
            _msg = u("Can't delete non-existent '{}' Mailbox.").format(mailbox)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_mailbox
    
    
    def update_mailbox(self,
                       mailbox=BLANK_STR,
                       enable_spam_protection=True,
                       discard_spam=False,
                       spam_redirect_folder=BLANK_STR,
                       use_manual_procmailrc=False,
                       manual_procmailrc=BLANK_STR,
                       inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_mailboxes = self.list_mailboxes()
        if already_exists(u('name'), mailbox, _existing_mailboxes):
            try:
                self._result = self._server.update_mailbox(self._session_id, 
                                                           mailbox, 
                                                           enable_spam_protection, 
                                                           discard_spam, 
                                                           spam_redirect_folder, 
                                                           use_manual_procmailrc, 
                                                           manual_procmail)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #mailbox not already in _existing_mailboxes
            _msg = u("Can't update non-existent '{}' Mailbox.").format(mailbox)
            self._runner.log(CALLER, FAILURE, _msg)
    #/update_mailbox
    
    
    def change_mailbox_password(self,
                                mailbox=BLANK_STR,
                                password=BLANK_STR,
                                inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_mailboxes = self.list_mailboxes()
        if already_exists(u('mailbox'), mailbox, _existing_mailboxes):
            try:
                self._result = self._server.change_mailbox_password(self._session_id, 
                                                                    mailbox, 
                                                                    password)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: # try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #mailbox not already in _existing_mailboxes
            _msg = u("Can't change password for non-existent '{}' mailbox.").format(mailbox)
            self._runner.log(CALLER, FAILURE, _msg)
    #/change_mailbox_password

#/Mailbox



class Email(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_emails(self):
        return self._server.list_emails(self._session_id)
    #/list_emails
    
    
    def create_email(self,
                     email_address=BLANK_STR,
                     targets=BLANK_STR,
                     autoresponder_on=False,
                     autoresponder_subject = BLANK_STR,
                     autoresponder_message=BLANK_STR,
                     autoresponder_from=BLANK_STR,
                     script_machine=BLANK_STR,
                     script_path=BLANK_STR,
                     inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_emails = self.list_emails()
        if not already_exists(u('email_address'), email_address, _existing_emails):
            try:
                self._result = self._server.create_email(self._session_id, 
                                                         email_address, 
                                                         targets, 
                                                         autoresponder_on, 
                                                         autoresponder_subject, 
                                                         autoresponder_message, 
                                                         autoresponder_from, 
                                                         script_machine, 
                                                         script_path)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #email_address already in _existing_emails
            _msg = u("Can't create mail address '{}' that already exists.").format(email_address)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_email
    
    
    def create_emails(self,
                      domain=BLANK_STR,
                      prefixes=None,
                      targets=BLANK_STR,
                      inspect=inspect):
        
        self._prefixes = []
        _std_prefixes = [u('www'),
                         u('admin'),
                         u('webmaster'),
                         u('postmaster'),
                         u('hostmaster'),
                         u('info'),
                         u('sales'),
                         u('marketing'),
                         u('support'),
                         u('abuse')]
        
        if prefixes is None:
            self._prefixes = _std_prefixes
        else:
            self._prefixes = prefixes
        
        for _prefix in self._prefixes:
            _email_address = _prefix + u("@") + domain
            self.create_email(_email_address, targets)
    #/create_emails
    
    
    def delete_email(self,
                     email_address=BLANK_STR,
                     inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_emails = self.list_emails()
        if already_exists(u('email_address'), email_address, _existing_emails):
            try:
                self._result = self._server.delete_email(self._session_id, 
                                                         email_address)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #email_address not already in _existing_emails
            _msg = u("Can't delete non-existent '{}' email address.").format(email_address)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_email
    
    
    def delete_emails(self,
                      domain=BLANK_STR,
                      prefixes=None,
                      inspect=inspect):
        
        self._prefixes = []
        _std_prefixes = [u('www'),
                         u('admin'),
                         u('webmaster'),
                         u('postmaster'),
                         u('hostmaster'),
                         u('info'),
                         u('sales'),
                         u('marketing'),
                         u('support'),
                         u('abuse')]
        
        if prefixes is None:
            self._prefixes = _std_prefixes
        else:
            self._prefixes = prefixes
        
        for _prefix in self._prefixes:
            _email_address = _prefix + u("@") + domain
            self.delete_email(_email_address)
    #/delete_emails
    
    
    def update_email(self,
                     email_address=BLANK_STR,
                     targets=None,
                     autoresponder_on=False,
                     autoresponder_subject = BLANK_STR,
                     autoresponder_message=BLANK_STR,
                     autoresponder_from=BLANK_STR,
                     script_machine=BLANK_STR,
                     script_path=BLANK_STR,
                     inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_emails = self.list_emails()
        if already_exists(u('email_address'), self.email_address, _existing_emails):
            try:
                self._result = self._server.update_email(self._session_id, 
                                                         email_address, 
                                                         targets, 
                                                         autoresponder_on, 
                                                         autoresponder_subject, 
                                                         autoresponder_message, 
                                                         autoresponder_from, 
                                                         script_machine, 
                                                         script_path)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #email_address not already in _existing_emails
            _msg = u("Can't update non-existent '{}' email address.").format(email_addess)
            self._runner.log(CALLER, FAILURE, _msg)
    #/update_email

#/Email



class Domain(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_domains(self):
        return self._server.list_domains(self._session_id)
    #/list_domains
    
    
    def create_domain(self,
                      domain=BLANK_STR,
                      subdomain=BLANK_STR,
                      inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_domains = self.list_domains()
        if (already_exists(u('domain'), domain, _existing_domains) and
            already_exists(u('subdomain'), subdomain, _existing_domains)):
            try:
                self._result = self._server.create_domain(self._session_id, 
                                                          domain, 
                                                          subdomain)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #domain or subdomain already in _existing_domains
            _msg = u("Can't create domain '{0}' or subdomain '{1}' that already exists.").format(domain, subdomain)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_domain
    
    
    def delete_domain(self,
                      domain=BLANK_STR,
                      subdomain=BLANK_STR,
                      inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_domains = self.list_domains()
        if not (already_exists(u('domain'), domain, _existing_domains) and
                already_exists(u('subdomain'), subdomain, _existing_domains)):
            try:
                self._result = self._server.delete_domain(self._session_id, 
                                                          domain, 
                                                          subdomain)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #domain or subdomain already in _existing_domains
            _msg = u("Can't delete non-existent '{0}' domain or '{1}' subdomain.").format(domain, subdomain)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_domain

#/Domain

    
    
class Website(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_websites(self):
        return self._server.list_websites(self._session_id)
    #/list_websites
    
    
    def list_bandwidth_usage(self):
        return self._server.list_bandwidth_usage(self._session_id)
    #/list_bandwidth_usage
    
    
    def create_website(self,
                       website_name=BLANK_STR,
                       ip=BLANK_STR,
                       https=False,
                       subdomains=BLANK_STR,
                       site_apps=None,
                       inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_websites = self.list_websites()
        if not already_exists(u('name'), website, _existing_websites):
            try:
                self._result = self._server.create_website(self._session_id, 
                                                           website_name, 
                                                           ip, 
                                                           https, 
                                                           subdomains, 
                                                           site_apps)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #website already in _existing_websites
            _msg = u("Can't create website '{}' that already exists.").format(website)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_website
    
    
    def delete_website(self,
                       website_name=BLANK_STR,
                       ip=BLANK_STR,
                       https=False,
                       inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_websites = self.list_websites()
        if not already_exists(u('name'), website, _existing_websites):
            try:
                self._result = self._server.delete_website(self._session_id, 
                                                           website_name, 
                                                           ip, 
                                                           https)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #website already in _existing_websites
            _msg = u("Can't delete non-existent '{}' website.").format(website)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_website
    
    
    def update_website(self,
                       website_name=BLANK_STR,
                       ip=BLANK_STR,
                       https=False,
                       subdomains=None,
                       site_apps=None,
                       inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_websites = self.list_websites()
        if not already_exists(u('name'), website, _existing_websites):
            try:
                self._result = self._server.create_website(self._session_id, 
                                                           website_name, 
                                                           ip, 
                                                           https, 
                                                           subdomains, 
                                                           site_apps)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #website already in _existing_websites
            _msg = u("Can't update non-existent '{}' website.").format(website)
            self._runner.log(CALLER, FAILURE, _msg)
    #/update_website

#/Website



class Application(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_apps(self):
        return self._server.list_apps(self._session_id)
    #/list_apps
    
    
    def list_app_types(self):
        return self._server.list_app_types(self._session_id)
    #/list_app_types
    
    
    def create_app(self,
                   name=BLANK_STR,
                   type=BLANK_STR,
                   autostart=False,
                   extra_info=BLANK_STR,
                   open_port=False,
                   inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_apps = self.list_apps()
        if already_exists(u('name'), name, _existing_apps):
            try:
                self._result = self._server.create_app(self._session_id, 
                                                       name, 
                                                       type, 
                                                       autostart, 
                                                       extra_info, 
                                                       open_port)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, FAILURE, self._result)
        else: #name already in _existing_apps
            _msg = u("Can't create application '{}' that already exists.").format(name)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_app
    
    
    def delete_app(self,
                   name=BLANK_STR,
                   inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_apps = self.list_apps()
        if not already_exists(u('name'), name, _existing_apps):
            try:
                self._result = self._server.create_app(self._session_id, 
                                                       name)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #name already in _existing_apps
            _msg = u("Can't delete non-existent '{}' application.").format(name)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_app

#/Application



class Cron(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def create_cron_job(self,
                        line=BLANK_STR,
                        inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        try:
            self._result = self._server.create_cron_job(self._session_id, 
                                                        line)
        except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
        except _xmlrpc.ProtocolError as error:
            _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
            self._runner.log(CALLER, FAILURE, _error)
        else: #try succeeded
            self._runner.log(CALLER, SUCCESS, self._result)
    #/create_cron_job
    
    
    def delete_cron_job(self,
                        line=BLANK_STR,
                        inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        try:
            self._result = self._server.delete_cron_job(self._session_id, 
                                                        line)
        except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
        except _xmlrpc.ProtocolError as error:
            _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
            self._runner.log(CALLER, FAILURE, _error)
        else: #try succeeded
            self._runner.log(CALLER, SUCCESS, self._result)
    #/delete_cron_job

#/Cron



class DNS(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_dns_overrides(self):
        return _server.list_dns_overrides(self._session_id)
    #/list_dns_overrides
    
    
    def create_dns_override(self,
                            domain=BLANK_STR,
                            a_ip=BLANK_STR,
                            cname=BLANK_STR,
                            mx_name=BLANK_STR,
                            mx_priority=BLANK_STR,
                            spf_record=BLANK_STR,
                            aaaa_ip=BLANK_STR,
                            inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_dns_overrides = self.list_dns_overrides()
        if already_exists(u('domain'), domain, _existing_dns_overrides):
            try:
                self._result = self._server.create_dns_override(self._session_id, 
                                                                domain, 
                                                                a_ip, 
                                                                cname, 
                                                                mx_name, 
                                                                mx_priority, 
                                                                spf_record, 
                                                                aaaa_ip)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #domain already in _existing_dns_overrides
            _msg = u("Can't create DNS override '{}' that already exists.").format(domain)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_dns_override
    
    
    def delete_dns_override(self,
                            domain=BLANK_STR,
                            a_ip=BLANK_STR,
                            cname=BLANK_STR,
                            mx_name=BLANK_STR,
                            mx_priority=BLANK_STR,
                            spf_record=BLANK_STR,
                            aaaa_ip=BLANK_STR,
                            inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_dns_overrides = self.list_dns_overrides()
        if not already_exists(u('domain'), domain, _existing_dns_overrides):
            try:
                self._result = self._server.create_dns_override(self._session_id, 
                                                                domain, 
                                                                a_ip, 
                                                                cname, 
                                                                mx_name, 
                                                                mx_priority, 
                                                                spf_record, 
                                                                aaaa_ip)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #domain already in _existing_dns_overrides
            _msg = u("Can't delete non-existent '{}' DNS override.").format(domain)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_dns_override
    
#/DNS



class Database(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_dbs(self):
        return self._server.list_dbs(self._session_id)
    #/list_dbs
    
    
    def list_db_users(self):
        return self._server.list_db_users(self._session_id)
    #/list_db_users
    
    
    def create_db(self,
                  name=BLANK_STR,
                  db_type=BLANK_STR,
                  password=BLANK_STR,
                  inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_databases = self.list_databases()
        if already_exists(u('name'), name, _existing_databases):
            try:
                self._result = self._server.create_db(self._session_id, 
                                                      name, 
                                                      db_type, 
                                                      password)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #name already in _existing_databases
            _msg = u("Can't create database '{}' that already exists.").format(name)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_db
    
    
    def delete_db(self,
                  name=BLANK_STR,
                  db_type=BLANK_STR,
                  inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_databases = self.list_databases()
        if not already_exists(u('name'), name, _existing_databases):
            try:
                self._result = self._server.create_db(self._session_id, 
                                                      name, 
                                                      db_type, 
                                                      password)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #name not already in _existing_databases
            _msg = u("Can't delete non-existent '{}' database.").format(name)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_db
    
    
    def create_db_user(self,
                       username=BLANK_STR,
                       password=BLANK_STR,
                       db_type=BLANK_STR,
                       inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_database_users = self.list_database_users()
        if already_exists(u('username'), username, _existing_database_users):
            try:
                self._result = self._server.create_db_user(self._session_id, 
                                                           username, 
                                                           password, 
                                                           db_type)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #username already in _existing_database_users
            _msg = u("Can't create database user '{}' that already exists.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_db_user
    
    
    def delete_db_user(self,
                       username=BLANK_STR,
                       db_type=BLANK_STR,
                       inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_database_users = self.list_database_users()
        if not already_exists(u('username'), username, _existing_database_users):
            try:
                self._result = self._server.delete_db_user(self._session_id, 
                                                           username, 
                                                           db_type)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #username already in _existing_database_users
            _msg = u("Can't delete non-existent '{}' database user.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_db_user
    
    
    def change_db_user_password(self,
                                username=BLANK_STR,
                                password=BLANK_STR,
                                db_type=BLANK_STR,
                                inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_database_users = self.list_database_users()
        if already_exists(u('username'), username, _existing_database_users):
            try:
                self._result = self._server.change_db_user_password(self._session_id, 
                                                                    username, 
                                                                    password, 
                                                                    db_type)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #username not already in _existing_database_users
            _msg = u("Can't change password for non-existent '{}' database user.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/change_db_user_password
    
    
    def make_user_owner_of_db(self,
                              username=BLANK_STR,
                              database=BLANK_STR,
                              db_type=BLANK_STR,
                              inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_database_users = self.list_database_users()
        if already_exists(u('username'), username, _existing_database_users):
            try:
                self._result = self._server.change_db_user_password(self._session_id, 
                                                                    username, 
                                                                    password, 
                                                                    db_type)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #username not already in _existing_database_users
            _msg = u("Can't change password for non-existent '{}' database user.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/make_user_owner_of_db
    
    
    def grant_db_permissions(self,
                             username=BLANK_STR,
                             database=BLANK_STR,
                             db_type=BLANK_STR,
                             inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_database_users = self.list_database_users()
        if already_exists(u('username'), username, _existing_database_users):
            try:
                self._result = self._server.grant_db_permissions(self._session_id, 
                                                                 username, 
                                                                 database, 
                                                                 db_type)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #username not already in _existing_database_users
            _msg = u("Can't grant permission for non-existent '{}' database user.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/grant_db_permissions
    
    
    def revoke_db_permissions(self,
                              username=BLANK_STR,
                              database=BLANK_STR,
                              db_type=BLANK_STR,
                              inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_database_users = self.list_database_users()
        if already_exists(u('username'), username, _existing_database_users):
            try:
                self._result = self._server.grant_db_permissions(self._session_id, 
                                                                 username, 
                                                                 password, 
                                                                 db_type)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, FAILURE, self._result)
        else: #username not already in _existing_database_users
            _msg = u("Can't revoke permission for non-existent '{}' database user.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/revoke_db_permissions
    
    
    def enable_addon(self,
                     database=BLANK_STR,
                     db_type=BLANK_STR,
                     addon=BLANK_STR,
                     inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_databases = self.list_databases()
        if already_exists(u('database'), database, _existing_databases):
            try:
                self._result = self._server.enable_addon(self._session_id, 
                                                         database, 
                                                         db_type, 
                                                         addon)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #database not already in _existing_databases
            _msg = u("Can't enable addon for non-existent '{}' database.").format(database)
            self._runner.log(CALLER, FAILURE, _msg)
    #/enable_addon
    
#/Database



class File(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def replace_in_file(self,
                        filename=BLANK_STR,
                        changes=None,
                        inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        try:
            self._result = self._server.replace_in_file(self._session_id, 
                                                        filename, 
                                                        changes)
        except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
        except _xmlrpc.ProtocolError as error:
            _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
            self._runner.log(CALLER, FAILURE, _error)
        else: #try succeeded
            self._runner.log(CALLER, SUCCESS, self._result)
    #/replace_in_file
    
    
    def write_file(self,
                   filename=BLANK_STR,
                   string=BLANK_STR,
                   mode=BLANK_STR,
                   inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        try:
            self._result = self._server.write_file(self._session_id, 
                                                   filename, 
                                                   string, 
                                                   mode)
        except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
        except _xmlrpc.ProtocolError as error:
            _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
            self._runner.log(CALLER, FAILURE, _error)
        else: #try succeeded
            self._runner.log(CALLER, SUCCESS, self._result)
    #/write_file

#/File



class ShellUser(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_users(self):
        return self._server.list_users(self._session_id)
    #/list_users
    
    
    def create_user(self,
                    username=BLANK_STR,
                    shell=BLANK_STR,
                    groups=None,
                    inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_shellusers = self.list_users()
        if not already_exists(u('username'), username, _existing_shellusers):
            try:
                self._result = self._server.create_user(self._session_id, 
                                                        username, 
                                                        shell, 
                                                        groups)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #username already in _existing_shellusers
            _msg = u("Can't create already existing '{}' shell user.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/create_user
    
    
    def delete_user(self,
                    username=BLANK_STR,
                    inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_shellusers = self.list_users()
        if already_exists(u('username'), username, _existing_shellusers):
            try:
                self._result = self._server.delete_user(self._session_id, 
                                                        username)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #username not already in _existing_shellusers
            _msg = u("Can't delete non-existent '{}' shell user.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/delete_user
    
    
    def change_user_password(self,
                             username=BLANK_STR,
                             password=BLANK_STR,
                             inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        _existing_shellusers = self.list_users()
        if already_exists(u('username'), username, _existing_shellusers):
            try:
                self._result = self._server.change_user_password(self._session_id, 
                                                                 username, 
                                                                 password)
            except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
            except _xmlrpc.ProtocolError as error:
                _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
                self._runner.log(CALLER, FAILURE, _error)
            else: #try succeeded
                self._runner.log(CALLER, SUCCESS, self._result)
        else: #username not already in _existing_shellusers
            _msg = u("Can't change password for non-existent '{}' shell user.").format(username)
            self._runner.log(CALLER, FAILURE, _msg)
    #/change_user_password

#/ShellUser



class Server(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_ips(self):
        return self._server.list_ips(self._session_id)
    #/list_ips
    
    
    def list_machines(self):
        return self._server.list_machines(self._session_id)
    #/list_machines

#/Server



class System(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def system(self,
               cmd,
               inspect=inspect):
        
        CALLER = inspect.getframeinfo(inspect.currentframe()).function.upper()
        self._result = OrderedDict()
        
        try:
            self._result = self._server.system(self._session_id,
                                               cmd)
        except _xmlrpc.Fault as fault:
                _fault = COMMA_SEP.join([fault.faultCode, fault.faultString])
                self._runner.log(CALLER, FAILURE, _fault)
        except _xmlrpc.ProtocolError as error:
            _error = COMMA_SEP.join([error.url, error.errcode, error.errmsg])
            self._runner.log(CALLER, FAILURE, _error)
        else:
            self._runner.log(CALLER, SUCCESS, self._result)
    #/system

#/System

class Runner(object):
    """
    Class that logs an execution result for each server call and reports the 
    full session results in HTML format.
    """
    
    
    def __init__(self):
        self._run_results = OrderedDict()
        self._run_results[SUCCESS] = []
        self._run_results[FAILURE] = []
        self._server = None
        self._session_id = BLANK_STR
        self._account = None
    #/__init__
    
    
    @property
    def server(self):
        return self._server
    
    @property
    def session_id(self):
        return self._session_id
    
    @property
    def account(self):
        return self._account
    
    
    def login_to_server(self, _username, _password):
        """
        Logs in to server using `_username` and `_password` and sets session variables.
        """
        
        self._server = _xmlrpc.ServerProxy(API_URL)
        self._session_id, _account = self._server.login(_username, _password)
        
        print(_account)
    #/login_to_server
    
    
    def log(self, _caller, _key, _result, datetime=datetime):
        """
        Logs individual execution result for a server call.
        """
        _result = [text_type(datetime.now()) + u(" | ") + _caller + u(" | ")] + [_result]
        self._run_results[_key].append(_result)
    #/log
    
    
    def enquote(self, _str):
        """
        Wraps string in single-quotes.
        """
        return u("'") + _str + u("'")
    #/enquote
    
    
    def collapse_dict_to_list(self, _dict):
        """
        Collapses a dictionary into a list by concatenating each key/value pair 
        into a string.
        """
        _list = []
        for k, v in _dict.items():
            _list.append(u(": ").join([self.enquote(text_type(k)),
                                        self.enquote(text_type(v))]))
        return _list
    #/collapse_dict_to_list
    
    
    def collapse_list_to_str(self, _list):
        """
        Collapses a list of strings into one string of comma-separated items.
        """
        _str = BLANK_STR
        _str = COMMA_SEP.join(_list)
        return _str
    #/collapse_list_to_str
    
    
    def process_results(self, _results):
        """
        Processes a dictionary of execution result lists into string 
        representations wrapped in the HTML needed to create <li> nodes.
        """
        _html = "      "
        for result_type, results_list in _results.items():
            for result_list in results_list:
                _li = BLANK_STR
                for result in result_list:
                    _list = []
                    _str = BLANK_STR
                    if isinstance(result, dict):
                        _list = self.collapse_dict_to_list(result)
                        _str = self.collapse_list_to_str(_list)
                    elif isinstance(result, list):
                        _str = self.collapse_list_to_str(_list)
                    elif isinstance(result, text_type):
                        _str = result
                    elif result is None:
                        _str = self.enquote(u("None"))
                    else:
                        _str = self.enquote(u("unknown!"))
                    
                    _li += _str
                _html += u("<li class='") + result_type + u("'>") + _li + u("</li>")
        return _html
    #/process_results
    
    
    def report(self):
        """
        Constructs an HTML report of execution results.
        """
        global HTML_START, HTML_END
        
        html_report = self.process_results(self._run_results)
        return HTML_START + html_report + HTML_END
    #/report
    
    
    def read_script_from_file(self, _script_file):
        try:
            with open(_script_file, u('r')) as _script_source:
                _script_code = compile(_script_source.read(), _script_file, u('exec'))
                exec(_script_code)
        except (OSError, IOError) as e:
            print(u("Error opening script file."))
    #/read_script_from_file
    
    
    def write_report_to_file(self, _report_file):
        try:
            with open(_report_file, u('a')) as _report_target:
                _report_target.write(self.report())
        except (OSError, IOError) as e:
            print(u("Error writing report file."))
    #/write_report_to_file
    
#/Runner


def main():
    """
    Parses arguments and handles file IO if specified.
    """
    
    parser = argparse.ArgumentParser(description=u("A robust client to the WebFaction server API."))
    
    parser.add_argument(u("username"), help=u("The WebFaction server control panel username."))
    parser.add_argument(u("password"), help=u("The WebFaction server control panel password."))
    parser.add_argument(u("--scriptfile"), help=u("File of scripted commands to execute."))
    parser.add_argument(u("--reportfile"), help=u("File into which to write run results."))
    
    args = parser.parse_args()
    
    runner = Runner()
    
    runner.login_to_server(args.username, args.password)
    
    if args.scriptfile:
        _script_file = os.path.normpath(args.scriptfile)
        runner.read_script_from_file(_script_file)
    
    if args.reportfile:
        _report_file = os.path.normpath(args.reportfile)
        runner.write_report_to_file(_report_file)
#/main


if __name__ == u("__main__"):
    main()

#/EOF