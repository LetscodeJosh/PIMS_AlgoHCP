"""
Matching algorithms for HCP deduplication:
- Jaro-Winkler similarity
- Levenshtein ratio
- Soundex phonetic encoding
- Token set ratio & Jaccard token similarity
"""

import math

def jaro_distance(s1: str, s2: str) -> float:
    """Calculate Jaro Distance between two strings."""
    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    max_dist = math.floor(max(len1, len2) / 2) - 1
    if max_dist < 0:
        max_dist = 0

    match1 = [False] * len1
    match2 = [False] * len2

    matches = 0
    transpositions = 0

    for i in range(len1):
        start = max(0, i - max_dist)
        end = min(i + max_dist + 1, len2)

        for j in range(start, end):
            if match2[j]:
                continue
            if s1[i] != s2[j]:
                continue
            match1[i] = True
            match2[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    k = 0
    for i in range(len1):
        if not match1[i]:
            continue
        while not match2[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    transpositions /= 2.0

    return ((matches / len1) + (matches / len2) + ((matches - transpositions) / matches)) / 3.0

def jaro_winkler_distance(s1: str, s2: str, p: float = 0.1) -> float:
    """Calculate Jaro-Winkler distance (boosts prefix matches)."""
    j_dist = jaro_distance(s1, s2)
    if j_dist < 0.7:
        return j_dist

    # Common prefix length up to 4 characters
    prefix_len = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break

    return j_dist + (prefix_len * p * (1.0 - j_dist))

def levenshtein_ratio(s1: str, s2: str) -> float:
    """Calculates normalized Levenshtein similarity ratio between 0 and 1."""
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    rows = len(s1) + 1
    cols = len(s2) + 1
    dist = [[0 for _ in range(cols)] for _ in range(rows)]

    for i in range(1, rows):
        dist[i][0] = i
    for i in range(1, cols):
        dist[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            cost = 0 if s1[row - 1] == s2[col - 1] else 1
            dist[row][col] = min(
                dist[row - 1][col] + 1,
                dist[row][col - 1] + 1,
                dist[row - 1][col - 1] + cost
            )

    max_len = max(len(s1), len(s2))
    return 1.0 - (dist[rows - 1][cols - 1] / max_len)

def soundex(name: str) -> str:
    """
    Standard Soundex phonetic encoding.
    Converts a word to a 4-character code based on pronunciation.
    """
    if not name:
        return ""
    
    name = name.upper()
    soundex_code = name[0]

    mappings = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }

    prev_digit = mappings.get(name[0], '0')

    for char in name[1:]:
        digit = mappings.get(char, '0')
        if digit != '0' and digit != prev_digit:
            soundex_code += digit
            if len(soundex_code) == 4:
                break
        prev_digit = digit

    soundex_code = soundex_code.ljust(4, '0')
    return soundex_code

def token_set_ratio(s1: str, s2: str) -> float:
    """
    Token Set Similarity.
    Splits strings into token sets, handles token reordering (e.g. 'Cruz Maria' vs 'Maria Cruz').
    """
    if not s1 or not s2:
        return 0.0

    tokens1 = set(s1.split())
    tokens2 = set(s2.split())

    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)

    if not union:
        return 0.0

    # Jaccard index
    jaccard = len(intersection) / len(union)

    # Combined with string distance of sorted tokens
    sorted1 = " ".join(sorted(tokens1))
    sorted2 = " ".join(sorted(tokens2))
    jw_sorted = jaro_winkler_distance(sorted1, sorted2)

    return (jaccard * 0.4) + (jw_sorted * 0.6)
