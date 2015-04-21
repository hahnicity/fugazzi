from multiprocessing import Pool
import psycopg2
import dill
import pickle


def insert(int_):
    connection = psycopg2.connect(database="amazon_ratings", user="fugazzi", password="fugazzi")
    cursor = connection.cursor()
    cursor.execute("insert into threading_test values ({});".format(int_))
    cursor.close()
    connection.commit()


def main():
    pool = Pool(10)
    results = pool.map(insert, range(100))
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
