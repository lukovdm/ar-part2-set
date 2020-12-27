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
        attr = Datatype(key)
        for opt in val:
            attr.declare(opt)
        attr = attr.create()
        datatypes[key] = attr

    card = Datatype("card")
    card.declare("c", *datatypes.items())
    card = card.create()
    getters = {list(types.keys())[i]: card.accessor(0, i) for i in range(len(types))}
    attrs = [datatypes[key].constructor(0)() for key in datatypes.keys()]

    cards = [Const(f"x__{i}", card) for i in range(card_count)]

    # s.add(
    #     cards[0]
    #     == card.c(
    #         datatypes["colour"].constructor(2)(),
    #         datatypes["shape"].constructor(0)(),
    #         datatypes["fill"].constructor(0)(),
    #         datatypes["count"].constructor(1)(),
    #     )
    # )
    # s.add(
    #     cards[1]
    #     == card.c(
    #         datatypes["colour"].constructor(2)(),
    #         datatypes["shape"].constructor(0)(),
    #         datatypes["fill"].constructor(1)(),
    #         datatypes["count"].constructor(1)(),
    #     )
    # )
    # s.add(
    #     cards[2]
    #     == card.c(
    #         datatypes["colour"].constructor(2)(),
    #         datatypes["shape"].constructor(2)(),
    #         datatypes["fill"].constructor(1)(),
    #         datatypes["count"].constructor(2)(),
    #     )
    # )
    # s.add(
    #     cards[3]
    #     == card.c(
    #         datatypes["colour"].constructor(2)(),
    #         datatypes["shape"].constructor(2)(),
    #         datatypes["fill"].constructor(1)(),
    #         datatypes["count"].constructor(1)(),
    #     )
    # )
    # s.add(
    #     cards[4]
    #     == card.c(
    #         datatypes["colour"].constructor(1)(),
    #         datatypes["shape"].constructor(1)(),
    #         datatypes["fill"].constructor(2)(),
    #         datatypes["count"].constructor(1)(),
    #     )
    # )
    # s.add(
    #     cards[5]
    #     == card.c(
    #         datatypes["colour"].constructor(0)(),
    #         datatypes["shape"].constructor(2)(),
    #         datatypes["fill"].constructor(2)(),
    #         datatypes["count"].constructor(2)(),
    #     )
    # )

    s.add(Distinct(cards))

    constraints = []

    if first_order:
        for c_1, c_2, c_3 in combinations(cards, 3):
            # con = Bool(f"1_{c_1}_{c_2}_{c_3}")
            s.add(
                # Implies(
                #     con,
                Not(
                    And(
                        [
                            Or(And(g(c_1) == g(c_2), g(c_2) == g(c_3)), Distinct(g(c_1), g(c_2), g(c_3)))
                            for _, g in getters.items()
                        ]
                    )
                ),
                # )
            )
            # constraints.append(con)
        log("made first order constraints")

    if second_order:
        c_2_o = Const("c_2_o", card)
        for a_1, a_2 in combinations(cards, 2):
            for b_1, b_2 in combinations(cards, 2):
                if a_1 in [b_1, b_2] or a_2 in [b_1, b_2]:
                    continue

                # con = Bool(f"2_{a_1}_{a_2}_{b_1}_{b_2}")
                s.add(
                    # Implies(
                    #     con,
                    Not(
                        Exists(
                            [c_2_o],
                            And(
                                [
                                    Or(
                                        And(g(a_1) == g(a_2), g(a_2) == g(c_2_o)),
                                        Distinct(g(a_1), g(a_2), g(c_2_o)),
                                    )
                                    for _, g in getters.items()
                                ]
                                + [
                                    Or(
                                        And(g(b_1) == g(b_2), g(b_2) == g(c_2_o)),
                                        Distinct(g(b_1), g(b_2), g(c_2_o)),
                                    )
                                    for _, g in getters.items()
                                ]
                            ),
                        )
                    ),
                    # )
                )
                # constraints.append(con)
        log("made second order constraints")

        # Old harder to understand second order code
        # for a_1, a_2 in combinations(cards, 2):
        #     for b_1, b_2 in combinations(cards, 2):
        #         if a_1 == b_1 or a_1 == b_2 or a_2 == b_1 or a_2 == b_2:
        #             continue
        #         s.add(Not(And([
        #             If(g(a_1) == g(a_2),
        #                 Or(And(g(b_1) == g(b_2), g(b_1) == g(a_1)),
        #                     And(Distinct(g(b_1), g(b_2)), g(b_1) != g(a_1), g(b_2) != g(a_1))),
        #                 Or(And(g(b_1) == g(b_2), Distinct(g(b_1), g(a_1), g(a_2))),
        #                     And(g(b_1) != g(b_2), Or([
        #                         And(g(a_1) != c, g(a_2) != c, g(b_1) != c, g(b_2) != c)
        #                         for c in [datatypes[k].constructor(i)() for i in range(datatypes[k].num_constructors())]
        #                     ]))))
        #             for k, g in getters.items()
        #         ])))

    if third_order:
        d_3_o = [Const(f"c_3_o__{i}", card) for i in range(3)]
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

                    # con = Bool(f"3_{a_1}_{a_2}_{b_1}_{b_2}_{c_1}_{c_2}")
                    s.add(
                        # Implies(
                        #     con,
                        Not(
                            Exists(
                                d_3_o,
                                And(
                                    [
                                        Or(
                                            And(g(a_1) == g(a_2), g(a_2) == g(d_3_o[0])),
                                            Distinct(g(a_1), g(a_2), g(d_3_o[0])),
                                        )
                                        for _, g in getters.items()
                                    ]
                                    + [
                                        Or(
                                            And(g(b_1) == g(b_2), g(b_2) == g(d_3_o[1])),
                                            Distinct(g(b_1), g(b_2), g(d_3_o[1])),
                                        )
                                        for _, g in getters.items()
                                    ]
                                    + [
                                        Or(
                                            And(g(c_1) == g(c_2), g(c_2) == g(d_3_o[2])),
                                            Distinct(g(c_1), g(c_2), g(d_3_o[2])),
                                        )
                                        for _, g in getters.items()
                                    ]
                                    + [
                                        Or(
                                            And(g(d_3_o[0]) == g(d_3_o[1]), g(d_3_o[1]) == g(d_3_o[2])),
                                            Distinct(g(d_3_o[0]), g(d_3_o[1]), g(d_3_o[2])),
                                        )
                                        for _, g in getters.items()
                                    ]
                                    + [Distinct(d_3_o)]
                                ),
                            )
                        ),
                        # )
                    )
                    # constraints.append(con)
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

    field.save(f"board_{len(cs)}{ex}.png")
    field.show()


if __name__ == "__main__":
    parser = ArgumentParser(description="Create a set board where certain sets can't be found.")
    parser.add_argument("card_count", metavar="n", type=int, help="amount of cards on board")
    parser.add_argument("-1", "--first", action="store_true", help="remove first order sets")
    parser.add_argument("-2", "--second", action="store_true", help="remove second order sets")
    parser.add_argument("-3", "--third", action="store_true", help="remove third order sets")
    parser.add_argument("-d", "--allow-doubles", action="store_true", help="allow doubles in third order sets")

    args = parser.parse_args()

    solver = Solver()
    log("==== Making model ====")
    cards, getters, cons = make_model(
        solver, set_constants(), args.card_count, args.first, args.second, args.third, args.allow_doubles
    )
    log("==== Starting checking ====")
    if solver.check(cons) == sat:
        log("==== Finished checking ====")
        log("sat :)")
        draw_board(
            cards,
            solver.model(),
            getters,
            f"_{'1' if args.first else ''}{'2' if args.second else ''}{'3' if args.third else ''}_{'d' if args.allow_doubles else 'nd'}",
        )
    else:
        log("unsat :(")
        print(solver.unsat_core())
