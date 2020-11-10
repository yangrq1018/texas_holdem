import unittest

from holdem.detect import histogram, decide_showdown
from holdem.card import TexasCard
from holdem.deck import Deck
from holdem.showdown import HighCard, Pair, TwoPair, ThreeOfAKind, Straight, Flush, FullHouse, \
    StraightFlush, RoyalFlush, FourOfAKind
from holdem.eval7_api import histogram as eval7_histogram, decide_showdown as eval7_decide_showdown


class TestInfra(unittest.TestCase):
    def test_card(self):
        print([TexasCard.from_str(s) for s in ('As', '2c', '3d', '5s', '4c')])

    def test_deck(self):
        all_cards = Deck.gen_poker()
        # print(all_cards)
        self.assertTrue(len(all_cards) == 52)

        deck = Deck()
        hole_card1 = TexasCard.from_str('7h')
        hole_card2 = TexasCard.from_str('9s')
        # remove two cards
        removed = deck.pop(hole_card1, hole_card2)
        self.assertTrue(len(removed.pool) == 52 - 2)
        print(deck.deal(5))

    def test_showdown_decision(self):
        hole_cards = (TexasCard.from_str('5h'), TexasCard.from_str('Th'))
        community_cards = Deck().pop(*hole_cards).deal(5)
        print(f'Hole cards: {hole_cards}')
        print(f'Community cards: {community_cards}')
        best = decide_showdown(hole_cards + community_cards)
        print('Best play -->')
        print(f'5 card picked: {best.cards()}')
        print(f'The type is \n {best}')


class TestShowdown(unittest.TestCase):
    high_card = "4h 8d 7c Td 2s 3c Jc"
    pair = "4h 8d 7c Td Ts 3c Jc"
    two_pair = "4h 7d 7c Td Ts Jc Jc"
    three_kind = "4h 7d Tc Td Ts 3c Jc"
    straight = "4h 3d 5c 6d 7s 3c Jc"
    flush = "4h 3h 5c 6h 7h 3h Jc"
    full_house = "8h 8d 8c Td 2s 2c Jc"
    four_kind = "8h 8d 8c 8d 2s 2c Jc"
    straight_flush = "4h 3h 5h 6h 7h 8h Jc"
    royal_flush = "Kh Ah 5c 6s Qh Jh Th"

    @staticmethod
    def showdown(string: str):
        cards = [TexasCard.from_str(s) for s in string.split(' ')]
        hole_cards = tuple(cards[:2])
        community_cards = tuple(cards[2:])
        result = decide_showdown(hole_cards + community_cards)
        return result

    def test_straight_detection(self):
        straight = "4h 3d 5c 6d 7s 3c Jc"
        min_straight = "Ah 3d 2c 4d 5s 3c Jc"
        self.assertIsInstance(self.showdown(straight), Straight)
        self.assertIsInstance(self.showdown(min_straight), Straight)

    def test_case_eq(self):
        self.assertIsInstance(self.showdown(self.high_card), HighCard)
        self.assertIsInstance(self.showdown(self.pair), Pair)
        self.assertIsInstance(self.showdown(self.two_pair), TwoPair)
        self.assertIsInstance(self.showdown(self.three_kind), ThreeOfAKind)
        self.assertIsInstance(self.showdown(self.straight), Straight)
        self.assertIsInstance(self.showdown(self.flush), Flush)
        self.assertIsInstance(self.showdown(self.full_house), FullHouse)
        self.assertIsInstance(self.showdown(self.four_kind), FourOfAKind)
        self.assertIsInstance(self.showdown(self.straight_flush), StraightFlush)
        self.assertIsInstance(self.showdown(self.royal_flush), RoyalFlush)

    def test_histogram(self):
        hole_cards_p1 = (TexasCard.from_str('As'), TexasCard.from_str('Ac'))
        hole_cards_p2 = (TexasCard.from_str('7c'), TexasCard.from_str('8d'))
        board = Deck().pop(*hole_cards_p1, *hole_cards_p2).pool
        result = histogram(hole_cards_p1, board)
        for k, v in result.items():
            print(f'{k:<13} : {v:.9f}')


class TestPyEval7(unittest.TestCase):
    high_card = "4h 8d 7c Td 2s 3c Jc"
    pair = "4h 8d 7c Td Ts 3c Jc"
    two_pair = "4h 7d 7c Td Ts Jc Jd"
    three_kind = "4h 7d Tc Td Ts 3c Jc"
    straight = "4h 3d 5c 6d 7s 3c Jc"
    flush = "4h 3h 5c 6h 7h 3d Jh"
    full_house = "8h 8d 8c Td 2s 2c Jc"
    four_kind = "8h 8d 8s 8c 2s 2c Jc"
    straight_flush = "4h 3h 5h 6h 7h 8h Jc"
    royal_flush = "Kh Ah 5c 6s Qh Jh Th"

    @staticmethod
    def showdown(string: str):
        cards = [TexasCard.from_str(s) for s in string.split(' ')]
        hole_cards = tuple(cards[:2])
        community_cards = tuple(cards[2:])
        result = eval7_decide_showdown(hole_cards + community_cards)
        return result

    def test_case_eq(self):
        self.assertEqual(self.showdown(self.high_card), HighCard)
        self.assertEqual(self.showdown(self.pair), Pair)
        self.assertEqual(self.showdown(self.two_pair), TwoPair, self.showdown(self.two_pair))
        self.assertEqual(self.showdown(self.three_kind), ThreeOfAKind)
        self.assertEqual(self.showdown(self.straight), Straight)
        self.assertEqual(self.showdown(self.flush), Flush)
        self.assertEqual(self.showdown(self.full_house), FullHouse)
        self.assertEqual(self.showdown(self.four_kind), FourOfAKind)
        self.assertEqual(self.showdown(self.straight_flush), StraightFlush)
        self.assertEqual(self.showdown(self.royal_flush), RoyalFlush)

    def test_eval7_histogram(self):
        hole_cards_p1 = (TexasCard.from_str('As'), TexasCard.from_str('Ac'))
        hole_cards_p2 = (TexasCard.from_str('7c'), TexasCard.from_str('8d'))
        board = Deck().pop(*hole_cards_p1, *hole_cards_p2).pool
        result = eval7_histogram(hole_cards_p1, board)
        for k, v in result.items():
            print(f'{k:<13} : {v:.9f}')
