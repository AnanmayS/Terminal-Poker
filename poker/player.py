import random
import time
from poker.evaluator import HandEvaluator  # Import the hand evaluator

class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = []
        self.folded = False
        self.current_bet = 0
        self.is_all_in = False
    
    def receive_card(self, card):
        """Add a card to the player's hand."""
        self.hand.append(card)
    
    def clear_hand(self):
        """Clear the player's hand."""
        self.hand = []
        self.folded = False
        self.current_bet = 0
        self.is_all_in = False
    
    def place_bet(self, amount):
        """Place a bet of the specified amount."""
        if amount > self.chips:
            amount = self.chips
            self.is_all_in = True
        
        self.chips -= amount
        self.current_bet += amount
        return amount
    
    def fold(self):
        """Fold the current hand."""
        self.folded = True
    
    def can_make_action(self):
        """Check if the player can make an action."""
        return not self.folded and not self.is_all_in and self.chips > 0


class BotPlayer(Player):
    def __init__(self, name, chips):
        super().__init__(name, chips)
        self.aggression = random.uniform(0.1, 0.9)  # Random aggression level
        self.decision_style = random.choice(['conservative', 'aggressive', 'balanced'])
        self.bluff_tendency = random.uniform(0, 0.3)  # Chance to bluff
        self.personality = random.choice(['tight', 'loose', 'unpredictable'])  # Add personality types
    
    def decide_action(self, game):
        """Decide what action to take based on the current game state."""
        # Simple bot strategy with quick decision making
        if self.folded or self.is_all_in:
            return None
        
        # Add a small delay to simulate thinking (0.1-0.5 seconds)
        time.sleep(random.uniform(0.1, 0.5))
        
        # Quick hand strength evaluation
        hand_strength = self._evaluate_hand_strength(game)
        
        # Calculate the cost to call
        cost_to_call = game.current_bet - self.current_bet
        
        # Occasionally bluff regardless of hand strength
        if random.random() < self.bluff_tendency:
            if cost_to_call == 0:
                bet_amount = int(self.chips * random.uniform(0.1, 0.3))
                bet_amount = max(game.min_bet, min(bet_amount, self.chips))
                return ('bet', bet_amount)
            elif random.random() < 0.5:  # 50% chance to bluff with a raise
                raise_amount = int(cost_to_call + (self.chips * random.uniform(0.1, 0.3)))
                raise_amount = max(game.min_bet, min(raise_amount, self.chips))
                return ('raise', raise_amount)
        
        # Decision based on bot's style and hand strength
        if self.decision_style == 'conservative':
            return self._conservative_decision(game, hand_strength, cost_to_call)
        elif self.decision_style == 'aggressive':
            return self._aggressive_decision(game, hand_strength, cost_to_call)
        else:  # balanced
            return self._balanced_decision(game, hand_strength, cost_to_call)
    
    def _conservative_decision(self, game, hand_strength, cost_to_call):
        """Conservative bot strategy - only plays strong hands."""
        if cost_to_call == 0:
            if hand_strength > 0.5:
                bet_amount = int(self.chips * hand_strength * 0.2)
                bet_amount = max(game.min_bet, min(bet_amount, self.chips))
                return ('bet', bet_amount)
            return ('check', 0)
        
        if hand_strength < 0.4:
            return ('fold', 0)
        
        if hand_strength > 0.7 and random.random() < 0.3:
            raise_amount = int(cost_to_call + (self.chips * hand_strength * 0.3))
            raise_amount = max(game.min_bet, min(raise_amount, self.chips))
            return ('raise', raise_amount)
        
        if cost_to_call < self.chips * 0.2 or hand_strength > 0.5:
            return ('call', cost_to_call)
        
        return ('fold', 0)
    
    def _aggressive_decision(self, game, hand_strength, cost_to_call):
        """Aggressive bot strategy - plays more hands and bets more."""
        if cost_to_call == 0:
            if random.random() < 0.7:
                bet_amount = int(self.chips * (hand_strength * 0.5 + 0.1))
                bet_amount = max(game.min_bet, min(bet_amount, self.chips))
                return ('bet', bet_amount)
            return ('check', 0)
        
        if hand_strength < 0.2 and cost_to_call > self.chips * 0.3:
            return ('fold', 0)
        
        if hand_strength > 0.5 or random.random() < 0.4:
            raise_amount = int(cost_to_call + (self.chips * (hand_strength * 0.6 + 0.1)))
            raise_amount = max(game.min_bet, min(raise_amount, self.chips))
            return ('raise', raise_amount)
        
        return ('call', cost_to_call)
    
    def _balanced_decision(self, game, hand_strength, cost_to_call):
        """Balanced bot strategy - mix of conservative and aggressive."""
        if cost_to_call == 0:
            if random.random() < hand_strength + 0.2:
                bet_amount = int(self.chips * hand_strength * 0.3)
                bet_amount = max(game.min_bet, min(bet_amount, self.chips))
                return ('bet', bet_amount)
            return ('check', 0)
        
        if hand_strength < 0.3 and cost_to_call > self.chips * 0.2:
            return ('fold', 0)
        
        if hand_strength > 0.6 and random.random() < 0.5:
            raise_amount = int(cost_to_call + (self.chips * hand_strength * 0.4))
            raise_amount = max(game.min_bet, min(raise_amount, self.chips))
            return ('raise', raise_amount)
        
        if cost_to_call < self.chips * 0.3 or hand_strength > 0.4:
            return ('call', cost_to_call)
        
        return ('fold', 0)
    
    def _evaluate_hand_strength(self, game):
        """
        Evaluate the strength of the current hand using the HandEvaluator.
        Returns a value between 0 (weakest) and 1 (strongest).
        """
        # If no community cards yet, evaluate based on hole cards only
        if not game.community_cards:
            # Pair in hole cards is strong
            if self.hand[0].rank == self.hand[1].rank:
                return 0.8 + random.uniform(0, 0.2)
            
            # High cards are stronger
            high_card_value = max(card.get_value() for card in self.hand)
            if high_card_value >= 10:  # 10, J, Q, K, A
                return 0.6 + random.uniform(0, 0.2)
            
            # Suited cards have potential
            if self.hand[0].suit == self.hand[1].suit:
                return 0.5 + random.uniform(0, 0.2)
            
            # Connected cards (straight potential)
            values = sorted([card.get_value() for card in self.hand])
            if abs(values[0] - values[1]) <= 2:
                return 0.4 + random.uniform(0, 0.2)
            
            # Weaker starting hand
            return 0.2 + random.uniform(0, 0.3)
        
        # With community cards, use the hand evaluator
        all_cards = self.hand + game.community_cards
        hand_value = HandEvaluator.evaluate_hand(all_cards)
        
        # Map hand types to strength values
        hand_type = hand_value[1]
        base_strength = {
            "High Card": 0.1,
            "Pair": 0.3,
            "Two Pair": 0.5,
            "Three of a Kind": 0.6,
            "Straight": 0.7,
            "Flush": 0.8,
            "Full House": 0.85,
            "Four of a Kind": 0.9,
            "Straight Flush": 0.95,
            "Royal Flush": 1.0
        }.get(hand_type, 0.1)
        
        # Add some randomness to make bots less predictable
        strength = base_strength + random.uniform(-0.1, 0.1)
        
        # Adjust based on bot personality
        if self.personality == 'tight':
            # Tight players only play strong hands
            strength = strength * 0.8 + 0.1
        elif self.personality == 'loose':
            # Loose players play more hands
            strength = strength * 0.6 + 0.3
        elif self.personality == 'unpredictable':
            # Unpredictable players have more variance
            strength = strength * 0.5 + random.uniform(0, 0.5)
        
        return min(1.0, max(0.1, strength)) 