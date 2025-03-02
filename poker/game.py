from .deck import Deck
from .evaluator import HandEvaluator
import time
import random

class PokerGame:
    PHASES = ['preflop', 'flop', 'turn', 'river', 'showdown']
    
    def __init__(self, players, small_blind=5, big_blind=10):
        if len(players) < 2:
            raise ValueError("Need at least 2 players for a poker game")
        
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_bet = big_blind
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer_idx = 0
        self.current_player_idx = 0
        self.phase = None
        self.hand_over = True
        self.winner = None
        self.last_raise_idx = -1
        self.bot_decision_time_limit = 5  # 5 seconds time limit for bot decisions
    
    @property
    def current_player(self):
        return self.players[self.current_player_idx]
    
    def start_new_hand(self):
        """Start a new hand of poker."""
        # Reset game state
        self.deck.reset()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.hand_over = False
        self.winner = None
        self.phase = self.PHASES[0]  # preflop
        
        # Reset player hands
        for player in self.players:
            player.clear_hand()
        
        # Rotate dealer position
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        
        # Set blinds
        sb_idx = (self.dealer_idx + 1) % len(self.players)
        bb_idx = (self.dealer_idx + 2) % len(self.players)
        
        # Post blinds
        sb_amount = min(self.small_blind, self.players[sb_idx].chips)
        self.pot += self.players[sb_idx].place_bet(sb_amount)
        
        bb_amount = min(self.big_blind, self.players[bb_idx].chips)
        self.pot += self.players[bb_idx].place_bet(bb_amount)
        self.current_bet = bb_amount
        
        # Deal cards to players
        for _ in range(2):
            for player in self.players:
                player.receive_card(self.deck.deal())
        
        # Set starting player (after big blind)
        self.current_player_idx = (bb_idx + 1) % len(self.players)
        self.last_raise_idx = bb_idx
    
    def next_player(self):
        """Move to the next player who can make an action."""
        original_idx = self.current_player_idx
        
        while True:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            
            # If we've gone all the way around or everyone has folded except one player
            if (self.current_player_idx == self.last_raise_idx or 
                sum(1 for p in self.players if not p.folded) <= 1 or
                all(not p.can_make_action() or p.current_bet == self.current_bet 
                    for p in self.players if not p.folded)):
                self.next_phase()
                return
            
            # Skip players who can't make actions
            if self.players[self.current_player_idx].can_make_action():
                return
    
    def next_phase(self):
        """Move to the next phase of the hand."""
        if self.phase == 'showdown' or sum(1 for p in self.players if not p.folded) <= 1:
            self.end_hand()
            return
        
        current_phase_idx = self.PHASES.index(self.phase)
        self.phase = self.PHASES[current_phase_idx + 1]
        
        # Deal community cards based on the phase
        if self.phase == 'flop':
            self.community_cards.extend(self.deck.deal(3))
        elif self.phase == 'turn' or self.phase == 'river':
            self.community_cards.append(self.deck.deal())
        elif self.phase == 'showdown':
            self.determine_winner()
        
        # Reset betting for the new phase
        for player in self.players:
            player.current_bet = 0
        self.current_bet = 0
        
        # Set first player (after dealer)
        self.current_player_idx = (self.dealer_idx + 1) % len(self.players)
        while self.players[self.current_player_idx].folded or not self.players[self.current_player_idx].can_make_action():
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            if self.current_player_idx == self.dealer_idx:
                # Everyone is folded or all-in
                self.next_phase()
                return
        
        self.last_raise_idx = -1
    
    def end_hand(self):
        """End the current hand and distribute the pot."""
        self.hand_over = True
        
        # If only one player remains, they win
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            self.winner = active_players[0].name
            active_players[0].chips += self.pot
            return
        
        # Otherwise, determine winner by hand strength
        self.determine_winner()
    
    def determine_winner(self):
        """Determine the winner of the current hand."""
        active_players = [p for p in self.players if not p.folded]
        
        if len(active_players) == 0:
            return
        
        if len(active_players) == 1:
            self.winner = active_players[0].name
            active_players[0].chips += self.pot
            return
        
        # Evaluate each player's hand
        best_hand_rank = 10  # Higher than any valid hand rank
        winners = []
        
        for player in active_players:
            # Combine player's hand with community cards
            all_cards = player.hand + self.community_cards
            hand_value = HandEvaluator.evaluate_hand(all_cards)
            
            # hand_value is now (rank_index, hand_type, tie_breakers, best_five_cards)
            if hand_value[0] < best_hand_rank:
                best_hand_rank = hand_value[0]
                winners = [player]
            elif hand_value[0] == best_hand_rank:
                # Compare tie breakers
                if not winners or hand_value[2] > HandEvaluator.evaluate_hand(winners[0].hand + self.community_cards)[2]:
                    winners = [player]
                elif hand_value[2] == HandEvaluator.evaluate_hand(winners[0].hand + self.community_cards)[2]:
                    winners.append(player)
        
        # Split pot among winners
        split_amount = self.pot // len(winners)
        remainder = self.pot % len(winners)
        
        for player in winners:
            player.chips += split_amount
            
        # Give remainder to the first winner (closest to dealer)
        if remainder > 0 and winners:
            winners[0].chips += remainder
        
        self.winner = ", ".join([player.name for player in winners])
    
    def fold(self):
        """Current player folds."""
        if self.hand_over:
            return
        
        self.current_player.fold()
        
        # Check if only one player remains
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            self.end_hand()
            return
        
        self.next_player()
    
    def check(self):
        """Current player checks."""
        if self.hand_over or self.current_player.current_bet < self.current_bet:
            return
        
        self.next_player()
    
    def call(self):
        """Current player calls the current bet."""
        if self.hand_over:
            return
        
        amount_to_call = self.current_bet - self.current_player.current_bet
        if amount_to_call <= 0:
            return self.check()
        
        bet_amount = self.current_player.place_bet(amount_to_call)
        self.pot += bet_amount
        
        self.next_player()
    
    def bet(self, amount):
        """Current player places a bet."""
        if self.hand_over or self.current_bet > 0:
            return
        
        if amount < self.min_bet and amount < self.current_player.chips:
            amount = self.min_bet
        
        bet_amount = self.current_player.place_bet(amount)
        self.pot += bet_amount
        self.current_bet = self.current_player.current_bet
        self.last_raise_idx = self.current_player_idx
        
        self.next_player()
    
    def raise_bet(self, amount):
        """Current player raises the current bet."""
        if self.hand_over:
            return
        
        total_amount = self.current_bet - self.current_player.current_bet + amount
        
        if total_amount < self.min_bet * 2 and total_amount < self.current_player.chips:
            total_amount = self.min_bet * 2
        
        bet_amount = self.current_player.place_bet(total_amount)
        self.pot += bet_amount
        self.current_bet = self.current_player.current_bet
        self.last_raise_idx = self.current_player_idx
        
        self.next_player()
    
    def bot_action(self):
        """Have the current bot player make an action with a time limit."""
        if not isinstance(self.current_player, type(self.players[0]).__bases__[0]):
            return
        
        # Set a time limit for bot decision
        start_time = time.time()
        
        # Get bot's decision
        try:
            # Add a timeout mechanism
            action = None
            while time.time() - start_time < self.bot_decision_time_limit:
                action = self.current_player.decide_action(self)
                # If we got a decision, break out of the loop
                if action is not None:
                    break
                # Small sleep to prevent CPU hogging
                time.sleep(0.1)
            
            # If we timed out or got no action, make a default action
            if action is None:
                # Default to a conservative action (check if possible, otherwise fold)
                if self.current_bet == 0 or self.current_bet == self.current_player.current_bet:
                    action = ('check', 0)
                else:
                    action = ('fold', 0)
                print(f"Bot {self.current_player.name} timed out, defaulting to {action[0]}")
        except Exception as e:
            # If any error occurs, default to a safe action
            print(f"Error in bot decision: {e}")
            action = ('fold', 0)
        
        # Add a small random delay (0.5-2 seconds) to make it feel more natural
        elapsed_time = time.time() - start_time
        if elapsed_time < 0.5:
            time.sleep(random.uniform(0.5, min(2.0, self.bot_decision_time_limit - elapsed_time)))
        
        if action is None:
            self.next_player()
            return
        
        action_type, amount = action
        
        if action_type == 'fold':
            self.fold()
        elif action_type == 'check':
            self.check()
        elif action_type == 'call':
            self.call()
        elif action_type == 'bet':
            self.bet(amount)
        elif action_type == 'raise':
            self.raise_bet(amount) 