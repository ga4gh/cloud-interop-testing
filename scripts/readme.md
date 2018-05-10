Challenge Template for Python
=============================

For those writing Synapse challenge scoring applications in Python, these scripts should serve as a starting point giving working examples of many of the tasks typical to running a challenge on Synapse. [Creating a Challenge Space in Synapse](https://www.synapse.org/#!Synapse:syn2453886) is a step-by-step guide to building out a challenge.

## Creating a scoring script

Starting with the scripts in this folder, simple challenges can be set up by creating a **challenge_config.py** with **challenge_config.template.py** and editting the **messages.py**. You'll need to add an evaluation queue for each question in your challenge and write appropriate validation and scoring functions. Then, customize the messages with challenge specific help for your solvers.

In the **challenge_config.template.py**, you can add in separate `validate`, `score1`, `score2`, and `score...` functions for each question in your challenge.  You can name these functions anything you want as long as you set up a evaluation queue and function or file mapping.  
```
evaluation_queues = [
    {
        'id':1,
        'scoring_func':score1
        'validation_func':validate_func
        'goldstandard':'path/to/sc1gold.txt'
    },
    {
        'id':2,
        'scoring_func':score2
        'validation_func':validate_func
        'goldstandard':'path/to/sc2gold.txt'

    }
]
evaluation_queue_by_id = {q['id']:q for q in evaluation_queues}
```

## Example

To create an example challenge:

    python challenge_demo.py demo --no-cleanup

This will create a challenge project with an example wiki and an evaluation queue. Several test files are then submitted to the challenge, which are then validated and scored. The demo command also creates **challenge_config.py** based on **challenge_config.template.py**. You'll need to configure scoring functions and other settings in this file to customize scoring to your own challenge questions.

The challenge.py script has several subcommands that help administrate a challenge. To see all the commands, type:

    python challenge.py -h

To list all submissions to a challenge:

    python challenge.py list [evaluation ID]

All the submissions have been scored at this point. If we wanted to rescore, we could reset the status of a submission:

    python challenge.py reset --status RECEIVED [submission ID]

### Messages and Notifications

The script can send several types of messages, which are configured in **messages.py**. The *--send-messages*
flag instructs the script to email the submitter when a submission fails validation or gets scored. The
*--notifications* flag sends error messages to challenge administrators, whose synapse user IDs must be
added to **challenge_config.py**. The flag *--acknowledge-receipt* is used when there will be a lag between
submission and scoring to let users know their submission has been received and passed validation.

### Validation and Scoring

Let's validate the submission we just reset, with the full suite of messages enabled:

    python challenge.py --send-messages --notifications --acknowledge-receipt validate [evaluation ID]

The script also takes a --dry-run parameter for testing. Let's see if scoring seems to work:

    python challenge.py --send-messages --notifications --dry-run score [evaluation ID]

OK, assuming that went well, now let's score for real:

    python challenge.py --send-messages --notifications score [evaluation ID]

Go to the challenge project in Synapse and take a look around. You will find a leaderboard in the wikis and also a Synapse table that mirrors the contents of the leaderboard. The script can output the leaderboard in .csv format:

    python challenge.py leaderboard [evaluation ID]

The demo script tags the challenge project and other assets with a UUID to ensure that they are uniquely
names. Use the UUID to delete the example and clean up associated resources:

    python challenge_demo.py cleanup [UUID]

### RPy2
Often it's more convenient to write statistical code in R. We've successfully used the [Rpy2](http://rpy.sourceforge.net/) library to pass file paths to scoring functions written in R and get back a named list of scoring statistics. Alternatively, there's R code included in the R folder of this repo to fully run a challenge in R.

## Setting Up Automatic Validation and Scoring on an EC2

Make sure challenge_config.py is set up properly and all the files in this repository are in one directory on the EC2.  Crontab is used to help run the validation and scoring command automatically.  To set up crontab, first open the crontab configuration file:

	crontab -e

Paste this into the file:

	# minute (m), hour (h), day of month (dom), month (mon)                      
	*/10 * * * * sh challenge_eval.sh>>~/challenge_runtimes.log
	5 5 * * * sh scorelog_update.sh>>~/change_score.log

Note: the first 5 * stand for minute (m), hour (h), day of month (dom), and month (mon). The configuration to have a job be done every ten minutes would look something like */10 * * * *
