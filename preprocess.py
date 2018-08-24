#!/usr/bin/env python3

#   Copyright (C) 2011, 2012  Povilas Kanapickas <povilas@radix.lt>
#
#   This file is part of cppreference-doc
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see http://www.gnu.org/licenses/.

from commands.preprocess import *
import argparse
from concurrent.futures import ProcessPoolExecutor
import os
import shutil

worker_rename_map = None
worker_root = None

def initworker(root, rename_map):
    global worker_rename_map
    worker_rename_map = rename_map
    global worker_root
    worker_root = root

def process_file(fn):
    preprocess_html_file(worker_root, fn, worker_rename_map)

def main():
    parser = argparse.ArgumentParser(prog='preprocess.py')
    parser.add_argument('--src', type=str, help='Source directory where raw website copy resides')
    parser.add_argument('--dst', type=str, help='Destination folder to put preprocessed archive to')
    args = parser.parse_args()

    root = args.dst
    src = args.src

    # copy the source tree
    rmtree_if_exists(root)
    shutil.copytree(src, root)

    rearrange_archive(root)

    rename_map = find_files_to_be_renamed(root)
    rename_files(rename_map)

    # clean the html files
    with ProcessPoolExecutor(initializer=initworker, initargs=(root, rename_map)) as executor:
        for fn in find_html_files(root):
            executor.submit(process_file, fn)

    # append css modifications

    with open("preprocess-css.css", "r", encoding='utf-8') as pp, \
         open(os.path.join(root, 'common/site_modules.css'), "a", encoding='utf-8') as out:
        out.writelines(pp)

    # clean the css files

    for fn in [ os.path.join(root, 'common/site_modules.css'),
                os.path.join(root, 'common/ext.css') ]:
        preprocess_css_file(fn)

if __name__ == "__main__":
    main()
