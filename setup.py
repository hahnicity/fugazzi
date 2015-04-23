from setuptools import find_packages, setup


setup(
    name="fugazzi",
    version="0.1",
    author="Gregory Rehm",
    author_email="grehm87@gmail.com",
    test_suite='tests',
    packages=find_packages(),
    requires=[
        "amazon_scraper",
        "psycopg2",
        "scipy",
    ],
)
