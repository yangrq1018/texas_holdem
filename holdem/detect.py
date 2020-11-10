import itertools
import time
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field
from typing import List

from paradise.util import Timeit
from tqdm import tqdm

from .constant import HAND_SEARCH_ORDER
from .showdown import *


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
    Beside the normal straight, A2345 is also a straight
    :param cards: assume sorted desc
    :return:
    If there exists a five-card straight in cards,
    return (five cards), highest card rank as int (1~14)
    (sorted desc); else, return None
    """
    cursor = cards[0]
    acc = [cursor]
    # check if ace in cards
    for card in cards[1:]:
        if cursor.rank.value - 1 == card.rank.value:
            cursor = card
            acc.append(card)
            if len(acc) == 5:
                return acc, max(acc, key=operator.attrgetter('rank')).rank
        elif cursor.rank.value == card.rank.value:
            pass
        elif cursor.rank.value - 1 > card.rank.value:
            # broken straight
            cursor = card
            acc = [cursor]

    if cursor.rank.value == 2 and len(acc) == 4 and Rank.Ace in [c.rank for c in cards]:
        # pick that ace card
        highest_rank = max(acc, key=operator.attrgetter('rank')).rank
        ace_card = next(c for c in cards if c.rank == Rank.Ace)
        acc.append(ace_card)
        return acc, highest_rank
    return None


# source: https://github.com/RoelandMatthijssens/holdem_calc/blob/master/holdem_calc/holdem_functions.py
def decide_showdown(table_cards):
    # all seven cards on the table, sorted desc
    table_cards = TexasCard.sort_desc(table_cards)
    max_suit, max_suit_count = get_max_suit(table_cards)
    # Determine if flush possible
    if max_suit_count >= 5:
        # flush is reachable
        # at least five cards are of different ranks, so full house, four of a kind is not possible

        # optimal play could be flush / straight / royal flush
        # flush_cards >= 5
        flush_cards = find_suit(table_cards, max_suit)
        # result are five cards sorted desc
        result = detect_straight(flush_cards)
        if result is not None:
            cards, max_rank = result
            # is straight flush
            if cards[-1].rank == Rank.Ten:
                return RoyalFlush(cards)
            else:
                return StraightFlush(cards, max_rank)
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
            cards, max_rank = result
            return Straight(cards, max_rank)

    # check if there is a three of a kind
    if best_rank.count == 3:
        three_cards = tuple(best_rank.cards)
        kg = kicker_gen(lambda c: c.rank != best_rank.rank)
        kickers = [next(kg) for _ in range(2)]
        return ThreeOfAKind(triplet=three_cards, kickers=kickers)

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
            return Pair(pair=strong_pair, kickers=kickers)

    # high card
    return HighCard(cards=table_cards[-5:])


@Timeit(message='Time elapsed')
def histogram(hole_cards: Tuple[TexasCard, TexasCard], board: Iterable[TexasCard]):
    start = time.time()
    results = defaultdict(lambda: 0)
    # possible to draw five from the pool
    possible_boards = list(itertools.combinations(board, 5))
    total_trial = len(possible_boards)

    for board in tqdm(possible_boards):
        best = decide_showdown(hole_cards + board)
        results[best.__class__] += 1

    od = OrderedDict()
    for t in HAND_SEARCH_ORDER:
        od[t.__name__] = results[t] / total_trial
    print(f'Time elapsed: {(time.time() - start)} seconds')
    return od
