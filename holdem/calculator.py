import itertools
# import sys
import operator
import time
import random
from typing import Iterable, Tuple

# from logbook import Logger, StreamHandler
from collections import defaultdict, OrderedDict, namedtuple

from tqdm import tqdm

from .card import TexasCard
from .showdown import *
from .hand import get_rank_distribution

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


# # Brutal force, check every 5-element subset of 2 holes + 5 community cards
# def showdown_decide_brutal(hole_cards, community_cards: Iterable[TexasCard]):
#     # five the best hand
#     hole_card1, hole_card2 = hole_cards
#     current_best = None
#     for card_comb in itertools.combinations([hole_card1, hole_card2] + list(community_cards), 5):
#         # form a hand
#         hand = Hand(*card_comb)
#         value = find_best_for_hand(hand)
#         if current_best is None:
#             current_best = value
#         else:
#             try:
#                 if value > current_best:
#                     current_best = value
#             except TieException:
#                 pass
#     return current_best
#

# suit with the most number of cards, if
def get_max_suit(community_cards: List[TexasCard]):
    ms = defaultdict(lambda: 0)
    for card in community_cards:
        ms[card.suit] += 1
    return max(ms.items(), key=operator.itemgetter(1))


BestRank = namedtuple('BestRank', ['rank', 'count'])


def sec_best_and_best_rank(rank_distribution):
    return [BestRank(k, v) for k, v in sorted(rank_distribution.items(), key=(lambda x: (x[1], x[0])),
                                              )[-2:]]


# return all card with the same suit = flush_suit, sorted asc, >= 5
# cards assume sorted desc
def find_suit(cards: List[TexasCard], flush_suit):
    assert len(cards) == 7
    same_suit = []
    for card in cards:
        if card.suit == flush_suit:
            same_suit.insert(0, card)
    return same_suit


def detect_straight(cards: List[TexasCard]):
    """
    cards assume sorted desc
    If there exists a five-card straight in cards, return the (five) straight cards (sorted asc);
    Else, return None
    """
    cursor = cards[0]
    acc = [cursor]
    for card in cards[1:]:
        if cursor.rank.value - 1 == card.rank.value:
            cursor = card
            acc.insert(0, card)
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
    table_cards = TexasCard.sort_desc(hole_cards + community_cards)  # sorted desc
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
            # >= 5
            flush_cards = find_suit(table_cards, max_suit)
            # check straight flush, take desc sorted cards
            result = detect_straight(TexasCard.sort_desc(flush_cards))
            if result is not None:
                # is straight flush
                if result[0].rank == Rank.Ten:
                    return RoyalFlush(Hand(*result))
                else:
                    return StraightFlush(Hand(*result))
            else:
                return Flush(Hand(*(flush_cards[-5:])))

    # Remaining: Four of a kind / Full house / Straight / Three of a kind / Two pair / Pair / High card

    # Trick: find most frequent rank and second most frequent rank
    rank_distribution = get_rank_distribution(table_cards)

    # The max_rank is the rank with most number of cards on that rank, if # of cards tie, choose the higher rank
    # use tuple inequality check
    sec_best_rank, best_rank = sec_best_and_best_rank(rank_distribution)

    def find_rank(rank):
        return [c for c in table_cards if c.rank == rank]

    def kicker_gen(func):
        # use to get tickers
        for c in table_cards:
            if func(c):
                yield c

    # check if there is a four of a kind
    if best_rank.count == 4:
        four_cards = find_rank(best_rank.rank)
        kicker = next(kicker_gen(lambda c: c.rank != best_rank.rank))
        hand_cards = four_cards + [kicker]
        return FourOfAKind(Hand(*hand_cards))
    if best_rank.count == 3 and sec_best_rank.count >= 2:
        # could be more than two cards
        small_end = find_rank(sec_best_rank.rank)[:2]
        hand_cards = find_rank(best_rank.rank) + small_end
        assert len(hand_cards) == 5
        return FullHouse(Hand(*hand_cards))

    # check if it is possible to have a straight
    if len(rank_distribution.keys()) >= 5:
        result = detect_straight(table_cards)
        if result:
            return Straight(Hand(*result))

    # check if there is a three of a kind
    if best_rank.count == 3:
        three_cards = find_rank(best_rank.rank)
        kg = kicker_gen(lambda c: c.rank != best_rank.rank)
        kickers = [next(kg) for _ in range(2)]
        hand_cards = three_cards + kickers
        return ThreeOfAKind(Hand(*hand_cards))

    # check if there is two pair / pair
    if best_rank.count == 2:
        strong_pair = find_rank(best_rank.rank)
        if sec_best_rank.count == 2:
            weak_pair = find_rank(sec_best_rank.rank)
            kicker = next(kicker_gen(lambda c: c.rank != best_rank.rank and c.rank != sec_best_rank.rank))
            hand_cards = strong_pair + weak_pair + [kicker]
            return TwoPair(Hand(*hand_cards))
        else:
            kg = kicker_gen(lambda c: c.rank != best_rank.rank)
            kickers = [next(kg) for _ in range(3)]
            hand_cards = strong_pair + kickers
            return Pair(Hand(*hand_cards))

    # high card
    return HighCard(Hand(*(table_cards[:5])))


TRIAL = 10000


def histogram(hole_cards, pool: Iterable[TexasCard], sample=None):
    start = time.time()
    results = defaultdict(lambda: 0)
    # possible to draw five from the pool
    sample_set = list(itertools.combinations(pool, 5))
    total_trial = len(sample_set)
    if sample:
        total_trial = sample
        random.shuffle(sample_set)
        sample_set = sample_set[:sample]

    for comm_cards in tqdm(sample_set):
        comm_cards = list(comm_cards)  # tuple -> list
        best = showdown_decide_smart(hole_cards, comm_cards)
        results[best.__class__] += 1

    od = OrderedDict()
    for t in HAND_SEARCH_ORDER:
        od[t.__name__] = results[t] / total_trial
    print(f'Time elapsed: {(time.time() - start)} seconds')
    return od
