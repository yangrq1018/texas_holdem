import itertools
import sys
from typing import Iterable

import numpy as np
from logbook import Logger, StreamHandler
from collections import defaultdict

from tqdm import tqdm

from .card import Suit, Card
from .showdown import *

logger = Logger('calculator')
StreamHandler(sys.stdout).push_application()


class Deck:
    def __init__(self, cards=None):
        if cards is None:
            self.pool = self.gen_poker()
        else:
            self.pool = list(cards)

    def random_draw(self, n):
        idxes = np.random.randint(0, len(self.pool), size=n)
        return [self.pool[i] for i in idxes]

    @staticmethod
    def gen_poker():
        """
        :return: a list of 52 poker cards, excluding the Jokers
        """
        cards = []
        for s, r in itertools.product(list(Suit), list(Rank)):
            cards.append(Card(s, r))
        return cards

    def pop(self, *remove: Card):
        """

        :param cards:
        :return: a decker with cards removed
        """
        cards = self.pool.copy()
        cards = [c for c in cards if c not in remove]
        return Deck(cards)


HAND_SEARCH_ORDER = [
    RoyalFlush,
    StraightFlush,
    FourOfAKind,
    FullHouse,
    Flush,
    Straight,
    ThreeOfAKind,
    TwoPair,
    Pair,
    HighCard
]


def find_best_for_hand(hand: Hand):
    for showdown_type in HAND_SEARCH_ORDER:
        if showdown_type.check(hand):
            showdown = showdown_type(hand)
            return showdown


def showdown_decide(hole_card1, hole_card2, community_cards: Iterable[Card]):
    # five the best hand
    current_best = None
    for card_comb in itertools.combinations([hole_card1, hole_card2] + list(community_cards), 5):
        # form a hand
        hand = Hand(*card_comb)
        value = find_best_for_hand(hand)
        if current_best is None:
            current_best = value
        else:
            try:
                if value > current_best:
                    current_best = value
            except TieException:
                pass
    return current_best


def histogram(hole_card1, hole_card2, pool: Iterable[Card], monte_carlo=False):
    results = defaultdict(lambda: 0)
    # possible to draw five from the pool
    sample_set = list(itertools.combinations(pool, 5))
    total_trial = len(sample_set)
    if monte_carlo:
        total_trial = 1000
        sample_set = sample_set[:total_trial]

    for comm_cards in tqdm(sample_set):
        best = showdown_decide(hole_card1, hole_card2, comm_cards)
        results[best.__class__] += 1

    results = dict(results)
    results = {k.__name__: v / total_trial for k, v in results.items()}
    for t in HAND_SEARCH_ORDER:
        if t.__name__ not in results:
            results[t.__name__] = 0
    return results
