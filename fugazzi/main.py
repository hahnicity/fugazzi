#!/usr/bin/env python
from argparse import ArgumentParser
from getpass import getpass
from itertools import islice
from warnings import warn

from amazon_scraper import AmazonScraper
from psycopg2 import DataError

from fugazzi.database import commit_review, create_connection


def build_parser():
    parser = ArgumentParser()
    parser.add_argument("search_term", help="The search term to look under")
    parser.add_argument("search_index", help="The category to search under (Books/Games/etc..)")
    parser.add_argument("access_key", help="Amazon Advertising API access key")
    parser.add_argument(
        "-m", "--max-reviews", type=int, default=None, help="The maximum number of reviews to iterate over"
    )
    parser.add_argument("--db-user", default="fugazzi", help="The name of the db user")
    parser.add_argument("--db-password", help="The database password")
    parser.add_argument("--storage-db", default="amazon_ratings", help="The name of the db to connect to in postgres")
    return parser


def parse_reviews(amazon, db_connection, reviews):
    """
    Fully parse through all the reviews for a product and store them all in the db
    """
    for review in reviews.parse_reviews_on_page():
        try:
            commit_review(db_connection, review.to_dict())
        except (DataError, Exception) as error:  # Be nice, just continue. For now catch all exceptions. This will not be the case in the future.
            warn("Dropping review due to {}".format(error.message))
            continue
    if reviews.next_page_url:
        parse_reviews(amazon, db_connection, amazon.reviews(URL=reviews.next_page_url))


def main():
    args = build_parser().parse_args()
    secret_key = getpass("Enter your secret key: ")
    amazon = AmazonScraper(args.access_key, secret_key, "tagtag")  # The tagtag thing is temporary
    db_connection = create_connection(args.storage_db, args.db_user, args.db_password)
    # If args.max_reviews is None then the generator will continue until the end
    generator = islice(amazon.search(Keywords=args.search_term, SearchIndex=args.search_index), args.max_reviews)
    for item in generator:
        reviews = amazon.reviews(URL=item.reviews_url)
        parse_reviews(amazon, db_connection, reviews)
    db_connection.close()



if __name__ == "__main__":
    main()
