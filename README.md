# HEAL Backend

You can find the front-end project [here](https://github.com/chrisrauch193/HEAL-frontend).

## Develop Guide

### Requirements

1. Prepare Python or a Python virtual environment.

2. Run `pip install -r requirements.txt` to install dependencies.

3. Use `.env.example` as a template to create `.env`, or export to the environment.

4. Run `./run.sh` to start the backend server in debug mode.

## One Time Only Initial Setup

Setup virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Install all dependencies

```bash
pip install -r requirements.txt
```

Create .env file for flask

```bash
cp .env.example .env
```

Initialise new database

```bash
sqlite3 src/database/database.db < src/database/init.sql
```

Now you can run the flask server anytime using the following command

```bash
./run.sh
```

If you are finished working and don't want to use the virtual environment (venv) anymore...

```bash
deactivate
```

## General Setup Anytime After Initial Setup

```bash
source venv/bin/activate
./run.sh
```

## If you need to delete the entire database and reinitialise it

```bash
rm src/database/database.db
sqlite3 src/database/database.db < src/database/init.sql
```
