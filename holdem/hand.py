from collections import OrderedDict
from functools import cached_property
from typing import List

from .card import TexasCard


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
        :return: OrderedDict(key, value) pairs where key is rank, value is a tuple of cards in that rank,
        keys are sorted in ascending order
        """
        d = []
        group = None
        for idx, card in enumerate(self.cards):
            if group is None:
                group = (card.rank, 1)
            else:
                if group[0] == card.rank:
                    group = (group[0], group[1] + 1)
                else:
                    d.append(group)
                    group = (card.rank, 1)
            if idx == len(self.cards) - 1:
                d.append(group)
        return OrderedDict(d)

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
