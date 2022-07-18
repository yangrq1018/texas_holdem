import itertools
from collections import OrderedDict, defaultdict
from typing import Iterable, List, Tuple

import eval7
from tqdm import tqdm

from holdem.card import TexasCard

from . import detect
from .constant import HAND_SEARCH_ORDER
from .showdown import (Flush, FourOfAKind, FullHouse, HighCard, Pair,
                       RoyalFlush, Straight, StraightFlush, ThreeOfAKind,
                       TwoPair)
from .util import Timeit

STR_MAP = {
    "High Card": HighCard,
    "Pair": Pair,
    "Two Pair": TwoPair,
    "Trips": ThreeOfAKind,
    "Straight": Straight,
    "Flush": Flush,
    "Full House": FullHouse,
    "Quads": FourOfAKind,
    "Straight Flush": StraightFlush
}


def decide_showdown(table_cards: Iterable[TexasCard], assist=True):
    """
    If table cards have duplicates, the eval7 implementation might go wrong!
    so check for it
    @param table_cards: five to seven cards
    @return:
    """
    if len(set(table_cards)) < len(tuple(table_cards)):
        raise ValueError('Duplicated cards')
    table_cards: List[TexasCard] = TexasCard.sort_desc(table_cards)
    hand = [eval7.Card(c.to_eval7_str()) for c in table_cards]
    int_type = eval7.evaluate(hand)
    str_type = eval7.handtype(int_type)
    best_type = STR_MAP[str_type]

    if assist and best_type == StraightFlush:
        # check with my implementation
        best = detect.decide_showdown(table_cards)
        assert isinstance(best, StraightFlush) or isinstance(best, RoyalFlush)
        if best.__class__ == RoyalFlush:
            best_type = RoyalFlush
    return best_type


@Timeit(message='Time elapsed')
def histogram(hole_cards: Tuple[TexasCard, TexasCard], pool: Iterable[TexasCard]):
    results = defaultdict(lambda: 0)
    possible_boards = list(itertools.combinations(pool, 5))
    total_trial = len(possible_boards)
    for comm_cards in tqdm(possible_boards):
        # return the showndown class
        best_cls = decide_showdown(hole_cards + comm_cards)
        results[best_cls] += 1
    od = OrderedDict()
    for t in HAND_SEARCH_ORDER:
        od[t.__name__] = results[t] / total_trial
    return od
