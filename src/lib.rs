use numpy::PyArrayDyn;
use pyo3::prelude::*;

#[pyfunction]
fn solve(
    ids: &PyArrayDyn<usize>,
    processing_times: &PyArrayDyn<usize>,
    due_dates: &PyArrayDyn<usize>,
) -> PyResult<(Vec<usize>, usize)> {
    let i_vec = ids.to_vec()?;
    let p_vec = processing_times.to_vec()?;
    let d_vec = due_dates.to_vec()?;
    let mut jobs = i_vec
        .iter()
        .zip(p_vec.iter().zip(d_vec.iter()))
        .map(|(i, (p, d))| Job::new(*i, *p, *d))
        .collect::<Vec<Job>>();
    jobs.sort_by_key(|x| x.due);
    sort(&mut jobs, 0);
    let delay = calc_delay(&jobs);
    let sorted_ids = jobs.iter().map(|x| x.id).collect::<Vec<usize>>();
    Ok((sorted_ids, delay))
}

/// A Python module implemented in Rust.
#[pymodule]
fn smsp_example_dp(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve, m)?)?;
    Ok(())
}

#[derive(Debug, Clone, Copy)]
struct Job {
    id: usize,
    p_time: usize,
    due: usize,
}

impl Job {
    fn new(id: usize, p_time: usize, due: usize) -> Self {
        Job { id, p_time, due }
    }
}

fn calc_delay(jobs: &[Job]) -> usize {
    let mut delay = 0;
    let mut t = 0;
    for job in jobs.iter() {
        t += job.p_time;
        delay += t.saturating_sub(job.due);
    }
    delay
}

fn sort(jobs: &mut [Job], start: usize) {
    if jobs.len() <= 1 {
        return;
    }
    let (max_ix, &max_job) = jobs
        .iter()
        .enumerate()
        .max_by_key(|(_ix, x)| x.p_time)
        .unwrap();
    let mut cur_start = start + jobs[0..max_ix].iter().map(|x| x.p_time).sum::<usize>();
    let mut tgt_ix = max_ix + 1;
    while tgt_ix < jobs.len() {
        let swapped_delay = (cur_start + jobs[tgt_ix].p_time).saturating_sub(jobs[tgt_ix].due)
            + (cur_start + jobs[tgt_ix].p_time + max_job.p_time).saturating_sub(max_job.due);
        let delay = (cur_start + max_job.p_time).saturating_sub(max_job.due)
            + (cur_start + jobs[tgt_ix].p_time + max_job.p_time).saturating_sub(jobs[tgt_ix].due);
        if swapped_delay >= delay {
            break;
        }
        cur_start += jobs[tgt_ix].p_time;
        jobs[tgt_ix - 1] = jobs[tgt_ix];
        tgt_ix += 1;
    }
    jobs[tgt_ix - 1] = max_job;
    cur_start += max_job.p_time;
    if tgt_ix > 1 {
        sort(&mut jobs[..tgt_ix - 1], start);
    }
    if tgt_ix < jobs.len() {
        sort(&mut jobs[tgt_ix..], cur_start);
    }
}
