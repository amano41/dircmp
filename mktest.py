#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, timedelta


def mkfile(dirname, filename, body=None):
    path = os.path.join(dirname, filename)
    with open(path, 'w') as f:
        f.write(body or filename)
    return path


def copy_timestamp(src, dest):
    stat = os.stat(src)
    os.utime(dest, (stat.st_atime, stat.st_mtime))


def set_timestamp(filename, date_string):
    time = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    timestamp = time.timestamp()
    os.utime(filename, (timestamp, timestamp))


def shift_timestamp(filename, days=0, hours=0, minutes=0, seconds=0):
    stat = os.stat(filename)
    time = datetime.fromtimestamp(stat.st_mtime)
    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    timestamp = (time + delta).timestamp()
    os.utime(filename, (timestamp, timestamp))


if __name__ == '__main__':

    if len(sys.argv) > 1:
        root = sys.argv[1]
    else:
        root = os.path.dirname(__file__)

    root = os.path.join(root, "test")
    dir1 = os.path.join(root, "dir1")
    dir2 = os.path.join(root, "dir2")
    sub1 = os.path.join(dir1, "sub")
    sub2 = os.path.join(dir2, "sub")

    os.mkdir(root)
    os.mkdir(dir1)
    os.mkdir(dir2)
    os.mkdir(sub1)
    os.mkdir(sub2)

    # まったく同一のファイル
    filename = "identical.txt"
    file1 = mkfile(dir1, filename)
    file2 = mkfile(dir2, filename)
    copy_timestamp(file1, file2)

    # 内容・サイズ・タイムスタンプが異なるファイル
    filename = "differing.txt"
    file1 = mkfile(dir1, filename, "this is a file")
    file2 = mkfile(dir2, filename, "here is an another file")
    shift_timestamp(file2, days=-1)

    # サイズ・タイムスタンプは同じだが内容が異なる
    filename = "diff_body.txt"
    file1 = mkfile(sub1, filename, "size and time are the same")
    file2 = mkfile(sub2, filename, "but contents are different")
    copy_timestamp(file1, file2)

    # タイムスタンプは同じだが内容・サイズが異なる
    filename = "diff_body_size.txt"
    file1 = mkfile(sub1, filename, "same timestamp")
    file2 = mkfile(sub2, filename, "different size and contents")
    copy_timestamp(file1, file2)

    # サイズは同じだが内容・タイムスタンプが異なる
    filename = "diff_body_time.txt"
    file1 = mkfile(sub1, filename, "this is file1")
    file2 = mkfile(sub2, filename, "this is file2")
    shift_timestamp(file2, days=-1)

    # 内容・サイズは同じだがタイムスタンプが異なる
    filename = "diff_time.txt"
    file1 = mkfile(sub1, filename)
    file2 = mkfile(sub2, filename)
    shift_timestamp(file2, days=-1)

    # 左だけにあるファイル
    mkfile(dir1, "left_only.txt")

    # 右だけにあるファイル
    mkfile(dir2, "right_only.txt")
