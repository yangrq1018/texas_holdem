import unittest
from holdem.card import Card, Suit, Rank
from holdem.hand import Hand


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



