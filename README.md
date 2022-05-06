# smsp-example

## about

- [リクルート事例で分かる数理最適化入門 第二回](https://atmarkit.itmedia.co.jp/ait/series/28443/)のexmaple用リポジトリ
- 1機械スケジューリング問題をLP([Cbc](https://github.com/coin-or/Cbc))
  /SAT([CP-SAT](https://developers.google.com/optimization/cp/cp_solver))/DPソルバーで解く実装
    - LP/SATは[OR-Tools](https://developers.google.com/optimization)を利用
    - DPは自前実装(rustで書いて[pyo3](https://github.com/PyO3/pyo3)でpython module化)

## How to use

### docker run

```shell
make docker-test
make docker-run
```

### コマンド

ソルバー実行

```
poetry run python main.py solve -s lp -f sample/sample_job.csv
```

計算時間計測

```
time -p timeout 10s poetry run python main.py test -s lp -n 10 -i 1 --fix-seed 1>null
```

## Note

- 今回の実装ではDP>SAT(CP-SAT)>LP(Cbc)の順に早い
    - LP(Cbc)だと10ジョブの問題を解くのに5秒位かかるが、DPだと10000ジョブ位でも1秒以内で解ける
    - SAT(CP-SAT)は30ジョブ位までが限界

#### 10ジョブ

```bash
# time -p timeout 10s poetry run python main.py test -s lp -n 10 -i 1 --fix-seed 1>null
real 5.48
user 5.61
sys 1.28

$ time -p timeout 10s poetry run python main.py test -s sat -n 10 -i 1 --fix-seed 1>null
real 0.51
user 1.24
sys 1.82

$ time -p timeout 10s poetry run python main.py test -s dp -n 10 -i 1 --fix-seed 1>null
real 0.44
user 0.72
sys 1.12
```

#### 30ジョブ

```bash
$ time -p timeout 10s poetry run python main.py test -s lp -n 30 -i 1 --fix-seed 1>null
Command exited with non-zero status 124
real 10.00
user 10.09
sys 1.32

$ time -p timeout 10s poetry run python main.py test -s sat -n 30 -i 1 --fix-seed 1>null
real 1.04
user 7.86
sys 5.32

$ time -p timeout 10s poetry run python main.py test -s dp -n 30 -i 1 --fix-seed 1>null
real 0.46
user 0.69
sys 1.17
```

#### 10000ジョブ

```bash
$ time -p timeout 10s poetry run python main.py test -s lp -n 10000 -i 1 --fix-seed 1>null
Command exited with non-zero status 124
real 10.06
user 9.49
sys 1.97

$ time -p timeout 10s poetry run python main.py test -s sat -n 10000 -i 1 --fix-seed 1>null
Command exited with non-zero status 124
real 10.07
user 147.79
sys 5.36

$ time -p timeout 10s poetry run python main.py test -s dp -n 10000 -i 1 --fix-seed 1>null
real 0.47
user 0.67
sys 1.21
```
