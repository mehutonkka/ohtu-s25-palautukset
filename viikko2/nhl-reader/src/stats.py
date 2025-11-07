import requests
from player import Player

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
    url = "https://studies.cs.helsinki.fi/nhlstats/2024-25/players"
    reader = PlayerReader(url)
    stats = PlayerStats(reader)
    players = stats.top_scorers_by_nationality("FIN")
    

    
    for player in players:
        print(player)
        #print(player.name, "team", player.team, "goals", player.goals, "assists", player.assists)

    


main()