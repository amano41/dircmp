#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import os
import sys
import argparse
from collections import defaultdict


def find_left_only(dir1, dir2):
    left = _make_hash_table(dir1)
    right = _make_hash_table(dir2)
    yield from _find_left_only(left, right)


def find_right_only(dir1, dir2):
    left = _make_hash_table(dir1)
    right = _make_hash_table(dir2)
    yield from _find_right_only(left, right)


def find_uniq(dir1, dir2):
    left = _make_hash_table(dir1)
    right = _make_hash_table(dir2)
    yield from _find_uniq(left, right)


def find_dups(dir1, dir2):
    left = _make_hash_table(dir1)
    right = _make_hash_table(dir2)
    yield from _find_dups(left, right)


def find_dups_within(dirname):
    table = _make_hash_table(dirname)
    for hash, files in table.items():
        if len(files) > 1:
            yield (hash, files)


def _find_left_only(left, right):
    for hash, files in left.items():
        if hash not in right:
            yield (hash, files)


def _find_right_only(left, right):
    yield from _find_left_only(right, left)


def _find_uniq(left, right):
    yield from _find_left_only(left, right)
    yield from _find_left_only(right, left)


def _find_dups(left, right):
    for hash in left.keys():
        if hash in right:
            yield (hash, left[hash], right[hash])


def _make_hash_table(root_path):
    table = defaultdict(list)
    for path in _find_files(root_path):
        hash = _calc_hash(path)
        table[hash].append(path)
    return table


def _find_files(root_path):
    for dirpath, dirnames, filenames in os.walk(root_path):
        for name in filenames:
            yield os.path.join(dirpath, name)


def _calc_hash(path):
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(2048 * hasher.block_size), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def _parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("dir1", type=str, help="left directory")
    parser.add_argument("dir2", type=str, nargs="?", default=None, help="right directory (optional)")
    parser.add_argument("-l", "--left", action="store_true", help="find left only")
    parser.add_argument("-r", "--right", action="store_true", help="find right only")
    parser.add_argument("-u", "--uniq", action="store_true", help="find unique")
    parser.add_argument("-d", "--dups", action="store_true", help="find duplicates")
    parser.add_argument("-a", "--all", action="store_true", help="find left only, right only, and duplicates")
    parser.add_argument("-s", "--separator", type=str, default="\t", help="specify field separator (default=\"\\t\")")

    return parser.parse_args()


def _print_files(label, hash, files, sep="\t"):
    for path in files:
        dirname, filename = os.path.split(path)
        print(sep.join([label, filename, dirname, hash]))


def main():

    args = _parse_args()

    dir1 = args.dir1
    dir2 = args.dir2

    sep = args.separator

    if not os.path.isdir(dir1):
        print("error: not a directory: {}".format(dir1), file=sys.stderr)
        exit()

    if dir2 is not None and not os.path.isdir(dir2):
        print("error: not a directory: {}".format(dir2), file=sys.stderr)
        exit()

    # dir2 を省略，または dir1 と dir2 に同じディレクトリを指定した場合
    # ディレクトリ dir1 内で重複しているファイルを検索
    if dir2 is None or os.path.samefile(dir1, dir2):
        for hash, files in find_dups_within(dir1):
            _print_files("duplicates", hash, files, sep)
        exit()

    left = _make_hash_table(dir1)
    right = _make_hash_table(dir2)

    # オプション引数が指定されていなかったらすべて出力する
    if not args.left and not args.right and not args.uniq and not args.dups:
        args.all = True

    # 左側ディレクトリのみに含まれているファイルを検索
    if args.left or args.all:
        for hash, files in _find_left_only(left, right):
            _print_files("left only", hash, files, sep)

    # 右側ディレクトリのみに含まれているファイルを検索
    if args.right or args.all:
        for hash, files in _find_right_only(left, right):
            _print_files("right only", hash, files, sep)

    # 片方のディレクトリのみに含まれているファイルを検索
    # left only と right only の出力を合わせたものと一致
    if args.uniq:
        for hash, files in _find_uniq(left, right):
            _print_files("unique", hash, files, sep)

    # 両方のディレクトリに含まれているファイルを検索
    if args.dups or args.all:
        for hash, left_files, right_files in _find_dups(left, right):
            _print_files("duplicates", hash, left_files, sep)
            _print_files("duplicates", hash, right_files, sep)


if __name__ == "__main__":
    main()
