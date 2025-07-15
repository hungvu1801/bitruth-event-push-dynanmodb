from insert_items import create_gifts, save_multiple_gifts


def ETL_csv_to_dydb(file_name) -> None:
    table = ""
    gifts = create_gifts(file_name=file_name)
    if not gifts:
        return
    print(gifts)

    print(save_multiple_gifts(table=table, gifts=gifts))
