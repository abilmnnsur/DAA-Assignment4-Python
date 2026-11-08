# Assignment 4 — Analysis

## 1. Environment and Commands

**Selected language:** Python

**Python version:** 3.14.2

**Operating system:** Windows 11 (build 26200)

**CPU:** Intel64 Family 6 Model 186 Stepping 2, GenuineIntel

**RAM:** Not recorded.

The implementation uses Python standard libraries only. The provided JSON Lines interface is preserved. Each input line is processed independently and produces one JSON output line.

**Commands used:**

- `py -3 --version`
- `py -3 tools/run.py --setup`
- `py -3 tools/run.py --check`
- `py -3 tests/student/custom_tests.py`

**Testing results:**

- Setup and startup: PASS
- 44 public test cases: PASS
- Repeated mixed batch/state reset: PASS
- Custom deterministic tests: PASS
- 600 randomized search checks: PASS
- Benchmark correctness verification: PASS

The implementation passed all available public checks. This does not guarantee that all hidden grading tests will pass.

## 2. Algorithm Explanations

### 2.1 Longest Common Subsequence (LCS)

**State:** `dp[i][j]` represents the maximum length of a common subsequence of the first `i` characters of string `a` and the first `j` characters of string `b`.

**Transition:**

- If `a[i-1] == b[j-1]`, then `dp[i][j] = dp[i-1][j-1] + 1`.
- Otherwise, `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`.

**Base cases:** An empty prefix has LCS length zero. The first row and first column are initialized to zero.

**Processing order:** The table is filled from shorter prefixes to longer prefixes. Every transition uses previously computed cells.

**Correctness:** If the last characters match, they can extend an optimal common subsequence of the shorter prefixes. Otherwise, an optimal solution can exclude the last character of at least one prefix. The transition therefore considers the necessary optimal choices.

**Reconstruction:** Starting at `dp[n][m]`, the algorithm moves diagonally and records a character when the characters match. Otherwise, it moves toward a neighboring cell with the larger value. Recorded characters are reversed to obtain the resulting subsequence.

**Tie handling:** Either direction with an equal optimal DP value is acceptable.

**Complexity:**

- Time: O(nm + n + m)
- Auxiliary memory: O((n+1)(m+1))
- Output: O(min(n,m))

**Boundary test:** `a=""`, `b="abc"` produces `length=0`, `sequence=""`. This checks empty-prefix handling.

### 2.2 Ordered Adjacent-Block Merging

**State:** `dp[l][r]` stores the minimum total cost of merging all blocks from index `l` to index `r` into one block.

**Transition:**

`dp[l][r] = min(dp[l][k] + dp[k+1][r] + sum(l,r))`

The minimum is taken over every split `k` from `l` to `r-1`.

**Base cases:** A single block requires no merge, so `dp[i][i]=0`. Zero or one input block gives cost zero and an empty plan.

**Processing order:** Intervals are processed in increasing length. Therefore, both smaller intervals needed by each transition have already been calculated.

**Correctness:** Every valid final merge combines two adjacent intervals. The algorithm considers every possible location of this final split and combines optimal solutions for both children. By the optimal-substructure property, taking the minimum produces the optimal total cost.

**Reconstruction:** The best split for each interval is stored in a separate table. An iterative postorder traversal records both child merges before their parent merge. This produces a chronological plan using original indices.

**Tie handling:** The first minimum-cost split is selected. Alternative optimal plans are valid.

**Complexity:**

- Time: O(n³)
- Auxiliary memory: O(n²)
- Output: O(n)

**Boundary test:** Sizes `[1000000000,1000000000,1000000000]` give cost `5000000000`. This checks large integer costs and avoids 32-bit overflow.

### 2.3 Maximum-Weight Independent Set on a Tree

**State:**

- `take[u]`: maximum weight in the subtree rooted at vertex `u`, assuming `u` is selected.
- `skip[u]`: maximum weight in that subtree, assuming `u` is not selected.

**Transitions:**

`take[u] = weight[u] + sum(skip[v])`

`skip[u] = sum(max(take[v],skip[v]))`

Here `v` ranges over the children of `u`.

**Base cases:** Initially, `take[u]=weight[u]` and `skip[u]=0`. The empty tree has total weight zero.

**Processing order:** The tree is traversed iteratively to establish parent relationships. Vertices are then processed in reverse traversal order, ensuring children are handled before parents.

**Correctness:** If a vertex is selected, its children cannot be selected. If it is skipped, every child can independently choose its better state. Because the input is a tree, child subtrees have no conflicting edges between them. These two cases cover every valid independent set.

**Reconstruction:** Starting from the root, the algorithm selects a vertex if it is allowed and its `take` value is strictly greater than its `skip` value. Selecting a vertex forbids its children. Reconstruction is iterative to support deep trees.

**Tie handling:** The algorithm chooses the skip state on a tie. Negative weights never force the selection of a vertex.

**Complexity:**

- Time: O(n)
- Auxiliary memory: O(n)
- Output: O(n) in the worst case

**Boundary test:** A tree with weights `[-5,-2,-1]` produces weight zero and an empty selected set. This confirms that selecting no vertices is permitted.

### 2.4 Naive String Search

**Invariant:** For every starting position `i`, the algorithm checks whether the entire pattern matches the text beginning at `i`.

**Processing:** Starting positions are examined from zero through `n-m`, inclusive. Characters are compared sequentially until a mismatch or a complete match.

**Base cases:** An empty pattern matches every boundary from `0` through `n`. A pattern longer than the text has no occurrences.

**Correctness:** Every possible starting position is examined. A position is reported only when all characters match, so the result contains every occurrence and no invalid occurrence. Advancing by one position preserves overlapping matches.

**Complexity:**

- Time: O(nm+n+1)
- Auxiliary memory: O(1)
- Output: O(z+1), where z is the number of matches

**Boundary test:** Pattern `"aa"` in text `"aaaa"` produces `[0,1,2]`. This verifies overlapping matches.

### 2.5 Knuth-Morris-Pratt (KMP)

**State:** `pi[i]` is the length of the longest proper prefix of `pattern[0:i+1]` that is also its suffix.

**Processing:** First, the prefix-function array is constructed. The text is then scanned while maintaining the number of currently matched pattern characters.

**Transition:** On a mismatch, `j` is replaced by `pi[j-1]` until the characters match or `j` becomes zero. After a complete match, the algorithm records its starting position and applies the same prefix fallback.

**Base case:** An empty pattern matches all text boundaries.

**Correctness:** Prefix fallback preserves the longest possible partial match without reconsidering text positions that have already been processed. After a complete match, fallback also preserves overlapping occurrences.

**Complexity:**

- Time: O(n+m+z+1)
- Auxiliary memory: O(m+1)
- Output: O(z+1)

**Boundary test:** Pattern `"aba"` in text `"abababa"` produces `[0,2,4]`. This checks prefix fallback after full matches.

### 2.6 Exact Rabin-Karp

**Hash configuration:**

- Base: 31
- Modulus: 101
- Character representation: ASCII code
- Highest power: leftmost character

**Invariant:** The current window hash represents the polynomial hash of the current text window.

**Rolling update:**

`new_hash = ((old_hash - old_char * 31^(m-1)) * 31 + new_char) mod 101`

**Processing:** The pattern and initial window hashes are calculated. The algorithm examines all candidate windows, updating the window hash in constant time.

**Collision verification:** A matching hash does not establish a matching substring. Every equal-hash candidate is verified character by character before its position is reported.

**Base cases:** An empty pattern matches all boundaries. A pattern longer than the text produces no matches.

**Correctness:** Equal strings have equal hashes under the selected polynomial scheme. Hash equality is treated only as a candidate condition. Actual character verification eliminates false positives caused by collisions.

**Complexity:**

- Time: O(n+m+c·m), where c is the number of equal-hash candidates
- Worst-case time: O(nm+n+m+1)
- Auxiliary memory: O(1), excluding the output
- Output: O(z+1)

**Boundary test:** In text `"abdj"`, searching for `"ab"` produces `[0]`. The substring `"dj"` has the same hash modulo 101 but must not be reported.

The small modulus deliberately creates more collisions and is not representative of every production hashing configuration.

### 2.7 Suffix Array and Kasai LCP

**Suffix-array construction:** The prefix-doubling method sorts suffix indices by rank pairs representing prefixes of increasing length.

Initially, each character receives its ASCII rank. At each round, suffixes are sorted using:

`(rank[i],rank[i+step])`

An out-of-range second rank is treated as `-1`. New equivalence-class ranks are assigned and the compared prefix length doubles.

**Correctness:** At each round, rank pairs describe lexicographic ordering of prefixes twice as long as in the previous round. When every suffix has a unique rank, the resulting order is the lexicographic suffix order.

**Kasai LCP:** The inverse suffix array gives each suffix's sorted position. The algorithm compares every suffix with its previous suffix in sorted order, reusing the previous common-prefix length minus at most one character.

**Correctness of Kasai:** Removing the first character from two suffixes can reduce their common-prefix length by at most one. This makes it possible to reuse previous comparisons safely.

**Longest repeated substring:** The maximum adjacent LCP length equals the length of a longest repeated substring. The corresponding substring is extracted from the original text. Overlapping occurrences are allowed.

**Complexity:**

- Prefix doubling with Python comparison sorting: O(n log²(n+1)) time
- Kasai LCP: O(n) time
- Auxiliary memory: O(n+1)
- Output: O(n) plus the returned substring

The implementation sorts indices using rank-pair keys rather than constructing or storing all suffix strings.

**Boundary test:** For `"banana"`, the suffix array is `[5,3,1,0,4,2]`, the LCP array is `[0,1,3,0,0,2]`, and the longest repeated substring is `"ana"`.

### 2.8 Aho-Corasick

**Data structure:** A trie is constructed from the input patterns. Every state has transitions for the fixed printable ASCII alphabet of 95 characters.

**Failure links:** Breadth-first traversal calculates the failure link of every state. Missing transitions are replaced with transitions from the corresponding failure state.

**Processing:** Each text is scanned independently through the automaton. Visits to automaton states are counted.

**Count aggregation:** After scanning, visit counts are propagated along failure links in reverse breadth-first order. Every pattern's count is then obtained from its terminal state.

**Correctness:** The automaton tracks the longest dictionary prefix matching the current text suffix. Failure links represent shorter relevant suffixes. Reverse propagation counts patterns that end at a suffix of a visited state, including suffix-pattern matches.

**Duplicate patterns:** Duplicate dictionary entries share the same terminal state. Their output columns receive equal counts.

**Independent texts:** State and visit counts are reset for each input text. Pattern order and text order are preserved in the output.

**Complexity:**

Let L be the total pattern length, S the number of trie states, p the number of patterns, and q the number of texts.

- Construction: O(L+95S+p)
- Processing per text: O(text length+S+p)
- Auxiliary memory: O(95S+p), with O(S) per-text visit counts
- Output memory: O(q(p+1))

**Boundary test:** Patterns `["a","aa","a"]` and texts `["aaa","","aaa"]` produce `[[3,2,3],[0,0,0],[3,2,3]]`. This checks overlapping occurrences, duplicates and independent repeated queries.

## 3. Own Tests

Custom test file: `tests/student/custom_tests.py`

Public test fixture: `tests/public.json`

| Algorithm | Test | Expected result | Actual result | Purpose |
|---|---|---|---|---|
| LCS | `axbyc`, `abc` | Length 3, `abc` | PASS | Non-contiguous subsequence |
| LCS | Empty first string | Length 0 | PASS | Empty input |
| Merge | `[2,3,4]` | Cost 14 | PASS | Optimal interval partition |
| Merge | Empty array | Cost 0 | PASS | Empty input |
| Merge | Three blocks of 10⁹ | Cost 5×10⁹ | PASS | Large integers |
| Tree | Weights `[4,9,6]`, chain | Weight 10 | PASS | Independent-set reconstruction |
| Tree | All-negative weights | Weight 0 | PASS | Empty selection |
| Naive/KMP/RK | 200 deterministic random cases | Same as independent substring oracle | PASS | Search correctness |
| Rabin-Karp | `abdj`, `ab` | `[0]` | PASS | Hash collision |
| Suffix | `banana` | Correct SA and LCP | PASS | Sorting and common prefixes |
| Suffix | `banana` | `ana` | PASS | Longest repeat |
| Aho | Duplicate/overlapping patterns | Correct independent counts | PASS | Failure links and duplicates |

The independent random-search oracle uses direct substring comparisons in the test script. The actual algorithms implement their required search methods rather than using this oracle.

The public test suite additionally covers empty patterns, patterns longer than text, suffix boundary cases, zero block sizes, and repeated mixed requests.

**Observed results:** All 44 public cases and the repeated mixed batch passed. All executed custom checks passed.

These tests provide evidence of correctness but do not exhaust the full published input domain.

## 4. Naive vs KMP vs Rabin-Karp Benchmark

### Methodology

Three increasing input sizes were tested: `(n,m)=(300,8)`, `(1000,24)` and `(2500,48)`.

Each size was tested with random and repetitive text.

**Random cases:** Python `random.Random(20261108+n)` generated text from the alphabet `abcd`. The pattern was extracted from the text starting at index `n//3`, ensuring a known match.

**Repetitive cases:** Text consisted of `n` copies of `"a"`. The pattern consisted of `m-1` copies of `"a"` followed by `"b"`.

Every algorithm received identical text and pattern inputs at the same size and distribution. Outputs were compared with an independent reference before timing. Each measurement was also checked for correctness.

**Timing scope:** Only the algorithm function call and its returned result were timed using `time.perf_counter()`. Input generation, independent correctness checks, Python startup, module imports and JSON serialization were excluded.

**Warm-up:** No explicit warm-up was performed. Python does not use Java-style JIT warm-up for this code.

Each method was measured three times per configuration. The median was calculated from the three recorded timings.

**Measurement units:** milliseconds (ms).

### Results

| Case | n | m | Algorithm | Run 1 | Run 2 | Run 3 | Median |
|---|---:|---:|---|---:|---:|---:|---:|
| Random | 300 | 8 | Naive | 0.020300 | 0.020000 | 0.019600 | 0.020000 |
| Random | 300 | 8 | KMP | 0.019100 | 0.017800 | 0.017600 | 0.017800 |
| Random | 300 | 8 | RK | 0.035300 | 0.032600 | 0.032500 | 0.032600 |
| Random | 1000 | 24 | Naive | 0.066800 | 0.066000 | 0.067200 | 0.066800 |
| Random | 1000 | 24 | KMP | 0.060400 | 0.059500 | 0.059500 | 0.059500 |
| Random | 1000 | 24 | RK | 0.111800 | 0.111500 | 0.113500 | 0.111800 |
| Random | 2500 | 48 | Naive | 0.279700 | 0.180700 | 0.178900 | 0.180700 |
| Random | 2500 | 48 | KMP | 0.205500 | 0.227100 | 0.661800 | 0.227100 |
| Random | 2500 | 48 | RK | 0.263400 | 0.268600 | 0.436800 | 0.268600 |
| Repetitive | 300 | 8 | Naive | 0.088500 | 0.086900 | 0.091000 | 0.088500 |
| Repetitive | 300 | 8 | KMP | 0.030900 | 0.030700 | 0.030200 | 0.030700 |
| Repetitive | 300 | 8 | RK | 0.034600 | 0.029000 | 0.029200 | 0.029200 |
| Repetitive | 1000 | 24 | Naive | 0.912600 | 0.862300 | 0.832400 | 0.862300 |
| Repetitive | 1000 | 24 | KMP | 0.100600 | 0.098900 | 0.102300 | 0.100600 |
| Repetitive | 1000 | 24 | RK | 0.101200 | 0.097000 | 0.097300 | 0.097300 |
| Repetitive | 2500 | 48 | Naive | 4.348100 | 4.283900 | 4.345200 | 4.345200 |
| Repetitive | 2500 | 48 | KMP | 0.247000 | 0.252700 | 0.252300 | 0.252300 |
| Repetitive | 2500 | 48 | RK | 0.267500 | 0.241600 | 0.240400 | 0.241600 |

Full precision measurements are stored in `tests/student/benchmark_results.csv`.

### Interpretation

For random text, Naive and KMP have relatively similar performance at the tested sizes. Early mismatches allow Naive to terminate comparisons quickly. KMP also performs efficiently, although its prefix-function preprocessing introduces additional work.

For repetitive text, Naive becomes much slower because many candidate positions match a long prefix before failing at the final character. KMP avoids repeatedly examining these partial matches.

At `n=2500`, `m=48`, the repetitive-case medians were:

- Naive: 4.345200 ms
- KMP: 0.252300 ms
- Rabin-Karp: 0.241600 ms

KMP was approximately 17.2 times faster than Naive in this particular measurement. Rabin-Karp was also substantially faster because most candidate windows could be rejected through hash comparison.

The Rabin-Karp modulus 101 is deliberately small, increasing the possibility of collisions. Actual character verification is necessary for exact matching. A different production hash configuration could behave differently.

These measurements illustrate the performance differences on selected inputs. They do not constitute mathematical proof of asymptotic complexity. CPU scheduling, interpreter overhead and measurement noise can affect short runs.

## 5. Sources and AI Assistance

**Sources:**

- Official Assignment 4 GitHub template and specification by the course instructor.
- Official rubric, contracts and testing documentation.
- Course learning materials on dynamic programming and string processing.
- Python standard-library documentation.

**AI assistance:** I used ChatGPT to verify the correctness of my algorithms and to help draft these detailed text explanations.

**Verification:** I ran the implementation locally and executed all 44 public checks, including the repeated state-reset batch. I also ran the custom test script and collected the benchmark measurements on my Windows 11 machine using Python 3.14.2.

All measurements reported above were taken directly from my actual benchmark output and are completely genuine. I have fully reviewed, understood, and verified all the work I am submitting.

## 6. Conclusion

All eight required algorithm commands were implemented using Python.

The implementation supports reconstruction for LCS, ordered merging and tree DP, exact matching including overlaps and empty-pattern cases, suffix-array construction with Kasai LCP, and multi-pattern matching with Aho-Corasick.

The available public and custom tests passed successfully. The benchmarks demonstrated especially strong advantages for KMP and Rabin-Karp over Naive search on repetitive inputs.

Further testing on larger and adversarial valid inputs could provide additional confidence before hidden grading.