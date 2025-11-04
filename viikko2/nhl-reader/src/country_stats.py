import requests
from player import Player

def main(country):
    url = "https://studies.cs.helsinki.fi/nhlstats/2024-25/players"
    response = requests.get(url).json()

    #print("JSON-muotoinen vastaus:")
    #print(response)

    players = []

    for player_dict in response:
        player = Player(player_dict)
        if player.nationality == country:
            players.append(player)

    players = sorted(players, key=lambda player: player.points, reverse=True)

    print("\nPlayers from ", country, ": \n")
    for player in players:
        print(player)
        #print(player.name, "team", player.team, "goals", player.goals, "assists", player.assists)

    


main('FIN')