=============
wf-api-client
=============

The WebFaction API client is a local client for interfacing to the WebFaction 
web hosting server API.  It provides class-based organization, convenience 
methods, script execution, and HTML-formatted run reporting.

Can be used as standalone module to execute a supplied script file or as an 
imported library module within individual script files.

Detailed documentation is available on http://wf-api-client.readthedocs.org/en/latest/.

:Author:    David J Cox

:Contact:   <davidjcox.at@gmail.com>

:Version:   0.1

Let me know what you think of it...

What's this all about?
----------------------

WebFaction provides a perfectly cromulent RESTful API for their server accounts.
It enables all aspects of server management to be batched remotely: CRUD actions
for domains, websites, email, databases, etc.  It even allows shell commands.
Excellent!

This client extends that utility similarly to other IT automation solutions like
Ansible, Salt, etc, by providing batching, parallelism, and reporting.

Class-based Organization
------------------------

Functional groups are implemented as classes with API calls grouped as methods.
Working with descriptive class instances makes complicated scripting easier, 
especially when driving more than server or using more than one worker thread.  
In addition to atomic methods, batched convenience methods have been added, for
e.g. creating/deleting RFC 2142 email prefixes in one call.

Convenience Methods
-------------------

In addition to batch methods, convenience methods are used to speed script 
execution by performing client-side evaluation to avoid needless remote API 
calls.  Creation/deletion calls are compared against a single inventory call to 
ensure that entities exist before attempting deletion or do not exist before 
attempting creation.  If not, client errors are reported.

Script Execution
----------------

Why have an API if it's not being scripted against?  The client provides 
scripting two ways: Scripts can be passed directly to the client in a standalone
module call, or the module can be imported as a library module within standalone
scripts.  See below for examples of both approaches.

HTML-formatted Run Reporting
----------------------------

Since RESTful services are stateless, they can't (shouldn't) provide history.  
This client does.  Every method call resulting in a remote API call returns the
status, datetime, API call name, and call result to a log function.  The running
tally of logged actions are collected and reported as a HTMl report file.  Call 
results are color-coded green for 'success' and red for 'failure'.  Elementary!

Examples
--------

Standalone module calls are invoked like this:

    python wfapiclient.py "username" "password" --scriptfile=/home/user/scripts/create_emails --reportfile=/tmp/create_emails.html


A standalone script calls methods directly using Python syntax.  The run report 
is automatically generated for a supplied file name.
Standalone scripts are structured like this:

    """`create_emails` script"""
    email = Email()
    email.create_emails(domain="example.com", targets="user@example.com")
    #EOF - `create_emails`


Standalone scripts import the module as a library and are responsible for 
instantiating the Runner class to log results and write out the run report.  It 
is more flexible in that multiple runner objects can be created to work on 
different servers at one time logging either to separate reports or to one 
shared report.
Standalone scripts are structured like this:

    """`create_emails` script"""
    import wfapiclient as wf
    
    runner1 = Runner()
    runner2 = Runner()
    
    #WebFaction automagically identifies target server by username/password.
    runner1.login_to_server("first_username", "first_password")
    runner2.login_to_server("second_username", "second_password")
    
    #Server objects are tied to runner instances for call execution and logging.
    email1 = Email(runner1)
    email1.create_emails(domain="first.example.com", targets="user1@first.example.com")
    
    email2 = Email(runner2)
    email2.create_emails(domain="second.example.com", targets="user2@second.example.com")
    
    #Either write report to separate report files...
    runner1.write_report_to_file("/tmp/create_emails1.html")
    runner2.write_report_to_file("/tmp/create_emails2.html")
    
    #...or write (append) reports to one shared file.
    runner1.write_report_to_file("/tmp/create_emails_shared.html")
    runner2.write_report_to_file("/tmp/create_emails_shared.html")
    
    #EOF - `create_emails`


Enjoy.
