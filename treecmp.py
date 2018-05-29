#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import filecmp
import os
import sys
import argparse
from collections import defaultdict


class TreeCmp:

    def __init__(self, dir1, dir2, shallow=True):

        if not os.path.isdir(dir1):
            raise NotADirectoryError(dir1)

        if not os.path.isdir(dir2):
            raise NotADirectoryError(dir2)

        self.left = dir1
        self.right = dir2
        self.shallow = shallow
        self.same_files = defaultdict(list)
        self.diff_files = defaultdict(list)
        self.funny_files = defaultdict(list)
        self.left_only = defaultdict(list)
        self.right_only = defaultdict(list)

        self.__cmp(self.left, self.right, shallow)

    def __cmp(self, dir1, dir2, shallow):
        dircmp = filecmp.dircmp(dir1, dir2)
        self.__recursive_cmp(dircmp, shallow)

    def __recursive_cmp(self, dircmp, shallow):

        dirs = (dircmp.left, dircmp.right)

        # 両方に存在するファイル
        match, mismatch, errors = filecmp.cmpfiles(dircmp.left, dircmp.right, dircmp.common_files, shallow)
        self.same_files[dirs].extend(match)
        self.diff_files[dirs].extend(mismatch)
        self.funny_files[dirs].extend(errors)

        # 左側のみに存在するファイル・ディレクトリ
        # ディレクトリの場合は再帰的にたどってファイルを追加
        for name in dircmp.left_only:
            path = os.path.join(dircmp.left, name)
            if os.path.isdir(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    self.left_only[(dirpath, "")].extend(filenames)
            else:
                self.left_only[dirs].append(name)

        # 右側のみに存在するファイル・ディレクトリ
        # ディレクトリの場合は再帰的にたどってファイルを追加
        for name in dircmp.right_only:
            path = os.path.join(dircmp.right, name)
            if os.path.isdir(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    self.right_only[("", dirpath)].extend(filenames)
            else:
                self.right_only[dirs].append(name)

        # 両方に存在するディレクトリ
        for subdir in dircmp.subdirs.values():
            self.__recursive_cmp(subdir, shallow)


def _parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("dir1", type=str, help="left directory")
    parser.add_argument("dir2", type=str, help="right directory")
    parser.add_argument("-f", "--full", action="store_false", dest="shallow", help="compare contents of files")
    parser.add_argument("-s", "--separator", type=str, default="\t", help="specify field separator (default=\"\\t\")")

    return parser.parse_args()


def _print_files(label, dict, sep="\t"):
    for dirs, files in dict.items():
        for filename in files:
            print(sep.join([label, filename, dirs[0], dirs[1]]))


def main():

    args = _parse_args()

    dir1 = args.dir1
    dir2 = args.dir2
    shallow = args.shallow
    sep = args.separator

    if not os.path.isdir(dir1):
        print("error: not a directory: {}".format(dir1), file=sys.stderr)
        exit()

    if not os.path.isdir(dir2):
        print("error: not a directory: {}".format(dir2), file=sys.stderr)
        exit()

    treecmp = TreeCmp(dir1, dir2, shallow)

    _print_files("same", treecmp.same_files, sep)
    _print_files("diff", treecmp.diff_files, sep)
    _print_files("funny", treecmp.funny_files, sep)
    _print_files("left only", treecmp.left_only, sep)
    _print_files("right only", treecmp.right_only, sep)


if __name__ == "__main__":
    main()
