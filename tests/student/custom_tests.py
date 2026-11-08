
import sys
import random
import time
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Python" / "source"))

import algorithms as alg


def check(name, condition):
    assert condition, f"FAILED: {name}"
    print(f"PASS: {name}")


# LCS
r = alg.lcs({"a": "axbyc", "b": "abc"})
check("LCS subsequence",
      r["length"] == 3 and r["sequence"] == "abc")

check("LCS empty",
      alg.lcs({"a": "", "b": "abc"}) ==
      {"length": 0, "sequence": ""})


# Merge DP
r = alg.merge({"sizes": [2, 3, 4]})
check("Merge optimum",
      r["cost"] == 14 and len(r["plan"]) == 2)

check("Merge empty",
      alg.merge({"sizes": []}) ==
      {"cost": 0, "plan": []})

check("Merge large integers",
      alg.merge({"sizes": [10**9] * 3})["cost"]
      == 5 * 10**9)


# Tree DP
r = alg.tree({
    "n": 3,
    "weights": [4, 9, 6],
    "edges": [[0, 1], [1, 2]]
})
check("Tree optimum",
      r["weight"] == 10 and set(r["selected"]) == {0, 2})

r = alg.tree({
    "n": 3,
    "weights": [-5, -2, -1],
    "edges": [[0, 1], [1, 2]]
})
check("Tree all negative",
      r["weight"] == 0 and r["selected"] == [])


# Search algorithms: independent oracle
rng = random.Random(20261108)
for _ in range(200):
    text = "".join(rng.choices("ab c!", k=rng.randrange(51)))
    pattern = "".join(rng.choices("ab c!", k=rng.randrange(11)))
    expected = [
        i for i in range(len(text) - len(pattern) + 1)
        if text.startswith(pattern, i)
    ]
    for task in ("naive", "kmp", "rk"):
        actual = getattr(alg, task)({
            "text": text, "pattern": pattern
        })["positions"]
        assert actual == expected, (task, text, pattern)

print("PASS: 600 randomized search checks")

check("RK hash collision",
      alg.rk({"text": "abdj", "pattern": "ab"})["positions"]
      == [0])


# Suffix array
r = alg.suffix({"text": "banana"})
check("Suffix array",
      r["sa"] == [5, 3, 1, 0, 4, 2])
check("Kasai LCP",
      r["lcp"] == [0, 1, 3, 0, 0, 2])
check("Longest repeat", r["repeated"] == "ana")


# Aho-Corasick
r = alg.aho({
    "patterns": ["a", "aa", "a"],
    "texts": ["aaa", "", "aaa"]
})
check("Aho overlaps and duplicates",
      r["counts"] ==
      [[3, 2, 3], [0, 0, 0], [3, 2, 3]])


# Reproducible benchmarks
lines = ["case,n,m,algorithm,run1_ms,run2_ms,run3_ms,median_ms"]

for kind in ("random", "repetitive"):
    for n, m in ((300, 8), (1000, 24), (2500, 48)):
        rng = random.Random(20261108 + n)

        if kind == "random":
            text = "".join(rng.choices("abcd", k=n))
            pattern = text[n // 3:n // 3 + m]
        else:
            text = "a" * n
            pattern = "a" * (m - 1) + "b"

        expected = [
            i for i in range(n - m + 1)
            if text.startswith(pattern, i)
        ]

        for task in ("naive", "kmp", "rk"):
            fn = getattr(alg, task)
            request = {"text": text, "pattern": pattern}
            assert fn(request)["positions"] == expected

            times = []
            for _ in range(3):
                start = time.perf_counter()
                actual = fn(request)["positions"]
                elapsed = (time.perf_counter() - start) * 1000
                assert actual == expected
                times.append(elapsed)

            median = statistics.median(times)
            values = ",".join(f"{t:.6f}" for t in times)

            lines.append(
                f"{kind},{n},{m},{task},{values},{median:.6f}"
            )

output = Path(__file__).with_name("benchmark_results.csv")
output.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("PASS: all benchmark outputs checked")
print("Benchmark results saved to:", output)
print("ALL CUSTOM TESTS PASSED")
