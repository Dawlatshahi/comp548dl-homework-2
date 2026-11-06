"""COMP-548DL Homework 2, Exercise 4."""

import os
from datetime import datetime, timedelta, timezone
from pprint import pprint
from uuid import uuid4

from pymongo import MongoClient


def save_edit(users, documents, doc_id, user_id, edit_id, content, saved_at):
    author = users.find_one({"_id": user_id}, {"name": 1, "email": 1})
    if author is None:
        return False

    edit = {
        "edit_id": edit_id,
        "content": content,
        "saved_at": saved_at,
        "user_id": user_id,
        "name": author["name"],
        "email": author["email"],
    }
    result = documents.update_one(
        {
            "_id": doc_id,
            "collaborators": user_id,
            "edits.edit_id": {"$ne": edit_id},
        },
        {"$push": {"edits": edit}},
    )
    return result.modified_count == 1


def get_edit(documents, doc_id, edit_id):
    result = documents.find_one(
        {"_id": doc_id},
        {"_id": 0, "edits": {"$elemMatch": {"edit_id": edit_id}}},
    )
    edits = result.get("edits", []) if result else []
    return edits[0] if edits else None


def get_history(documents, doc_id):
    result = documents.find_one({"_id": doc_id}, {"_id": 0, "edits": 1})
    if result is None:
        return None
    return sorted(result["edits"], key=lambda edit: (edit["saved_at"], edit["edit_id"]))


def main():
    uri = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017/")
    with MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True) as client:
        client.admin.command("ping")
       
        db = client["hw2_" + uuid4().hex[:12]]
        print("Database:", db.name)
        users, documents = db.users, db.documents
        doc_id, farzana, ali = "doc_1001", "usr_501", "usr_502"
        now = datetime.now(timezone.utc)

        users.insert_many([
            {"_id": farzana, "name": "Farzana", "email": "farzana@homework.test"},
            {"_id": ali, "name": "Ali", "email": "ali@homework.test"},
        ])
        print("\nGet user")
        pprint(users.find_one({"_id": farzana}))

        documents.insert_one({
            "_id": doc_id, "title": "Project notes", "created_at": now,
            "collaborators": [], "edits": [],
        })
        print("\nGet document metadata")
        pprint(documents.find_one({"_id": doc_id}, {"title": 1, "created_at": 1}))

        documents.update_one(
            {"_id": doc_id}, {"$addToSet": {"collaborators": {"$each": [farzana, ali]}}}
        )
        print("\nCollaborators after adding Farzana and Ali")
        pprint(documents.find_one({"_id": doc_id}, {"_id": 0, "collaborators": 1}))


        ali_saved = save_edit(users, documents, doc_id, ali, "edit_002",
                              "Review the data sources.\n", now + timedelta(minutes=2))
        farzana_saved = save_edit(users, documents, doc_id, farzana, "edit_001",
                                  "Define the project goals.\n", now + timedelta(minutes=1))
        assert ali_saved and farzana_saved

        print("\nGet edit_002")
        edit = get_edit(documents, doc_id, "edit_002")
        assert edit and edit["email"] == "ali@homework.test"
        pprint(edit)

        documents.update_one({"_id": doc_id}, {"$pull": {"collaborators": ali}})
        print("\nCollaborators after removing Ali")
        membership = documents.find_one({"_id": doc_id}, {"_id": 0, "collaborators": 1})
        assert membership["collaborators"] == [farzana]
        pprint(membership)

        accepted = save_edit(users, documents, doc_id, ali, "edit_003",
                             "This save should be rejected.\n", now + timedelta(minutes=3))
        assert not accepted
        print("Ali's new edit accepted:", accepted)

        print("\nGet all edits in saved_at order")
        history = get_history(documents, doc_id)
        assert [edit["edit_id"] for edit in history] == ["edit_001", "edit_002"]
        pprint(history)
        print("\nAll demo checks passed.")


if __name__ == "__main__":
    main()
