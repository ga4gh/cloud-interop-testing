## Messages for challenge scoring script.

import string
import sys
import warnings


## Module level state. You'll need to set a synapse object at least
## before using this module.
syn = None
send_messages = True
send_notifications = True
acknowledge_receipt = False
dry_run = False


## Edit these URLs to point to your challenge and its support forum
defaults = dict(
    challenge_instructions_url = "https://www.synapse.org/syn8507133",
    support_forum_url = "https://www.synapse.org/#!Synapse:syn8507133/discussion/default",
    scoring_script = "GA4GH-DREAM Admins")

##---------------------------------------------------------
## Message templates:
## Edit to fit your challenge.
##---------------------------------------------------------

validation_failed_subject_template = "Validation error in submission to {queue_name}"
validation_failed_template = """\
<p>Hello {username},</p>

<p>Sorry, but we were unable to validate your submission to the {queue_name} evaluation queue.</p>

<p>Please refer to the challenge instructions which can be found at \
{challenge_instructions_url} and to the error message below:</p>

<p>submission name: <b>{submission_name}</b><br>
submission ID: <b>{submission_id}</b></p>

<blockquote><pre>
{message}
</pre></blockquote>

<p>If you have questions, please ask on the forums at {support_forum_url}.</p>

<p>Sincerely,<br>
{scoring_script}</p>
"""

validation_passed_subject_template = "Submission received to {queue_name}"
validation_passed_template = """\
<p>Hello {username},</p>

<p>We have received your submission to the {queue_name} evaluation queue and confirmed \
that it is correctly formatted.</p>

<p>submission name: <b>{submission_name}</b><br>
submission ID: <b>{submission_id}</b></p>

<p>You should expect to receive a follow-up message soon with instructions for how to document \
your methods for running the workflow.</p>

<p>If you have questions, please ask on the forums at {support_forum_url} or refer to the challenge \
instructions which can be found at {challenge_instructions_url}.</p>

<p>Sincerely,<br>
{scoring_script}</p>
"""

report_initialized_subject_template = "Report wiki initialized for submission to {queue_name}"
report_initialized_template = """\
<p>Hello {username},</p>

<p>Now that your submission (ID: {submission_id}) for the {queue_name} evaluation queue \
has been successfully validated, we've initialized a Synapse wiki where you can document your methods.</p>

<p>Please navigate to the Synapse entity located at https://www.synapse.org/#!Synapse:{report_entity_id} \
and select 'Tools' -> 'Edit File Wiki' to edit the report. At a minimum, you should complete all \
YAML-style fields in the "Submission overview" section; however, we strongly encourage you to provide \
detailed documentation under the "Steps" section.</p>
 
<p>If you have questions, please ask on the forums at {support_forum_url}.</p>

<p>Sincerely,<br>
{scoring_script}</p>
"""

report_reminder_subject_template = "REMINDER: report wiki incomplete for submission to {queue_name}"
report_reminder_template = """\
<p>Hello {username},</p> 
<p>Your submission (ID: {submission_id}) for the {queue_name} evaluation queue \
was previously validated; however, the status of the corresponding Synapse wiki \
is still either "INITIALIZED" or "IN_PROGRESS". In order for your submission to \
be counted in the final results for the Workflow Execution Challenge, <u>the report \
wiki must also be successfully validated by <b>January 6th, 2018</b></u>. Follow the \
instructions below to  document your methods and complete your submission.</p>
<p>Please navigate to the Synapse entity located at \
https://www.synapse.org/#!Synapse:{report_entity_id} \
and select '<b>Tools</b>' -> '<b>Edit File Wiki</b>' to edit the report. \
At a minimum, you should complete all YAML-style fields in the \
"<b>Submission overview</b>" section; however, we strongly encourage you to provide \
detailed documentation under the "<b>Steps</b>" section. You can also refer to the \
<a href="https://www.synapse.org/#!Synapse:syn8507133/wiki/451412"><b>Document Submissions</b> \
page</a> on the challenge site for more details.</p>
<p>If you have questions, please ask on the forums at {support_forum_url}.</p>

<p>Sincerely,<br>
{scoring_script}</p>
"""

report_validation_failed_subject_template = "Report validation error for submission in {queue_name}"
report_validation_failed_template = """\
<p>Hello {username},</p>

<p>Sorry, but we were unable to validate the report for your submission (ID: {submission_id}) \ 
to the {queue_name} evaluation queue.</p>

<p>Please refer to the challenge instructions which can be found at \
{challenge_instructions_url} and to the error message below:</p>

<p>submission ID: <b>{submission_id}</b><br>
report link: https://www.synapse.org/#!Synapse:{report_entity_id}</p>

<blockquote><pre>
{message}
</pre></blockquote>

<p>If you have questions, please ask on the forums at {support_forum_url}.</p>

<p>Sincerely,<br>
{scoring_script}</p>
"""

report_validation_passed_subject_template = "Submission report approved in {queue_name}"
report_validation_passed_template = """\
<p>Hello {username},</p>

<p>We have confirmed that the report for your submission to the {queue_name} evaluation queue \
is complete and correctly formatted.</p>

<p>submission ID: <b>{submission_id}</b><br>
report link: https://www.synapse.org/#!Synapse:{report_entity_id}</p>

<p>If you have questions, please ask on the forums at {support_forum_url} or refer to the challenge \
instructions which can be found at {challenge_instructions_url}.</p>

<p>Sincerely,<br>
{scoring_script}</p>
"""

scoring_succeeded_subject_template = "Scored submission to {queue_name}"
scoring_succeeded_template = """\
<p>Hello {username},</p>

<p>Your submission \"{submission_name}\" (ID: {submission_id}) to the {queue_name} has been scored:</p>

<blockquote><pre>
{message}
</pre></blockquote>

<p>If you have questions, please ask on the forums at {support_forum_url}.</p>

<p>Sincerely,<br>
{scoring_script}</p>
"""

scoring_error_subject_template = "Exception while scoring submission to {queue_name}"
scoring_error_template = """\
<p>Hello {username},</p>

<p>Sorry, but we were unable to process your submission to the {queue_name}.</p>

<p>Please refer to the challenge instructions which can be found at \
{challenge_instructions_url} and to the error message below:</p>

<p>submission name: <b>{submission_name}</b><br>
submission ID: <b>{submission_id}</b></p>

<blockquote><pre>
{message}
</pre></blockquote>

<p>If you have questions, please ask on the forums at {support_forum_url}.</p>

<p>Sincerely,<br>
{scoring_script}</p>
"""

notification_subject_template = "Exception while scoring submission to {queue_name}"
error_notification_template = """\
<p>Hello Challenge Administrator,</p>

<p>The scoring script for {queue_name} encountered an error:</p>

<blockquote><pre>
{message}
</pre></blockquote>

<p>Sincerely,<br>
{scoring_script}</p>
"""


class DefaultingFormatter(string.Formatter):
    """
    Python's string.format has the annoying habit of raising a KeyError
    if you don't completely fill in the template. Let's do something a
    bit nicer.
    Adapted from: http://stackoverflow.com/a/19800610/199166
    """
    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            value = kwds.get(key, defaults.get(key, None))
            if value is None:
                value = "{{{0}}}".format(key)
                warnings.warn("Missing template variable %s" % value)
            return value
        else:
            Formatter.get_value(key, args, kwds)

formatter = DefaultingFormatter()

##---------------------------------------------------------
## functions for sending various types of messages
##---------------------------------------------------------

def validation_failed(userIds, **kwargs):
    if send_messages:
        return send_message(userIds=userIds, 
                            subject_template=validation_failed_subject_template,
                            message_template=validation_failed_template,
                            kwargs=kwargs)

def validation_passed(userIds, **kwargs):
    if acknowledge_receipt:
        return send_message(userIds=userIds,
                            subject_template=validation_passed_subject_template,
                            message_template=validation_passed_template,
                            kwargs=kwargs)

def report_initialized(userIds, **kwargs):
    if send_messages:
        return send_message(userIds=userIds, 
                            subject_template=report_initialized_subject_template,
                            message_template=report_initialized_template,
                            kwargs=kwargs)

def report_reminder(userIds, **kwargs):
    if send_messages:
        return send_message(userIds=userIds, 
                            subject_template=report_reminder_subject_template,
                            message_template=report_reminder_template,
                            kwargs=kwargs)

def report_validation_failed(userIds, **kwargs):
    if send_messages:
        return send_message(userIds=userIds, 
                            subject_template=report_validation_failed_subject_template,
                            message_template=report_validation_failed_template,
                            kwargs=kwargs)

def report_validation_passed(userIds, **kwargs):
    if send_messages:
        return send_message(userIds=userIds,
                            subject_template=report_validation_passed_subject_template,
                            message_template=report_validation_passed_template,
                            kwargs=kwargs)

def scoring_succeeded(userIds, **kwargs):
    if send_messages:
        return send_message(userIds=userIds,
                            subject_template=scoring_succeeded_subject_template,
                            message_template=scoring_succeeded_template,
                            kwargs=kwargs)

def scoring_error(userIds, **kwargs):
    if send_messages:
        return send_message(userIds=userIds,
                            subject_template=scoring_error_subject_template,
                            message_template=scoring_error_template,
                            kwargs=kwargs)

def error_notification(userIds, **kwargs):
    if send_notifications:
        return send_message(userIds=userIds,
                            subject_template=notification_subject_template,
                            message_template=error_notification_template,
                            kwargs=kwargs)

def send_message(userIds, subject_template, message_template, kwargs):
    subject = formatter.format(subject_template, **kwargs)
    message = formatter.format(message_template, **kwargs)
    if dry_run:
        print "\nDry Run: would have sent:"
        print subject
        print "-" * 60
        print message
        return None
    elif syn:
        response = syn.sendMessage(
            userIds=userIds,
            messageSubject=subject,
            messageBody=message,
            contentType="text/html")
        print "sent: ", unicode(response).encode('utf-8')
        return response
    else:
        sys.stderr.write("Can't send message. No Synapse object configured\n")



