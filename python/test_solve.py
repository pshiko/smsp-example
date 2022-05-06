import numpy as np
import pandas as pd
import pytest

from python.solve import solve_lp_problem, solve_sat_problem, solve_dp_problem


def get_testdata(n_jobs, seed=123) -> pd.DataFrame:
    np.random.seed(seed)
    p_time_min, p_time_max = 1, 15
    p_times = np.random.randint(p_time_min, p_time_max, n_jobs)
    due_dates = (np.clip(p_times + np.random.randint(-3, 2, n_jobs), p_time_min, None)).cumsum()
    np.random.shuffle(due_dates)
    df = pd.DataFrame({
        'job_id': [f'v_{v}' for v in np.arange(n_jobs)],
        'p_time': p_times,
        'due': due_dates,
    })
    df = df.sort_values(by='due').reset_index(drop=True)
    return df


@pytest.mark.parametrize(('n_jobs', 'expect'), [
    (6, 6),
    (8, 24),
    (10, 92),
])
def test_solve_lp_problem(n_jobs, expect):
    df = get_testdata(n_jobs, seed=123)
    result = solve_lp_problem(df)
    assert result['objective_value'] == expect


@pytest.mark.parametrize(('n_jobs', 'expect'), [
    (6, 6),
    (8, 24),
    (10, 92),
])
def test_solve_sat_problem(n_jobs, expect):
    df = get_testdata(n_jobs, seed=123)
    result = solve_sat_problem(df)
    assert result['objective_value'] == expect


@pytest.mark.parametrize(('n_jobs', 'expect'), [
    (6, 6),
    (8, 24),
    (10, 92),
])
def test_solve_dp_problem(n_jobs, expect):
    df = get_testdata(n_jobs, seed=123)
    result = solve_dp_problem(df)
    assert result['objective_value'] == expect
