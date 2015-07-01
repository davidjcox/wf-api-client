=============
wf-api-client
=============

The WebFaction API client is a local client for interfacing to the WebFaction 
web hosting server API.  It provides class-based organization, convenience 
methods, script execution, and HTML-formatted run reporting.

It can be used as standalone module to execute a supplied script file or as an 
imported library module within individual script files.

Detailed documentation is available on http://wf-api-client.readthedocs.org/en/latest/.

:Author:    David J Cox

:Contact:   <davidjcox.at@gmail.com>

:Version:   1.0

Let me know what you think of it...

What's new?
-----------
The client continues to be Python 2/3 compatible, as it should be.  A full test 
suite has been added, which also doubles as an example of how to write a 
standalone script for the client.

What's this all about?
----------------------

WebFaction provides a perfectly cromulent RESTful API for their server accounts.
It enables all aspects of server management to be executed remotely: CRUD 
actions for domains, websites, email, databases, etc.  It even allows shell 
commands.  Excellent!

However, despite its excellence, there are a few design decisions that cause 
misgivings for me:

- The WebFaction API uses positional arguments.  
    When working with remote servers, I prefer commands to be as explicit as 
    possible, because like Unix, APIs can be unforgiving.  This client uses 
    keyword arguments to guard against a slip of concentration wiping something 
    important out.  It translates the keyword arguments into positional ones 
    for each API call.

- The WebFaction API has small inconsistencies in calling convention.
    This is a nitpick, but one that's important when remotely administering 
    servers.  Some API calls define collections using lists.  Others define 
    collections using positional arguments only.  Once again, a mistake waiting 
    to be made if a call signature is recalled incorrectly.  This client uses 
    lists for all collections and unwraps them back into individual positional 
    arguments for those API calls that require it.

In addition to these translation functions, the WebFaction API client provides 
additional utility similar to other IT automation solutions like Ansible, Salt, 
etc, by providing batching, parallelism, and reporting, described as follows.

Class-based Organization
------------------------

Functional groups are implemented as classes with API calls grouped as methods.
Working with descriptive class instances makes complicated scripting easier, 
especially when driving more than one server or using more than one worker 
thread.  In addition to atomic methods, batched convenience methods have been 
added, for e.g. creating/deleting RFC 2142 email prefixes in one call.

Convenience Methods
-------------------

In addition to batch methods, convenience methods are used to speed script 
execution by performing client-side evaluation to avoid unnecessary remote API 
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

Tests
-----

A full test suite is provided in the `wfapiclienttests.py` file.  It is 
standalone script and, so, doubles as a fine example for standalone scripts. The 
tests must be run against a live, accessible WeFaction server using valid 
credentials.  The tests are not idempotent but can be considered nearly so in
that all test actions against the server will not cause side effects for the 
existing configuration and all test create and update actions are deleted 
afterward.  Should some event prevent successful completion of the tests, all 
test objects created on the server are obviously identifiable with some 
variation of 'wf_test' pre-pended to their name and should be considered safe 
to delete manually.


Examples
--------

Tests are executed like so::

    python wfapiclienttests.py "username" "password" "/path/to/report.html"


Standalone scripts import the module as a library and are responsible for 
instantiating the Runner class to log results and write out the run report.  It 
is more flexible in that multiple runner objects can be created to work on 
different servers at one time logging either to separate reports or to one 
shared report.
Standalone scripts are structured like this:

.. code:: python

    """`create_emails` script"""
    
    import wfapiclient as wf
    
    runner1 = wf.Runner()
    runner2 = wf.Runner()
    
    #WebFaction automagically identifies target server by username/password.
    runner1.login_to_server("first_username", "first_password")
    runner2.login_to_server("second_username", "second_password")
    
    #Server objects are tied to runner instances for call execution and logging.
    email1 = wf.Email(runner1)
    email1.create_emails(domain="first.example.com", targets="user1@first.example.com")
    
    email2 = wf.Email(runner2)
    email2.create_emails(domain="second.example.com", targets="user2@second.example.com")
    
    #Either write report to separate report files...
    runner1.write_report_to_file("/tmp/create_emails1.html")
    runner2.write_report_to_file("/tmp/create_emails2.html")
    
    #...or write (append) reports to one `shared` file.
    runner1.write_report_to_file("/tmp/create_emails_shared.html")
    runner2.write_report_to_file("/tmp/create_emails_shared.html")
    
    #EOF - `create_emails`


Direct module calls are invoked like this::

    python wfapiclient.py "username" "password" \
                            --scriptfile=/home/user/scripts/create_emails \
                            --reportfile=/tmp/create_emails.html


Scripts for importation by the module call methods directly using Python syntax.
The run report is automatically generated using a supplied destination file name.
Imported scripts are structured like this:

.. code:: python

    """`create_emails` script"""
    
    #Class object creation requires `self` reference to Runner().
    email = Email(self)
    email.create_emails(domain="example.com", targets="user@example.com")
    
    #EOF - `create_emails`


That's it.  Have fun.
