from datetime import datetime

from nose.tools import eq_

from fugazzi.analyze import get_date_to_ratings_data, normalize_time


def test_get_date_to_ratings_data():
    now = datetime.now()
    data = [(None, now, None, 1.0, None, None, None, "54"),
            (None, now, None, 1.0, None, None, None, "45"),
            (None, now, None, 0.8, None, None, None, "45")]
    first = ('54', [(now.strftime("%s"), 1.0)])
    second = ('45', [(now.strftime("%s"), 1.0), (now.strftime("%s"), 0.8)])
    output = get_date_to_ratings_data(data)
    eq_(output.next(), first)
    eq_(output.next(), second)


def test_normalize_time():
    now = int(datetime.now().strftime("%s"))
    later = now + 100
    intermediate = now + 50
    data = [(now, 1.0), (intermediate, 0.4), (later, 0.2)]
    expected = [(0.0, 1.0), (0.5, 0.4), (1.0, 0.2)]
    result = normalize_time(data)
    eq_(expected, result)
