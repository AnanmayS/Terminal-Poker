class Card:
    SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self, suit, rank):
        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        if rank not in self.RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def __repr__(self):
        return self.__str__()
    
    def get_value(self):
        """Get the numerical value of the card for comparison."""
        return self.RANKS.index(self.rank)
    
    def get_suit_value(self):
        """Get the numerical value of the suit for comparison."""
        return self.SUITS.index(self.suit)
    
    def get_image_name(self):
        """Get the image filename for this card."""
        rank_map = {'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'}
        rank_str = rank_map.get(self.rank, self.rank)
        return f"{rank_str}_of_{self.suit}.png" 