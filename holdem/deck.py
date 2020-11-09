import itertools
from functools import cached_property
from typing import List

import numpy as np

from holdem.card import Suit, Rank, TexasCard


class Deck:
    def __init__(self, cards: List[TexasCard] = None):
        if cards is None:
            self._pool = self.gen_poker()
        else:
            self._pool = list(cards)

    def random_draw(self, n):
        """
        Draw texas cards from the decker
        """
        idxes = np.random.randint(0, len(self.pool), size=n)
        return [self.pool[i] for i in idxes]

    @cached_property
    def pool(self):
        # give a copy
        return list(self._pool)

    @staticmethod
    def gen_poker():
        """
        :return: a list of 52 poker cards, excluding the Jokers
        """
        cards = []
        for s, r in itertools.product(list(Suit), list(Rank)):
            cards.append(TexasCard(s, r))
        return cards

    def pop(self, *remove: TexasCard):
        """
        :param remove: cards to be pop out
        :return: new Deck object with cards removed
        """
        cards = [c for c in self._pool if c not in remove]
        return Deck(cards)

    def __repr__(self):
        return f'<Deck obj, pool={len(self._pool)} cards>'
