import requests
from player import Player
from rich import print

class PlayerReader:
    def __init__(self, url):
        self.url = url
        self.players = []
        response = requests.get(self.url).json()

        for player_dict in response:
            player = Player(player_dict)
            self.players.append(player)

    def get_players(self):
        response = requests.get(self.url).json()

        for player_dict in response:
            player = Player(player_dict)
            self.players.append(player)
    


class PlayerStats:
    def __init__(self,reader):
        self.players = reader.players
        

    def top_scorers_by_nationality(self, nation):
        top_scorers = []
        for player in self.players:
            if player.nationality == nation:
                top_scorers.append(player)
        
        top_scorers = sorted(top_scorers, key=lambda player: player.points, reverse=True)
        return top_scorers

    
def main():
    seasons = ["2018-19","2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
    season = input("Season [2018-19/2019-20/2020-21/2021-22/2022-23/2023-24/2024-25/2025-26] (2024-25): ")
    if season not in seasons:
        season = "2024-25"

    nationalities = ["USA", "FIN", "CAN", "SWE", "CZE", "RUS", "SLO", "FRA", "GBR", "SVK", "DEN", "NED", "AUT", "BLR", "GER", "SUI", "NOR", "UZB", "LAT", "AUS"]
    nationality = input("Nationality [USA/FIN/CAN/SWE/CZE/RUS/SLO/FRA/GBR/SVK/DEN/NED/AUT/BLR/GER/SUI/NOR/UZB/LAT/AUS] (): ")
    if nationality not in nationalities:
        main()
    url = f"https://studies.cs.helsinki.fi/nhlstats/{season}/players"
    reader = PlayerReader(url)
    stats = PlayerStats(reader)
    players = stats.top_scorers_by_nationality(nationality)
    

    
    for player in players:
        print(f"[green]{player.name:25}[/green] [red]{player.team:20}[/red] {player.goals:2} + {player.assists:2} = {player.points:2}")
        #print(player.name, "team", player.team, "goals", player.goals, "assists", player.assists)

    


main()