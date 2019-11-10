# -*- coding: utf-8 -*-
"""
Clement Michard (c) 2015
"""

import traceback
from enum import Enum


def print_tree_ud(node,
                  file=None, _prefix="", _last=True,
                  childattr='children', nameattr='name', namelambda=None,
                  ):
    if hasattr(node, nameattr):
        def name(node):
            return getattr(node, nameattr)
    else:
        def name(node):
            return str(node)

    if namelambda:
        name = namelambda

    if hasattr(node, childattr):
        def children(node):
            return getattr(node, childattr)
    else:
        def children(node):
            return []

    print(_prefix, '└-' or "`- " if _last else '├-' or "|- ", name(node), sep="", file=file)
    _prefix += "   " if _last else '│  ' or "|  "
    child_count = len(children(node))
    for i, child in enumerate(children(node)):
        _last = i == (child_count - 1)
        print_tree_ud(child,
                      file, _prefix, _last,
                      childattr=childattr, nameattr=nameattr, namelambda=namelambda,
                      )


def print_tree_lr(current_node, childattr='children', nameattr='name', indent='', last='updown'):
    if hasattr(current_node, nameattr):
        def name(node):
            return getattr(node, nameattr)
    else:
        def name(node):
            return str(node)

    if hasattr(current_node, childattr):
        def children(node):
            return getattr(node, childattr)
    else:
        def children(node):
            return []

    def nb_children(node):
        t = []
        if hasattr(node, childattr):
            for child in children(node):
                t.append(nb_children(child))
        res = sum(t)
        return res + 1

    size_branch = {}
    for child in children(current_node):
        size_branch[child] = nb_children(child)

    """ Creation of balanced lists for "up" branch and "down" branch. """
    up = sorted(children(current_node), key=lambda node: nb_children(node))
    down = []
    while up and sum(size_branch[node] for node in down) < sum(size_branch[node] for node in up):
        down.append(up.pop())

    """ Printing of "up" branch. """
    for child in up:
        next_last = 'up' if up.index(child) is 0 else ''
        next_indent = '{0}{1}{2}'.format(
            indent, ' ' if 'up' in last else '│', ' ' * len(name(current_node)))
        print_tree_lr(child, childattr, nameattr, next_indent, next_last)

    """ Printing of current node. """
    if last == 'up':
        start_shape = '┌'
    elif last == 'down':
        start_shape = '└'
    elif last == 'updown':
        start_shape = ' '
    else:
        start_shape = '├'

    if up:
        end_shape = '┤'
    elif down:
        end_shape = '┐'
    else:
        end_shape = ' '

    print('{0}{1}{2}{3}'.format(
        indent, start_shape, name(current_node), end_shape))

    """ Printing of "down" branch. """
    for child in down:
        next_last = 'down' if down.index(child) is len(down) - 1 else ''
        next_indent = '{0}{1}{2}'.format(
            indent, ' ' if 'down' in last else '│', ' ' * len(name(current_node)))
        print_tree_lr(child, childattr, nameattr, next_indent, next_last)


class Layout(Enum):
    LR = 1
    UD = 2


def print_tree(root, childattr='children', nameattr='name', layout=None):
    if layout is Layout.LR:
        return print_tree_lr(root, childattr=childattr, nameattr=nameattr)
    else:
        return print_tree_ud(root, childattr=childattr, nameattr=nameattr)
