import click

from .calculator import Deck, histogram
from .card import Card


def card_parser(card_arg):
    return [Card.from_str(c) for c in card_arg.split(',')]


@click.command()
@click.option('-h', '--hole', 'hole_cards', type=card_parser)
@click.option('-m', '--monte-carlo', is_flag=True)
def main(hole_cards, monte_carlo):
    # hole_cards = [Card.from_str('h5'), Card.from_str('h10')]
    remaining_cards = Deck().pop(*hole_cards).pool
    result = histogram(hole_cards[0], hole_cards[1], remaining_cards, monte_carlo=monte_carlo)
    for k, v in result.items():
        print(f'{k:<13} : {v:.4f}')



