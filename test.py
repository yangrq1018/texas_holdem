import unittest
from holdem.card import Card, Suit, Rank
from holdem.hand import Hand
from holdem.showdown import HighCard, TieException, Pair, TwoPair, ThreeOfAKind, Straight, Flush, FullHouse, \
    StraightFlush, RoyalFlush
from holdem.calculator import showdown_decide, Deck, histogram


class Test(unittest.TestCase):
    # 's2,h12,d7,c14,s10'
    cards = [Card(Suit.Spade, Rank.Two),
             Card(Suit.Heart, Rank.Queen),
             Card(Suit.Diamond, Rank.Seven),
             Card(Suit.Club, Rank.Ace),
             Card(Suit.Spade, Rank.Jack)]

    hand = Hand(*cards)
    # 顺子牌
    straight_hand = Hand.from_str('s2,s3,s4,s5,s6')
    # 同花牌
    flush_hand = Hand.from_str('d4,d5,d8,d11,d3')

    def test_hand(self):
        print(self.hand)
        print(self.straight_hand)
        print(self.flush_hand)

    def test_group_by_rank(self):
        print(self.hand.group_by_rank)

    def test_suits(self):
        print(self.hand.suits)
        self.assertFalse(Suit.is_flush(self.hand.suits))
        self.assertTrue(Suit.is_flush(self.flush_hand.suits))

    def test_straight(self):
        print(self.hand.ranks)
        self.assertFalse(Rank.is_straight(self.hand.ranks))
        self.assertTrue(Rank.is_straight(self.straight_hand.ranks))


class TestShowndown(unittest.TestCase):
    weak_high_card = HighCard(Hand.from_str('s2,s4,h5,d9,c8'))
    strong_high_card = HighCard(Hand.from_str('s2,s4,h5,d9,c13'))
    tie_high_card = HighCard(Hand.from_str('d2,c4,s5,s9,s8'))

    weak_one_pair = Pair(Hand.from_str('s2,h2,h5,d9,c8'))
    strong_one_pair = Pair(Hand.from_str('s2,h3,h5,d11,c11'))

    weak_two_pair = TwoPair(Hand.from_str('s3,h3,s7,h7,c4'))
    strong_two_pair = TwoPair(Hand.from_str('s10,h10,s11,h11,c5'))

    weak_three = ThreeOfAKind(Hand.from_str('s5,h5,c5,d10,d11'))
    strong_three = ThreeOfAKind(Hand.from_str('s12,h12,c12,d3,d2'))

    weak_straight = Straight(Hand.from_str('s3,s4,s5,h7,h6'))
    strong_straight = Straight(Hand.from_str('s10,s11,s12,s13,h14'))

    weak_flush = Flush(Hand.from_str('s3,s4,s5,s7,s6'))
    strong_flush = Flush(Hand.from_str('s3,s4,s5,s13,s14'))

    weak_full_house = FullHouse(Hand.from_str('s5,h5,d5,s8,d8'))
    strong_full_house = FullHouse(Hand.from_str('d14,h14,s14,h9,d9'))

    weak_straight_flush = StraightFlush(Hand.from_str('h5,h7,h6,h9,h8'))
    strong_straight_flush = StraightFlush(Hand.from_str('h10,h11,h12,h13,h9'))  # not royal

    royal_flush = RoyalFlush(Hand.from_str('h10,h11,h12,h13,h14'))

    def test_compare(self):
        # same hand value, resolve to tie compare
        self.assertTrue(self.strong_one_pair > self.weak_one_pair)
        # different hand values
        self.assertTrue(self.weak_one_pair > self.strong_high_card)

    def test_high_card(self):
        self.assertTrue(self.strong_high_card > self.weak_high_card)
        self.assertFalse(self.weak_high_card > self.strong_high_card)
        with self.assertRaises(TieException):
            _ = self.weak_high_card > self.tie_high_card
        # check high card
        self.assertTrue(HighCard.check(self.strong_high_card.hand))

    def test_one_pair(self):
        self.assertTrue(self.strong_one_pair > self.weak_one_pair)
        with self.assertRaises(TieException):
            _ = self.weak_one_pair > Pair(Hand.from_str('d2,c2,h5,d9,c8'))
        # win by kickers
        self.assertTrue(self.strong_one_pair < Pair(Hand.from_str('s2,h3,h6,c11,h11')))
        self.assertTrue(self.strong_one_pair < Pair(Hand.from_str('s2,h4,d5,c11,h11')))

        self.assertTrue(Pair.check(self.strong_one_pair.hand))
        # pair is also high card
        self.assertTrue(HighCard.check(self.strong_one_pair.hand))
        # but high card is not pair
        self.assertFalse(Pair.check(self.strong_high_card.hand))

    def test_two_pair(self):
        self.assertTrue(self.strong_two_pair > self.weak_two_pair)
        with self.assertRaises(TieException):
            _ = self.strong_two_pair > self.strong_two_pair
        self.assertTrue(TwoPair.check(self.strong_two_pair.hand))
        self.assertFalse(TwoPair.check(self.strong_one_pair.hand))
        self.assertFalse(TwoPair.check(self.weak_high_card.hand))

    def test_three_of_a_kind(self):
        self.assertTrue(self.strong_three > self.weak_three)

    def test_straight(self):
        self.assertTrue(self.strong_straight > self.weak_straight)
        with self.assertRaises(TieException):
            _ = self.strong_straight > self.strong_straight
        self.assertTrue(Straight.check(self.strong_straight.hand))
        self.assertTrue(Straight.check(self.weak_straight.hand))
        self.assertFalse(Straight.check(self.strong_two_pair.hand))

    def test_flush(self):
        self.assertTrue(Flush.check(self.strong_flush.hand))
        self.assertFalse(Flush.check(self.weak_three.hand))
        self.assertTrue(self.strong_flush > self.weak_flush)

    def test_full_house(self):
        self.assertTrue(FullHouse.check(self.strong_full_house.hand))
        self.assertTrue(FullHouse.check(self.weak_full_house.hand))
        self.assertTrue(self.strong_full_house > self.weak_full_house)
        self.assertFalse(FullHouse.check(self.strong_straight.hand))

    def test_straight_flush(self):
        self.assertTrue(StraightFlush.check(self.weak_straight_flush.hand))
        self.assertTrue(StraightFlush.check(self.strong_straight_flush.hand))
        self.assertTrue(self.strong_straight_flush > self.weak_straight_flush)
        with self.assertRaises(TieException):
            # heart straight flush to spade straight flush, tie
            _ = self.strong_straight_flush > StraightFlush(Hand.from_str('s10,s11,s12,s13,s9'))
        self.assertFalse(StraightFlush.check(Hand.from_str('s10,s11,s12,s13,h9')))
        self.assertFalse(StraightFlush.check(Hand.from_str('s10,s11,s12,s14,s9')))

        for Type in (Straight, Flush, StraightFlush, HighCard):
            self.assertTrue(Type.check(self.strong_straight_flush.hand))

    def test_royal_flush(self):
        self.assertTrue(RoyalFlush.check(self.royal_flush.hand))
        self.assertFalse(RoyalFlush.check(self.strong_straight_flush.hand))
        self.assertTrue(self.royal_flush > self.strong_straight_flush)


class TestCalculator(unittest.TestCase):
    deck = Deck()

    def test_poker(self):
        all_cards = Deck.gen_poker()
        print(all_cards)
        self.assertTrue(len(all_cards) == 52)

    def test_showdown_decision(self):
        hole_cards = [Card.from_str('h5'), Card.from_str('h10')]
        community_cards = self.deck.random_draw(5)
        print(f'Hole cards: {hole_cards}')
        print(f'Community cards: {community_cards}')
        best = showdown_decide(hole_cards[0], hole_cards[1], community_cards)
        print('Best play -->')
        print(f'5 card picked: {best.hand}')
        print(f'The type is \n {best}')

    def test_histogram(self):
        hole_cards = [Card.from_str('h5'), Card.from_str('h10')]
        remaining_cards = Deck().pop(*hole_cards).pool
        result = histogram(hole_cards[0], hole_cards[1], remaining_cards, monte_carlo=True)
        print(result)
