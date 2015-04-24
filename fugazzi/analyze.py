from argparse import ArgumentParser
from itertools import groupby, imap

from numpy import array
from prettytable import PrettyTable
import psycopg2
from sklearn.cluster import KMeans


def build_parser():
    parser = ArgumentParser()
    parser.add_argument("--db-user", default="fugazzi", help="The name of the db user")
    parser.add_argument("--db-password", help="The database password")
    parser.add_argument("--storage-db", default="amazon_ratings", help="The name of the db to connect to in postgres")
    parser.add_argument("-l" , "--limit", type=int, help="Limit the number of reviews to analyze")
    return parser


def normalize_time(data):
    """
    Normalize the time data that we get assuming its in form

    [(time1, rating1), (time2, rating2), ...]

    The times should be in the range [0,1] afterwards
    """
    minimum = float(min(data, key=lambda x: x[0])[0])
    maximum = float(max(data, key=lambda x: x[0])[0])
    if minimum == maximum:
        return data
    return map(lambda x: ((int(x[0]) - minimum) / (maximum - minimum), x[1]), data)


def get_data(db_name, username, password, limit):
    """
    Get all review data from the db.
    """
    db_connection = psycopg2.connect(dbname=db_name, user=username, password=password)
    cursor = db_connection.cursor()
    # This might prove to be a bad idea when we have a ton of reviews but for now who cares
    cmd = "select * from reviews;" if not limit else "select * from reviews limit {};".format(limit)
    cursor.execute(cmd)
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

    [(asin, [(item0_1.strftime(%s), item0_3), (item1_1.strftime(%s),...)], (...), ...]

    Each sublist corresponds to dates and ratings of reviews for a specific product.
    At the moment we don't care which one, we just care that it's distinct. Products
    can be iterated over and analyzed this way while reducing memory impact from all
    the data sloshing around.
    """
    data = iter(sorted(data, key=lambda x: x[-1]))
    grouping = groupby(data, lambda x: x[-1])  # The last item in x is the asin
    return imap(
        lambda asin_group: (asin_group[0], map(
            lambda entry: (entry[1].strftime("%s"), entry[3]), asin_group[-1]
        )),
    grouping)


def perform_kmeans(data):
    for asin, asin_data in data:
        if not asin_data:
            continue
        results = []
        #asin_data = array(normalize_time(asin_data))
        for clusters in range(2, 11):
            if clusters > len(asin_data):
                break
            kmeans = KMeans(n_clusters=clusters)
            kmeans.fit(asin_data)
            score = kmeans.score(asin_data)
            try:
                previous_score = results[-1][1]
            except IndexError:
                improvement = 0.0
            else:
                improvement = (score - previous_score) / previous_score

            results.append((clusters, score, improvement))
        pt = PrettyTable(["clusters", "score", "improvement"])
        for item in results:
            pt.add_row(item)
        print "Results for asin {}:".format(asin)
        print pt
        raw_input("Would you like to continue? ^C gets you out of here!")


def main():
    args = build_parser().parse_args()
    all_data = get_data(args.storage_db, args.db_user, args.db_password, args.limit)
    transformed_data = get_date_to_ratings_data(all_data)
    perform_kmeans(transformed_data)


if __name__ == "__main__":
    main()
