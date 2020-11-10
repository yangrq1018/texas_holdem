import enum
import operator
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

    def __repr__(self):
        m = {
            1: 'd',
            2: 'c',
            3: 'h',
            4: 's'
        }
        return m[self.value]


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

    def __repr__(self):
        m = {
            10: 'T',
            11: 'J',
            12: 'Q',
            13: 'K',
            14: 'A'
        }
        return m[self.value] if self.value in m else str(self.value)

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


class TexasCard:
    """
    Special card type for Texas Hold'em, override the greater and equal method as Hold'em only cares about rank, ignores
    suit.
    """

    @staticmethod
    def sort_desc(cards):
        # sort in reverse order
        return sorted(cards, key=operator.attrgetter('rank'), reverse=True)

    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        # Texas hol;dem rule: The card's numerical rank is of sole importance; suit values are irrelevant
        return self.rank == other.rank and self.suit == other.suit

    def __str__(self):
        return self.__repr__()

    def to_eval7_str(self):
        return repr(self.rank) + repr(self.suit)

    def __hash__(self):
        _key = self.suit, self.rank
        return hash(_key)

    def __repr__(self):
        _special = {
            Rank.Ten: 'T',
            Rank.Ace: 'A',
            Rank.Jack: 'J',
            Rank.Queen: 'Q',
            Rank.King: 'K'
        }
        return f'<card {repr(self.rank) + repr(self.suit)}>'

    @classmethod
    def from_str(cls, card_str: str):
        """
        :param card_str: strings like 'a10'
        :return:
        """
        rank, suit_str = re.match(r'([AJQKT]|\d)([dchs])', card_str).groups()
        if rank == 'A':
            rank = 14
        elif rank == 'K':
            rank = 13
        elif rank == 'Q':
            rank = 12
        elif rank == 'J':
            rank = 11
        elif rank == 'T':
            rank = 10
        else:
            rank = int(rank)

        if suit_str == 'd':
            suit = Suit.Diamond
        elif suit_str == 'c':
            suit = Suit.Club
        elif suit_str == 'h':
            suit = Suit.Heart
        elif suit_str == 's':
            suit = Suit.Spade
        else:
            raise ValueError(suit_str)

        return TexasCard(suit, Rank(rank))
