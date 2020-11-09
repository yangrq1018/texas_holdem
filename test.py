import unittest
from holdem.card import TexasCard, Suit, Rank, Cards
from holdem.showdown import HighCard, TieException, Pair, TwoPair, ThreeOfAKind, Straight, Flush, FullHouse, \
    StraightFlush, RoyalFlush, FourOfAKind
from holdem.calculator import histogram, showdown_decide_smart
from holdem.deck import Deck


class TestCalculator(unittest.TestCase):
    deck = Deck()

    def test_deck(self):
        all_cards = Deck.gen_poker()
        print(all_cards)
        self.assertTrue(len(all_cards) == 52)

        deck = Deck()
        hole_card1 = TexasCard.from_str('h7')
        hole_card2 = TexasCard.from_str('s9')
        # remove two cards
        removed = deck.pop(hole_card1, hole_card2)
        self.assertTrue(len(removed.pool) == 52 - 2)

    def test_showdown_decision(self):
        hole_cards = [TexasCard.from_str('h5'), TexasCard.from_str('h10')]
        community_cards = self.deck.random_draw(5)
        print(f'Hole cards: {hole_cards}')
        print(f'Community cards: {community_cards}')
        best = showdown_decide_smart(hole_cards, community_cards)
        print('Best play -->')
        print(f'5 card picked: {best}')
        print(f'The type is \n {best}')

    def test_histogram(self):
        hole_cards = [TexasCard.from_str('s14'), TexasCard.from_str('c14')]

        result = histogram(hole_cards,
                           Deck().pop(*hole_cards).pop(TexasCard.from_str('d7'), TexasCard.from_str('d8')).pool)
        for k, v in result.items():
            print(f'{k:<13} : {v:.4f}')


class TestShowdown(unittest.TestCase):
    high_card = "h4 d8, c7 d10 s2 c3 c11"
    pair = "h4 d8, c7 d10 s10 c3 c11"
    two_pair = "h4 d7, c7 d10 s10 c11 c11"
    three_kind = "h4 d7, c10 d10 s10 c3 c11"
    straight = "h4 d3, c5 d6 s7 c3 c11"
    flush = "h4 h3, c5 h6 h7 h3 c11"
    full_house = "h8 d8, c8 d10 s2 c2 c11"
    four_kind = "h8 d8, c8 d8 s2 c2 c11"
    straight_flush = "h4 h3, h5 h6 h7 h8 c11"
    royal_flush = "h13 h14, c5 s6 h12 h11 h10"

    # Royal Flush: (9,)
    # Straight Flush: (8, high card)
    # Four of a Kind: (7, quad card, kicker)
    # Full House: (6, trips card, pair card)
    @staticmethod
    def parser(string: str):
        """
        'h4 d8, c4 d4 s8 c8 c9 -> (hole1, hole2) and (five community cards)
        """
        hs, cs = [s.strip() for s in string.split(',')]
        hole_cards = [TexasCard.from_str(s.strip()) for s in hs.split(' ')]
        community_cards = [TexasCard.from_str(s.strip()) for s in cs.split(' ')]
        return hole_cards, community_cards

    @staticmethod
    def showdown(string: str):
        hole_cards, community_cards = TestShowdown.parser(string)
        return showdown_decide_smart(hole_cards, community_cards)

    def test_cases(self):
        print(self.showdown(self.high_card))
        print(self.showdown(self.pair))
        print(self.showdown(self.two_pair))
        print(self.showdown(self.three_kind))
        print(self.showdown(self.straight))
        print(self.showdown(self.flush))
        print(self.showdown(self.full_house))
        print(self.showdown(self.four_kind))
        print(self.showdown(self.straight_flush))
        print(self.showdown(self.royal_flush))

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
