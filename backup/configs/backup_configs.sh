#!/bin/bash

# /!\ This script should be improve later
# This script will create an empty local git repository. And copy / commit
# Modification in this git, each time you call this script

# env variables you may want to change
BACKUP_DIR=${BACKUP_DIR:-"/opt/backups/$HOSTNAME/configs"}
FILE_TO_BACKUP=${FILE_TO_BACKUP:-"/etc/ansible /etc/origin"}

function git_exec {
    git --work-tree=$BACKUP_DIR  --git-dir=$BACKUP_DIR/.git $1
}


# Add small security
if [[ "$1" != "--go" ]]; then
    echo 'Infos:'
    echo '    /!\ This script should be improve later'
    echo '    This script will create an empty local git repository in BACKUP_DIR. And copy / commit'
    echo '    Modification in this git, each time you call this script'
    echo 'Usage:'
    echo "    $0 --go"
    exit 1
fi

if ! [[ -d  $BACKUP_DIR ]]; then
    echo "Create and init the backup dir $BACKUP_DIR ..."
    mkdir -p $BACKUP_DIR
    git_exec "init"
fi

echo "Backup files ..."
rsync -av --delete --exclude="/.git" $FILE_TO_BACKUP $BACKUP_DIR/
echo "Add files in git ..."
git_exec "add -A"
git_exec 'commit -a -m "'$(date +"%Y-%m-%d_%H:%M:%S")'"'
