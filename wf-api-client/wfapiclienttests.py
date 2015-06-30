"""wf-api-client tests"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import inspect
import argparse

import wfapiclient as wf



BLANK_STR = ""
SUCCESS = "success"

TEST_DOMAIN = "example"
TEST_DOMAIN_COM = TEST_DOMAIN + ".com"
TEST_SUBDOMAINS = ["www", "ftp", "mail", "test"]
TEST_IPV4 = "192.0.2.2"
TEST_IPV6 = "2001:DB8::1"
TEST_APP_NAME = "wf_test_static_application"
TEST_APP_NAME_1 = TEST_APP_NAME + "_1"
TEST_APP_NAME_2 = TEST_APP_NAME + "_2"
TEST_APP_ROOT = "/"
TEST_WEBSITE_NAME = "wf_test_website"
TEST_MAILBOX = "wf_test_mailbox"
TEST_MAILBOX_PASSWORD = "wf_test_mailbox_password"
TEST_SPAM_FOLDER = "wf_test_spam_folder"
TEST_EMAIL_ADDRESS = "wftest@example.com"
TEST_EMAIL_TARGETS = [TEST_MAILBOX]
TEST_DB_NAME = "wf_test_postgresql_db"
TEST_DB_TYPE = "postgresql"
TEST_DB_DEFAULT_USER_PASSWORD = "wf_test_postgresql_db_default_user_password"
TEST_DB_ADMIN_USERNAME = "wfpgsqladmin"
TEST_DB_ADMIN_PASSWORD = "wf_test_postgresql_db_admin_password"
TEST_DB_USER_USERNAME = "wfpgsqluser"
TEST_DB_USER_PASSWORD = "wf_test_postgresql_db_user_password"
TEST_SHELLUSER_NAME = "wfshelluser"
TEST_SHELLUSER_PASSWORD = "wf_test_shelluser_password"
TEST_SHELLUSER_SHELL = "bash"
TEST_FILE_NAME = "wf_test_file.txt"
TEST_FILE_PERIOD = "."
TEST_FILE_ORIGINAL = "Test file written remotely via WebFaction API"
TEST_FILE_ORIGINAL_TEXT = TEST_FILE_ORIGINAL + TEST_FILE_PERIOD
TEST_FILE_CHANGE = " using `wf-api-client`"
TEST_FILE_CHANGED_TEXT = TEST_FILE_ORIGINAL + TEST_FILE_CHANGE + TEST_FILE_PERIOD



def run_tests():
    parser = argparse.ArgumentParser(description="Tests for the WebFaction API client.")
    
    parser.add_argument("username", help="The WebFaction server control panel username.")
    parser.add_argument("password", help="The WebFaction server control panel password.")
    parser.add_argument("reportfile", help="File into which to write test results.")
    
    args = parser.parse_args()
    
    runner1 = wf.Runner()
    
    runner1.login_to_server(args.username, args.password)
    
    CALLER = "WF_API_TESTS"
    
    
    #Server tests
    server1 = wf.Server(runner1)
    
    server_ips = server1.list_ips()
    runner1.log(CALLER, SUCCESS, server_ips)
    
    server_machines = server1.list_machines()
    runner1.log(CALLER, SUCCESS, server_machines)
    #/Server tests
    
    
    #Domain CREATE tests
    domain1 = wf.Domain(runner1)
    
    domain1.create_domain(domain=TEST_DOMAIN_COM,
                          subdomain=TEST_SUBDOMAINS)
    #/Domain tests
    
    
    #DNS CREATE tests
    dns1 = wf.DNS(runner1)
    
    dns1.create_dns_override(domain="ftp." + TEST_DOMAIN_COM,
                             a_ip=TEST_IPV4,
                             cname=TEST_DOMAIN_COM,
                             mx_name="mail." + TEST_DOMAIN_COM,
                             mx_priority="10",
                             spf_record="v=spf1 a:mail." + TEST_DOMAIN + " -all",
                             aaaa_ip=TEST_IPV6)
    dns1.delete_dns_override(domain="ftp." + TEST_DOMAIN_COM,
                             a_ip=TEST_IPV4,
                             cname=TEST_DOMAIN_COM,
                             mx_name="mail." + TEST_DOMAIN_COM,
                             mx_priority="10",
                             spf_record="v=spf1 a:mail." + TEST_DOMAIN + " -all",
                             aaaa_ip=TEST_IPV6)
    #/DNS tests
    
    
    #Application CREATE tests
    application1 = wf.Application(runner1)
    
    application1.create_app(name=TEST_APP_NAME_1,
                            type="static",
                            autostart=False,
                            extra_info=BLANK_STR,
                            open_port=False)
    
    application1.create_app(name=TEST_APP_NAME_2,
                            type="static",
                            autostart=False,
                            extra_info=BLANK_STR,
                            open_port=False)
    #/Application tests
    
    
    #Website CREATE/UPDATE tests
    website1 = wf.Website(runner1)
    
    webserver_ip = server_ips[0]['ip'] #`server_ips` from `Server tests` above.
    
    bandwidth_usages = website1.list_bandwidth_usage()
    runner1.log(CALLER, SUCCESS, bandwidth_usages)
    
    website1.create_website(website_name=TEST_WEBSITE_NAME,
                            ip=webserver_ip,
                            https=True,
                            subdomains=["test." + TEST_DOMAIN],
                            site_apps=[TEST_APP_NAME_1, TEST_APP_ROOT])
    website1.update_website(website_name=TEST_WEBSITE_NAME,
                            ip=webserver_ip,
                            https=True,
                            subdomains=[TEST_DOMAIN_COM],
                            site_apps=[TEST_APP_NAME_1, TEST_APP_ROOT])
    #/Website tests
    
    
    #Mailbox CREATE/UPDATE tests
    mailbox1 = wf.Mailbox(runner1)
    
    PROCMAILRULE = """
    :0
    * ^From.*test
    * ^Subject:.*testing wf-api-client
    {
       :0 c
       ! """ + TEST_EMAIL_ADDRESS + """
    }
    """
    
    mailbox1.create_mailbox(mailbox=TEST_MAILBOX,
                            enable_spam_protection=True,
                            discard_spam=True,
                            spam_redirect_folder=TEST_SPAM_FOLDER,
                            use_manual_procmailrc=True,
                            manual_procmailrc=PROCMAILRULE)
    mailbox1.change_mailbox_password(mailbox=TEST_MAILBOX,
                                     password=TEST_MAILBOX_PASSWORD )
    mailbox1.update_mailbox(mailbox=TEST_MAILBOX ,
                            enable_spam_protection=False,
                            discard_spam=False,
                            spam_redirect_folder=BLANK_STR,
                            use_manual_procmailrc=False,
                            manual_procmailrc=BLANK_STR)
    #/Mailbox tests
    
    
    #Email CREATE/UPDATE tests
    email1 = wf.Email(runner1)
    
    email1.create_email(email_address=TEST_EMAIL_ADDRESS,
                        targets=TEST_EMAIL_TARGETS,
                        autoresponder_on=True,
                        autoresponder_subject="From the mailbox of test email:",
                        autoresponder_message="Test email is not available.",
                        autoresponder_from=TEST_EMAIL_ADDRESS,
                        script_machine=BLANK_STR,
                        script_path=BLANK_STR)
    email1.create_emails(domain=TEST_DOMAIN_COM,
                         prefixes=None,
                         targets=TEST_EMAIL_TARGETS)
    email1.update_email(email_address=TEST_EMAIL_ADDRESS,
                        targets=TEST_EMAIL_TARGETS,
                        autoresponder_on=False,
                        autoresponder_subject=BLANK_STR,
                        autoresponder_message=BLANK_STR,
                        autoresponder_from=BLANK_STR,
                        script_machine=BLANK_STR,
                        script_path=BLANK_STR)
    #/Email tests
    
    
    #Database CREATE/UPDATE tests
    database1 = wf.Database(runner1)
    
    database1.create_db(name=TEST_DB_NAME,
                        db_type=TEST_DB_TYPE,
                        password=TEST_DB_DEFAULT_USER_PASSWORD)
    database1.enable_addon(database=TEST_DB_NAME,
                           db_type=TEST_DB_TYPE,
                           addon="postgis")
    database1.create_db_user(username=TEST_DB_USER_USERNAME,
                             password=TEST_DB_ADMIN_PASSWORD,
                             db_type=TEST_DB_TYPE)
    database1.change_db_user_password(username=TEST_DB_USER_USERNAME,
                                      password=TEST_DB_USER_PASSWORD,
                                      db_type=TEST_DB_TYPE)
    database1.create_db_user(username=TEST_DB_ADMIN_USERNAME,
                             password=TEST_DB_ADMIN_PASSWORD,
                             db_type=TEST_DB_TYPE)
    database1.make_user_owner_of_db(username=TEST_DB_ADMIN_USERNAME,
                                    database=TEST_DB_NAME,
                                    db_type=TEST_DB_TYPE)
    database1.grant_db_permissions(username=TEST_DB_USER_USERNAME,
                                   database=TEST_DB_NAME,
                                   db_type=TEST_DB_TYPE)
    database1.revoke_db_permissions(username=TEST_DB_USER_USERNAME,
                                    database=TEST_DB_NAME,
                                    db_type=TEST_DB_TYPE)
    #/Database tests
    
    
    #Server tests
    server1 = wf.Server(runner1)
    
    server_ips = server1.list_ips()
    runner1.log(CALLER, SUCCESS, server_ips)
    
    server_machines = server1.list_machines()
    runner1.log(CALLER, SUCCESS, server_machines)
    #/Server tests
    
    
    #ShellUser CREATE/UPDATE/DELETE tests
    shelluser1 = wf.ShellUser(runner1)
    
    shelluser1.create_user(username=TEST_SHELLUSER_NAME,
                           shell=TEST_SHELLUSER_SHELL,
                           groups=[])
    shelluser1.change_user_password(username=TEST_SHELLUSER_NAME,
                                    password=TEST_SHELLUSER_PASSWORD)
    shelluser1.delete_user(username=TEST_SHELLUSER_NAME)
    #/ShellUser tests
    
    
    #Cron CREATE/DELETE tests
    cron1 = wf.Cron(runner1)
    
    CRONTABLINE = """
    *       *       *       *       *       /sbin/ping -c 1 127.0.0.1 > /dev/null
    """
    
    cron1.create_cronjob(line=CRONTABLINE)
    cron1.delete_cronjob(line=CRONTABLINE)
    #/Cron tests
    
    
    #File CREATE/UPDATE tests
    file1 = wf.File(runner1)
    
    file1.write_file(filename=TEST_FILE_NAME,
                     str=TEST_FILE_ORIGINAL_TEXT,
                     mode="w")
    file1.replace_in_file(filename=TEST_FILE_NAME,
                          changes=[TEST_FILE_ORIGINAL_TEXT, 
                                   TEST_FILE_CHANGED_TEXT])
    #/File tests
    
    
    #System tests
    system1 = wf.System(runner1)
    
    system1.system(cmd="rm -f ~/" + TEST_FILE_NAME)
    #/System tests
    
    
    #Application DELETE tests
    application1.delete_app(name=TEST_APP_NAME_2)
    application1.delete_app(name=TEST_APP_NAME_1)
    #/Application tests
    
    
    #Database DELETE tests
    database1.delete_db(name=TEST_DB_NAME,
                        db_type=TEST_DB_TYPE)
    database1.delete_db_user(username=TEST_DB_ADMIN_USERNAME,
                             db_type=TEST_DB_TYPE)
    
    database1.delete_db_user(username=TEST_DB_USER_USERNAME,
                             db_type=TEST_DB_TYPE)
    
    database1.delete_db_user(username=TEST_DB_NAME,
                             db_type=TEST_DB_TYPE)
    #/Database tests
    
    
    #Email DELETE tests
    email1.delete_emails(domain=TEST_DOMAIN_COM,
                         prefixes=None)
    
    email1.delete_email(email_address=TEST_EMAIL_ADDRESS)
    #/Email tests
    
    
    #DNS DELETE tests
    # dns1.delete_dns_override(domain="ftp." + TEST_DOMAIN_COM,
                             # a_ip=TEST_IPV4,
                             # cname=TEST_DOMAIN_COM,
                             # mx_name="mail." + TEST_DOMAIN_COM,
                             # mx_priority="10",
                             # spf_record="v=spf1 a:mail." + TEST_DOMAIN + " -all",
                             # aaaa_ip=TEST_IPV6)
    #/DNS tests
    
    
    #Mailbox DELETE tests
    mailbox1.delete_mailbox(mailbox=TEST_MAILBOX)
    #/Mailbox tests
    
    
    #Website DELETE tests
    website1.delete_website(website_name=TEST_WEBSITE_NAME,
                            ip=webserver_ip,
                            https=True)
    #/Website tests
    
    
    #Domain DELETE tests
    domain1.delete_domain(domain=TEST_DOMAIN_COM)
    #/Domain tests
    
    
    #Write log
    runner1.write_report_to_file(args.reportfile)
#/run_tests


if __name__ == "__main__":
    run_tests()


#EOF - wf-api-client tests
