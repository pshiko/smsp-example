import argparse
import json
from enum import Enum

import pandas as pd
from tqdm.auto import tqdm

from python.solve import solve_sat_problem, solve_lp_problem, solve_dp_problem
from python.test_solve import get_testdata


class Solver(Enum):
    SAT: str = 'sat'
    LP: str = 'lp'
    DP: str = 'dp'


def solve(args):
    df = pd.read_csv(args.file)
    solver = Solver(args.solver)
    if solver == Solver.SAT:
        result = solve_sat_problem(df)
    elif solver == Solver.LP:
        result = solve_lp_problem(df)
    elif solver == Solver.DP:
        result = solve_dp_problem(df)
    print(json.dumps(result))


def test_load(args):
    solver = Solver(args.solver)
    results = []
    iter = tqdm(range(args.iter)) if args.v else range(args.iter)
    seed = 123 if args.fix_seed else None
    for _ in iter:
        df = get_testdata(args.num, seed=seed)
        if solver == Solver.SAT:
            result = solve_sat_problem(df)
        elif solver == Solver.LP:
            result = solve_lp_problem(df)
        elif solver == Solver.DP:
            result = solve_dp_problem(df)
        if args.v:
            results.append(result)
    if args.v:
        print(json.dumps({'results': results}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    solve_parser = subparsers.add_parser('solve', help='solve the problem described in the csv file')
    solve_parser.add_argument('-s', '--solver', required=True, choices=[e.value for e in Solver],
                              help='type of solver to use')
    solve_parser.add_argument('-f', '--file', required=True,
                              help='csv file path of the problem. ex. sample/sample_job.csv')
    solve_parser.set_defaults(func=solve)

    test_parser = subparsers.add_parser('test', help='solve randomly generated problems to measure computational load')
    test_parser.add_argument('-s', '--solver', choices=[e.value for e in Solver], help='type of solver to use')
    test_parser.add_argument('-n', '--num', type=int, required=True, help='number of job in each test')
    test_parser.add_argument('-i', '--iter', type=int, required=True, help='number of test ')
    test_parser.add_argument('-v', '-V', action='store_true', help='print results')
    test_parser.add_argument('--fix-seed', action='store_true', help='fix random seed')
    test_parser.set_defaults(func=test_load)

    args = parser.parse_args()
    args.func(args)
