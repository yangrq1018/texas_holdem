import click

from .detect import histogram
from .deck import Deck
from .card import TexasCard


def card_parser(card_arg):
    return [TexasCard.from_str(c) for c in card_arg.split(',')]


@click.command()
@click.option('-h', '--hole', 'hole_cards', type=card_parser)
@click.option('-e', '--exact', is_flat=True)
def main(hole_cards, exact):
    remaining_cards = Deck().pop(*hole_cards).pool
    result = histogram(hole_cards, remaining_cards)
    for k, v in result.items():
        print(f'{k:<13} : {v:.6f}')
