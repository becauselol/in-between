import random

class Deck:
    def __init__(self):
        self.cards = self.create_new_set()

    def create_new_set(self):
        cards = list(range(1, 14)) * 4
        random.shuffle(cards)
        return cards
        
    def draw_card(self):
        if len(self.cards) == 0:
            self.cards = self.create_new_set()
        value = self.cards.pop()
        return value

    def num_cards_left(self):
        return len(self.cards)

    def reset(self):
        self.cards = self.create_new_set()
