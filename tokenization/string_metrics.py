import re
from nltk.util import ngrams

_NGRAM = 3


def get_jaccard_index(_a, _b, is_sentence=False, is_word=False):
    if is_sentence:
        _a, _b = _get_sentence_ngrams(_a), _get_sentence_ngrams(_b)
    elif is_word:
        _a, _b = _get_word_ngrams(_a), _get_word_ngrams(_b)
    _a, _b = set(_a), set(_b)
    intersection = len(_a & _b)
    union = len(_a | _b)
    return intersection / union if union > 0 else 1


def get_jaccard_distance(_a, _b, is_sentence=True):
    if is_sentence:
        return 1 - get_jaccard_index(_get_sentence_ngrams(_a), _get_sentence_ngrams(_b))
    else:
        return 1 - get_jaccard_index(_get_word_ngrams(_a), _get_word_ngrams(_b))


def _get_word_ngrams(_a, ngram=_NGRAM):
    if not _a:
        return None
    pattern = r'[^a-zA-Zа-яА-Я]?'
    ng = ngrams(re.sub(pattern, ' ', _a).split(), ngram)
    return list(ng)


def _get_sentence_ngrams(_a, ngram=_NGRAM):
    if not _a:
        return None
    pattern = r'[^a-zA-Zа-яА-Я]+'
    ng = ngrams(re.sub(pattern, ' ', _a).split(), ngram)
    return list(ng)


def _get_lower_case(_a, _b):
    return [i.lower() for i in _a], [i.lower() for i in _b]


def get_jaro_similarity(_a, _b):
    _a, _b = _get_lower_case(_a, _b)
    _scan_window = _get_scan_window(_a, _b)
    m, t, t_matches = 0, 0, []
    if len(_a) < len(_b):
        _c = _a
        _a = _b
        _b = _c
    for i in range(len(_a)):
        if i < len(_b) and _a[i] == _b[i]:
            m += 1
        j = i - 1
        j_count = 0
        while 0 < j and j_count < _scan_window:
            j, j_count, m = _get_matches(_a, _b, _scan_window, i, j, j_count, m, t_matches)
            j -= 1
        j = i + 1
        j_count = 0
        while j < len(_b) and j_count < _scan_window:
            j, j_count, m = _get_matches(_a, _b, _scan_window, i, j, j_count, m, t_matches)
            j += 1
    for i in range(0, len(t_matches), 2):
        if i + 1 < len(t_matches):
            t_matches[i + 1].reverse()
            if t_matches[i] == t_matches[i + 1]:
                t += 1
    return ((m / len(_a)) + (m / len(_b)) + ((m - t) / m)) * (1 / 3) if m != 0 else 0


def _get_matches(_a, _b, _scan_window, i, j, j_count, m, t_matches):
    if j >= len(_b):
        j = len(_b) - 1
    j_count += 1
    if _a[i] == _b[j] and i != j and i - j < _scan_window:
        m += 1
        t_matches.append([i, j])
    return j, j_count, m


def _get_scan_window(_a, _b):
    return round(max(len(_a), len(_b)) / 2) - 1


def _get_prefix_length(_a, _b):
    _a, _b = _get_lower_case(_a, _b)
    count = 0
    recommended_value = 4
    for i in range(len(_a)):
        if i < len(_b) and _a[i] == _b[i]:
            count += 1
    return min(count, recommended_value)


def get_jaro_winkler_similarity(_a, _b, scaling=0.1):
    if scaling < 0 or scaling > 0.25:
        scaling = 0.25
    jaro_distance = get_jaro_similarity(_a, _b)
    prefix_length = _get_prefix_length(_a, _b)
    return jaro_distance + (prefix_length * scaling * (1 - jaro_distance))


jaccard_str = 'S1 = {}\nS2 = {}\nJaccard index = {}\nJaccard distance = {}\n'
jaro_str = 'S1 = {}\nS2 = {}\nJaro similarity = {}\nJaro-Winkler similarity = {}\n'
s1, s2 = 'I do not like green eggs and ham', 'I do not like them, Sam I am'
s3, s4 = 'aaaaaaaa', 'aaabbbbbbaa'
s5, s6 = 'CRATE', 'TRACE'
s7, s8 = ['M', 'A', 'R', 'H', 'T', 'A'], ['M', 'A', 'R', 'T', 'H', 'A']
s9, s10 = 'DICKSONX', 'DIXON'
print(jaccard_str.format(s1, s2, get_jaccard_index(s1, s2, is_sentence=True),
                         get_jaccard_distance(s1, s2, is_sentence=True)))
print(jaccard_str.format(s3, s4, get_jaccard_index(s3, s4, is_word=True),
                         get_jaccard_distance(s3, s4, is_sentence=False)))
print(jaccard_str.format(s5, s6, get_jaccard_index(s5, s6, is_word=True),
                         get_jaccard_distance(s5, s6, is_sentence=False)))
print(jaro_str.format(s7, s8, get_jaro_similarity(s7, s8), get_jaro_winkler_similarity(s7, s8)))
print(jaro_str.format(s9, s10, get_jaro_similarity(s9, s10), get_jaro_winkler_similarity(s9, s10)))
print(jaro_str.format(s5, s6, get_jaro_similarity(s5, s6), get_jaro_winkler_similarity(s5, s6)))
