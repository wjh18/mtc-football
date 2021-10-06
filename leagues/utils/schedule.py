import random
from pprint import pprint
from collections import Counter

from algorithm_x import AlgorithmX

from django.apps import apps


def fetch_league_structure(league):
    Division = apps.get_model('leagues.Division')
    teams = league.teams.all()
    conferences = league.conferences.all()
    divisions = Division.objects.filter(conference__in=conferences)

    league_structure = {
        'teams': teams,
        'conferences': conferences,
        'divisions': divisions,
    }

    return league_structure


def generate_div_matchups(league_structure):
    """
    Generate divisional matchups (6 total per team):
    2 per team from the same division (2m x 3t)
    """
    div_matchups = []
    for division in league_structure['divisions']:
        for team in division.teams.all():
            for rival_team in division.teams.all().exclude(id=team.id):
                div_matchups.append([team, rival_team])

    return div_matchups


def generate_conf_matchups(league_structure):
    """
    Generate inter-conference matchups (6 total per team):
    1 matchup against each team in a single same conf division (1m x 4t)
    1 matchup against a team from the 2 remaining same conf divs (1m x 2t)
    """
    conf_matchups = []
    for conference in league_structure['conferences']:
        # Pair up divisions
        division_list = [div.teams.all() \
                         for div in list(conference.divisions.all())]
        division_pair1 = random.sample(division_list, 2)
        division_pair2 = (list(set(division_list) - set(division_pair1)))
        division_pairs = [division_pair1, division_pair2]

        # Generate 2 additional interconference matchups
        opposite_pairs = []
        for d in division_pairs[0]:
            for div in division_pairs[1]:
                new_pair = [d, div]
                opposite_pairs.append(new_pair)

        matchups3 = []
        for new_pair in opposite_pairs:
            for t1, t2 in zip(new_pair[0], new_pair[1]):
                matchup3 = [t1, t2]
                matchups3.append(matchup3)

        # Ensure that each team has one home and one away game
        good_list_0 = []
        good_list_1 = []
        for pair in matchups3:
            if pair[0] in good_list_0 or pair[1] in good_list_1:
                a, b = pair[1], pair[0]
            else:
                a, b = pair
            good_list_0.append(a)
            good_list_1.append(b)

        good_list = list(zip(good_list_0, good_list_1))
        for pair in good_list:
            conf_matchups.append(list(pair))

        # Generate 4 interconference matchups against a single division
        for div_pair in division_pairs:
            team_counter = 1
            for team in div_pair[0]:
                opp_counter = 1
                for opponent in div_pair[1]:

                    if team_counter % 2 == 0:
                        matchup = [team, opponent]
                    else:
                        matchup = [opponent, team]

                    if opp_counter % 2 != 0:
                        matchup.reverse()

                    conf_matchups.append(matchup)

                    opp_counter += 1
                team_counter += 1

    return conf_matchups


def generate_non_conf_matchups(league_structure):
    """
    Generate non-conf matchups (5 total per team):
    1 matchup against each team in a single non-conf division (1m x 4t)
    1 matchup against a team from a different non-conf div (1m x 1t)
    """
    non_conf_matchups = []

    # Queryset of each conference's divisions, one in random order
    conf1, conf2 = league_structure['conferences'][0], \
                   league_structure['conferences'][1]
    conf1_divs = conf1.divisions.all().order_by('name')
    conf2_divs = conf2.divisions.all().order_by('?')

    # Build pairs of cross-conference divisions
    div_pairs = [[t1.teams.all(), t2.teams.all()] \
                 for t1, t2 in zip(conf1_divs, conf2_divs)]

    # Generate matchups with cross-conference division pairs
    for div_pair in div_pairs:
        team_counter = 1
        for team in div_pair[0]:
            opp_counter = 1
            for opponent in div_pair[1]:
                if team_counter % 2 == 0:
                    matchup = [team, opponent]
                else:
                    matchup = [opponent, team]
                if opp_counter % 2 != 0:
                    matchup.reverse()
                non_conf_matchups.append(matchup)
                opp_counter += 1
            team_counter += 1

    # Build new, unique div pairs (reverse the ordered conf's divisions)
    conf1_divs_reversed = conf1_divs.reverse()
    new_div_pairs = [[t1.teams.all(), t2.teams.all()] \
                     for t1, t2 in zip(conf1_divs_reversed, conf2_divs)]

    # Generate 1 additional cross-conference matchup per team
    for div_pair in new_div_pairs:
        home_or_away = 1
        for t1, t2, in zip(div_pair[0], div_pair[1]):
            additional_matchup = [t1, t2]
            if home_or_away % 2 == 0:
                additional_matchup.reverse()
            home_or_away += 1
            non_conf_matchups.append(additional_matchup)

    return non_conf_matchups


def generate_matchups(league_structure):
    matchups = []

    ### Generate divisional matchups
    div_matchups = generate_div_matchups(league_structure)
    matchups.extend(div_matchups)

    ### Generate conference matchups
    conf_matchups = generate_conf_matchups(league_structure)
    matchups.extend(conf_matchups)

    ### Generate cross-conference matchups
    non_conf_matchups = generate_non_conf_matchups(league_structure)
    matchups.extend(non_conf_matchups)
            
    return matchups


def set_schedule(matchups, limit=500):
    # `limit` is a computation limit passed on to the AlgorithmX solver. If
    # it's too small then no solutions will be found. If it's too big then it
    # will take longer to find a solution.

    teams = {team for matchup in matchups for team in matchup}
    columns = [0]

    def add_column():
        """A helper function for creating a new column,
        and returning its index."""
        columns[0] += 1
        return columns[0] - 1

    # Create all the columns for this Exact Cover problem.

    # `matchup[matchup_idx]` -> matchup `matchup_idx` has occurred.
    matchup = [add_column() for matchup_idx in range(len(matchups))]

    # `team_in_week[team][week]` -> `team` had matchup or bye during `week`.
    team_in_week = {team: [add_column() for week in range(18)] \
                    for team in teams}

    # `team_bye[team]` -> `team` has a bye week.
    team_bye = {team: add_column() for team in teams}

    # `week_bye[week][i]` -> `week` has its `i`-th bye team.
    # (4 <= `week` < 12, 0 <= `i` < 4)
    week_bye = {week: [add_column() for i in range(4)] \
                for week in range(5, 13)}

    rows = []

    # Add rows for matchup assignments.
    for matchup_idx in range(len(matchups)):
        team1, team2 = matchups[matchup_idx]
        for week in range(18):
            tag = (
                'match', (matchup_idx, week),
                'Matchup %s in week %d' % (matchups[matchup_idx], week)
            )
            # Represents that matchup `matchup_idx` will occur during `week`.
            # In this case the following facts will be fulfilled:
            # - `matchup[matchup_idx]`: Matchup `matchup_idx` has occurred.
            # - `team_in_week[team1][week]`: `team1` has appeared in `week`.
            # - `team_in_week[team2][week]`: `team2` has appeared in `week`.
            rows.append(([
                matchup[matchup_idx],
                team_in_week[team1][week],
                team_in_week[team2][week]
            ], tag))

    # Add rows for bye assignments.
    for team in teams:
        for week in range(5, 13):
            for i in range(4):
                tag = (
                    'bye', (team, week),
                    'Team %s is bye during week %d' % (team, week)
                )
                # Represents that `team` is team number `i` with bye in `week`.
                #  In this case the following facts will be fulfilled:
                # - `team_in_week[team][week]`: `team` has appeared in `week`.
                # - `team_bye[team]`: `team` now has a bye week.
                # - `week_bye[week][i]`: `week` now has its `i`-ith bye team.
                rows.append(([
                    team_in_week[team][week],
                    team_bye[team], week_bye[week][i]
                ], tag))

    while True:
        # Create an AlgorithmX solver with the specified number of columns.
        solver = AlgorithmX(columns[0])

        # Shuffle the rows and add to the solver.
        random.shuffle(rows)
        for row, tag in rows:
            solver.appendRow(row, tag)

        # Try to find a solution within the given computation limit.
        for solution in solver.solve(limit=limit):

            # A solution was found! Convert it to a schedule and return it.
            schedule = [[] for week in range(18)]
            for (tp, args, desc) in solution:
                if tp == 'match':
                    matchup_idx, week = args
                    schedule[week].append(matchups[matchup_idx])

            return schedule

        # No solution was found. Shuffle and retry!


def create_schedule(league_id):

    League = apps.get_model('leagues.League')
    league = League.objects.get(pk=league_id)
    league_structure = fetch_league_structure(league)
    matchups = generate_matchups(league_structure)
    schedule = set_schedule(matchups)

    return schedule


# # Tests

# def test_schedule(league_id="fe386ad0-5c1c-4c55-87e8-755fe1b14543"):
#     schedule = create_schedule(league_id)


# def count_matchups(matchups):
#     # Generator expression to test amount of matches per team
#     total_matchups = Counter(x for match in matchups for x in match)
#     # Generator expression to test amount of home games per team
#     home_matchups = Counter(match[0] for match in matchups)
