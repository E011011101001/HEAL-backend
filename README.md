# HEAL Backend

You can find the front-end project [here](https://github.com/chrisrauch193/HEAL-frontend).

## Develop Guide

### Requirements

1. Prepare Python or a Python virtual environment.

2. Run `pip install -r requirements.txt` to install dependencies.

3. Use `.env.example` as a template to create `.env`, or export to the environment.

4. Run `./run.sh` to start the backend server in debug mode.

## If you need to delete the entire database and reinitialise it

```bash
rm src/database/database.db
./run.sh
```

## NOTE

If there is no db file currently then the run.sh command will create it
