import itertools
# import sys
import time
import random
from typing import Iterable

# from logbook import Logger, StreamHandler
from collections import defaultdict, OrderedDict

from tqdm import tqdm

from .card import TexasCard
from .showdown import *

# logger = Logger('calculator')
# StreamHandler(sys.stdout).push_application()

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


def showdown_decide(hole_card1, hole_card2, community_cards: Iterable[TexasCard]):
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


TRIAL = 10000


def histogram(hole_card1, hole_card2, pool: Iterable[TexasCard], monte_carlo=False):
    start = time.time()
    results = defaultdict(lambda: 0)
    # possible to draw five from the pool
    sample_set = list(itertools.combinations(pool, 5))
    total_trial = len(sample_set)
    if monte_carlo:
        total_trial = TRIAL
        random.shuffle(sample_set)
        sample_set = sample_set[:total_trial]

    for comm_cards in tqdm(sample_set):
        best = showdown_decide(hole_card1, hole_card2, comm_cards)
        results[best.__class__] += 1

    od = OrderedDict()
    for t in HAND_SEARCH_ORDER:
        od[t.__name__] = results[t] / total_trial
    print(f'Time elapsed: {(time.time() - start)} seconds')
    return od
