import enum
import re


class Suit(enum.Enum):
    Diamond = 1
    Club = 2
    Heart = 3
    Spade = 4

    def __gt__(self, other):
        return self.value > other.value

    @staticmethod
    def is_flush(suits):
        # 同花判定
        first = suits[0]
        for suit in suits[1:]:
            if suit != first:
                return False
        return True


class Rank(enum.Enum):
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    Ace = 14

    def __gt__(self, other):
        return self.value > other.value

    @staticmethod
    def is_straight(ranks):
        # 顺子判定
        ranks = sorted(ranks)
        cursor = ranks[0]
        for rank in ranks[1:]:
            if rank.value != cursor.value + 1:
                return False
            cursor = rank
        return True


class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def __gt__(self, other):
        return self.rank > other.rank

    def __eq__(self, other):
        # Texas holdem rule: The card's numerical rank is of sole importance; suit values are irrelevant
        return self.rank == other.rank

    def __repr__(self):
        return f'<{self.rank.name} {self.suit.name}>'

    suit_map = {
        'd': 1,
        'c': 2,
        'h': 3,
        's': 4
    }

    @classmethod
    def from_str(cls, card_str: str):
        """
        :param card_str: strings like 'a10'
        :return:
        """
        suit_str, rank_str = re.match(r'([a-z])(\d+)', card_str).groups()
        return Card(Suit(cls.suit_map[suit_str]), Rank(int(rank_str)))
