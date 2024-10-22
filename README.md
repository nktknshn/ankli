# AnKli

AnKli is a command line tool for Anki.

## Commands

- notes-types
- notes
- card-types
- cards
- script
- sync

## Before running commands

```bash
export ANKI2_STORAGE_PATH=/home/user/.local/share/Anki2/User \1/collection.anki2
```

### Sync command

```bash
# get the token
ankli sync login

export ANKI2_HKEY= #the token

# get the status
ankli sync status

# backup the remote collection without touching the local one
ankli sync download /home/user/backup/

# perform the safe sync
ankli sync sync

# perform the full sync overwriting the remote collection
# backup of the remote collection will be created before the sync
ankli sync full upload /home/user/backup/

# perform the full sync overwriting the local collection
# backup of the local collection will be created before the sync
ankli sync full download /home/user/backup/

```

### Notes types 

```bash
# will show a 
ankli notes-types list

# if you want a detailed output
ankli notes-types list -l

# exclude notes types without notes
ankli notes-types list -e

```

### Notes

```bash
ankli notes list
```

### Cards types 

### Cards

### Running scripts

```bash
ankli script run script.py [script_args ...]
```