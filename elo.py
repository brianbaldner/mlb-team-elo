import math

class Rating:
    def __init__(self, start_elo=1500):
        self.elo = start_elo
    def get_elo(self):
        return self.elo
    def set_elo(self, elo):
        self.elo = elo

def update_elo(winner: Rating, loser: Rating, draw=False, K=30):
    # Calculate the Winning Probability of Player B
    Pw = probability(winner, loser)

    # Calculate the Winning Probability of Player A
    Pl = probability(loser, winner)

    # Update the Elo Ratings
    winner.set_elo(winner.get_elo() + K * ((0.5 if draw else 1) - Pw))
    loser.set_elo(loser.get_elo() + K * ((0.5 if draw else 0) - Pl))

# Function to calculate the Probability
def probability(winner: Rating, loser: Rating):
    # Calculate and return the expected score
    return 1.0 / (1 + math.pow(10, (loser.get_elo() - winner.get_elo()) / 400.0))

