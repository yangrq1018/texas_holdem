"""
Class representing the possible hand values
"""
import abc
import enum
from typing import Tuple, Iterable

from holdem.card import Rank, TexasCard


class Power(enum.Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

    def __gt__(self, other):
        return self.value > other.value


class TieException(Exception):
    pass


class Showdown:
    __power__ = None

    def __init__(self, cards: Iterable[TexasCard]):
        """
        Signature should be the same as child to allow diamond inheritance
        :param cards:
        """

        self.kickers = cards

    def __gt__(self, other):
        if self.__power__ != other.__power__:
            return self.__power__ > other.__power__
        # compare by values
        if self.values() == other.values():
            raise TieException()
        return self.values() > other.values()

    def values(self) -> Tuple[Rank, ...]:
        # default implementation, compare kickers
        return tuple(k.rank for k in self.kickers)


class HighCard(Showdown):
    __power__ = Power.HIGH_CARD

    def __init__(self, cards):
        super().__init__(cards=cards)


class Pair(Showdown):
    __power__ = Power.PAIR

    def __init__(self, pair: Tuple[TexasCard, ...], cards: Iterable[TexasCard]):
        """

        :param pair: two cards
        :param cards: sorted desc
        """
        super().__init__(cards=cards)
        self.pair = tuple(pair)

    def values(self) -> Tuple[Rank, ...]:
        # priority of the pair cards
        return (self.pair[0].rank,) + super().values()


class TwoPair(Showdown):
    __power__ = Power.TWO_PAIR

    def __init__(self, pair_major: Tuple[TexasCard, ...], pair_minor: Tuple[TexasCard, ...],
                 kicker: TexasCard):
        """
        :param pair_major: the major pair
        :param pair_minor: the minor pair
        :param kicker: a single kicker card
        """
        super().__init__(cards=[kicker])
        self.pair_major = pair_major
        self.pair_minor = pair_minor

    def values(self) -> Tuple[Rank, ...]:
        return (self.pair_major[0].rank, self.pair_minor[0].rank) + super().values()


class ThreeOfAKind(Showdown):
    __power__ = Power.THREE_OF_A_KIND

    def __init__(self, triplet: Tuple[TexasCard, ...], cards):
        super().__init__(cards=cards)
        self.triplet = triplet

    def values(self) -> Tuple[Rank, ...]:
        return (self.triplet[0].rank,) + super().values()


class Straight(Showdown):
    __power__ = Power.STRAIGHT

    def __init__(self, cards=None, **kwargs):
        super(Straight, self).__init__(cards=cards)


class Flush(Showdown):
    __power__ = Power.FLUSH

    def __init__(self, cards=None, **kwargs):
        super().__init__(cards=cards)


class FullHouse(Showdown):
    __power__ = Power.FULL_HOUSE

    def __init__(self, triplet: Tuple[TexasCard, ...], twins: [TexasCard, TexasCard, TexasCard]):
        # no kickers
        super().__init__(cards=[])
        self.triplet = triplet
        self.twins = twins
        assert len(self.triplet) == 3
        assert len(self.twins) == 2

    def values(self) -> Tuple[Rank, ...]:
        return self.triplet[0].rank, self.twins[0].rank


class FourOfAKind(Showdown):
    __power__ = Power.FOUR_OF_A_KIND

    def __init__(self, quad: Tuple[TexasCard, ...], kicker: TexasCard):
        super().__init__(cards=[kicker])
        self.quad = quad

    def values(self) -> Tuple[Rank, ...]:
        return self.quad[0].rank,


class StraightFlush(Flush, Straight):
    __power__ = Power.STRAIGHT_FLUSH

    # resolve constructor
    def __init__(self, cards):
        super().__init__(cards)


class RoyalFlush(StraightFlush):
    __power__ = Power.ROYAL_FLUSH

    def __init__(self, cards):
        super().__init__(cards)
