"""
Checks the pricer against the worked example in the course notes, without the dashboard.

    python verify.py

It recomputes the American put with S(0) = 9, K = 10, T = 0.25, sigma = 0.3, r = 0.06
and n = 5, prints the tree parameters, every node and the price, compares them with the
figures in the notes, and then refines the tree to show the price settling on the exact
value of 1.126. It also checks the European price on the same tree against the Black and
Scholes formula, which is the standard way of showing that the lattice is coded correctly.
"""

from optionlib import binomial as bn
from optionlib import blackscholes as bs
from optionlib import presets

S0, K, T, SIGMA, R, N = 9.0, 10.0, 0.25, 0.30, 0.06, 5
LINE = "-" * 72


def main():
    print(LINE)
    print("MTA 7108, Course Work 2: binomial pricing of an American put")
    print(f"S(0) = {S0:g}, K = {K:g}, T = {T:g} years, sigma = {SIGMA:g}, "
          f"r = {R:g}, n = {N}")
    print(LINE)

    par = bn.parameters(T, SIGMA, R, N, "simple")
    print(f"dt = {par['dt']:.6f}   u = {par['u']:.4f}   d = {par['d']:.4f}   "
          f"beta = {par['beta']:.4f}")
    print(f"p  = {par['p']:.4f}       beta p = {par['beta_p']:.4f}   "
          f"beta (1 - p) = {par['beta_q']:.4f}")
    print()

    value, _, nodes = bn.price(S0, K, T, SIGMA, R, N, "Put", "American", "simple")
    print(f"{'k':>2} {'i':>2} {'S(0)u^i d^(k-i)':>16} {'Exercise':>10} {'Wait':>10} "
          f"{'Value':>10}  Decision")
    for nd in nodes:
        wait = "-" if nd["Wait"] is None else f"{nd['Wait']:10.4f}"
        print(f"{nd['k']:>2} {nd['i']:>2} {nd['Stock price']:16.4f} "
              f"{nd['Exercise']:10.4f} {wait:>10} {nd['Value']:10.4f}  {nd['Decision']}")
    print()
    print(f"Price of the American put with n = {N}: {value:.4f}")
    print()

    print("Against the figures in the notes")
    print(LINE)
    rows = presets.check_lecture_example(bn.parameters, bn.price, bn.limit_price)
    for r in rows:
        mark = "ok" if r["Agrees"] else "DIFFERS"
        print(f"  {r['Quantity']:<28} computed {r['Computed']:>8}   "
              f"notes {r['In the notes']:>8}   {mark}")
    ok = all(r["Agrees"] for r in rows)
    print()

    print("Refining the tree")
    print(LINE)
    for n in [5, 10, 25, 50, 100, 250, 500, 1000]:
        v = bn.price(S0, K, T, SIGMA, R, n, "Put", "American", "simple")[0]
        print(f"  n = {n:>5}   price = {v:.4f}")
    limit = bn.limit_price(S0, K, T, SIGMA, R, "Put", "American", "simple", n=2000)
    print(f"  settling on {limit:.4f}, against 1.126 in the notes")
    print()

    print("The European price on the same tree, against Black and Scholes")
    print(LINE)
    euro = bn.limit_price(S0, K, T, SIGMA, R, "Put", "European", "simple", n=2000)
    formula = bs.european(S0, K, T, SIGMA, R, "Put")
    print(f"  tree  {euro:.6f}")
    print(f"  formula {formula:.6f}")
    print(f"  difference {abs(euro - formula):.6f}")
    print(f"  early exercise premium {limit - euro:.4f}")
    print()
    print("All checks passed." if ok and abs(euro - formula) < 1e-3
          else "Some checks did not pass.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
