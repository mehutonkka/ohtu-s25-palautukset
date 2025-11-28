class TennisGame:
    POINTS_FOR_WIN = 4
    ADVANTAGE_POINT = 1
    WIN_POINT_DIFF = 2
    def __init__(self, player1_name, player2_name):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_points = 0
        self.player2_points = 0
        self.scores = Scores()

    def won_point(self, player_name):
        if player_name == self.player1_name:
            self.player1_points += 1
        else:
            self.player2_points += 1

    def get_score(self):
        if self.player1_points == self.player2_points:
            return self.tied_score()
        if self.endgame():
            return self.endgame_score()
        return self.regular_score()
    
    def tied_score(self):
        if self.player1_points >= 3:
            return "Deuce"
        return self.scores.equal_scores[self.player1_points]
    
    def endgame(self):
        if self.player1_points >= self.POINTS_FOR_WIN or self.player2_points >= self.POINTS_FOR_WIN:
            return True
        return False
    
    def endgame_score(self):
        diff = self.player1_points - self.player2_points
        if diff == self.ADVANTAGE_POINT:
            return f"Advantage {self.player1_name}"
        if diff == -self.ADVANTAGE_POINT:
            return f"Advantage {self.player2_name}"
        if diff >= self.WIN_POINT_DIFF:
            return f"Win for {self.player1_name}"
        return f"Win for {self.player2_name}"
    
    def regular_score(self):
        player1_score = self.scores.point_names[self.player1_points]
        player2_score = self.scores.point_names[self.player2_points]
        return f"{player1_score}-{player2_score}"

class Scores:
    def __init__(self):
        self.equal_scores = {0: "Love-All", 1: "Fifteen-All", 2: "Thirty-All"}
        self.point_names = {0: "Love", 1: "Fifteen", 2: "Thirty", 3: "Forty"}
