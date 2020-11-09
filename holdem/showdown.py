"""
Class representing the possible hand values
"""
import abc
import enum
from typing import List

from holdem.card import Rank
from holdem.hand import Hand


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


class Showdown(abc.ABC):
    __power__ = None

    def __init__(self, hand):
        # kickers in descending order
        self.hand = hand
        self.kickers: List[Rank] = []

    def __gt__(self, other):
        if self.__power__ != other.__power__:
            return self.__power__ > other.__power__
        # solve tie
        return self.solve_tie(other)

    @abc.abstractmethod
    def solve_tie(self, other):
        pass

    def solve_kickers(self, other):
        for tk, ok in zip(self.kickers, other.kickers):
            if tk != ok:
                return tk > ok
        raise TieException()

    @staticmethod
    @abc.abstractmethod
    def check(hand: Hand):
        """
        :param hand: hand to be check against this power class
        :return: True if qualified, else False
        """
        pass


class HighCard(Showdown):
    __power__ = Power.HIGH_CARD

    def __init__(self, hand: Hand):
        super().__init__(hand)
        # all cards are kickers
        self.kickers = [c.rank for c in reversed(hand.cards)]

    def solve_tie(self, other):
        return self.solve_kickers(other)

    @staticmethod
    def check(hand: Hand):
        # High card doesn't need to be checked
        return True


class Pair(Showdown):
    __power__ = Power.PAIR

    def __init__(self, hand: Hand):
        """
        Then hand is assumed to have only one pair
        :param hand:
        """
        super().__init__(hand)
        gbr = hand.group_by_rank
        for rank in reversed(gbr.keys()):
            if gbr[rank] == 2:
                self.pair: Rank = rank
            else:
                # kickers in descending order
                self.kickers.append(rank)
        assert len(self.kickers) == 3 and self.pair is not None

    def solve_tie(self, other):
        """
        :param other: Pair
        :return:
        True if this beats other, False if other beats this.
        Raise TieException otherwise
        """
        if self.pair != other.pair:
            return self.pair > other.pair
        # compare kickers
        return self.solve_kickers(other)

    @staticmethod
    def check(hand: Hand):
        for _, count in hand.group_by_rank.items():
            if count == 2:
                return True
        return False


class TwoPair(Showdown):
    __power__ = Power.TWO_PAIR

    def __init__(self, hand: Hand):
        super().__init__(hand)
        gbr = hand.group_by_rank
        self.pair1 = None  # low rank
        self.pair2 = None  # high rank
        for rank in reversed(gbr.keys()):
            if gbr[rank] == 2:
                if self.pair2 is None:
                    self.pair2: Rank = rank
                else:
                    self.pair1: Rank = rank
            else:
                self.kickers.append(rank)  # append Card, not rank
        assert len(self.kickers) == 1 and self.pair1 is not None and self.pair2 is not None

    def solve_tie(self, other):
        if self.pair2 != other.pair2:
            return self.pair2 > other.pair2
        if self.pair1 != other.pair1:
            return self.pair1 > other.pair1
        return self.solve_kickers(other)

    @staticmethod
    def check(hand: Hand):
        acc = 0
        for _, count in hand.group_by_rank.items():
            if count == 2:
                acc += 1
        return acc == 2


class ThreeOfAKind(Showdown):
    __power__ = Power.THREE_OF_A_KIND

    def __init__(self, hand: Hand):
        super().__init__(hand)
        gbr = hand.group_by_rank

        for rank in reversed(gbr.keys()):
            if gbr[rank] == 3:
                self.three = rank
            else:
                self.kickers.append(rank)

        assert len(self.kickers) == 2 and self.three is not None

    def solve_tie(self, other):
        if self.three != other.three:
            return self.three > other.three
        return self.solve_kickers(other)

    @staticmethod
    def check(hand: Hand):
        for _, count in hand.group_by_rank.items():
            if count == 3:
                return True
        return False


class Straight(Showdown):
    __power__ = Power.STRAIGHT

    def __init__(self, hand: Hand):
        super().__init__(hand)
        # all cards are kickers
        self.kickers = [c.rank for c in reversed(hand.cards)]

    def solve_tie(self, other):
        # In tie solution, Straight is not different from high cards
        return self.solve_kickers(other)

    @staticmethod
    def check(hand: Hand):
        cursor_card = hand.cards[0]
        for card in hand.cards[1:]:
            if card.rank.value != cursor_card.rank.value + 1:
                return False
            cursor_card = card
        return True


class Flush(Showdown):
    __power__ = Power.FLUSH

    def __init__(self, hand: Hand):
        super().__init__(hand)
        # all cards are kickers
        self.kickers = [c.rank for c in reversed(hand.cards)]

    def solve_tie(self, other):
        return self.solve_kickers(other)

    @staticmethod
    def check(hand: Hand):
        # 花色一样, check the suits property
        pivotal = hand.suits[0]
        for suit in hand.suits[1:]:
            if suit != pivotal:
                return False
            pivotal = suit
        return True


class FullHouse(Showdown):
    __power__ = Power.FULL_HOUSE

    def __init__(self, hand: Hand):
        # no kickers
        super().__init__(hand)
        gbr = hand.group_by_rank
        for rank in gbr.keys():
            if gbr[rank] == 3:
                self.big_end = rank
            if gbr[rank] == 2:
                self.small_end = rank

    def solve_tie(self, other):
        if self.big_end != other.big_end:
            return self.big_end > other.big_end
        if self.small_end != other.small_end:
            return self.small_end > other.small_end
        raise TieException()

    @staticmethod
    def check(hand: Hand):
        has_small = False
        has_big = False
        gbr = hand.group_by_rank
        for rank in gbr.keys():
            if gbr[rank] == 3:
                has_big = True
            if gbr[rank] == 2:
                has_small = True
        return has_small and has_big


class FourOfAKind(Showdown):
    __power__ = Power.FOUR_OF_A_KIND

    def __init__(self, hand: Hand):
        super().__init__(hand)
        gbr = hand.group_by_rank

        for rank in reversed(gbr.keys()):
            if gbr[rank] == 4:
                self.four = rank
            else:
                self.kickers.append(rank)

        assert len(self.kickers) == 1 and self.four is not None

    def solve_tie(self, other):
        if self.four != other.four:
            return self.four > other.four
        return self.solve_kickers(other)

    @staticmethod
    def check(hand: Hand):
        for _, count in hand.group_by_rank.items():
            if count == 4:
                return True
        return False


class StraightFlush(Flush):
    __power__ = Power.STRAIGHT_FLUSH

    @staticmethod
    def check(hand: Hand):
        if not Flush.check(hand):
            return False
        if not Straight.check(hand):
            return False
        return True


class RoyalFlush(StraightFlush):
    __power__ = Power.ROYAL_FLUSH

    @staticmethod
    def check(hand: Hand):
        if not StraightFlush.check(hand):
            return False
        # check straight starts at ten
        return hand.cards[0].rank == Rank.Ten
