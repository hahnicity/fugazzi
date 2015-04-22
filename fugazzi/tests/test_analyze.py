from datetime import datetime

from fugazzi.analyze import get_date_to_ratings_data


def test_get_date_to_ratings_data():
    now = datetime.now()
    data = [(None, now, None, 1.0, None, None, None, "54"),
            (None, now, None, 1.0, None, None, None, "45"),
            (None, now, None, 0.8, None, None, None, "45")]
    first = [(now.strftime("%s"), 1.0)]
    second = [(now.strftime("%s"), 1.0), (now.strftime("%s"), 0.8)]
    output = get_date_to_ratings_data(data)
    assert output.next() == first
    assert output.next() == second
