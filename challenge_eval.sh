# Automation of validation and scoring
# Make sure you point to the directory where challenge.py belongs and a log directory must exist for the output
cd ~/ga4gh-dream-challenge/scoring_harness
#---------------------
#Validate submissions
#---------------------
#Remove --send-messages to do rescoring without sending emails to participants
python challenge.py -u "james.eddy@sagebase.org" --acknowledge-receipt --notifications validate --all >> log/score.log 2>&1

# add sleep to avoid precondition errors
sleep 10m

#---------------------------
#Validate submission reports
#---------------------------
#Remove --send-messages to do rescoring without sending emails to participants
python challenge.py -u "james.eddy@sagebase.org" --send-messages --notifications validate_reports --all >> log/score.log 2>&1

#--------------------
#Score submissions
#--------------------
#python challenge.py -u "synpase user here" --send-messages --notifications score --all >> log/score.log 2>&1
