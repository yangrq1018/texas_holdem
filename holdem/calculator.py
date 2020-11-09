import itertools
# import sys
import operator
import time
# from logbook import Logger, StreamHandler
from collections import defaultdict, OrderedDict, namedtuple
from dataclasses import dataclass, field
from typing import List
from . import check

import numpy as np
from tqdm import tqdm

from .showdown import *

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


@dataclass
class BestRankItem:
    rank: Rank = None
    count: int = 0
    cards: List[TexasCard] = field(default_factory=list)


def get_rank_distribution(cards: Iterable[TexasCard]):
    """

    :param cards: descending sorted
    :return: OrdedDict[Rank, (count, cards)], keys sorted descending
    """
    d = defaultdict(BestRankItem)
    for card in cards:
        obj = d[card.rank]
        obj.rank = card.rank
        obj.count += 1
        obj.cards.append(card)
    return d


# suit with the most number of cards
# ties doesn't matter here, 2==2 ties cannot change anything
def get_max_suit(community_cards: List[TexasCard]):
    ms = defaultdict(lambda: 0)
    for card in community_cards:
        ms[card.suit] += 1
    return max(ms.items(), key=operator.itemgetter(1))


def find_suit(cards: List[TexasCard], flush_suit):
    """

    :param cards: sorted desc
    :param flush_suit: Suit
    :return: all card with the same suit = flush_suit, sorted desc, at least five
    """
    same_suit = []
    for card in cards:
        if card.suit == flush_suit:
            same_suit.append(card)
    return same_suit


def detect_straight(cards: List[TexasCard]):
    """
    :param cards: assume sorted desc
    :return: If there exists a five-card straight in cards, return the highest (five) straight cards
    (sorted desc); else, return None
    """
    assert is_sorted_cards(cards)
    cursor = cards[0]
    acc = [cursor]
    for card in cards[1:]:
        if cursor.rank.value - 1 == card.rank.value:
            cursor = card
            acc.append(card)
            if len(acc) == 5:
                return acc
        elif cursor.rank.value == card.rank.value:
            pass
        elif cursor.rank.value - 1 > card.rank.value:
            # broken straight
            cursor = card
            acc = [cursor]
    return None


# Return Values:
# Royal Flush: (9,)
# Straight Flush: (8, high card)
# Four of a Kind: (7, quad card, kicker)
# Full House: (6, trips card, pair card)
# Flush: (5, [flush high card, flush second high card, ..., flush low card])
# Straight: (4, high card)
# Three of a Kind: (3, trips card, (kicker high card, kicker low card))
# Two Pair: (2, high pair card, low pair card, kicker)
# Pair: (1, pair card, (kicker high card, kicker med card, kicker low card))
# High Card: (0, [high card, second high card, third high card, etc.])
# source: https://github.com/RoelandMatthijssens/holdem_calc/blob/master/holdem_calc/holdem_functions.py
def showdown_decide_smart(hole_cards, community_cards):
    # all seven cards on the table, sorted desc
    table_cards = TexasCard.sort_desc(hole_cards + community_cards)
    max_suit, max_suit_count = get_max_suit(community_cards)
    # Determine if flush possible
    if max_suit_count >= 3:
        for hole_card in hole_cards:
            if hole_card.suit == max_suit:
                max_suit_count += 1
        if max_suit_count >= 5:
            # flush is reachable
            # at least five cards are of different ranks, so full house, four of a kind is not possible

            # optimal play could be flush / straight / royal flush
            # flush_cards >= 5
            flush_cards = find_suit(table_cards, max_suit)
            # result are five cards sorted desc
            result = detect_straight(flush_cards)
            if result is not None:
                # is straight flush
                if result[-1].rank == Rank.Ten:
                    return RoyalFlush(result)
                else:
                    return StraightFlush(result)
            else:
                return Flush(flush_cards[-5:])

    # Remaining: Four of a kind / Full house / Straight / Three of a kind / Two pair / Pair / High card

    # Trick: find most frequent rank and second most frequent rank
    rank_distribution = get_rank_distribution(table_cards)

    # sort the k, v pair by count(value[0] first, then by the rank(key)
    # lambda tuple unpacking is removed in python 3
    rank_distribution_sorted = sorted(rank_distribution.items(),
                                      key=lambda kv: (kv[1].count, kv[0]))
    sec_best_rank, best_rank = [v for _, v in rank_distribution_sorted[-2:]]
    sec_best_rank: BestRankItem
    best_rank: BestRankItem

    def kicker_gen(func):
        # use to get tickers
        for c in table_cards:
            if func(c):
                yield c

    # check if there is a four of a kind
    if best_rank.count == 4:
        four_cards = tuple(best_rank.cards)
        kicker = next(kicker_gen(lambda c: c.rank != best_rank.rank))
        return FourOfAKind(quad=four_cards, kicker=kicker)
    if best_rank.count == 3 and sec_best_rank.count >= 2:
        # could be more than two cards
        triplet = tuple(best_rank.cards)
        twins = tuple(sec_best_rank.cards[:2])  # could be more than two
        return FullHouse(triplet, twins)

    # check if it is possible to have a straight
    if len(rank_distribution.keys()) >= 5:
        result = detect_straight(table_cards)
        if result:
            return Straight(result)

    # check if there is a three of a kind
    if best_rank.count == 3:
        three_cards = tuple(best_rank.cards)
        kg = kicker_gen(lambda c: c.rank != best_rank.rank)
        kickers = [next(kg) for _ in range(2)]
        return ThreeOfAKind(triplet=three_cards, cards=kickers)

    # check if there is two pair / pair
    if best_rank.count == 2:
        strong_pair = tuple(best_rank.cards)
        if sec_best_rank.count == 2:
            weak_pair = tuple(sec_best_rank.cards)
            kicker = next(kicker_gen(lambda c: c.rank != best_rank.rank and c.rank != sec_best_rank.rank))
            return TwoPair(pair_major=strong_pair, pair_minor=weak_pair, kicker=kicker)
        else:
            kg = kicker_gen(lambda c: c.rank != best_rank.rank)
            kickers = [next(kg) for _ in range(3)]
            return Pair(pair=strong_pair, cards=kickers)

    # high card
    return HighCard(cards=table_cards[-5:])


def histogram(hole_cards, pool: Iterable[TexasCard], sample=None):
    start = time.time()
    results = defaultdict(lambda: 0)
    # possible to draw five from the pool
    sample_set = list(itertools.combinations(pool, 5))
    total_trial = len(sample_set)
    if sample:
        total_trial = sample
        idxes = np.random.randint(0, len(sample_set), size=sample)
        sample_set = [sample_set[i] for i in idxes]

    for comm_cards in tqdm(sample_set):
        comm_cards = list(comm_cards)  # tuple -> list
        best = showdown_decide_smart(hole_cards, comm_cards)
        # brutal search best
        brutal_best = None
        for five_card in itertools.combinations(hole_cards + comm_cards, 5):
            for t in HAND_SEARCH_ORDER:
                check_t = getattr(check, t.__name__)
                if check_t.check(check.Hand(*five_card)):
                    if brutal_best is None:
                        brutal_best = t
                    elif brutal_best.__power__ < t.__power__:
                        brutal_best = t
        # print(brutal_best.__name__, best.__class__.__name__)
        assert brutal_best.__name__ == best.__class__.__name__

        # check
        # if True:
        #     hand = check.Hand(*best.cards())
        #     for t in HAND_SEARCH_ORDER:
        #         if t.__name__ != best.__class__.__name__:
        #             check_t = getattr(check, t.__name__)
        #             assert not check_t.check(hand)
        #         else:
        #             assert getattr(check, best.__class__.__name__).check(hand)
        #             break
        results[best.__class__] += 1

    od = OrderedDict()
    for t in HAND_SEARCH_ORDER:
        od[t.__name__] = results[t] / total_trial
    print(f'Time elapsed: {(time.time() - start)} seconds')
    return od
