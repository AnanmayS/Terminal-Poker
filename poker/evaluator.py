from collections import Counter
from itertools import combinations

class HandEvaluator:
    # Hand rankings from highest to lowest
    HAND_RANKINGS = [
        "Royal Flush",
        "Straight Flush",
        "Four of a Kind",
        "Full House",
        "Flush",
        "Straight",
        "Three of a Kind",
        "Two Pair",
        "One Pair",
        "High Card"
    ]
    
    @staticmethod
    def evaluate_hand(cards):
        """
        Evaluate a poker hand (5-7 cards) and return a tuple of 
        (hand_rank_index, hand_type, tie_breaker_values)
        Lower hand_rank_index is better.
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate a poker hand")
        
        # Get all possible 5-card combinations if more than 5 cards
        best_hand_rank = 9  # Start with high card (worst hand)
        best_hand_type = "High Card"
        best_tie_breakers = []
        best_five_cards = []
        
        # Check all possible 5-card combinations
        for five_cards in combinations(cards, 5):
            # Sort cards by rank for easier evaluation
            sorted_cards = sorted(five_cards, key=lambda card: card.get_value(), reverse=True)
            
            # Check for each hand type from best to worst
            hand_value = HandEvaluator._evaluate_five_card_hand(sorted_cards)
            
            # If this hand is better than our current best, update it
            if hand_value[0] < best_hand_rank or (
                hand_value[0] == best_hand_rank and hand_value[2] > best_tie_breakers
            ):
                best_hand_rank = hand_value[0]
                best_hand_type = hand_value[1]
                best_tie_breakers = hand_value[2]
                best_five_cards = sorted_cards
        
        return (best_hand_rank, best_hand_type, best_tie_breakers, best_five_cards)
    
    @staticmethod
    def _evaluate_five_card_hand(cards):
        """Evaluate a 5-card poker hand."""
        assert len(cards) == 5, "Must evaluate exactly 5 cards"
        
        # Royal Flush
        royal_flush = HandEvaluator._check_royal_flush(cards)
        if royal_flush[0]:
            return (0, "Royal Flush", royal_flush[1])
        
        # Straight Flush
        straight_flush = HandEvaluator._check_straight_flush(cards)
        if straight_flush[0]:
            return (1, "Straight Flush", straight_flush[1])
        
        # Four of a Kind
        four_kind = HandEvaluator._check_four_of_a_kind(cards)
        if four_kind[0]:
            return (2, "Four of a Kind", four_kind[1])
        
        # Full House
        full_house = HandEvaluator._check_full_house(cards)
        if full_house[0]:
            return (3, "Full House", full_house[1])
        
        # Flush
        flush = HandEvaluator._check_flush(cards)
        if flush[0]:
            return (4, "Flush", flush[1])
        
        # Straight
        straight = HandEvaluator._check_straight(cards)
        if straight[0]:
            return (5, "Straight", straight[1])
        
        # Three of a Kind
        three_kind = HandEvaluator._check_three_of_a_kind(cards)
        if three_kind[0]:
            return (6, "Three of a Kind", three_kind[1])
        
        # Two Pair
        two_pair = HandEvaluator._check_two_pair(cards)
        if two_pair[0]:
            return (7, "Two Pair", two_pair[1])
        
        # One Pair
        one_pair = HandEvaluator._check_one_pair(cards)
        if one_pair[0]:
            return (8, "One Pair", one_pair[1])
        
        # High Card
        high_card = HandEvaluator._check_high_card(cards)
        return (9, "High Card", high_card[1])
    
    @staticmethod
    def _check_royal_flush(cards):
        # Check for royal flush (A, K, Q, J, 10 of same suit)
        if len(set(card.suit for card in cards)) != 1:
            return (False, [])
            
        ranks = set(card.rank for card in cards)
        if ranks == set(['A', 'K', 'Q', 'J', '10']):
            return (True, [14])  # Ace high
        return (False, [])
    
    @staticmethod
    def _check_straight_flush(cards):
        # Check for straight flush (5 cards in sequence, same suit)
        if len(set(card.suit for card in cards)) != 1:
            return (False, [])
            
        # Check if it's a straight
        straight = HandEvaluator._check_straight(cards)
        if straight[0]:
            return (True, straight[1])
        return (False, [])
    
    @staticmethod
    def _check_four_of_a_kind(cards):
        # Check for four of a kind
        rank_counts = Counter([card.rank for card in cards])
        for rank, count in rank_counts.items():
            if count == 4:
                four_kind_value = [card.get_value() for card in cards if card.rank == rank][0]
                kickers = [card.get_value() for card in cards if card.rank != rank]
                return (True, [four_kind_value] + kickers)
        return (False, [])
    
    @staticmethod
    def _check_full_house(cards):
        # Check for full house (three of a kind and a pair)
        rank_counts = Counter([card.rank for card in cards])
        three_kind_rank = None
        pair_rank = None
        
        for rank, count in rank_counts.items():
            if count == 3:
                three_kind_rank = rank
            elif count == 2:
                pair_rank = rank
        
        if three_kind_rank and pair_rank:
            three_kind_value = [card.get_value() for card in cards if card.rank == three_kind_rank][0]
            pair_value = [card.get_value() for card in cards if card.rank == pair_rank][0]
            return (True, [three_kind_value, pair_value])
        
        return (False, [])
    
    @staticmethod
    def _check_flush(cards):
        # Check for flush (5 cards of the same suit)
        if len(set(card.suit for card in cards)) == 1:
            values = [card.get_value() for card in cards]
            values.sort(reverse=True)
            return (True, values)
        return (False, [])
    
    @staticmethod
    def _check_straight(cards):
        # Check for straight (5 cards in sequence)
        values = sorted(set([card.get_value() for card in cards]))
        
        # Check for A-5 straight (Ace can be low)
        if set(values) == set([0, 1, 2, 3, 12]):  # 2,3,4,5,A
            return (True, [3])  # 5 high straight
        
        # Check for regular straight
        if len(values) == 5 and values[4] - values[0] == 4:
            return (True, [values[4]])  # Return highest card value
        
        return (False, [])
    
    @staticmethod
    def _check_three_of_a_kind(cards):
        # Check for three of a kind
        rank_counts = Counter([card.rank for card in cards])
        for rank, count in rank_counts.items():
            if count == 3:
                three_kind_value = [card.get_value() for card in cards if card.rank == rank][0]
                kickers = [card.get_value() for card in cards if card.rank != rank]
                kickers.sort(reverse=True)
                return (True, [three_kind_value] + kickers)
        return (False, [])
    
    @staticmethod
    def _check_two_pair(cards):
        # Check for two pair
        rank_counts = Counter([card.rank for card in cards])
        pairs = []
        
        for rank, count in rank_counts.items():
            if count == 2:
                pairs.append((rank, [card.get_value() for card in cards if card.rank == rank][0]))
        
        if len(pairs) == 2:
            pairs.sort(key=lambda x: x[1], reverse=True)
            pair_values = [pair[1] for pair in pairs]
            kickers = [card.get_value() for card in cards if card.rank != pairs[0][0] and card.rank != pairs[1][0]]
            return (True, pair_values + kickers)
        
        return (False, [])
    
    @staticmethod
    def _check_one_pair(cards):
        # Check for one pair
        rank_counts = Counter([card.rank for card in cards])
        for rank, count in rank_counts.items():
            if count == 2:
                pair_value = [card.get_value() for card in cards if card.rank == rank][0]
                kickers = [card.get_value() for card in cards if card.rank != rank]
                kickers.sort(reverse=True)
                return (True, [pair_value] + kickers)
        return (False, [])
    
    @staticmethod
    def _check_high_card(cards):
        # High card
        values = [card.get_value() for card in cards]
        values.sort(reverse=True)
        return (True, values) 