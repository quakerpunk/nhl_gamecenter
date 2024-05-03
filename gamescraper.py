from bs4 import BeautifulSoup
import re

def make_soup(url):
    #soup = BeautifulSoup(gamecenter_html, 'html.parser')
    #if (debug):
    #    with open("test_gamecenter.html") as fp:
    #        soup = BeautifulSoup(fp, 'html.parser')
    #else:
    import requests
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    return soup

def convert_player_data(raw_player_data):
    player_expression = re.match(r"\d{1,2} \w{1}\.(?P<player_name>\w+)(?P<goal_number>\(\d{1,2}\))",raw_player_data)
    return "{} {}".format(
        player_expression.group('player_name').title(),
        player_expression.group('goal_number'))

def convert_period(period_int):
    period_int = int(period_int)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(period_int % 10, 4)]
    if 1 <= period_int <= 3:
        return str(period_int) + suffix
    elif period_int >= 4:
        period_int = period_int - 3
        return str(period_int) + suffix + " OT"

def get_three_stars(url):
    gamecenter = make_soup(url)

def build_goals_dict(url):
    gamecenter = make_soup(url)
    all_goals = {}
    # get the fourth table row form the MainTable id'd table
    scoring_summary = gamecenter.select("#MainTable > tr:nth-child(4) table")[0]
    for row in scoring_summary.find_all("tr", class_=True):
        # Reset primary and secondary assists each time so we don't use old data.
        primary_assist = ""
        secondary_assist = ""
        cells = row.find_all("td")

        # The NHL records penalty shots in the scoring summary whether they're successful or not.
        # We can filter these out if the cell has a colspan attribute
        bad_cell = row.find_all("td", attrs={"colspan": True})
        if bad_cell:
            continue

        period = convert_period(cells[1].string)
        scoring_team = cells[4].string
        goal_type = cells[3].string
        goal_scorer = convert_player_data(cells[5].get_text())
        if cells[6].string and cells[6].string != "unassisted":
            primary_assist = " from {}".format(convert_player_data(cells[6].string))
            if cells[7].string:
                secondary_assist = " and {}".format(convert_player_data(cells[7].string))
        time_of_goal = cells[2].string
        full_goal_text = '- {scoring_team} - {goal_type} - {goal_scorer}{primary_assist}{secondary_assist} - {time_of_goal}'.format(
            scoring_team=scoring_team, goal_type=goal_type, goal_scorer=goal_scorer, primary_assist=primary_assist, secondary_assist=secondary_assist,time_of_goal=time_of_goal)
        if period in all_goals.keys():
            all_goals[period].append(full_goal_text)
        else:
            all_goals[period] = [full_goal_text]
    return all_goals

def get_goals(url, **header_details):
    goals_by_period = build_goals_dict(url)
    header_level = header_details['header_level'] or 3
    header_symbol =  header_details['header_symbol'] or '*'
    goal_string = ""

    for period, goals in goals_by_period.items():
        goal_string += (header_symbol * header_level) + " " + period + "\n"
        goal_string += "\n".join(goals)
        goal_string += "\n"
    return goal_string


if __name__ == "__main__":
    test_url = "https://www.nhl.com/scores/htmlreports/20232024/GS030152.HTM"
    print(get_goals(test_url, header_symbol='*', header_level=3))
