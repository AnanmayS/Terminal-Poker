# Console Poker Game

This project is a console-based Texas Hold'em poker game that delivers an immersive poker experience. It features a visually engaging text interface, a robust set of gameplay mechanics, and intelligent bot opponents that have different strategies.

## Features

- **Beautiful Visual Interface**
  - ASCII card display with colored suits
  - Animated card dealing and community card reveals
  - Position indicators for dealer, small blind, and big blind
  - Colorful terminal interface with clear game state display

- **Intelligent Bot Opponents**
  - Multiple bot personalities (tight, loose, unpredictable)
  - Different playing styles (conservative, aggressive, balanced)
  - Realistic decision-making based on hand strength
  - Adjustable difficulty levels (easy, medium, hard)

- **Advanced Game Mechanics**
  - Real-time hand odds calculator using Monte Carlo simulation
  - Comprehensive hand evaluation with all poker hand rankings
  - Detailed player statistics tracking
  - Action history display for each round

- **Game Management**
  - Save and load game functionality
  - Customizable starting chips and blind levels
  - Detailed player statistics and performance tracking

## Setup

1. No external dependencies required! The game runs with Python's standard library.

2. Run the console game:
   ```
   python console_poker.py
   ```

## Game Rules

Texas Hold'em poker rules:
- Each player is dealt 2 private cards (hole cards)
- 5 community cards are dealt in three stages:
  - The Flop: First 3 community cards
  - The Turn: 4th community card
  - The River: 5th community card
- Players can check, bet, call, raise, or fold during betting rounds
- The best 5-card hand wins (from the 7 available cards - 2 hole cards + 5 community cards)

## Hand Rankings (Highest to Lowest)

1. Royal Flush: A, K, Q, J, 10 of the same suit
2. Straight Flush: Five sequential cards of the same suit
3. Four of a Kind: Four cards of the same rank
4. Full House: Three of a kind plus a pair
5. Flush: Five cards of the same suit
6. Straight: Five sequential cards of different suits
7. Three of a Kind: Three cards of the same rank
8. Two Pair: Two different pairs
9. One Pair: Two cards of the same rank
10. High Card: Highest card when no other hand is made

## Bot Difficulty Levels

- **Easy**: Bots make more mistakes, are more predictable, and bluff less frequently
- **Medium**: Bots have balanced play styles with moderate aggression and occasional bluffs
- **Hard**: Bots are more skilled, unpredictable, and aggressive with strategic bluffing

## Statistics Tracking

The game tracks various statistics for each player:
- Hands played and win percentage
- Biggest pot won
- Best hand achieved
- Action breakdown (folds, checks, calls, bets, raises)
- Net profit/loss

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
