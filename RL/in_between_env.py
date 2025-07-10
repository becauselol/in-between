import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import math
from deck import Deck
from typing import Type

CARD_VALUES = list(range(1, 14))  # Ace = 1, King = 13
NUM_CARDS = 13

class InBetweenEnv(gym.Env):
    def __init__(self, deck_class: Type[Deck], n_players=2):
        super().__init__()

        self.deck_class = deck_class
        self.deck = Deck()
        self.pot = 0
        self.n_players = n_players
        # 0 represents passing while any number between 1 to 20 is * 5 * pot size
        self.action_space = spaces.Discrete(21)
        # this is just the value of the two cards to bet
        self.observation_space = spaces.MultiDiscrete([12, 11])

        # store card observations
        self.low = -1
        self.high = -1

    def _pot_bin(self, pot):
        if pot == 0:
            return 0
        value = math.floor(math.log10(pot) * 6)
        if value < 0:
            print(self.pot)
            print(value)
        return int(min(value, 10))

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.deck = Deck()
        self.pot = 1

        # we need to reset the deck
        c1 = self.deck.draw_card()
        c2 = self.deck.draw_card()
        if c1 < c2:
            self.low = c1
            self.high = c2
        else:
            self.low = c2
            self.high = c1
        while self.deck.num_cards_left() >= 3 and abs(self.low - self.high) <= 1:
            # do we draw?
            # we need to reset the deck
            if self.deck.num_cards_left() < 3:
                self.deck.reset()

            c1 = self.deck.draw_card()
            c2 = self.deck.draw_card()
            if c1 < c2:
                self.low = c1
                self.high = c2
            else:
                self.low = c2
                self.high = c1

        obs = (self.high - self.low - 1, self._pot_bin(self.pot))
        return obs, {}

    def _get_card_obs(self):
        # we need to reset the deck
        c1 = self.deck.draw_card()
        c2 = self.deck.draw_card()
        if c1 < c2:
            self.low = c1
            self.high = c2
        else:
            self.low = c2
            self.high = c1
        while self.deck.num_cards_left() >= 3 and abs(self.low - self.high) <= 1:
            # we need to reset the deck
            c1 = self.deck.draw_card()
            c2 = self.deck.draw_card()
            if c1 < c2:
                self.low = c1
                self.high = c2
            else:
                self.low = c2
                self.high = c1

        if self.deck.num_cards_left() < 3:
            return False

        return self.high - self.low - 1
        
    def step(self, action):
        if self.deck.num_cards_left() < 3:
            return (-1, 0), 0, True, False, {}

        if action == 0:
            if self.pot <= 0:
                self.pot = 1

            return (self._get_card_obs(), self._pot_bin(self.pot)), -1, self.deck.num_cards_left() < 3, False, {}
            
        bet = math.floor((action * 5)/100 * self.pot)

        target = self.deck.draw_card()
        reward = 0
        if self.low < target < self.high:
            self.pot -= bet
            reward = bet
        elif target in (self.low, self.high):
            self.pot += 2 * bet
            reward -= 2 * bet
        else:
            self.pot += bet
            reward -= bet

        if self.pot <= 0:
            self.pot = 1
            reward -= 1
            
        
        card_obs = self._get_card_obs()
        if card_obs == False:
            return (-1, 0), 0, True, False, {}

        obs = (card_obs, self._pot_bin(self.pot))
        return obs, reward, self.deck.num_cards_left() < 3, False, {}