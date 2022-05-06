from dataclasses import dataclass
from itertools import product
from typing import Optional, Dict

import numpy as np
import pandas as pd
import smsp_example_dp
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model


def solve_lp_problem(df: pd.DataFrame, solver: str = 'CBC', M: Optional[int] = None) -> Dict:
    n_jobs = len(df)
    if M is None:
        M = df['p_time'].sum()

    # Solver
    solver: pywraplp.Solver = pywraplp.Solver.CreateSolver(solver)

    # Variables
    order_values = {
        (i, j): solver.IntVar(0, 1, f'x_{i}_{j}') for i, j in product(range(n_jobs), range(n_jobs))
    }
    start_time = {
        i: solver.IntVar(0, solver.infinity(), name=f's_{i}') for i in range(n_jobs)
    }
    delay_time = {
        i: solver.IntVar(0, solver.infinity(), name=f'd_{i}') for i in range(n_jobs)
    }

    # Constraints
    for i, j in product(range(n_jobs), range(n_jobs)):
        if i == j:
            continue
        solver.Add(start_time[i] + df.loc[i, 'p_time'] <= start_time[j] + M * (1 - order_values[(i, j)]))

    for i in range(n_jobs):
        for j in range(i + 1, n_jobs):
            solver.Add((order_values[(i, j)] + order_values[(j, i)]) == 1)

    for i in range(n_jobs):
        solver.Add((start_time[i] + df.loc[i, 'p_time'] - df.loc[i, 'due']) <= delay_time[i])

    solver.Minimize(sum(delay_time.values()))
    status = solver.Solve()
    assert status == pywraplp.Solver.OPTIMAL

    objective_value = solver.Objective().Value()
    jobs = {}
    for k in start_time.keys():
        j = df.loc[k, 'job_id']
        s = start_time[k].solution_value()
        d = delay_time[k].solution_value()
        jobs[j] = {'start_time': s, 'delay': d}
    return {
        'objective_value': objective_value,
        'jobs': jobs,
    }


def solve_sat_problem(df: pd.DataFrame) -> Dict:
    @dataclass
    class Task:
        start: cp_model.IntVar
        end: cp_model.IntVar
        delay: cp_model.IntVar
        interval: cp_model.IntervalVar

    n_jobs = len(df)
    horizon = 1001001001

    # Solver
    solver = cp_model.CpSolver()
    model = cp_model.CpModel()

    # Variables
    task_info: Dict[int, Task] = {}
    for i in range(n_jobs):
        p_time = df.loc[i, 'p_time']
        start_var = model.NewIntVar(0, horizon, name=f'start_{i}')
        end_var = model.NewIntVar(0, horizon, name=f'end_{i}')
        delay = model.NewIntVar(0, horizon, name=f'delay_{i}')
        interval_var = model.NewIntervalVar(start_var, p_time, end_var, f'interval_{i}')
        task_info[i] = Task(start_var, end_var, delay, interval_var)

    # Constraints
    model.AddNoOverlap([task.interval for task in task_info.values()])
    for i in range(n_jobs):
        model.Add(task_info[i].end - df.loc[i, 'due'] <= task_info[i].delay)
    model.Minimize(sum([task.delay for task in task_info.values()]))
    status = solver.Solve(model)

    assert status == cp_model.OPTIMAL
    objective_value = solver.ObjectiveValue()
    jobs = {}
    for k, t in task_info.items():
        j = df.loc[k, 'job_id']
        s = solver.Value(t.start)
        d = solver.Value(t.delay)
        jobs[j] = {'start_time': s, 'delay': d}
    return {
        'objective_value': objective_value,
        'jobs': jobs,
    }


def solve_dp_problem(df: pd.DataFrame) -> Dict:
    sorted_ix, objective_value = smsp_example_dp.solve(
        ids=df.index.values.astype(np.uint64),
        processing_times=df['p_time'].values.astype(np.uint64),
        due_dates=df['due'].values.astype(np.uint64),
    )
    df = df.iloc[sorted_ix, :].copy()
    df['end_time'] = df['p_time'].cumsum().values
    df['start_time'] = df['end_time'].shift(1, fill_value=0).values
    df['delay'] = (df['end_time'] - df['due']).clip(0).values
    jobs = df[['job_id', 'start_time', 'delay']].set_index('job_id').to_dict(orient='index')
    return {
        'objective_value': objective_value,
        'jobs': jobs,
    }
