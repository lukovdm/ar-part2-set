#!/bin/env python3
from z3 import *

names = ["S", "A", "B", "C"]

def assert_array(solver, array, data):
    for offset_i, i in enumerate(data):
        for offset_j, j in enumerate(i):
            solver.add(array[offset_i][offset_j] == j)


flatten = lambda t: [item for sublist in t for item in sublist]


def exercise_constants(ex_ind):
    graph = [[-1, 29, 21, -1], [29, -1, 17, 32], [21, 17, -1, 37], [-1, 32, 37, -1]]
    v_cap = [-1, 120, 120, 200]
    v_init_cap = [-1, 40, 30, 145]
    t_max_cap = [300,  320, 318]

    return graph, v_cap, v_init_cap, t_max_cap[ex_ind]


def toy_constants():
    graph = [
        [-1,  1, -1],
        [ 1, -1,  2],
        [-1,  2, -1]
    ]
    v_cap = [-1, 4, 6]
    v_init_cap = [-1, 4, 6]
    t_max_cap = 13

    return graph, v_cap, v_init_cap, t_max_cap


def make_model(solver, graph, v_cap, v_init_cap, t_max_cap, t_bound):
    vil_size = len(v_cap)

    distances = Array("distances", IntSort(), ArraySort(IntSort(), IntSort()))
    assert_array(solver, distances, graph)

    truck_c = IntVector("truck_c", t_bound+1)
    vil_c = [Array(f"vil_c__{t}", IntSort(), IntSort()) for t in range(t_bound+1)]
    loc = IntVector("loc", t_bound+1)

    loop_start = Int("loop_start")
    loop_end = Int("loop_end")

    # Initial values
    solver.add(truck_c[0] == t_max_cap)
    solver.add(loc[0] == 0)
    for vil in range(1, vil_size):
        solver.add(vil_c[0][vil] == v_init_cap[vil])

    # Invariants
    for t in range(t_bound + 1):
        solver.add(truck_c[t] <= t_max_cap)
        solver.add(truck_c[t] >= 0)
        solver.add(loc[t] < vil_size)
        solver.add(loc[t] >= 0)
        for vil in range(1, vil_size):
            solver.add(vil_c[t][vil] <= v_cap[vil])
            solver.add(vil_c[t][vil] >= 0)

    # Time steps
    for t in range(t_bound):
        # Loc
        solver.add(Or([
            And(distances[loc[t]][vil] >= 0, loc[t + 1] == vil)
            for vil in range(vil_size)
        ]))

        # truck content
        solver.add(If(
            loc[t + 1] == 0,
            truck_c[t + 1] == t_max_cap,
            truck_c[t + 1] <= truck_c[t],
        ))

        # village content
        for vil in range(1, vil_size):
            solver.add(
                vil_c[t + 1][vil] == vil_c[t][vil] - distances[loc[t]][loc[t + 1]] + 
                        If(And(loc[t + 1] == vil, vil_c[t][vil] - distances[loc[t]][loc[t + 1]] >= 0), truck_c[t] - truck_c[t + 1], 0)
            )

    # There has to be a loop
    solver.add(Or(flatten([
        [
            And(
                vil_c[t_1] == vil_c[t_2], 
                truck_c[t_1] == truck_c[t_2], 
                loc[t_1] == loc[t_2], 
                loop_start == t_2, loop_end == t_1
            ) for t_2 in range(0, t_1)
        ] for t_1 in range(0, t_bound)
    ])))

    return truck_c, vil_c, loc, vil_size, loop_start, loop_end


def check_bound(time_bound, constants):
    s = Solver()
    t_c, v_c, l, v_s, l_s, l_e = make_model(s, *constants, time_bound)
    # print(s.assertions())
    if s.check() == sat:
        print("sat :)")
        m = s.model()
        l_s = m.eval(l_s)
        l_e = m.eval(l_e)
        for t in range(time_bound+1):
            if t == l_s:
                print(f"--------- Time {t} --------- <- Loop starts here")
            elif t == l_e:
                print(f"--------- Time {t} --------- <- Loop ends here")
            else:
                print(f"--------- Time {t} ---------")
            print(f"truck location = {names[m.eval(l[t]).as_long()]}")
            print(f"truck content = {m.eval(t_c[t])}")
            for vil in range(1,v_s):
                print(f"village {names[vil]} = {m.eval(v_c[t][vil])} ")
        return True
    else:
        print("unsat :(")
        return False

if __name__ == "__main__":
    # for t_b in range(20):
    #     print(f"=============== Checking for bound {t_b} ===============")
    #     if check_bound(t_b, toy_constants()):
    #         break
    
    for t_b in range(20):
        print(f"=============== Checking for bound {t_b} ===============")
        if check_bound(t_b, exercise_constants(0)):
            break
