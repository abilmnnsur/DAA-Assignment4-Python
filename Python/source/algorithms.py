
"""Assignment 4: Dynamic Programming and String Processing."""

from collections import deque


# 1. LONGEST COMMON SUBSEQUENCE
def lcs(request):
    a, b = request["a"], request["b"]
    n, m = len(a), len(b)

    if n == 0 or m == 0:
        return {"length": 0, "sequence": ""}

    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    result = []
    i, j = n, m

    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            result.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    result.reverse()

    return {
        "length": dp[n][m],
        "sequence": "".join(result)
    }


# 2. ORDERED ADJACENT-BLOCK MERGING
def merge(request):
    sizes = request["sizes"]
    n = len(sizes)

    if n <= 1:
        return {"cost": 0, "plan": []}

    prefix = [0] * (n + 1)

    for i in range(n):
        prefix[i + 1] = prefix[i] + sizes[i]

    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1

            total = prefix[r + 1] - prefix[l]
            best = float("inf")
            best_k = l

            for k in range(l, r):
                current = (
                    dp[l][k]
                    + dp[k + 1][r]
                    + total
                )

                if current < best:
                    best = current
                    best_k = k

            dp[l][r] = best
            split[l][r] = best_k

    plan = []
    stack = [(0, n - 1, False)]

    while stack:
        l, r, done = stack.pop()

        if l == r:
            continue

        k = split[l][r]

        if done:
            plan.append([l, k, r])
        else:
            stack.append((l, r, True))
            stack.append((k + 1, r, False))
            stack.append((l, k, False))

    return {
        "cost": dp[0][n - 1],
        "plan": plan
    }


# 3. MAXIMUM WEIGHT INDEPENDENT SET ON A TREE
def tree(request):
    n = request["n"]

    if n == 0:
        return {"weight": 0, "selected": []}

    weights = request["weights"]
    edges = request["edges"]

    adj = [[] for _ in range(n)]

    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    parent = [-1] * n
    parent[0] = 0

    order = [0]

    for u in order:
        for v in adj[u]:
            if v != parent[u]:
                parent[v] = u
                order.append(v)

    take = weights[:]
    skip = [0] * n

    for u in reversed(order):
        if u == 0:
            continue

        p = parent[u]

        take[p] += skip[u]
        skip[p] += max(take[u], skip[u])

    selected = []
    stack = [(0, False)]

    while stack:
        u, forbidden = stack.pop()

        choose = not forbidden and take[u] > skip[u]

        if choose:
            selected.append(u)

        for v in adj[u]:
            if v != parent[u]:
                stack.append((v, choose))

    return {
        "weight": max(0, take[0], skip[0]),
        "selected": selected
    }


# 4. NAIVE STRING SEARCH
def naive(request):
    text = request["text"]
    pattern = request["pattern"]

    n = len(text)
    m = len(pattern)

    if m == 0:
        return {"positions": list(range(n + 1))}

    positions = []

    for i in range(n - m + 1):
        j = 0

        while j < m and text[i + j] == pattern[j]:
            j += 1

        if j == m:
            positions.append(i)

    return {"positions": positions}


# 5. KNUTH-MORRIS-PRATT
def kmp(request):
    text = request["text"]
    pattern = request["pattern"]

    n = len(text)
    m = len(pattern)

    if m == 0:
        return {"positions": list(range(n + 1))}

    pi = [0] * m
    j = 0

    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = pi[j - 1]

        if pattern[i] == pattern[j]:
            j += 1

        pi[i] = j

    positions = []
    j = 0

    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = pi[j - 1]

        if text[i] == pattern[j]:
            j += 1

        if j == m:
            positions.append(i - m + 1)
            j = pi[j - 1]

    return {"positions": positions}


# 6. RABIN-KARP WITH EXACT VERIFICATION
def rk(request):
    text = request["text"]
    pattern = request["pattern"]

    n = len(text)
    m = len(pattern)

    if m == 0:
        return {"positions": list(range(n + 1))}

    if m > n:
        return {"positions": []}

    base = 31
    mod = 101

    high = pow(base, m - 1, mod)

    pattern_hash = 0
    window_hash = 0

    for i in range(m):
        pattern_hash = (
            pattern_hash * base + ord(pattern[i])
        ) % mod

        window_hash = (
            window_hash * base + ord(text[i])
        ) % mod

    positions = []

    for i in range(n - m + 1):
        if window_hash == pattern_hash:
            j = 0

            while j < m and text[i + j] == pattern[j]:
                j += 1

            if j == m:
                positions.append(i)

        if i + m < n:
            window_hash = (
                (window_hash - ord(text[i]) * high) * base
                + ord(text[i + m])
            ) % mod

    return {"positions": positions}


# 7. SUFFIX ARRAY + KASAI LCP
def suffix(request):
    text = request["text"]
    n = len(text)

    if n == 0:
        return {
            "sa": [],
            "lcp": [],
            "repeated": ""
        }

    sa = list(range(n))
    rank = [ord(c) for c in text]

    step = 1

    while True:
        sa.sort(
            key=lambda i: (
                rank[i],
                rank[i + step] if i + step < n else -1
            )
        )

        new_rank = [0] * n
        kinds = 0

        previous = sa[0]

        for i in sa[1:]:
            first = (
                rank[previous],
                rank[previous + step]
                if previous + step < n else -1
            )

            second = (
                rank[i],
                rank[i + step] if i + step < n else -1
            )

            if first != second:
                kinds += 1

            new_rank[i] = kinds
            previous = i

        rank = new_rank

        if kinds == n - 1:
            break

        step *= 2

    inverse = [0] * n

    for i, start in enumerate(sa):
        inverse[start] = i

    lcp = [0] * n
    length = 0

    for i in range(n):
        position = inverse[i]

        if position == 0:
            length = 0
            continue

        j = sa[position - 1]

        while (
            i + length < n
            and j + length < n
            and text[i + length] == text[j + length]
        ):
            length += 1

        lcp[position] = length

        if length > 0:
            length -= 1

    best_index = max(range(n), key=lcp.__getitem__)
    best_length = lcp[best_index]
    best_start = sa[best_index]

    repeated = text[best_start:best_start + best_length]

    return {
        "sa": sa,
        "lcp": lcp,
        "repeated": repeated
    }


# 8. AHO-CORASICK
def aho(request):
    patterns = request["patterns"]
    texts = request["texts"]

    if not texts:
        return {"counts": []}

    if not patterns:
        return {"counts": [[] for _ in texts]}

    alphabet = 95

    go = [[-1] * alphabet]
    fail = [0]
    terminals = []

    # Build trie
    for pattern in patterns:
        node = 0

        for char in pattern:
            c = ord(char) - 32
            nxt = go[node][c]

            if nxt == -1:
                nxt = len(go)
                go[node][c] = nxt

                go.append([-1] * alphabet)
                fail.append(0)

            node = nxt

        terminals.append(node)

    # Build failure links
    queue = deque()

    for c in range(alphabet):
        v = go[0][c]

        if v == -1:
            go[0][c] = 0
        else:
            queue.append(v)

    order = []

    while queue:
        u = queue.popleft()
        order.append(u)

        current = go[u]
        fallback = go[fail[u]]

        for c in range(alphabet):
            v = current[c]

            if v == -1:
                current[c] = fallback[c]
            else:
                fail[v] = fallback[c]
                queue.append(v)

    # Count occurrences independently in each text
    results = []
    reversed_order = order[::-1]
    total_states = len(go)

    for text in texts:
        visits = [0] * total_states
        state = 0

        for char in text:
            c = ord(char) - 32
            state = go[state][c]
            visits[state] += 1

        for u in reversed_order:
            visits[fail[u]] += visits[u]

        row = [visits[node] for node in terminals]
        results.append(row)

    return {"counts": results}
