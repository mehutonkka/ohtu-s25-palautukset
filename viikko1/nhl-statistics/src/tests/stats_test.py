import unittest
from statistics_service import StatisticsService, SortBy
from player import Player

class PlayerReaderStub:
    def get_players(self):
        return [
            Player("Semenko", "EDM", 4, 12),  #  4+12 = 16
            Player("Lemieux", "PIT", 45, 54), # 45+54 = 99
            Player("Kurri",   "EDM", 37, 53), # 37+53 = 90
            Player("Yzerman", "DET", 42, 56), # 42+56 = 98
            Player("Gretzky", "EDM", 35, 89)  # 35+89 = 124
        ]

class TestStatisticsService(unittest.TestCase):
    def setUp(self):
        # annetaan StatisticsService-luokan oliolle "stub"-luokan olio
        self.stats = StatisticsService(
            PlayerReaderStub()
        )
    def test_top(self):
        self.stats.top(1)
        self.stats.top(4, SortBy.GOALS)
        self.stats.top(3, SortBy.ASSISTS)
        self.stats.top(2, SortBy.POINTS)

    def test_search(self):
        self.stats.search("Gretzky")
        self.stats.search("moi")

    def test_team(self):
        self.stats.team("PIT")