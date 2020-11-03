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
    elif "_" in title_data:
        return '"' + title_data + '"'
