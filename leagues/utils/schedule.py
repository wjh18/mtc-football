import random
from pprint import pprint
from collections import Counter

from algorithm_x import AlgorithmX

from django.apps import apps


def fetch_league_structure(league):
    teams = league.teams.all()
    conferences = league.conferences.all()
    division_model = apps.get_model('leagues.Division')
    divisions = division_model.objects.filter(conference__league=league)

    league_structure = {
        'teams': teams,
        'conferences': conferences,
        'divisions': divisions,
    }

    return league_structure

def generate_matchups(league_structure):
    matchups = []
    ### Generate divisional matchups
    for division in league_structure['divisions']:
        for team in division.teams.all():
            team_exclude = division.teams.all().exclude(id=team.id)
            for included_team in team_exclude:
                matchups.append([team, included_team])

    ### Generate inter-conference matchups
    for conference in league_structure['conferences']:
        division_list = [div.teams.all() for div in list(conference.divisions.all())]
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
            if pair[0] in good_list_0 or \
               pair[1] in good_list_1:

                a, b = pair[1], pair[0]
            else:
                a, b = pair

            good_list_0.append(a)
            good_list_1.append(b)

        good_list = list(zip(good_list_0, good_list_1))

        for pair in good_list:
            matchups.append(list(pair))

        # For 4 interconference matchups with single division
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

                    matchups.append(matchup)

                    opp_counter += 1
                team_counter += 1

    ### Generate cross-conference matchups
    # Get a queryset of each conferences divisions, one in random order
    afc_divs = league_structure['conferences'].get(name='AFC').divisions.all().order_by('name')
    nfc_divs = league_structure['conferences'].get(name='NFC').divisions.all().order_by('?')
    # Build pairs of cross-conference divisions
    div_pairs = [[t1.teams.all(), t2.teams.all()] for t1, t2 in zip(afc_divs, nfc_divs)]
    
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
                matchups.append(matchup)
                opp_counter += 1
            team_counter += 1
            
    # Generate 1 additional cross-conference matchup per team
    # *Without same div pairs as above (reverse the ordered conf's divisions)
    afc_divs_reversed = afc_divs.reverse()
    div_pairs_2 = [[t1.teams.all(), t2.teams.all()] for t1, t2 in zip(afc_divs_reversed, nfc_divs)]
    for div_pair in div_pairs_2:
        r = 1
        for t1, t2, in zip(div_pair[0], div_pair[1]):
            additional_matchup = [t1, t2]
            if r % 2 == 0:
                additional_matchup.reverse()
            r += 1
            matchups.append(additional_matchup)            
            
    return matchups

def count_matchups(matchups):
    # Generator expression to test amount of matches per team
    total_matchups = Counter(x for match in matchups for x in match)
    # Generator expression to test amount of home games per team
    home_matchups = Counter(match[0] for match in matchups)

def set_schedule(matchups, limit=500):
    # `limit` is a computation limit passed on to the AlgorithmX solver. If
    # it's too small then no solutions will be found. If it's too big then it
    # will take longer to find a solution.

    teams = {team for matchup in matchups for team in matchup}

    # A helper function for creating a new column, and returning its index.
    columns = [0]

    def add_column():
        columns[0] += 1
        return columns[0] - 1

    # Create all the columns for this Exact Cover problem.

    # `matchup[matchup_idx]` represents the fact that the matchup `matchup_idx` has occurred.
    matchup = [add_column() for matchup_idx in range(len(matchups))]

    # `team_in_week[team][week]` represents the fact that `team` has appeared during `week` (either in a matchup or as a bye).
    team_in_week = {team: [add_column() for week in range(18)] for team in teams}

    # `team_bye[team]` represents the fact that `team` has a bye week.
    team_bye = {team: add_column() for team in teams}

    # `week_bye[week][i]` represents the fact that `week` has its `i`-th bye team. (4 <= `week` < 12, 0 <= `i` < 4)
    week_bye = {week: [add_column() for i in range(4)] for week in range(5, 13)}

    rows = []

    # Add rows for matchup assignments.
    for matchup_idx in range(len(matchups)):
        team1, team2 = matchups[matchup_idx]
        for week in range(18):
            tag = (
                'match', (matchup_idx, week),
                'Matchup %s in week %d' % (matchups[matchup_idx], week)
            )
            # This represents the assignment that matchup `matchup_idx` will
            # occur during `week`. In that case the following facts will be fulfilled:
            # - `matchup[matchup_idx]`: Matchup `matchup_idx` has now occurred
            # - `team_in_week[team1][week]`: `team1` has now appeared during `week`.
            # - `team_in_week[team2][week]`: `team2` has now appeared during `week`.
            rows.append(([matchup[matchup_idx], team_in_week[team1][week], team_in_week[team2][week]], tag))

    # Add rows for bye assignments.
    for team in teams:
        for week in range(5, 13):
            for i in range(4):
                tag = (
                    'bye', (team, week),
                    'Team %s is bye during week %d' % (team, week)
                )
                # This represents the assignment that `team` will be team
                # number `i` to be bye during `week`. In this case the
                # following facts will be fulfilled:
                # - `team_in_week[team][week]`: `team` has now appeared during `week`.
                # - `team_bye[team]`: `team` now has a bye week.
                # - `week_bye[week][i]`: `week` now has its `i`-ith bye team.
                rows.append(([team_in_week[team][week], team_bye[team], week_bye[week][i]], tag))

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

    league_model = apps.get_model('leagues.League')
    league = league_model.objects.get(pk=league_id)
    league_structure = fetch_league_structure(league)
    matchups = generate_matchups(league_structure)
    schedule = set_schedule(matchups)

    return schedule

# Test
def test_schedule(league_id="fe386ad0-5c1c-4c55-87e8-755fe1b14543"):
    schedule = create_schedule(league_id)