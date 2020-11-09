"""
Class representing the possible hand values
"""
import abc
import enum
import operator
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


def is_sorted(l):
    # desc
    return all(l[i] >= l[i + 1] for i in range(len(l) - 1))


def is_sorted_cards(cards):
    return is_sorted([c.rank.value for c in cards])


def is_straight_flush(cards):
    ranks = [c.rank.value for c in cards]
    assert len(ranks) == 5
    assert max(ranks) - min(ranks) == 4
    assert len(set(ranks)) == 5
    assert is_sorted(ranks)
    suits = [c.suit for c in cards]
    assert all(s == suits[0] for s in suits)
    assert not any([cards[i] == cards[i + 1] for i in range(len(cards) - 1)])


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

    def cards(self):
        return tuple(self.kickers)


class HighCard(Showdown):
    __power__ = Power.HIGH_CARD

    def __init__(self, cards):
        super().__init__(cards=cards)

    def check(self):
        assert is_sorted_cards(self.kickers)


class Pair(Showdown):
    __power__ = Power.PAIR

    def __init__(self, pair: Tuple[TexasCard, ...], cards: Iterable[TexasCard]):
        """

        :param pair: two cards
        :param cards: sorted desc
        """
        super().__init__(cards=cards)
        self.pair = tuple(pair)

    def check(self):
        assert self.pair[0].rank == self.pair[1].rank
        assert len(self.pair) == 2
        assert is_sorted_cards(self.kickers)

    def values(self) -> Tuple[Rank, ...]:
        # priority of the pair cards
        return (self.pair[0].rank,) + super().values()

    def cards(self):
        return self.pair + super().cards()


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
        self.pair_major = tuple(pair_major)
        self.pair_minor = tuple(pair_minor)

    def values(self) -> Tuple[Rank, ...]:
        return (self.pair_major[0].rank, self.pair_minor[0].rank) + super().values()

    def check(self):
        assert self.pair_minor[0].rank == self.pair_minor[1].rank
        assert self.pair_major[0].rank == self.pair_major[1].rank

    def cards(self):
        return self.pair_major + self.pair_minor + super().cards()


class ThreeOfAKind(Showdown):
    __power__ = Power.THREE_OF_A_KIND

    def __init__(self, triplet: Tuple[TexasCard, ...], cards):
        super().__init__(cards=cards)
        self.triplet = tuple(triplet)

    def values(self) -> Tuple[Rank, ...]:
        return (self.triplet[0].rank,) + super().values()

    def check(self):
        assert self.triplet[0].rank == self.triplet[1].rank == self.triplet[2].rank

    def cards(self):
        return self.triplet + super().cards()


class Straight(Showdown):
    __power__ = Power.STRAIGHT

    def __init__(self, cards):
        super().__init__(cards=cards)

    def check(self):
        assert max(self.kickers, key=operator.attrgetter('rank')).rank.value - min(self.kickers,
                                                                                   key=operator.attrgetter(
                                                                                       'rank')).rank.value == 4

        ranks = [k.rank.value for k in self.kickers]
        assert is_sorted(ranks)
        assert len(set(ranks)) == 5


class Flush(Showdown):
    __power__ = Power.FLUSH

    def __init__(self, cards):
        super().__init__(cards)


class FullHouse(Showdown):
    __power__ = Power.FULL_HOUSE

    def __init__(self, triplet: Tuple[TexasCard, ...], twins: [TexasCard, TexasCard, TexasCard]):
        # no kickers
        super().__init__(cards=[])
        self.triplet = tuple(triplet)
        self.twins = tuple(twins)
        assert len(self.triplet) == 3
        assert len(self.twins) == 2

    def values(self) -> Tuple[Rank, ...]:
        return (self.triplet[0].rank, self.twins[0].rank) + super().values()

    def cards(self):
        return self.triplet + self.twins


class FourOfAKind(Showdown):
    __power__ = Power.FOUR_OF_A_KIND

    def __init__(self, quad: Tuple[TexasCard, ...], kicker: TexasCard):
        super().__init__(cards=[kicker])
        self.quad = tuple(quad)

    def values(self) -> Tuple[Rank, ...]:
        return (self.quad[0].rank,) + super().values()

    def cards(self):
        return self.quad + super().cards()


class StraightFlush(Flush, Straight):
    __power__ = Power.STRAIGHT_FLUSH

    def check(self):
        is_straight_flush(list(self.kickers))


class RoyalFlush(StraightFlush):
    __power__ = Power.ROYAL_FLUSH
