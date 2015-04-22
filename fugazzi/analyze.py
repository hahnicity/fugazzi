from argparse import ArgumentParser
from itertools import groupby, imap

import psycopg2


def build_parser():
    parser = ArgumentParser()
    parser.add_argument("--db-user", default="fugazzi", help="The name of the db user")
    parser.add_argument("--db-password", help="The database password")
    parser.add_argument("--storage-db", default="amazon_ratings", help="The name of the db to connect to in postgres")
    return parser


def get_data(db_name, username, password):
    """
    Get all review data from the db.
    """
    db_connection = psycopg2.connect(dbname=db_name, user=username, password=password)
    cursor = db_connection.cursor()
    # This might prove to be a bad idea when we have a ton of reviews but for now who cares
    cursor.execute("select * from reviews;")
    all_data = iter(cursor.fetchall())
    cursor.close()
    db_connection.close()
    return all_data


def get_date_to_ratings_data(data):
    """
    Transform the data so that reviews are grouped by asin and that it only returns
    datetime (normalized on [0,1]) and the rating.

    This thing should get some unit tests cause the logic is a bit silly. Takes a data stuct that
    looks like
    [(item0_0, item0_1, ...), (item1_0, item1_1, ...), ...]

    and transforms it to

    [[(item0_1.strftime(%s), item0_3), (item1_1.strftime(%s), ...),...] ...]

    Each sublist corresponds to dates and ratings of reviews for a specific product.
    At the moment we don't care which one, we just care that it's distinct. Products
    can be iterated over and analyzed this way while reducing memory impact from all
    the data sloshing around.
    """
    grouping = groupby(data, lambda x: x[-1])  # The last item is the asin
    return imap(
        lambda asin_group: map(
            lambda entry: (entry[1].strftime("%s"), entry[3]), asin_group[-1]
        ),
    grouping)



def main():
    args = build_parser().parse_args()
    all_data = get_data(args.storage_db, args.db_user, args.db_password)
    transformed_data = get_date_to_ratings_data(all_data)


if __name__ == "__main__":
    main()
