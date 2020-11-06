# generate db table name
def table_name(title_data) -> str:
    if type(title_data) == list:
        return (
            '"'
            + title_data[0].replace(" ", "-")
            + "_"
            + title_data[1].replace(" ", "-")
            + '"'
        )
    else:
        return '"' + title_data.replace(" ", "-") + '"'


# turn list into tuples
def tuplify(data: list) -> list:
    return [(d,) for d in data]
