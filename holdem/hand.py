from collections import OrderedDict, defaultdict
from functools import cached_property
from typing import List

from .card import TexasCard, Rank


def get_rank_distribution(cards: List[TexasCard]):
    # keys are reversely sorted, only non-zero ranks
    d = defaultdict(lambda: 0)

    for card in cards:
        d[card.rank] += 1

    result = OrderedDict()
    for rank in reversed(list(Rank)):
        if d[rank] != 0:
            result[rank] = d[rank]
    return result


class Hand:
    """
    Represent a hand of five cards
    """

    def __init__(self, *cards: TexasCard):
        assert len(cards) == 5

        # sort by ranks
        self.cards: List[TexasCard] = sorted(cards)

    @cached_property
    def group_by_rank(self):
        """
        Only rank with at least one card is returned
        :return: OrderedDict(key, value) pairs where key is rank, value is the count of cards in that rank, value != 0
        keys are sorted in ascending order
        """
        return get_rank_distribution(self.cards)

    @classmethod
    def from_str(cls, hand_str: str):
        """
        :param hand_str: strings like 'd10,a2,s7,h11,h2',,
        :return: return Hands like [Diamond Jack, Ace Two, Spade Seven, Heart Queen, Heart Two]
        """
        cards = [TexasCard.from_str(card_str) for card_str in hand_str.split(',')]
        return cls(*cards)

    @cached_property
    def suits(self):
        """
        :return: Tuple (five suits of the cards)
        """
        return tuple(card.suit for card in self.cards)

    @cached_property
    def ranks(self):
        """
        :return: Tuple (five ranks of the cards)
        """
        return tuple(card.rank for card in self.cards)

    @cached_property
    def highest_card(self):
        """
        :return: card with the highest rank
        """
        return self.cards[-1]

    def __repr__(self):
        return self.cards.__repr__()

    def play(self):
        """
        :return: the best wind type the player can play
        """
        pass
