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

if sys.version_info < (3,):
    #Import compatible xmlrpc library.
    import xmlrpclib as _xmlrpc
    
    #Import python2-compatible collections Iterable.
    from collections import Iterable as _Iterable
    
    #Define python2-compatible string function.
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
    
    #Define python2-compatible string comparators.
    text_type = unicode
    binary_type = str    
else:
    #Import python3-compatible xmlrpc library.
    import xmlrpc.client as _xmlrpc
    
    #Import python3-compatible collections Iterable.
    from collections.abc import Iterable as _Iterable
    
    #Define python3-compatible string function.
    def u(x):
        return x
    
    #Define python3-compatible string comparators.
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



def get_frame_name(_frame):
    return inspect.getframeinfo(_frame).function.upper()
#/get_frame_name


def get_arguments(_frame, inspect=inspect):
    """
    Inspects the calling signature of the passed `function` and retrieves the 
    corresponding `argument` for each parameter in its `parameters`.
    """
    _arguments = []
    
    _frame_information = inspect.getargvalues(_frame)
    _parameters = _frame_information[0][1:]
    _signature = _frame_information[3]
    
    for _parameter in _parameters:
        _argument = _signature[_parameter]
        if isinstance(_argument, text_type):
            _arguments.append(u(_argument))
        else:
            _arguments.append(_argument)
    
    return _arguments
#/get_arguments


def enquote(string):
    """
    Wraps string in single-quotes.
    """
    return u("'") + string + u("'")
#/enquote


def concatenate_list_to_string(list):
    """
    Collapses a list of strings into one string of comma-separated items.
    """
    _string = BLANK_STR
    
    list = [text_type(_item) for _item in list]
    _string = COMMA_SEP.join(list)
    
    return _string
#/concatenate_list_to_string


def flatten_iterable(iterable,
                     string_sep=None,
                     split_word=False,
                     iterable_type=_Iterable):
    """
    Flattens any iterable type, other than a file, into a sequence of items. 
    Must be called by casting to a container type, e.g.,
        `list_sequence = list(flatten_iterable(collection))`.
    Strings can be further manipulated by providing a string separator to split
    lines, or by providing a split word directive to continue splitting words 
    down to letters.
    """
    if isinstance(iterable, dict): #Dictionary.
        for _value in iterable.values(): #Iterate values, not keys.
            if isinstance(_value, iterable_type):
                for _item in flatten_iterable(_value,
                                               string_sep=string_sep,
                                               split_word=split_word,
                                               iterable_type=_Iterable):
                    yield _item #Return next iterable item.
            else:
                yield _value #Return next dictionary value.
    elif isinstance(iterable, text_type): #String.
        if string_sep is not None: #Optionally, split lines into words.
            for _word in iterable.split(string_sep):
                if split_word: #Optionally, split word into letters.
                    for _letter in _word:
                        yield _letter #Return next letter.
                else:
                    yield _word #Return next word.
        else:
            yield iterable # Return next line.
    elif (isinstance(iterable, list) or
          isinstance(iterable, tuple) or
          isinstance(iterable, set)): #List, tuple, or set.
        for _item in iterable:
            if isinstance(_item, iterable_type):
                for _subitem in flatten_iterable(_item,
                                                  string_sep=string_sep,
                                                  split_word=split_word,
                                                  iterable_type=_Iterable):
                    yield _subitem #Return next iterable item.
            else:
                yield _item #String, most likely.
    else:
        yield iterable #Item was not iterable, so just return it.
#/flatten_iterable


def already_exists(candidate, returned_api_collection):
    """
    Checks for existence of one `candidate` set of key, value pairs within one 
    and only one `_dictionary` within a `returned_api_collection` list of 
    dictionaries returned by an API list call.
    """
    _exists = []
    
    for _dictionary in returned_api_collection:
        _subgroup = set(flatten_iterable(candidate))
        _group = set(flatten_iterable(_dictionary))
        if _subgroup.issubset(_group):
            _exists.append(True)
    
    return _exists.count(True) == 1
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
                       manual_procmailrc=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't create Mailbox '{}' that already exists."
        _existing_mailboxes = self.list_mailboxes()
        _mailbox = {u('mailbox'): mailbox}
        
        if not already_exists(_mailbox, _existing_mailboxes):
            self._runner.try_api_call(_caller,
                                      self._server.create_mailbox,
                                      _arguments)
        else: #_mailbox already in _existing_mailboxes
            self._runner.log(_caller, FAILURE, u(_msg).format(mailbox))
    #/create_mailbox
    
    
    def delete_mailbox(self,
                       mailbox=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't delete non-existent '{}' Mailbox."
        _existing_mailboxes = self.list_mailboxes()
        _mailbox = {u('mailbox'): mailbox}
        
        if already_exists(_mailbox, _existing_mailboxes):
            self._runner.try_api_call(_caller,
                                      self._server.delete_mailbox,
                                      _arguments)
        else: #_mailbox not already in _existing_mailboxes
            self._runner.log(_caller, FAILURE, u(_msg).format(mailbox))
    #/delete_mailbox
    
    
    def update_mailbox(self,
                       mailbox=BLANK_STR,
                       enable_spam_protection=True,
                       discard_spam=False,
                       spam_redirect_folder=BLANK_STR,
                       use_manual_procmailrc=False,
                       manual_procmailrc=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't update non-existent '{}' Mailbox."
        _existing_mailboxes = self.list_mailboxes()
        _mailbox = {u('mailbox'): mailbox}
        
        if already_exists(_mailbox, _existing_mailboxes):
            self._runner.try_api_call(_caller,
                                      self._server.update_mailbox,
                                      _arguments)
        else: #_mailbox not already in _existing_mailboxes
            self._runner.log(_caller, FAILURE, u(_msg).format(mailbox))
    #/update_mailbox
    
    
    def change_mailbox_password(self,
                                mailbox=BLANK_STR,
                                password=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't change password for non-existent '{}' mailbox."
        _existing_mailboxes = self.list_mailboxes()
        _mailbox = {u('mailbox'): mailbox}
        
        if already_exists(_mailbox, _existing_mailboxes):
            self._runner.try_api_call(_caller,
                                      self._server.change_mailbox_password,
                                      _arguments)
        else: #_mailbox not already in _existing_mailboxes
            self._runner.log(_caller, FAILURE, u(_msg).format(mailbox))
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
                     targets=[],
                     autoresponder_on=False,
                     autoresponder_subject = BLANK_STR,
                     autoresponder_message=BLANK_STR,
                     autoresponder_from=BLANK_STR,
                     script_machine=BLANK_STR,
                     script_path=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't create mail address '{}' that already exists."
        _existing_email_addresses = self.list_emails()
        _email_address = {u('email_address'): email_address}
        
        if not already_exists(_email_address, _existing_email_addresses):
            _arguments[1] = u(", ").join(_arguments[1])
            self._runner.try_api_call(_caller,
                                      self._server.create_email,
                                      _arguments)
        else: #_email_address already in _existing_email_addresses
            self._runner.log(_caller, FAILURE, u(_msg).format(email_address))
    #/create_email
    
    
    def create_emails(self,
                      domain=BLANK_STR,
                      prefixes=None,
                      targets=BLANK_STR):
        
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
                     email_address=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't delete non-existent '{}' email address."
        _existing_email_addresses = self.list_emails()
        _email_address = {u('email_address'): email_address}
        
        if already_exists(_email_address, _existing_email_addresses):
            self._runner.try_api_call(_caller,
                                      self._server.delete_email,
                                      _arguments)
        else: #_email_address not already in _existing_email_addresses
            self._runner.log(_caller, FAILURE, u(_msg).format(email_address))
    #/delete_email
    
    
    def delete_emails(self,
                      domain=BLANK_STR,
                      prefixes=None):
        
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
                     targets=[],
                     autoresponder_on=False,
                     autoresponder_subject = BLANK_STR,
                     autoresponder_message=BLANK_STR,
                     autoresponder_from=BLANK_STR,
                     script_machine=BLANK_STR,
                     script_path=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _arguments[1] = u(", ").join(_arguments[1])
        _msg = "Can't update non-existent '{}' email address."
        _existing_email_addresses = self.list_emails()
        _email_address = {u('email_address'): email_address}
        
        if already_exists(_email_address, _existing_email_addresses):
            self._runner.try_api_call(_caller,
                                      self._server.update_email,
                                      _arguments)
        else: #_email_address not already in _existing_email_addresses
            self._runner.log(_caller, FAILURE, u(_msg).format(email_address))
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
                      subdomain=[]):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _subdomains = _arguments.pop(-1)
        
        for _subdomain in _subdomains:
            _arguments.append(_subdomain)
        self._runner.try_api_call(_caller,
                                  self._server.create_domain,
                                  _arguments)
    #/create_domain
    
    
    def delete_domain(self,
                      domain=BLANK_STR,
                      subdomain=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _subdomains = _arguments.pop(-1)
        
        for _subdomain in _subdomains:
            _arguments.append(_subdomain)
        self._runner.try_api_call(_caller,
                                  self._server.delete_domain,
                                  _arguments)
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
                       subdomains=[],
                       site_apps=[]):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't create website '{}' that already exists."
        _existing_websites = self.list_websites()
        _website_name = {u('website_name'): website_name}
        
        if not already_exists(_website_name, _existing_websites):
            self._runner.try_api_call(_caller,
                                      self._server.create_website,
                                      _arguments)
        else: #_website_name already in _existing_websites
            self._runner.log(_caller, FAILURE, u(_msg).format(website_name))
    #/create_website
    
    
    def delete_website(self,
                       website_name=BLANK_STR,
                       ip=BLANK_STR,
                       https=False):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't delete non-existent '{}' website."
        _existing_websites = self.list_websites()
        _website_name = {u('website_name'): website_name}
        
        if already_exists(_website_name, _existing_websites):
            self._runner.try_api_call(_caller,
                                      self._server.delete_website,
                                      _arguments)
        else: #_website_name not already in _existing_websites
            self._runner.log(_caller, FAILURE, u(_msg).format(website_name))
    #/delete_website
    
    
    def update_website(self,
                       website_name=BLANK_STR,
                       ip=BLANK_STR,
                       https=False,
                       subdomains=[],
                       site_apps=[]):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't update non-existent '{}' website."
        _existing_websites = self.list_websites()
        _website_name = {u('website_name'): website_name}
        
        if already_exists(_website_name, _existing_websites):
            self._runner.try_api_call(_caller,
                                      self._server.update_website,
                                      _arguments)
        else: #_website_name not already in _existing_websites
            self._runner.log(_caller, FAILURE, u(_msg).format(website_name))
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
                   open_port=False):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't create application '{}' that already exists."
        _existing_apps = self.list_apps()
        _app_name = {u('name'): name}
        
        if not already_exists(_app_name, _existing_apps):
            self._runner.try_api_call(_caller,
                                      self._server.create_app,
                                      _arguments)
        else: #_app_name already in _existing_apps
            self._runner.log(_caller, FAILURE, u(_msg).format(name))
    #/create_app
    
    
    def delete_app(self,
                   name=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't delete non-existent '{}' application."
        _existing_apps = self.list_apps()
        _app_name = {u('name'): name}
        
        if already_exists(_app_name, _existing_apps):
            self._runner.try_api_call(_caller,
                                      self._server.delete_app,
                                      _arguments)
        else: #_app_name not already in _existing_apps
            self._runner.log(_caller, FAILURE, u(_msg).format(name))
    #/delete_app

#/Application



class Cron(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def create_cronjob(self,
                        line=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        
        self._runner.try_api_call(_caller,
                                  self._server.create_cronjob,
                                  _arguments)
    #/create_cronjob
    
    
    def delete_cronjob(self,
                        line=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        
        self._runner.try_api_call(_caller,
                                  self._server.delete_cronjob,
                                  _arguments)
    #/delete_cronjob

#/Cron



class DNS(object):
    def __init__(self, _runner=None):
        self._runner = _runner
        self._server = self._runner.server
        self._session_id = self._runner.session_id
    #/__init__
    
    
    def list_dns_overrides(self):
        return self._server.list_dns_overrides(self._session_id)
    #/list_dns_overrides
    
    
    def create_dns_override(self,
                            domain=BLANK_STR,
                            a_ip=BLANK_STR,
                            cname=BLANK_STR,
                            mx_name=BLANK_STR,
                            mx_priority=BLANK_STR,
                            spf_record=BLANK_STR,
                            aaaa_ip=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        
        self._runner.try_api_call(_caller,
                                  self._server.create_dns_override,
                                  _arguments)
    #/create_dns_override
    
    
    def delete_dns_override(self,
                            domain=BLANK_STR,
                            a_ip=BLANK_STR,
                            cname=BLANK_STR,
                            mx_name=BLANK_STR,
                            mx_priority=BLANK_STR,
                            spf_record=BLANK_STR,
                            aaaa_ip=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        
        self._runner.try_api_call(_caller,
                                  self._server.delete_dns_override,
                                  _arguments)
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
                  db_type=u("postgresql"),
                  password=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't create database '{}' that already exists."
        _existing_databases = self.list_dbs()
        _db_name = {u('name'): name}
        
        if not already_exists(_db_name, _existing_databases):
            self._runner.try_api_call(_caller,
                                      self._server.create_db,
                                      _arguments)
        else: #_db_name already in _existing_databases
            self._runner.log(_caller, FAILURE, u(_msg).format(name))
    #/create_db
    
    
    def delete_db(self,
                  name=BLANK_STR,
                  db_type=u("postgresql")):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't delete non-existent '{}' database."
        _existing_databases = self.list_dbs()
        _db_name = {u('name'): name}
        
        if already_exists(_db_name, _existing_databases):
            self._runner.try_api_call(_caller,
                                      self._server.delete_db,
                                      _arguments)
        else: #_db_name not already in _existing_databases
            self._runner.log(_caller, FAILURE, u(_msg).format(name))
    #/delete_db
    
    
    def create_db_user(self,
                       username=BLANK_STR,
                       password=BLANK_STR,
                       db_type=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't create database user '{}' that already exists."
        _existing_database_users = self.list_db_users()
        _db_user = {u('username'): username}
        
        if not already_exists(_db_user, _existing_database_users):
            self._runner.try_api_call(_caller,
                                      self._server.create_db_user,
                                      _arguments)
        else: #_db_user already in _existing_database_users
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
    #/create_db_user
    
    
    def delete_db_user(self,
                       username=BLANK_STR,
                       db_type=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't delete non-existent '{}' database user."
        _existing_database_users = self.list_db_users()
        _db_user = {u('username'): username}
        
        if already_exists(_db_user, _existing_database_users):
            self._runner.try_api_call(_caller,
                                      self._server.delete_db_user,
                                      _arguments)
        else: #_db_user already in _existing_database_users
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
    #/delete_db_user
    
    
    def change_db_user_password(self,
                                username=BLANK_STR,
                                password=BLANK_STR,
                                db_type=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't change password for non-existent '{}' database user."
        _existing_database_users = self.list_db_users()
        _db_user = {u('username'): username}
        
        if already_exists(_db_user, _existing_database_users):
            self._runner.try_api_call(_caller,
                                      self._server.change_db_user_password,
                                      _arguments)
        else: #_db_user not already in _existing_database_users
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
    #/change_db_user_password
    
    
    def make_user_owner_of_db(self,
                              username=BLANK_STR,
                              database=BLANK_STR,
                              db_type=u("postgresql")):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't change password for non-existent '{}' database user."
        _existing_database_users = self.list_db_users()
        _db_user = {u('username'): username}
        
        if already_exists(_db_user, _existing_database_users):
            self._runner.try_api_call(_caller,
                                      self._server.make_user_owner_of_db,
                                      _arguments)
        else: #_db_user not already in _existing_database_users
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
    #/make_user_owner_of_db
    
    
    def grant_db_permissions(self,
                             username=BLANK_STR,
                             database=BLANK_STR,
                             db_type=u("postgresql")):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't grant permission for non-existent '{}' database user."
        _existing_database_users = self.list_db_users()
        _db_user = {u('username'): username}
        
        if already_exists(_db_user, _existing_database_users):
            self._runner.try_api_call(_caller,
                                      self._server.grant_db_permissions,
                                      _arguments)
        else: #_db_user not already in _existing_database_users
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
    #/grant_db_permissions
    
    
    def revoke_db_permissions(self,
                              username=BLANK_STR,
                              database=BLANK_STR,
                              db_type=u("postgresql")):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't revoke permission for non-existent '{}' database user."
        _existing_database_users = self.list_db_users()
        _db_user = {u('username'): username}
        
        if already_exists(_db_user, _existing_database_users):
            self._runner.try_api_call(_caller,
                                      self._server.revoke_db_permissions,
                                      _arguments)
        else: #_db_user not already in _existing_database_users
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
    #/revoke_db_permissions
    
    
    def enable_addon(self,
                     database=BLANK_STR,
                     db_type=u("postgresql"),
                     addon=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't enable addon for non-existent '{}' database."
        _existing_databases = self.list_dbs()
        _database = {u('database'): database}
        
        if already_exists(_database, _existing_databases):
            self._runner.try_api_call(_caller,
                                      self._server.enable_addon,
                                      _arguments)
        else: #_database not already in _existing_databases
            self._runner.log(_caller, FAILURE, u(_msg).format(database))
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
                        changes=[]):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        
        self._runner.try_api_call(_caller,
                                  self._server.replace_in_file,
                                  _arguments)
    #/replace_in_file
    
    
    def write_file(self,
                   filename=BLANK_STR,
                   str=BLANK_STR,
                   mode=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        
        self._runner.try_api_call(_caller,
                                  self._server.write_file,
                                  _arguments)
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
                    groups=[]):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't create already existing '{}' shell user."
        _existing_shellusers = self.list_users()
        _shell_user = {u('username'): username}
        
        if not already_exists(_shell_user, _existing_shellusers):
            self._runner.try_api_call(_caller,
                                      self._server.create_user,
                                      _arguments)
        else: #_shell_user already in _existing_shellusers
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
    #/create_user
    
    
    def delete_user(self,
                    username=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't delete non-existent '{}' shell user."
        _existing_shellusers = self.list_users()
        _shell_user = {u('username'): username}
        
        if already_exists(_shell_user, _existing_shellusers):
            self._runner.try_api_call(_caller,
                                      self._server.delete_user,
                                      _arguments)
        else: #_shell_user not already in _existing_shellusers
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
    #/delete_user
    
    
    def change_user_password(self,
                             username=BLANK_STR,
                             password=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        _msg = "Can't change password for non-existent '{}' shell user."
        _existing_shellusers = self.list_users()
        _shell_user = {u('username'): username}
        
        if already_exists(_shell_user, _existing_shellusers):
            self._runner.try_api_call(_caller,
                                      self._server.change_user_password,
                                      _arguments)
        else: #_shell_user not already in _existing_shellusers
            self._runner.log(_caller, FAILURE, u(_msg).format(username))
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
               cmd=BLANK_STR):
        
        _current_frame = inspect.currentframe()
        _caller = get_frame_name(_current_frame)
        _arguments = get_arguments(_current_frame)
        
        self._runner.try_api_call(_caller,
                                  self._server.system,
                                  _arguments)
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
        Logs in to server using `_username` and `_password` and sets session 
        variables.
        """
        
        self._server = _xmlrpc.ServerProxy(API_URL)
        self._session_id, self._account = self._server.login(_username,
                                                              _password)
        
        print(u(" Logged in to server '{0}' as user '{1}'.").format(
                                                    self._account['web_server'],
                                                    self._account['username']))
    #/login_to_server
    
    
    def log(self, _caller, _key, _result, datetime=datetime):
        """
        Logs individual execution result for a server call.
        """
        _result = [text_type(datetime.now()) + u(" | ") + u(_caller) + u(" | ")] + [_result]
        self._run_results[_key].append(_result)
    #/log
    
    
    def try_api_call(self, _caller, _api_call, _args):
        """
        Calls passed API signature with passed arguments and logs results.
        """
        
        try:
            _result = _api_call(self._session_id, *_args)
        except TypeError as error:
            self.log(_caller, FAILURE, _error)
        except _xmlrpc.Fault as fault:
            _fault = COMMA_SEP.join([u(text_type(fault.faultCode)),
                                      u(text_type(fault.faultString))])
            self.log(_caller, FAILURE, _fault)
        except _xmlrpc.ProtocolError as error:
            _error = COMMA_SEP.join([u(text_type(error.url)),
                                      u(text_type(error.errcode)),
                                      u(text_type(error.errmsg))])
            self.log(_caller, FAILURE, _error)
        else: #try succeeded
            self.log(_caller, SUCCESS, _result)
    #/try_api_call
    
    
    def process_results(self):
        """
        Processes a dictionary of execution result lists into string 
        representations wrapped in the HTML needed to create <li> nodes.
        """
        _html = "      "
        for result_type, results_list in self._run_results.items():
            for result_list in results_list:
                _li = BLANK_STR
                for result in result_list:
                    _list = []
                    _string = BLANK_STR
                    if isinstance(result, dict) or isinstance(result, list):
                        _list = list(flatten_iterable(result))
                        _string = concatenate_list_to_string(_list)
                    elif (isinstance(result, text_type) and result != BLANK_STR):
                        _string = result
                    else:
                        _string = enquote(u("API returns empty result for this type of call."))
                    
                    _li += _string
                _html += u("<li class='") + result_type + u("'>") + _li + u("</li>")
        return _html
    #/process_results
    
    
    def report(self):
        """
        Constructs an HTML report of execution results.
        """
        global HTML_START, HTML_END
        
        html_report = self.process_results()
        return HTML_START + html_report + HTML_END
    #/report
    
    
    def read_script_from_file(self, _script_file):
        try:
            with open(_script_file, u('r')) as _script_source:
                _script_code = compile(_script_source.read(),
                                       _script_file,
                                       u('exec'))
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

#/EOF - wfapiclient