# mailer
---
Command line mail utility

Installation:
=============
1. Clone the repo on your computer and `cd` to the root folder of the project.
2. run `python setup.py install`

Usage:
======

*NOTE: The following examples call the program `delta-mail`. This is how it is currently named, however the name is expected to be changed soon.*

- Sending the exact same mail to a list of people. No variables in the mail template
	
	`delta-mail -r="bob@job.com,job@bob.com" -s="Welcome" input.mmtmpl`

- Sending the exact same mail to a list of people. However, the email template
can contain variables that are specific to this particular batch of mails.
	
	`delta-mail -r="bob@job.com,job@bob.com" --globals=variables.mvar -s="Welcome to {{EventName}}" input.mmtmpl`
	
- Sending personalised mails. Requires the use of a `.ml` (mailing list) file
	
	`delta-mail -R=receivers.ml -s="Welcome {{name}}!" input.mmtmpl`

- Sending personalised mails. Requires the use of a `.ml` file. In addition, one
can use a `.mvar` (mail variables) file to specify variables common to this particular batch of mails.
	
	`delta-mail -R=receivers.ml --globals=globalvars.mvar -s="Welcome {{name}}!" input.mmtmpl`

- Automatically finding out the type of the mail to be sent
	
	`delta-mail --smartsend=./mail-campaigns/festember/c1`

The folder `./mail-campaigns/festember/c1` should have the following structure:
	
	- template.mmtmpl
	- mailinglist.ml
	- subject.txt
	- globals.mvar

The first two files are required. The last file is optional. If the `subject.txt` file is missing, then the subject will be taken as the directory name (here, `c1`).
	
(For the first type of command, the subject can NOT be a template.)

Format of a `.ml` file:
=======================

First line contains the list of fields (tab separated) - the variables that 
are referred to in the mmtpl file. The first field is invariably the `email` 
field. The following fields can be anything.

The next line is left blank

From the third line, each row will contain the values of the appropriate fields,
and this data will be used to make personalised emails

Example:
	
	email	fname	lname	dob
	
	bob@rob.com	Bob	Rob	26-8-2015
	hog@rob.com	Hog	Rob	26-8-1996
	
This file, when used as the -R option, will generate two mails.

Format of a `.mvar` file:
=========================

Each line is of form:
{VARIABLE}={VALUE}

Empty lines are ignored

Spaces to the right of the equal-to sign are considered part of the value. 
Trailing spaces in variable names are ignored. Spaces aren't allowed in the 
variable names themselves. Though they may contain any other characters (other 
than = of course)
