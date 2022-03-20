name = "late_package"

version = "1.0.0"

@late()
def requires():
    return ["dependency"]
