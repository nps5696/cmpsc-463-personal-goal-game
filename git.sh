#!/bin/bash

# Old and new credentials
OLD_EMAIL="nsizov@pebblepost.com"
CORRECT_NAME="nps5696"
CORRECT_EMAIL="nps5696@psu.edu"

# Filter-branch command
git filter-branch --env-filter '
OLD_EMAIL="'"$OLD_EMAIL"'"
CORRECT_NAME="'"$CORRECT_NAME"'"
CORRECT_EMAIL="'"$CORRECT_EMAIL"'"
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags

