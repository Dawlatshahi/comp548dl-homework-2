# COMP-548DL Homework 2 Exercise 4
**Student Name and ID:** Farzana Asadi (U254N2745)

This demo implements the MongoDB model described in Exercise 3. Open Docker Desktop, then start the local server.

```bash
docker run -d --name hw2-mongo -p 127.0.0.1:27017:27017 mongodb/mongodb-community-server:8.0-ubi8
docker exec hw2-mongo mongosh --quiet --eval 'db.adminCommand({ping: 1})'
```

If the container already exists and is stopped, run `docker start hw2-mongo`. Once the ping reports `ok: 1`, run these commands from the folder containing `demo.py`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python demo.py | tee example-output.txt
```

The demo creates a fresh database per run and prints its name. It inserts and reads users and document metadata, adds and removes collaborators, saves and reads individual edits, and returns a history ordered by timestamp. It checks that Ali's earlier edit survives his removal and that his subsequent save is rejected. The final line should read `All demo checks passed.`
