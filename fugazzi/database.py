import re

import psycopg2


def create_connection(db, user, password):
    """
    Create a database connection. Just specify None if you are not using a password
    """
    db_connection = psycopg2.connect(database=db, user=user, password=password)
    cursor = db_connection.cursor()
    cursor.execute("PREPARE review_insert (varchar, timestamp with time zone, char, real, text, varchar, varchar) as insert into reviews values ($1, $2, $3, $4, $5, $6, $7);")
    cursor.close()
    return db_connection


def commit_review(connection, review_dict):
    """
    Commit a review into storage. For now hardcode the schema. It is not guarnateed to
    change drastically anyhow.
    """
    cursor = connection.cursor()
    regex = re.compile(r"'")
    author = regex.sub(r"''", review_dict["author"])
    text = regex.sub(r"''", review_dict["text"])
    title = regex.sub(r"''", review_dict["title"])
    cursor.execute(u"EXECUTE review_insert('{}', '{}', '{}', {}, '{}', '{}', '{}');".format(
        author,
        str(review_dict["date"]),
        review_dict["id"],
        review_dict["rating"],
        text,
        title,
        review_dict["url"],
    ))
    cursor.close()
    connection.commit()
