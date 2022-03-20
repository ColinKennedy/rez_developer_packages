name = "early_package"

version = "1.0.0"

@early()
def requires():
    return ["dependency"]
