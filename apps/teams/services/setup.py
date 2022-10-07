import csv
import os


def read_team_info_from_csv():
    """
    Read locations, names, and abbr of teams from CSV.
    Return a dict w/ abbrs as keys and remaining data as values.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "../data/nfl-teams.csv"), "r"
    ) as team_data_file:

        team_reader = csv.reader(team_data_file, delimiter=",")
        next(team_reader)  # Skip headings

        team_dicts = []
        for row in team_reader:
            loc, name, abbr, conf, div = row[1:6]
            team_dict = {
                "loc": loc,
                "name": name,
                "abbr": abbr,
                "conf": conf,
                "div": f"{conf} {div}",
            }
            team_dicts.append(team_dict)

    return team_dicts
