#!/usr/bin/env python3
import os
import time
import random
import sys
import json
import pickle
from datetime import datetime
from poker.game import PokerGame
from poker.player import Player, BotPlayer
from poker.evaluator import HandEvaluator

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

# Card suit symbols
HEARTS = f"{Colors.RED}♥{Colors.RESET}"
DIAMONDS = f"{Colors.RED}♦{Colors.RESET}"
CLUBS = f"{Colors.BLACK}♣{Colors.RESET}"
SPADES = f"{Colors.BLACK}♠{Colors.RESET}"

# Global variable to track round actions
round_actions = []

class PlayerStats:
    """Track player statistics across multiple hands."""
    def __init__(self, player_name):
        self.player_name = player_name
        self.hands_played = 0
        self.hands_won = 0
        self.chips_won = 0
        self.chips_lost = 0
        self.biggest_pot_won = 0
        self.best_hand = None
        self.best_hand_type = None
        self.fold_percentage = 0
        self.folds = 0
        self.calls = 0
        self.checks = 0
        self.bets = 0
        self.raises = 0
        self.all_ins = 0
    
    def update_action_stats(self, action_type):
        """Update action statistics."""
        if action_type == "fold":
            self.folds += 1
        elif action_type == "call":
            self.calls += 1
        elif action_type == "check":
            self.checks += 1
        elif action_type == "bet":
            self.bets += 1
        elif action_type == "raise":
            self.raises += 1
        elif action_type == "all-in":
            self.all_ins += 1
        
        # Calculate fold percentage
        total_actions = self.folds + self.calls + self.checks + self.bets + self.raises + self.all_ins
        if total_actions > 0:
            self.fold_percentage = (self.folds / total_actions) * 100
    
    def update_hand_stats(self, won, pot_size=0, hand=None, hand_type=None):
        """Update hand statistics."""
        self.hands_played += 1
        
        if won:
            self.hands_won += 1
            self.chips_won += pot_size
            
            if pot_size > self.biggest_pot_won:
                self.biggest_pot_won = pot_size
        else:
            self.chips_lost += pot_size
        
        # Update best hand if applicable
        if hand and hand_type:
            if not self.best_hand or self._is_better_hand(hand_type, self.best_hand_type):
                self.best_hand = hand
                self.best_hand_type = hand_type
    
    def _is_better_hand(self, new_type, old_type):
        """Compare hand types to determine which is better."""
        hand_ranks = {
            "High Card": 0,
            "Pair": 1,
            "Two Pair": 2,
            "Three of a Kind": 3,
            "Straight": 4,
            "Flush": 5,
            "Full House": 6,
            "Four of a Kind": 7,
            "Straight Flush": 8,
            "Royal Flush": 9
        }
        
        return hand_ranks.get(new_type, 0) > hand_ranks.get(old_type, 0)
    
    def get_win_percentage(self):
        """Get the win percentage."""
        if self.hands_played == 0:
            return 0
        return (self.hands_won / self.hands_played) * 100
    
    def get_net_profit(self):
        """Get the net profit."""
        return self.chips_won - self.chips_lost

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_suit_symbol(suit):
    """Get the colored symbol for a card suit."""
    if suit == 'hearts':
        return HEARTS
    elif suit == 'diamonds':
        return DIAMONDS
    elif suit == 'clubs':
        return CLUBS
    elif suit == 'spades':
        return SPADES
    return suit

def print_card(card, hidden=False):
    """Print a single card with ASCII art."""
    if hidden:
        print(f"┌─────────┐")
        print(f"│░░░░░░░░░│")
        print(f"│░░░░░░░░░│")
        print(f"│░░░░░░░░░│")
        print(f"└─────────┘")
        return

    rank = card.rank
    suit = get_suit_symbol(card.suit)
    
    # Adjust display for 10
    if rank == '10':
        rank_display = '10'
    else:
        rank_display = f"{rank} "
    
    print(f"┌─────────┐")
    print(f"│ {rank_display}      │")
    print(f"│    {suit}    │")
    print(f"│      {rank_display}│")
    print(f"└─────────┘")

def print_cards_horizontal(cards, hidden=False):
    """Print multiple cards horizontally."""
    if not cards:
        return
    
    lines = [[] for _ in range(5)]
    
    for card in cards:
        if hidden:
            card_lines = [
                "┌─────────┐",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "└─────────┘"
            ]
        else:
            rank = card.rank
            suit = get_suit_symbol(card.suit)
            
            # Adjust display for 10
            if rank == '10':
                rank_display = '10'
                rank_display_end = '10'
            else:
                rank_display = f"{rank} "
                rank_display_end = f" {rank}"
            
            card_lines = [
                "┌─────────┐",
                f"│ {rank_display}      │",
                f"│    {suit}    │",
                f"│      {rank_display_end}│",
                "└─────────┘"
            ]
        
        for i, line in enumerate(card_lines):
            lines[i].append(line)
    
    for line_parts in lines:
        print("  ".join(line_parts))

def animate_card_dealing(game, player_idx=0):
    """Animate dealing cards to players and community cards."""
    clear_screen()
    print(f"\n{Colors.BOLD}{Colors.BG_GREEN}{Colors.WHITE} DEALING NEW HAND {Colors.RESET}\n")
    
    # Animate dealing hole cards to each player
    print(f"{Colors.BOLD}Dealing hole cards...{Colors.RESET}")
    
    # First card to each player
    for i, player in enumerate(game.players):
        time.sleep(0.3)  # Pause between each card deal
        
        # Show dealing animation
        sys.stdout.write(f"\rDealing to {player.name}... ")
        sys.stdout.flush()
        time.sleep(0.2)
        
        # Show the card being dealt
        if i == player_idx:  # Human player
            print(f"You received: ", end="")
            rank = player.hand[0].rank
            suit = get_suit_symbol(player.hand[0].suit)
            print(f"{Colors.BOLD}{rank}{suit}{Colors.RESET}")
        else:
            print(f"Card dealt.")
    
    # Second card to each player
    for i, player in enumerate(game.players):
        time.sleep(0.3)  # Pause between each card deal
        
        # Show dealing animation
        sys.stdout.write(f"\rDealing to {player.name}... ")
        sys.stdout.flush()
        time.sleep(0.2)
        
        # Show the card being dealt
        if i == player_idx:  # Human player
            print(f"You received: ", end="")
            rank = player.hand[1].rank
            suit = get_suit_symbol(player.hand[1].suit)
            print(f"{Colors.BOLD}{rank}{suit}{Colors.RESET}")
        else:
            print(f"Card dealt.")
    
    # Show human player's complete hand
    print(f"\n{Colors.BOLD}Your hand:{Colors.RESET}")
    print_cards_horizontal(game.players[player_idx].hand)
    
    print(f"\n{Colors.BOLD}Press Enter to continue...{Colors.RESET}")
    input()

def animate_community_cards(game, phase):
    """Animate dealing community cards based on the game phase."""
    if phase == 'flop':
        print(f"\n{Colors.BOLD}{Colors.BG_BLUE}{Colors.WHITE} DEALING THE FLOP {Colors.RESET}")
        
        # Animate dealing the flop (3 cards)
        for i in range(3):
            time.sleep(0.5)
            print(f"Dealing community card {i+1}...")
            print_card(game.community_cards[i])
            time.sleep(0.3)
        
        # Show all flop cards together
        print(f"\n{Colors.BOLD}The Flop:{Colors.RESET}")
        print_cards_horizontal(game.community_cards[:3])
        
    elif phase == 'turn':
        print(f"\n{Colors.BOLD}{Colors.BG_BLUE}{Colors.WHITE} DEALING THE TURN {Colors.RESET}")
        
        # Animate dealing the turn (4th card)
        time.sleep(0.5)
        print(f"Dealing the turn...")
        print_card(game.community_cards[3])
        
        # Show all community cards so far
        print(f"\n{Colors.BOLD}Community Cards:{Colors.RESET}")
        print_cards_horizontal(game.community_cards[:4])
        
    elif phase == 'river':
        print(f"\n{Colors.BOLD}{Colors.BG_BLUE}{Colors.WHITE} DEALING THE RIVER {Colors.RESET}")
        
        # Animate dealing the river (5th card)
        time.sleep(0.5)
        print(f"Dealing the river...")
        print_card(game.community_cards[4])
        
        # Show all community cards
        print(f"\n{Colors.BOLD}Community Cards:{Colors.RESET}")
        print_cards_horizontal(game.community_cards)
    
    # Clear round actions when new community cards are dealt
    global round_actions
    round_actions = []
    
    print(f"\n{Colors.BOLD}Press Enter to continue...{Colors.RESET}")
    input()

def calculate_hand_odds(player_hand, community_cards, num_opponents):
    """
    Calculate approximate odds of winning based on current hand and community cards.
    This is a simplified Monte Carlo simulation.
    """
    from poker.deck import Deck
    
    # Number of simulations to run
    NUM_SIMULATIONS = 200
    
    # Create a new deck and remove known cards
    wins = 0
    
    for _ in range(NUM_SIMULATIONS):
        deck = Deck()
        
        # Remove known cards from the deck
        for card in player_hand + community_cards:
            deck.cards = [c for c in deck.cards if not (c.rank == card.rank and c.suit == card.suit)]
        
        # Deal remaining community cards
        remaining_community = []
        for _ in range(5 - len(community_cards)):
            if deck.cards:
                remaining_community.append(deck.deal())
        
        # Complete community cards
        sim_community = community_cards + remaining_community
        
        # Deal opponent hands
        opponent_hands = []
        for _ in range(num_opponents):
            if len(deck.cards) >= 2:
                opponent_hands.append([deck.deal(), deck.deal()])
        
        # Evaluate player's hand
        player_cards = player_hand + sim_community
        player_value = HandEvaluator.evaluate_hand(player_cards)
        
        # Check if player wins
        player_wins = True
        for opp_hand in opponent_hands:
            opp_cards = opp_hand + sim_community
            opp_value = HandEvaluator.evaluate_hand(opp_cards)
            
            # Compare hand values (lower rank index is better)
            if opp_value[0] < player_value[0]:
                player_wins = False
                break
            elif opp_value[0] == player_value[0]:
                # If same hand type, compare kickers
                player_kickers = player_value[2]
                opp_kickers = opp_value[2]
                
                for i in range(min(len(player_kickers), len(opp_kickers))):
                    if opp_kickers[i] > player_kickers[i]:
                        player_wins = False
                        break
                    elif player_kickers[i] > opp_kickers[i]:
                        break
        
        if player_wins:
            wins += 1
    
    # Calculate win percentage
    win_percentage = (wins / NUM_SIMULATIONS) * 100
    return round(win_percentage, 1)

def print_game_state(game, player_idx=0):
    """Print the current state of the game in a visually appealing way."""
    clear_screen()
    
    # Print game header
    print(f"\n{Colors.BOLD}{Colors.BG_GREEN}{Colors.WHITE} TEXAS HOLD'EM POKER {Colors.RESET}\n")
    
    # Print game info
    print(f"{Colors.BOLD}Phase:{Colors.RESET} {game.phase.capitalize()}")
    print(f"{Colors.BOLD}Pot:{Colors.RESET} ${game.pot}")
    print(f"{Colors.BOLD}Current Bet:{Colors.RESET} ${game.current_bet}")
    print()
    
    # Print community cards
    print(f"{Colors.BOLD}{Colors.BG_BLUE}{Colors.WHITE} COMMUNITY CARDS {Colors.RESET}")
    if game.community_cards:
        print_cards_horizontal(game.community_cards)
    else:
        print("No community cards yet")
    print()
    
    # Calculate positions
    dealer_idx = game.dealer_idx
    sb_idx = (dealer_idx + 1) % len(game.players)
    bb_idx = (dealer_idx + 2) % len(game.players)
    
    # Print players
    print(f"{Colors.BOLD}{Colors.BG_MAGENTA}{Colors.WHITE} PLAYERS {Colors.RESET}")
    for i, player in enumerate(game.players):
        is_current = (player == game.current_player)
        is_human = (i == player_idx)
        
        # Highlight current player
        if is_current:
            print(f"{Colors.BG_YELLOW}{Colors.BLACK}", end="")
        
        # Print player info
        print(f"Player: {player.name} ", end="")
        if is_human:
            print(f"({Colors.GREEN}YOU{Colors.RESET})", end="")
        else:
            print(f"({Colors.RED}BOT{Colors.RESET})", end="")
        
        # Print position indicators
        if i == dealer_idx:
            print(f" {Colors.WHITE}{Colors.BG_BLUE}D{Colors.RESET}", end="")
        if i == sb_idx:
            print(f" {Colors.WHITE}{Colors.BG_GREEN}SB{Colors.RESET}", end="")
        if i == bb_idx:
            print(f" {Colors.WHITE}{Colors.BG_RED}BB{Colors.RESET}", end="")
        
        print(f" | Chips: ${player.chips} | Bet: ${player.current_bet}", end="")
        
        if player.folded:
            print(f" | {Colors.YELLOW}FOLDED{Colors.RESET}", end="")
        elif player.is_all_in:
            print(f" | {Colors.CYAN}ALL-IN{Colors.RESET}", end="")
        
        if is_current:
            print(f"{Colors.RESET}", end="")
        
        print()
        
        # Print player's cards
        # Always show human player's cards
        # Show all players' cards if the hand is over (game.winner is not None)
        if is_human:
            print("Your cards:")
            print_cards_horizontal(player.hand)
        elif game.winner is not None:
            # Show all cards when the hand is over
            print(f"{player.name}'s cards:")
            print_cards_horizontal(player.hand)
        else:
            print(f"{player.name}'s cards:")
            print_cards_horizontal([None, None], hidden=True)
        
        print()
    
    # Calculate and display win odds for human player if not folded
    human_player = game.players[player_idx]
    if not human_player.folded and game.phase != 'pre-deal':
        active_opponents = sum(1 for p in game.players if p != human_player and not p.folded)
        if active_opponents > 0:
            win_odds = calculate_hand_odds(human_player.hand, game.community_cards, active_opponents)
            print(f"\n{Colors.BOLD}Your estimated win probability: {Colors.CYAN}{win_odds}%{Colors.RESET}")
    
    # Print position legend
    print(f"Position Legend: {Colors.WHITE}{Colors.BG_BLUE}D{Colors.RESET} = Dealer, "
          f"{Colors.WHITE}{Colors.BG_GREEN}SB{Colors.RESET} = Small Blind (${game.small_blind}), "
          f"{Colors.WHITE}{Colors.BG_RED}BB{Colors.RESET} = Big Blind (${game.big_blind})")
    print()
    
    # Print round actions if there are any
    if round_actions:
        print(f"{Colors.BOLD}{Colors.BG_CYAN}{Colors.WHITE} ROUND ACTIONS {Colors.RESET}")
        for action in round_actions:
            print(action)
        print()
    
    # Print winner if game is over
    if game.winner:
        print(f"\n{Colors.BOLD}{Colors.BG_GREEN}{Colors.WHITE} WINNER: {game.winner} {Colors.RESET}\n")

def get_player_action(game, player_idx=0):
    """Get action from the human player."""
    player = game.players[player_idx]
    cost_to_call = game.current_bet - player.current_bet
    
    print(f"\n{Colors.BOLD}{Colors.BG_CYAN}{Colors.WHITE} YOUR TURN {Colors.RESET}")
    print("Available actions:")
    
    actions = []
    
    # Always show fold option
    print(f"1. {Colors.RED}Fold{Colors.RESET}")
    actions.append("fold")
    
    # Show check/call option
    if cost_to_call == 0:
        print(f"2. {Colors.BLUE}Check{Colors.RESET}")
        actions.append("check")
    else:
        print(f"2. {Colors.BLUE}Call ${cost_to_call}{Colors.RESET}")
        actions.append("call")
    
    # Show bet/raise option
    if game.current_bet == 0:
        print(f"3. {Colors.GREEN}Bet{Colors.RESET}")
        actions.append("bet")
    else:
        print(f"3. {Colors.GREEN}Raise{Colors.RESET}")
        actions.append("raise")
    
    # Get player choice
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ")
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(actions):
                print("Invalid choice. Please try again.")
                continue
            
            action = actions[int(choice) - 1]
            
            # If bet or raise, get amount
            if action in ["bet", "raise"]:
                min_amount = game.min_bet
                max_amount = player.chips
                
                if action == "raise":
                    min_amount = min(game.min_bet * 2, max_amount)
                
                while True:
                    try:
                        amount_str = input(f"Enter amount (${min_amount}-${max_amount}): ")
                        amount = int(amount_str)
                        if amount < min_amount:
                            print(f"Minimum amount is ${min_amount}.")
                            continue
                        if amount > max_amount:
                            print(f"You only have ${max_amount} chips.")
                            continue
                        return action, amount
                    except ValueError:
                        print("Please enter a valid number.")
            
            return action, 0
        
        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")

def animate_bot_thinking(player_name, duration=1.0):
    """Show an animation while the bot is thinking."""
    start_time = time.time()
    thinking_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    
    while time.time() - start_time < duration:
        sys.stdout.write(f"\r{Colors.YELLOW}{thinking_frames[i]} {player_name} is thinking...{Colors.RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
        i = (i + 1) % len(thinking_frames)
    
    # Don't clear the line anymore, just return to beginning of line
    sys.stdout.write("\r")
    sys.stdout.flush()

def display_player_stats(stats):
    """Display player statistics in a visually appealing way."""
    clear_screen()
    print(f"\n{Colors.BOLD}{Colors.BG_CYAN}{Colors.WHITE} PLAYER STATISTICS {Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Player:{Colors.RESET} {stats.player_name}")
    print(f"{Colors.BOLD}Hands Played:{Colors.RESET} {stats.hands_played}")
    print(f"{Colors.BOLD}Hands Won:{Colors.RESET} {stats.hands_won} ({stats.get_win_percentage():.1f}%)")
    print(f"{Colors.BOLD}Biggest Pot Won:{Colors.RESET} ${stats.biggest_pot_won}")
    print(f"{Colors.BOLD}Net Profit:{Colors.RESET} ${stats.get_net_profit()}")
    
    print(f"\n{Colors.BOLD}Action Breakdown:{Colors.RESET}")
    print(f"Folds: {stats.folds} ({stats.fold_percentage:.1f}%)")
    print(f"Checks: {stats.checks}")
    print(f"Calls: {stats.calls}")
    print(f"Bets: {stats.bets}")
    print(f"Raises: {stats.raises}")
    print(f"All-ins: {stats.all_ins}")
    
    if stats.best_hand and stats.best_hand_type:
        print(f"\n{Colors.BOLD}Best Hand:{Colors.RESET} {stats.best_hand_type}")
        print("Cards: ", end="")
        for card in stats.best_hand:
            suit_symbol = get_suit_symbol(card.suit)
            print(f"{card.rank}{suit_symbol} ", end="")
        print()
    
    print(f"\n{Colors.BOLD}Press Enter to continue...{Colors.RESET}")
    input()

def process_player_action(game, action_type, amount, player_idx=0, player_stats=None):
    """Process the human player's action."""
    player_name = game.players[player_idx].name
    action_text = ""
    
    if action_type == "fold":
        action_text = f"{Colors.YELLOW}{player_name} folds.{Colors.RESET}"
        print(action_text)
        game.fold()
    elif action_type == "check":
        action_text = f"{Colors.BLUE}{player_name} checks.{Colors.RESET}"
        print(action_text)
        game.check()
    elif action_type == "call":
        cost_to_call = game.current_bet - game.players[player_idx].current_bet
        action_text = f"{Colors.BLUE}{player_name} calls ${cost_to_call}.{Colors.RESET}"
        print(action_text)
        game.call()
    elif action_type == "bet":
        action_text = f"{Colors.GREEN}{player_name} bets ${amount}.{Colors.RESET}"
        print(action_text)
        game.bet(amount)
    elif action_type == "raise":
        action_text = f"{Colors.GREEN}{player_name} raises to ${game.current_bet + amount}.{Colors.RESET}"
        print(action_text)
        game.raise_bet(amount)
    
    # Add the action to the round history
    global round_actions
    round_actions.append(action_text)
    
    # Update player statistics if provided
    if player_stats:
        player_stats.update_action_stats(action_type)
    
    time.sleep(1)  # Pause to let the player see the action

def process_bot_action(game, action_type, amount, bot_name, bot_stats=None):
    """Process a bot's action with visual feedback."""
    action_text = ""
    
    if action_type == "fold":
        action_text = f"{Colors.YELLOW}{bot_name} folds.{Colors.RESET}"
        print(action_text)
        game.fold()
    elif action_type == "check":
        action_text = f"{Colors.BLUE}{bot_name} checks.{Colors.RESET}"
        print(action_text)
        game.check()
    elif action_type == "call":
        cost_to_call = game.current_bet - game.current_player.current_bet
        action_text = f"{Colors.BLUE}{bot_name} calls ${cost_to_call}.{Colors.RESET}"
        print(action_text)
        game.call()
    elif action_type == "bet":
        action_text = f"{Colors.GREEN}{bot_name} bets ${amount}.{Colors.RESET}"
        print(action_text)
        game.bet(amount)
    elif action_type == "raise":
        action_text = f"{Colors.GREEN}{bot_name} raises to ${game.current_bet + amount}.{Colors.RESET}"
        print(action_text)
        game.raise_bet(amount)
    
    # Add the action to the round history
    global round_actions
    round_actions.append(action_text)
    
    # Update bot statistics if provided
    if bot_stats:
        bot_stats.update_action_stats(action_type)
    
    time.sleep(1)  # Pause to let the player see the action

def display_hand_rankings(game):
    """Display each player's hand and ranking at the end of the game."""
    print(f"\n{Colors.BOLD}{Colors.BG_CYAN}{Colors.WHITE} FINAL HAND RANKINGS {Colors.RESET}\n")
    
    active_players = [p for p in game.players if not p.folded]
    player_hands = []
    
    for player in active_players:
        # Combine player's hand with community cards
        all_cards = player.hand + game.community_cards
        hand_value = HandEvaluator.evaluate_hand(all_cards)
        player_hands.append((player, hand_value))
    
    # Sort players by hand strength (lower rank index is better)
    player_hands.sort(key=lambda x: (x[1][0], -sum(x[1][2])))
    
    for i, (player, hand_value) in enumerate(player_hands):
        rank = i + 1
        hand_type = hand_value[1]
        best_five_cards = hand_value[3]  # Get the best 5 cards
        
        # Print player's ranking
        print(f"{Colors.BOLD}#{rank}: {player.name}{Colors.RESET}")
        print(f"Hand: {Colors.GREEN}{hand_type}{Colors.RESET}")
        
        # Print player's hole cards
        print("Hole cards: ", end="")
        for card in player.hand:
            suit_symbol = get_suit_symbol(card.suit)
            print(f"{card.rank}{suit_symbol} ", end="")
        print()
        
        # Print the best 5 cards
        print("Best five cards: ", end="")
        for card in best_five_cards:
            suit_symbol = get_suit_symbol(card.suit)
            print(f"{card.rank}{suit_symbol} ", end="")
        print()
        
        print()

def display_game_over(players):
    """Display game over message and final rankings based on chip counts."""
    # Don't clear the screen to preserve the final hand state
    print(f"\n{Colors.BOLD}{Colors.BG_RED}{Colors.WHITE} GAME OVER {Colors.RESET}\n")
    
    # Sort players by chip count (highest to lowest)
    sorted_players = sorted(players, key=lambda p: p.chips, reverse=True)
    
    print(f"{Colors.BOLD}{Colors.BG_CYAN}{Colors.WHITE} FINAL RANKINGS {Colors.RESET}\n")
    
    for i, player in enumerate(sorted_players):
        rank = i + 1
        is_human = isinstance(player, Player) and not isinstance(player, BotPlayer)
        
        # Highlight human player
        if is_human:
            print(f"{Colors.BOLD}#{rank}: {player.name} (YOU) - ${player.chips}{Colors.RESET}")
        else:
            print(f"#{rank}: {player.name} - ${player.chips}")
    
    print("\nThanks for playing!")

def create_bot_players(num_bots, starting_chips, difficulty):
    """Create bot players with characteristics based on difficulty level."""
    bot_players = []
    
    for i in range(num_bots):
        bot = BotPlayer(f"Bot {i+1}", starting_chips)
        
        # Adjust bot characteristics based on difficulty
        if difficulty == "easy":
            # Easy bots make more mistakes and are more predictable
            bot.aggression = random.uniform(0.1, 0.5)
            bot.bluff_tendency = random.uniform(0, 0.1)
            bot.decision_style = random.choice(['conservative', 'balanced'])
            bot.personality = random.choice(['tight', 'loose'])
            bot.skill_level = "beginner"
        
        elif difficulty == "medium":
            # Medium bots have balanced characteristics
            bot.aggression = random.uniform(0.3, 0.7)
            bot.bluff_tendency = random.uniform(0.1, 0.2)
            bot.decision_style = random.choice(['conservative', 'aggressive', 'balanced'])
            bot.personality = random.choice(['tight', 'loose', 'unpredictable'])
            bot.skill_level = "intermediate"
        
        elif difficulty == "hard":
            # Hard bots are more skilled and unpredictable
            bot.aggression = random.uniform(0.5, 0.9)
            bot.bluff_tendency = random.uniform(0.2, 0.3)
            bot.decision_style = random.choice(['aggressive', 'balanced'])
            bot.personality = random.choice(['tight', 'unpredictable'])
            bot.skill_level = "advanced"
        
        bot_players.append(bot)
    
    return bot_players

def save_game_state(game, player_stats, bot_stats, filename=None):
    """Save the current game state to a file."""
    if not filename:
        # Generate a filename based on current date/time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"poker_save_{timestamp}.pkl"
    
    # Create a dictionary with all the game state
    save_data = {
        'game': game,
        'player_stats': player_stats,
        'bot_stats': bot_stats,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to file using pickle
    try:
        with open(filename, 'wb') as f:
            pickle.dump(save_data, f)
        print(f"\n{Colors.GREEN}Game saved successfully to {filename}{Colors.RESET}")
        return True
    except Exception as e:
        print(f"\n{Colors.RED}Error saving game: {str(e)}{Colors.RESET}")
        return False

def load_game_state(filename):
    """Load a saved game state from a file."""
    try:
        with open(filename, 'rb') as f:
            save_data = pickle.load(f)
        
        print(f"\n{Colors.GREEN}Game loaded successfully from {filename}{Colors.RESET}")
        print(f"Saved on: {save_data['timestamp']}")
        
        return save_data['game'], save_data['player_stats'], save_data['bot_stats']
    except Exception as e:
        print(f"\n{Colors.RED}Error loading game: {str(e)}{Colors.RESET}")
        return None, None, None

def list_saved_games():
    """List all saved game files in the current directory."""
    saved_games = [f for f in os.listdir('.') if f.startswith('poker_save_') and f.endswith('.pkl')]
    
    if not saved_games:
        print(f"\n{Colors.YELLOW}No saved games found.{Colors.RESET}")
        return {}
    
    print(f"\n{Colors.BOLD}{Colors.BG_CYAN}{Colors.WHITE} SAVED GAMES {Colors.RESET}\n")
    
    saved_games_dict = {}
    
    for i, filename in enumerate(saved_games, 1):
        # Try to extract timestamp from filename
        try:
            timestamp = filename.replace('poker_save_', '').replace('.pkl', '')
            formatted_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_time = "Unknown date"
        
        # Try to get file info
        try:
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
            
            # Extract player info
            player_name = None
            for player in save_data['game'].players:
                if isinstance(player, Player) and not isinstance(player, BotPlayer):
                    player_name = player.name
                    player_chips = player.chips
                    break
            
            print(f"{i}. {filename}")
            print(f"   Saved: {formatted_time}")
            print(f"   Player: {player_name} (${player_chips})")
            print()
            
            saved_games_dict[i] = {
                'filename': filename,
                'player_name': player_name,
                'chips': player_chips,
                'date': formatted_time
            }
        except:
            print(f"{i}. {filename} (Unable to read details)")
    
    return saved_games_dict

def play_game():
    """Main game loop."""
    clear_screen()
    print(f"\n{Colors.BOLD}{Colors.BG_GREEN}{Colors.WHITE} WELCOME TO CONSOLE POKER {Colors.RESET}\n")
    
    # Ask if player wants to load a saved game
    print(f"{Colors.BOLD}Would you like to:{Colors.RESET}")
    print("1. Start a new cash game")
    print("2. Load a saved game")
    
    choice = input("\nEnter your choice (1-2): ")
    
    if choice == '2':
        # List saved games
        saved_games = list_saved_games()
        
        if not saved_games:
            print("No saved games found. Starting a new game.")
            choice = '1'
        else:
            # Let player select a saved game
            print("\nSelect a saved game to load:")
            for i, (filename, info) in enumerate(saved_games.items(), 1):
                print(f"{i}. {info['player_name']} - ${info['chips']} - {info['date']}")
            
            while True:
                try:
                    save_choice = int(input("\nEnter your choice (or 0 to start a new game): "))
                    if 0 <= save_choice <= len(saved_games):
                        break
                    print(f"Please enter a number between 0 and {len(saved_games)}.")
                except ValueError:
                    print("Please enter a valid number.")
            
            if save_choice == 0:
                choice = '1'
            else:
                # Load the selected game
                filename = list(saved_games.keys())[save_choice - 1]
                loaded_data = load_game_state(filename)
                
                if loaded_data:
                    game = loaded_data['game']
                    player_stats = loaded_data['player_stats']
                    bot_stats = loaded_data['bot_stats']
                    
                    print(f"\nGame loaded successfully! Welcome back, {game.players[0].name}!")
                    time.sleep(1)
                    
                    # Start the loaded game
                    play_loaded_game(game, player_stats, bot_stats)
                    return
                else:
                    print("Failed to load game. Starting a new game.")
                    choice = '1'
    
    # Start a new game
    if choice == '1' or choice not in ['1', '2']:
        player_name = input("Enter your name: ")
        if not player_name.strip():
            player_name = "Player"
        
        # Get number of bots
        while True:
            try:
                num_bots = int(input("Enter number of bot opponents (1-7): "))
                if 1 <= num_bots <= 7:
                    break
                print("Please enter a number between 1 and 7.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get difficulty level
        print(f"\n{Colors.BOLD}Select difficulty level:{Colors.RESET}")
        print(f"1. {Colors.GREEN}Easy{Colors.RESET} - Bots make more mistakes and are more predictable")
        print(f"2. {Colors.YELLOW}Medium{Colors.RESET} - Bots have balanced play styles")
        print(f"3. {Colors.RED}Hard{Colors.RESET} - Bots are more skilled and unpredictable")
        
        while True:
            try:
                difficulty_choice = int(input("Enter your choice (1-3): "))
                if 1 <= difficulty_choice <= 3:
                    break
                print("Please enter a number between 1 and 3.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Map choice to difficulty level
        difficulty = ["easy", "medium", "hard"][difficulty_choice - 1]
        
        # Get starting chips
        while True:
            try:
                starting_chips = int(input("Enter starting chips (1000-10000): "))
                if 1000 <= starting_chips <= 10000:
                    break
                print("Please enter a number between 1000 and 10000.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get blind levels
        while True:
            try:
                small_blind = int(input("Enter small blind amount (5-100): "))
                if 5 <= small_blind <= 100:
                    break
                print("Please enter a number between 5 and 100.")
            except ValueError:
                print("Please enter a valid number.")
        
        big_blind = small_blind * 2
        
        # Create players
        human_player = Player(player_name, starting_chips)
        bot_players = create_bot_players(num_bots, starting_chips, difficulty)
        all_players = [human_player] + bot_players
        
        # Initialize game
        game = PokerGame(all_players, small_blind, big_blind)
        
        # Initialize player statistics
        player_stats = PlayerStats(player_name)
        bot_stats = {bot.name: PlayerStats(bot.name) for bot in bot_players}
        
        # Start the game
        play_cash_game(game, player_stats, bot_stats)

if __name__ == "__main__":
    play_game() 