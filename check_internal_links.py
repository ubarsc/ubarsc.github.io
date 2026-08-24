#!/usr/bin/env python3

"""
Script for checking internal links for each blog posts.

Builds a set of valid page links then searches each
blog post for links and checks these are valid.

If successful, return 0 else 1. Intended to be run on
each new PR.
"""

import os
import sys

POSTS_DIR = '_posts'
END_LINK = '.html)'


def get_link_path(fname):
    """
    For a given path for a blog post, turn this into a link
    that Jekyll would generate it by looking at the date
    and categories entries in the file.
    """
    date = None
    categories = None
    for line in open(fname):
        if line.startswith('date:'):
            arr = line.split()
            date = arr[1].replace('-', '/')
        elif line.startswith('categories:'):
            arr = line.split()
            categories = '/'.join([x.lower() for x in arr[1:]])

        if date is not None and categories is not None:
            break

    if date is None or categories is None:
        raise SystemExit(f'missing date or categories for fname {fname}')

    # get the basename and convert to .html
    htmlfname = os.path.basename(fname).replace('.markdown', '.html')
    # take off the leading date in the fname
    htmlfname = htmlfname[11:]

    path = categories + '/' + date + '/' + htmlfname
    return path


def check_all_links(fname, thislink, paths):
    """
    Check all the internal links in the file pointed at 
    by fname. thislink is the Jekyll link for this file.
    paths is a set of valid Jekyll links.

    Returns count of invalid links.
    """

    # list of tuples (original, what that is in destination)
    broken_links = []
    for line in open(fname):
        htmlindex = line.find(END_LINK)
        if htmlindex != -1:
            bracket = line.rfind('(', 0, htmlindex)
            if bracket == -1:
                # assume start of line and bracket on previous line
                bracket = 0

            # important: strip to remove any leading or trailing whitespace
            linkpath = line[bracket + 1:htmlindex + len(END_LINK) - 1].strip()
            if linkpath.startswith('http'):
                # we don't check 'outside' links
                continue
            #print(f'link is {linkpath}')
            thislinkdir, _ = os.path.split(thislink)
            thislinkdircomps = thislinkdir.split('/')
            linkdir, linkfname = os.path.split(linkpath)
            for el in linkdir.split('/'):
                if el == '..':
                    thislinkdircomps.pop()
                else:
                    thislinkdircomps.append(el)

            linkdest = '/'.join(thislinkdircomps) + '/' + linkfname
            #print(f'link dest = {linkdest}')
            if linkdest not in paths:
                broken_links.append((linkpath, linkdest))

    if len(broken_links) > 0:
        print(f'Broken Links in file {fname}:')
        for orig, dest in broken_links:
            print(f'original {orig} -> destination would be {dest}')

    return len(broken_links)


def main():
    """
    Main function. 

    Builds a set of valid Jekyll links, then use
    this to check all the internal links within the files.
    """
    paths = set()
    # build all the available paths
    for dirpath, dirnames, filenames in os.walk(POSTS_DIR):
        for fname in filenames:
            inpath = os.path.join(dirpath, fname)
            linkpath = get_link_path(inpath)
            paths.add(linkpath)

    # go through again but check the links this time
    nbroken = 0
    for dirpath, dirnames, filenames in os.walk(POSTS_DIR):
        for fname in filenames:
            inpath = os.path.join(dirpath, fname)
            linkpath = get_link_path(inpath)
            nbroken += check_all_links(inpath, linkpath, paths)

    # return appropriate value to the OS.
    if nbroken > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
