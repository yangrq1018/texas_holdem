import click

from .detect import histogram
from .deck import Deck
from .card import TexasCard


def card_parser(arg):
    return TexasCard.from_str(arg)


@click.command()
@click.argument('hole_cards', type=card_parser, nargs=-1)
@click.option('-p', 'progress', is_flag=True, help="show progress bar (tqdm based)")
@click.option('-x', 'exclude', type=lambda arg: [card_parser(a) for a in arg.split(',')], help="exclude other cards from the pool")
def main(hole_cards, progress, exclude):
    """Calculate the histgram for a hand of 'HOLE_CARDS'.
    HOLE_CARDS should be comma-separated cards
    """
    if not hole_cards:
        return "I need some cards"
    hole_cards = list(hole_cards)
    if exclude is None:
        exclude = []
    remaining_cards = Deck().pop(*hole_cards, *exclude).pool
    result = histogram(hole_cards, remaining_cards, progress=progress)
    for k, v in result.items():
        print(f'{k:<13} : {v:.6f}')
