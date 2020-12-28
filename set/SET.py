#!/bin/env python3
from typing import Dict, List
from itertools import combinations
from math import sqrt
from PIL import Image
from time import time
from argparse import ArgumentParser

from z3 import *

t = time()


def log(message):
    print(f"[{time() - t:.3f} s] {message}")


def is_set_prop(c_1, c_2, c_3):
    return Or(And(c_1 == c_2, c_2 == c_3), Distinct(c_1, c_2, c_3))


def last_card(g, k, datatypes, c_1, c_2):
    return If(
        g(c_1) == g(c_2),
        g(c_1),
        If(
            Distinct(datatypes[k].constructor(0)(), g(c_1), g(c_2)),
            datatypes[k].constructor(0)(),
            If(
                Distinct(datatypes[k].constructor(1)(), g(c_1), g(c_2)),
                datatypes[k].constructor(1)(),
                datatypes[k].constructor(2)(),
            ),
        ),
    )


def set_constants() -> Dict[str, List[str]]:
    types = {
        "colour": ["purple", "red", "green"],
        "shape": ["oval", "diamond", "squiggle"],
        "fill": ["empty", "shaded", "filled"],
        "count": ["1", "2", "3"],
    }

    return types


def make_model(
    s: Solver, types: Dict[str, List[str]], card_count: int, first_order, second_order, third_order, doubles
):
    datatypes: Dict[str, Datatype] = {}
    for key, val in types.items():
        assert len(val) == 3
        attr = Datatype(key)
        for opt in val:
            attr.declare(opt)
        attr = attr.create()
        datatypes[key] = attr

    card = Datatype("card")
    card.declare("c", *datatypes.items())
    card = card.create()
    getters = {list(types.keys())[i]: card.accessor(0, i) for i in range(len(types))}
    attrs = [dt.constructor(0)() for dt in datatypes.values()]

    cards = [Const(f"x__{i}", card) for i in range(card_count)]

    # optimisations
    s.add(cards[0] == card.c(*attrs))
    s.add(And([
        Implies(getters[k](cards[1]) == getters[k](cards[0]),
            And([
                getters[o_k](cards[1]) == getters[o_k](cards[0])
                for o_k in list(datatypes.keys())[i:]
            ])
        )
        for i, k in enumerate(datatypes.keys())
    ]))

    # constraints
    s.add(Distinct(cards))

    constraints = []

    if first_order:
        for c_1, c_2, c_3 in combinations(cards, 3):
            s.add(Not(And([is_set_prop(g(c_1), g(c_2), g(c_3)) for _, g in getters.items()])))
        log("made first order constraints")

    if second_order:
        for a_1, a_2 in combinations(cards, 2):
            for b_1, b_2 in combinations(cards, 2):
                if a_1 in [b_1, b_2] or a_2 in [b_1, b_2]:
                    continue
                s.add(
                    Not(
                        And(
                            [
                                last_card(g, k, datatypes, a_1, a_2) == last_card(g, k, datatypes, b_1, b_2)
                                for k, g in getters.items()
                            ]
                        )
                    )
                )
        log("made second order constraints")

    if third_order:
        for a_1, a_2 in combinations(cards, 2):
            for b_1, b_2 in combinations(cards, 2):
                if (
                    not doubles
                    and (a_1 in [b_1, b_2] or a_2 in [b_1, b_2])
                    or (a_1 in [b_1, b_2] and a_2 in [b_1, b_2])
                ):
                    continue
                for c_1, c_2 in combinations(cards, 2):
                    if (
                        not doubles
                        and (c_1 in [a_1, b_1, a_2, b_2] or c_2 in [a_1, b_1, a_2, b_2])
                        or (a_1 in [c_1, c_2] and a_2 in [c_1, c_2])
                        or (b_1 in [c_1, c_2] and b_2 in [c_1, c_2])
                    ):
                        continue

                    s.add(
                        Not(
                            And(
                                [
                                    is_set_prop(
                                        last_card(g, k, datatypes, a_1, a_2),
                                        last_card(g, k, datatypes, b_1, b_2),
                                        last_card(g, k, datatypes, c_1, c_2),
                                    )
                                    for k, g in getters.items()
                                ]
                            )
                        )
                    )
        log("made third order constraints")

    return cards, getters, constraints


def draw_board(cs, m, gs, ex):
    names = [
        f"img/{m.eval(gs['colour'](card))}{m.eval(gs['shape'](card))}{m.eval(gs['fill'](card))}{m.eval(gs['count'](card))}.png"
        for card in cs
    ]
    images = [Image.open(n) for n in names]
    c_w, c_h = images[0].size

    i_w = int(sqrt(len(cs)))
    i_h = len(cs) / i_w
    i_h = int(i_h + 1) if int(i_h) != i_h else int(i_h)

    field = Image.new("RGB", (i_w * c_w, i_h * c_h))

    for i, im in enumerate(images):
        field.paste(im, (i % i_w * c_w, int(i / i_w) * c_h))

    field.save(f"board_{ex}.png")
    field.show()


def main(card_count, first, second, third, doubles):
    solver = Solver()
    log("---- Making model ----")
    cards, getters, cons = make_model(
        solver, set_constants(), card_count, first, second, third, doubles
    )
    log("---- Starting checking ----")
    result = solver.check(cons)
    filename = f"{card_count}_{'1' if first else ''}{'2' if second else ''}{'3' if third else ''}_{'d' if doubles else 'nd'}"
    if result == sat:
        log("---- Finished checking ----")
        log("sat :)")
        draw_board(
            cards,
            solver.model(),
            getters,
            filename,
        )
    else:
        log("unsat :(")
        print(solver.unsat_core())
    
    with open(f"res_{filename}.txt", "w") as f:
        f.write(str(result) + "\n")
        f.write(str(time() - t) + "\n")
        f.write(str(solver.statistics()) + "\n")

    return result


if __name__ == "__main__":
    parser = ArgumentParser(description="Create a set board where certain sets can't be found.")
    parser.add_argument("card_count", metavar="n", type=int, help="amount of cards on board")
    parser.add_argument("-1", "--first", action="store_true", help="remove first order sets")
    parser.add_argument("-2", "--second", action="store_true", help="remove second order sets")
    parser.add_argument("-3", "--third", action="store_true", help="remove third order sets")
    parser.add_argument("-d", "--allow-doubles", action="store_true", help="allow doubles in third order sets")
    parser.add_argument("-i", "--increasing", action="store_true", help="check for increasing card count till unsat from n")

    args = parser.parse_args()

    if args.increasing:
        n = args.card_count
        log(f"==== Checking for n = {n} ====")
        while main(n, args.first, args.second, args.third, args.allow_doubles) == sat:
            n += 1
            log(f"==== Checking for n = {n} ====")
    else:
        main(args.card_count, args.first, args.second, args.third, args.allow_doubles)
