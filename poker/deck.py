import random
from .card import Card

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        """Reset the deck with all 52 cards."""
        self.cards = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def deal(self, num_cards=1):
        """Deal a specified number of cards from the deck."""
        if num_cards > len(self.cards):
            raise ValueError("Not enough cards in the deck")
        
        dealt_cards = []
        for _ in range(num_cards):
            dealt_cards.append(self.cards.pop())
        
        return dealt_cards if num_cards > 1 else dealt_cards[0] 