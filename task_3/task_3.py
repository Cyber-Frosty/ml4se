import tokenize
from io import BytesIO

from collections import Counter

from typing import List, Dict, Tuple

import keyword


def get_substrings_from_code(code: str) -> List[str]:
    tokenize_substrings = tokenize.tokenize(BytesIO(code.encode('utf-8')).readline)
    _ = next(tokenize_substrings)
    return [item.string for item in tokenize_substrings if item.string]


def format_substrings(substrings: List[str]) -> List[Tuple[int, ...]]:
    byte_substrings = [item.encode('utf-8') for item in substrings]
    int_substrings = []
    for substring in byte_substrings:
        int_substrings.append(tuple([item for item in substring]))
    return int_substrings


def get_base_vocabulary(word_frequencies: Dict[Tuple[int, ...], int]) -> Dict[int, str]:
    vocabulary = {}
    for key, value in word_frequencies.items():
        for letter in key:
            vocabulary[letter] = chr(letter)
    return vocabulary


def get_stats(word_frequencies: Dict[Tuple[int, ...], int]) -> Dict[Tuple[int, int], int]:
    counts = {}
    for key, value in word_frequencies.items():
        for pair in zip(key, key[1:]):
            counts[pair] = counts.get(pair, 0) + value
    return counts


def merge(token: Tuple[int, ...], pair: Tuple[int, int], new_int: int):
    new_token = []
    index = 0
    while index < len(token):
        if index < len(token) - 1 and token[index] == pair[0] and token[index + 1] == pair[1]:
            new_token.append(new_int)
            index += 2
        else:
            new_token.append(token[index])
            index += 1
    return tuple(new_token)


def get_merged_frequencies(word_frequencies: Dict[Tuple[int, ...], int],
                           merged_pair: Tuple[int, int], pair_id: int) -> Dict[Tuple[int, ...], int]:
    new_frequencies = {}
    for key, value in word_frequencies.items():
        new_key = merge(key, merged_pair, pair_id)
        new_frequencies[new_key] = value
    return new_frequencies


def bpe(word_frequencies, vocabulary, merge_count):
    merged_pairs = {}
    for iteration in range(merge_count):
        stats = get_stats(word_frequencies)
        if not stats:
            break
        most_freq_pair = max(stats, key=stats.get)
        if stats[most_freq_pair] == 1:
            break

        new_int = 256 + iteration
        merged_pairs[most_freq_pair] = new_int
        vocabulary[new_int] = f'{vocabulary[most_freq_pair[0]]}{vocabulary[most_freq_pair[1]]}'

        word_frequencies = get_merged_frequencies(word_frequencies, most_freq_pair, new_int)
    return merged_pairs, vocabulary


def get_tokenized_code(int_substrings: List[Tuple[int, ...]], vocabulary: Dict[int, str],
                       merged_pairs: Dict[Tuple[int, int], int]) -> List[str]:
    tokenized_code = []
    for substring in int_substrings:
        new_substring = substring
        for pair, pair_code in merged_pairs.items():
            new_substring = merge(new_substring, pair, pair_code)
        tokenized_code += list(new_substring)

    tokenized_code = list(map(lambda x: vocabulary[x], tokenized_code))
    return tokenized_code


def tokenize_code(code: str, merge_count: int = 20, check_keywords: bool = False)\
        -> List[str]:
    str_substrings = get_substrings_from_code(code)

    if check_keywords:
        keywords = set(keyword.kwlist)
        keywords.add('    ')
        keywords_in_code = keywords & set(str_substrings)

    int_substrings = format_substrings(str_substrings)
    word_frequencies = dict(Counter(int_substrings))
    vocabulary = get_base_vocabulary(word_frequencies)
    merged_pairs, vocabulary = bpe(word_frequencies, vocabulary, merge_count)

    if check_keywords:
        # noinspection PyUnboundLocalVariable
        found_keywords = set(vocabulary.values()) & keywords_in_code
        print(f'Found {len(found_keywords)} keywords out of {len(keywords_in_code)}')
        print(found_keywords)

    tokenized_code = get_tokenized_code(int_substrings, vocabulary, merged_pairs)
    return tokenized_code


if __name__ == '__main__':
    with open('task_3.in') as f:
        s = f.read()
    result = tokenize_code(s,)
    print(result)
