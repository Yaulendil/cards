from .deck import Card, Deck, Suit
from .hands import Hand, poker

__all__ = ("Card", "Deck", "Hand", "poker", "Suit", "test")


d = Deck()
d.populate()

com = Hand(discard=d, draw=d)

h0 = Hand(com, discard=d, draw=d)
h1 = Hand(com, discard=d, draw=d)


def test(nc: int = 5, nh: int = 2):
    print()
    d.shuffle()

    com.draw(nc)
    h0.draw(nh)
    h1.draw(nh)

    c0 = poker.evaluate(h0)
    c1 = poker.evaluate(h1)
    v0 = c0.value()
    v1 = c1.value()

    print("Public:", com)
    print(h0)
    print(" ", c0)
    print(h1)
    print(" ", c1)
    print()

    if v0 == v1:
        print("TIED")
    elif v0 > v1:
        print("Winner:", h0, "with", c0)
    else:
        print("Winner:", h1, "with", c1)
    print()

    com.dump()
    h0.dump()
    h1.dump()
