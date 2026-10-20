# MTA 7108, Course Work 2: binomial pricing of an American option ("Option Desk")

**Okello Efprem** · Student No. 2600724999 · Registration No. 2026/HD13/24999U
Department of Mathematics, Makerere University

The exercise was to implement the binomial pricing of an American put on a computer and to
improve the accuracy by increasing the number of steps. This application builds the tree, works
back from expiry comparing exercise with waiting at every node, refines the tree, and checks
itself against the worked example from the course notes.

## The mathematics it implements

Over a step of length `dt = T/n` the stock is multiplied by `u` or by `d`, and the risk neutral
probability is the one that makes the stock earn the risk free rate:

```
u = exp(sigma*sqrt(dt)),   d = 1/u,   beta = exp(-r*dt)
p = (1 + r*dt - d) / (u - d)
```

The stock after `k` steps with `i` of them upward is `S(0) u^i d^(k-i)`, and at expiry the
option is worth its payoff. Working back from expiry:

```
European:  V_k(i) = beta*p*V_{k+1}(i+1) + beta*(1-p)*V_{k+1}(i)
American:  V_k(i) = max{ payoff at S_k(i),
                         beta*p*V_{k+1}(i+1) + beta*(1-p)*V_{k+1}(i) }
```

That maximum is the whole difference between the two styles, and the amount by which the
American price exceeds the European one on the same tree is the early exercise premium. The
European price has a closed form (Black and Scholes), so comparing the tree with it is the
quickest check that the code is right; the American put has none, which is why it has to go on
a computer.

![Pricing the American put from the course notes](docs/cw2_price.png)

![The lattice and the node table](docs/cw2_tree.png)

## Checked against the course notes

Worked example 14.7: an American put with `S(0) = 9`, `K = 10`, `T = 0.25` years,
`sigma = 0.3`, `r = 0.06` and `n = 5` steps.

| Quantity | Computed | In the notes |
|---|---|---|
| Up factor u | 1.0694 | 1.0694 |
| Down factor d | 0.9351 | 0.9351 |
| Discount factor beta | 0.9970 | 0.9970 |
| Risk neutral probability p | 0.5056 | 0.5056 |
| Weight beta·p | 0.5041 | 0.5041 |
| Weight beta·(1−p) | 0.4929 | 0.4929 |
| Price with n = 5 | 1.1375 | 1.1375 |
| Price as n grows | 1.1257 | 1.126 |

At the root, `V_0(0) = max{10 − 9, 0.5041×0.6994 + 0.4929×1.5925} = max{1.0000, 1.1375}`, so
the put is not exercised today. Deeper in the tree the decision goes the other way:
`V_4(0) = max{3.1181, 3.0882} = 3.1181`, and there it is exercised.

The European put on the same inputs comes to 1.088078 on a large tree against 1.088062 from the
Black and Scholes formula, so the lattice and the closed form agree.

![Refining the tree](docs/cw2_convergence.png)

Run the check yourself, with no dashboard:

```bat
python verify.py
```

## Running it

```bat
python -m pip install -r requirements.txt
python launch.py
```

`python launch.py --mode web` opens it in a browser instead. On Windows, `install.bat` does the
installation and puts a shortcut on the Desktop, and `run_dashboard.bat` starts it by
double-click. Full instructions, with the derivations, the figures and the checks, are in
[`docs/Option_Desk_User_Guide.pdf`](docs/Option_Desk_User_Guide.pdf) (LaTeX source in
[`docs/report`](docs/report), compiled with `pdflatex main.tex` run twice).

## What the application shows

| Tab | What it holds |
|---|---|
| Price | The price, the value of exercising today, the early exercise premium, Black and Scholes, the tree parameters, delta, gamma and theta, and the value against the stock price |
| The tree | The lattice with the exercise nodes marked, and every node in the table used in the notes |
| Convergence | The price at each number of steps, and the value it settles on |
| Early exercise | The boundary: the stock price at or below which the put should be exercised at each step |
| Lecture example | The worked example recomputed and compared with the notes, node by node |
| Valuations | Every valuation note saved on this computer |

## What is in the folder

```
app.py              the dashboard and its six tabs
launch.py           starts the window or the web version
verify.py           checks the pricer against the course notes
optionlib/
    binomial.py     the tree, the early exercise test, convergence
    blackscholes.py the European formula, used as a check
    pdf_report.py   the valuation note PDF
    records.py      valuation numbers, the log, saved PDFs
    presets.py      the worked example from the notes
    ui.py           layout, cards and charts
docs/               the guide, its LaTeX source and the figures
requirements.txt    the packages needed
```

Written in Python 3.11. Valuations saved on a computer go to a `data` folder that this
repository ignores.
