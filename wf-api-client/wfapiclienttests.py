"""wf-api-client tests"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import argparse
import wfapiclient as wf

if sys.version_info < (3,):
    #define python2-compatible string function
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    #define python3-compatible string function
    def u(x):
        return x
#/compatible string function

BLANK_STR = u("")



def run_tests():
    parser = argparse.ArgumentParser(description=u("Tests for the WebFaction API client."))
    
    parser.add_argument(u("username"), help=u("The WebFaction server control panel username."))
    parser.add_argument(u("password"), help=u("The WebFaction server control panel password."))
    parser.add_argument(u("reportfile"), help=u("File into which to write test results."))
    
    args = parser.parse_args()
    
    runner1 = wf.Runner()
    
    runner1.login_to_server(args.username, args.password)
    
    
    #Domain CREATE tests
    domain1 = wf.Domain(runner1)
    
    domain1.list_domains()
    domain1.create_domain(domain=u("example.com"),
                          subdomain=[u("www"), u("ftp"), u("mail"), u("test")])
    domain1.list_domains()
    #/Domain tests
    
    
    #DNS CREATE tests
    dns1 = wf.DNS(runner1)
    
    dns1.list_dns_overrides()
    dns1.create_dns_override(domain=u("ftp.example.com"),
                             a_ip=u("192.0.2.1"),
                             cname=u("example.com"),
                             mx_name=u("mail.example.com"),
                             mx_priority=u("10"),
                             spf_record=u("v=spf1 a:mail.example.com -all"),
                             aaaa_ip=u("2001:DB8::1"))
    dns1.list_dns_overrides()
    #/DNS tests
    
    
    #Application CREATE tests
    application1 = wf.Application(runner1)
    
    application1.list_apps()
    application1.list_app_types()
    application1.create_app(name=u("test_static_application"),
                            type=u("static"),
                            autostart=False,
                            extra_info=BLANK_STR,
                            open_port=False)
    application1.list_apps()
    application1.list_app_types()
    #/Application tests
    
    
    #Website CREATE/UPDATE tests
    website1 = wf.Website(runner1)
    
    website1.list_bandwidth_usage()
    website1.list_websites()
    website1.create_website(website_name=u("Test Website Entry"),
                            ip=u("192.0.2.1"),
                            https=True,
                            subdomains=[u("test.example")],
                            site_apps=[u("test_static_application"), u("/")])
    website1.list_websites()
    website1.update_website(website_name=u("Test Website Entry"),
                            ip=u("192.0.2.2"),
                            https=False,
                            subdomains=[u("test.example")],
                            site_apps=[u("test_static_application"), u("/")])
    website1.list_websites()
    #/Website tests
    
    
    #Mailbox CREATE/UPDATE tests
    mailbox1 = wf.Mailbox(runner1)
    
    PROCMAILRULE = u("""
    :0
    * ^From.*test
    * ^Subject:.*testing wf-api-client
    {
       :0 c
       ! test@example.com
    }
    """)
    
    mailbox1.list_mailboxes()
    mailbox1.create_mailbox(mailbox=u("test_mailbox"),
                            enable_spam_protection=True,
                            discard_spam=True,
                            spam_redirect_folder=u("test_spam_folder"),
                            use_manual_procmailrc=True,
                            manual_procmailrc=PROCMAILRULE)
    mailbox1.list_mailboxes()
    mailbox1.change_mailbox_password(mailbox=u("test_mailbox"),
                                     password=u("test_mailbox_password"))
    mailbox1.update_mailbox(mailbox=u("test_mailbox"),
                            enable_spam_protection=False,
                            discard_spam=False,
                            spam_redirect_folder=BLANK_STR,
                            use_manual_procmailrc=False,
                            manual_procmailrc=BLANK_STR)
    mailbox1.list_mailboxes()
    #/Mailbox tests
    
    
    #Email CREATE/UPDATE tests
    email1 = wf.Email(runner1)
    
    email1.list_emails()
    email1.create_email(email_address=u("test.email@example.com"),
                        targets=u("test_mailbox"),
                        autoresponder_on=True,
                        autoresponder_subject=u("From the mailbox of test email:"),
                        autoresponder_message=u("Test email is not available."),
                        autoresponder_from=u("test.email@example.com"),
                        script_machine=BLANK_STR,
                        script_path=BLANK_STR)
    email1.list_emails()
    email1.create_emails(domain=u("example.com"),
                         prefixes=None,
                         targets=u("test.email@example.com"))
    email1.list_emails()
    email1.update_email(email_address=u("test.email@example.com"),
                        targets=[u("test_mailbox")],
                        autoresponder_on=False,
                        autoresponder_subject=BLANK_STR,
                        autoresponder_message=BLANK_STR,
                        autoresponder_from=BLANK_STR,
                        script_machine=BLANK_STR,
                        script_path=BLANK_STR)
    email1.list_emails()
    #/Email tests
    
    
    #Database CREATE/UPDATE tests
    database1 = wf.Database(runner1)
    
    database1.list_dbs()
    database1.create_db(name=u("test_postgresql_db"),
                        db_type=u("postgresql"),
                        password=u("test_postgresql_db_password"))
    database1.list_dbs()
    database1.enable_addon(database=u("test_postgresql_db"),
                           db_type=u("postgresql"),
                           addon=u("postgis"))
    database1.list_db_users()
    database1.create_db_user(username=u("test_postgresql_db_ADMIN_user"),
                             password=u("test_postgresql_db_user_password"),
                             db_type=u("postgresql"))
    database1.list_db_users()
    database1.change_db_user_password(username=u("test_postgresql_db_ADMIN_user"),
                                      password=u("test_postgresql_db_user_password_1"),
                                      db_type=u("postgresql"))
    database1.make_user_owner_of_db(username=u("test_postgresql_db_ADMIN_user"),
                                    database=u("test_postgresql_db"),
                                    db_type=u("postgresql"))
    database1.create_db_user(username=u("test_postgresql_db_POWERUSER_user"),
                             password=u("test_postgresql_db_user_password_2"),
                             db_type=u("postgresql"))
    database1.grant_db_permissions(username=u("test_postgresql_db_POWERUSER_user"),
                                   database=u("test_postgresql_db"),
                                   db_type=u("postgresql"))
    database1.revoke_db_permissions(username=u("test_postgresql_db_POWERUSER_user"),
                                    database=u("test_postgresql_db"),
                                    db_type=u("postgresql"))
    #/Database tests
    
    
    #Server tests
    server1 = wf.Server(runner1)
    
    server1.list_ips()
    server1.list_machines()
    #/Server tests
    
    
    #ShellUser CREATE/UPDATE/DELETE tests
    shelluser1 = wf.ShellUser(runner1)

    shelluser1.list_users()
    shelluser1.create_user(username=u("test_shelluser"),
                           shell=u("bash"),
                           groups=[])
    shelluser1.list_users()
    shelluser1.change_user_password(username=u("test_shelluser"),
                                    password=u("test_shelluser_password"))
    shelluser1.delete_user(username=u("test_shelluser"))
    shelluser1.list_users()
    #/ShellUser tests
    
    
    #Cron CREATE/DELETE tests
    cron1 = wf.Cron(runner1)
    
    CRONTABLINE = u("""
    *       *       *       *       *       /sbin/ping -c 1 127.0.0.1 > /dev/null
    """)
    
    cron1.create_cron_job(line=CRONTABLINE)
    cron1.delete_cron_job(line=CRONTABLINE)
    #/Cron tests
    
    
    #File CREATE/UPDATE tests
    file1 = wf.File(runner1)
    
    file1.write_file(filename=u("test_file.txt"),
                     str=u("Test file written remotely via WebFaction API."),
                     mode=u("w"))
    file1.replace_in_file(filename=u("test_file.txt"),
                          changes=[u("WebFaction API."), 
                                   u("WebFaction API using `wf-api-client`.")])
    #/File tests
    
    
    #System tests
    system1 = wf.System(runner1)
    
    system1.system(cmd=u("rm -f ~/test_file.txt"))
    #/System tests
    
    
    #Application DELETE tests
    application1.delete_app(name=u("test_static_application"))
    application1.list_apps()
    application1.list_app_types()
    #/Application tests
    
    
    #Database DELETE tests
    database1.delete_db_user(username=u("test_postgresql_db_POWERUSER_user"),
                             db_type=u("postgresql"))
    database1.delete_db_user(username=u("test_postgresql_db_ADMIN_user"),
                             db_type=u("postgresql"))
    database1.list_db_users()
    database1.delete_db(name=u("test_postgresql_db"),
                        db_type=u("postgresql"))
    database1.list_dbs()
    #/Database tests
    
    
    #Email DELETE tests
    email1.delete_email(email_address=u("test.email@example.com"))
    email1.list_emails
    email1.delete_emails(domain=u("example.com"),
                         prefixes=None)
    email1.list_emails()
    #/Email tests
    
    
    #Mailbox DELETE tests
    mailbox1.delete_mailbox(mailbox=u("test_mailbox"))
    mailbox1.list_mailboxes()
    #/Mailbox tests
    
    
    #Website DELETE tests
    website1.delete_website(website_name=u("Test Website Entry"),
                            ip=u("192.0.2.2"),
                            https=False)
    website1.list_websites()
    #/Website tests
    
    
    #DNS DELETE tests
    dns1.delete_dns_override(domain=u("ftp.example.com"),
                             a_ip=u("192.0.2.1"),
                             cname=u("example.com"),
                             mx_name=u("mail.example.com"),
                             mx_priority=u("10"),
                             spf_record=u("v=spf1 a:mail.example.com -all"),
                             aaaa_ip=u("2001:DB8::1"))
    dns1.list_dns_overrides()
    #/DNS tests
    
    
    #Domain DELETE tests
    domain1.delete_domain(domain=u("example.com"),
                          subdomain=[u("www"), u("ftp"), u("mail"), u("test")])
    domain1.list_domains()
    #/Domain tests
    
    
    #Write log
    runner1.write_report_to_file(args.reportfile)
#/run_tests


if __name__ == u("__main__"):
    run_tests()


#EOF - wf-api-client tests
