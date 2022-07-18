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
        return f'<card {repr(self.rank) + repr(self.suit)}>'

    @classmethod
    def from_str(cls, card_str: str):
        """
        :param card_str: strings like 'As' (Spade Ace), '2c' (Club 2)
        :return:

        Note: card 10 is denoted as T, for single-letter rank consistency.
        """
        match = re.match(r'([AJQKTajqkt]|\d)([dchsDCHS])', card_str)
        if match is None:
            raise ValueError(f"Cannot parse card string: {card_str}")
        rank, suit_str = match.groups()

        match rank.upper():
            case 'A':
                rank = 14
            case 'K':
                rank = 13
            case 'Q':
                rank = 12
            case  'J':
                rank = 11
            case 'T':
                rank = 10
            case _:
                try:
                    rank = int(rank)
                except ValueError as err:
                    raise ValueError(f"Illegal number rank: {err}")
                
        if suit_str.lower() == 'd':
            suit = Suit.Diamond
        elif suit_str.lower() == 'c':
            suit = Suit.Club
        elif suit_str.lower() == 'h':
            suit = Suit.Heart
        elif suit_str.lower() == 's':
            suit = Suit.Spade
        else:
            raise ValueError(f"Illege suit: {suit_str}")

        return TexasCard(suit, Rank(rank))
