import numpy as np
import matplotlib.pyplot as plt
import random

# Constants
CARD_VALUES = list(range(1, 14))  # Ace = 1, King = 13
NUM_PLAYERS = 4

def draw_card(deck):
    """Draw a card from the deck. Refill and shuffle if empty."""
    if not deck:
        deck.extend(CARD_VALUES * 4)
        random.shuffle(deck)
    return deck.pop()

def choose_bet_amount(window_size, pot):
    """
    Strategy: Bet proportionally to window size.
    Larger window => more confident => higher bet.
    Scaled linearly, capped at pot size.
    """
    return pot
    # max_window = 11  # Maximum possible in-between window (e.g., 1 and 13)
    # bet = 20
    # # bet = int((window_size / max_window) * pot)
    # return max(1, min(bet, pot))  # Ensure at least 1, and not more than pot

def simulate_multiplayer_game(num_deck_cycles=1000, k=3, initial_pot=0):
    """
    Simulate multiplayer in-between game with 4 players.
    Each deck cycle counts as one 'round' (52 cards x 4 = 208 cards).
    """
    deck = CARD_VALUES * 4
    random.shuffle(deck)
    pot = initial_pot

    # Track each player's betting stats
    player_balances = [0 for _ in range(NUM_PLAYERS)]
    player_bets = [0 for _ in range(NUM_PLAYERS)]
    player_winnings = [0 for _ in range(NUM_PLAYERS)]
    balance_history = [[] for _ in range(NUM_PLAYERS)]
    end_balance_history = [[0] for _ in range(NUM_PLAYERS)]

    CURRENT_PLAYER = 0

    for _ in range(num_deck_cycles):
        deck = CARD_VALUES * 4
        random.shuffle(deck)

        while len(deck) >= 3:
            player = CURRENT_PLAYER

            # reset pot
            if pot == 0:
                for p in range(NUM_PLAYERS):
                    player_balances[p] -= 1
                pot += NUM_PLAYERS

            if len(deck) < 3:
                for p in range(NUM_PLAYERS):
                    balance_history[p].append(player_balances[p])
                break  # Not enough cards for another play

            card1 = draw_card(deck)
            card2 = draw_card(deck)

            # Rule: Skip if consecutive
            if abs(card1 - card2) == 1:
                for p in range(NUM_PLAYERS):
                    balance_history[p].append(player_balances[p])
                continue

            # Rule: Skip if pair (not simulating higher/lower yet)
            if card1 == card2:
                for p in range(NUM_PLAYERS):
                    balance_history[p].append(player_balances[p])
                continue

            low = min(card1, card2)
            high = max(card1, card2)
            window = high - low - 1

            # Only bet if window > k and pot has enough funds
            if pot == 0:
                print("pot is zero")
                continue
            if window <= k or pot == 0:
                for p in range(NUM_PLAYERS):
                    balance_history[p].append(player_balances[p])
                continue

            bet = choose_bet_amount(window, pot)
            third_card = draw_card(deck)
            player_bets[player] += bet

            if low < third_card < high:
                # Player wins: take amount from pot
                pot -= bet
                player_balances[player] += bet
                player_winnings[player] += bet
            elif third_card == low or third_card == high:
                # if we hit the same card, double the bet paid
                pot += 2 * bet
                player_balances[player] -= 2 * bet
            else:
                # Player loses: add amount to pot
                pot += bet
                player_balances[player] -= bet

            for p in range(NUM_PLAYERS):
                balance_history[p].append(player_balances[p])

            CURRENT_PLAYER += 1
            CURRENT_PLAYER = CURRENT_PLAYER % 4

        for p in range(NUM_PLAYERS):
            end_balance_history[p].append(player_balances[p])

    net_per_round = [[] for _ in range(NUM_PLAYERS)]
    for p in range(NUM_PLAYERS):
        for i in range(1, len(end_balance_history[p])):
            net_per_round[p].append(end_balance_history[p][i] - end_balance_history[p][i - 1])

    # Summarize results
    results = {
        f"Player {i+1}": {
            "Total Bets": player_bets[i],
            "Total Winnings": player_winnings[i],
            "Net Profit": player_balances[i],
            "Net per round": sum(net_per_round[i]) / len(net_per_round[i]),
            "Variance of earnings per round": np.var(net_per_round[i]),
            "ROI": (player_winnings[i] / player_bets[i]) if player_bets[i] > 0 else 0
        }
        for i in range(NUM_PLAYERS)
    }
    results["Final Pot"] = pot
    return balance_history, end_balance_history, results

# Run the simulation
if __name__ == "__main__":
    history, end_balance_history, results = simulate_multiplayer_game(num_deck_cycles=100000, k=7, initial_pot=0)
    for player, stats in results.items():
        if player == "Final Pot":
            print(f"Final pot: {stats}")
        else:
            print(f"\n--- {player} ---")
            for key, value in stats.items():
                print(f"{key}: {value}")

    plt.figure(figsize=(12, 6))
    for i, balances in enumerate(history):
        plt.plot(balances, label=f'Player {i+1}')
    plt.xlabel('Turns')
    plt.ylabel('Player Balance')
    plt.title('Player Balances Over Time in In-Between')
    plt.legend()
    plt.grid(True)
    plt.show() 
