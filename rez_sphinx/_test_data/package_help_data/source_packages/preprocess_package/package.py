name = "package_to_test"

version = "2.1.0"

help = [["foo", "bar"]]


def preprocess(*_, **item):
    # An example function that does nothing. It's just used for unittesting
    data = item["data"]
    this = item["this"]
