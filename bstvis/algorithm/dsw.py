#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The Day-Warren-Stout-algorithm transforms a BST into a perfect BST:

1 Rotate the tree into a vine - O(n).
2 Starting at the root rotate every other node of the vine - O(n).

Q. Stout and B. Warren - Tree Rebalancing in Optimal Time and Space
http://web.eecs.umich.edu/~qstout/pap/CACM86.pdf

T. Rolfe - One-Time Binary Search Tree Balancing:
The Day/Stout/Warren (DSW) Algorithm
http://penguin.ewu.edu/~trolfe/DSWpaper/
"""


def dsw(t, advanced=True):
    """
    Day algorithm - almost perfect binary search tree if advanced is False.
    Warren, Stoud algorithm - perfect binary search tree if advanced is True.
    """
    p = t.root
    if not p:
        return
    t.view(highlight_nodes=[p])

    # n is the number of nodes.
    n = 1

    # Phase 1: Make a right leaning chain/linked list (vine)
    #  - Go to the maximum node.
    while p.right:
        p = p.right
        # t.view(highlight_nodes=[p])

    # Go up and rotate all left children.
    while p.left or p.parent:
        while p.left:
            p.left.rotate()
            # t.view(highlight_nodes=[p])

        if p.parent:
            p = p.parent
            n += 1
            # t.view(highlight_nodes=[p])

    # Phase 2: Compress the tree by rotating every other node.
    # TODO: Explain Phase 2.

    def compress(p, count):
        """
        Starting at p rotate every other right child count times.
        """
        for c in range(count):
            p = p.right
            p.rotate()
            t.view(highlight_nodes=[p])
            p = p.right

    # Day - almost perfect binary tree
    if not advanced:
        # The right leaning chain has n nodes and n - 1 edges.
        # So we can go right n - 1 times which means we can rotate every other
        # node (n - 1)//2 times.
        m = (n - 1)//2

        while m > 0:
            # Rotate m times.
            compress(t.root, m)

            n -= m + 1
            m = n//2

    # Stoud, Warren - perfect binary tree
    else:
        d = (1 << (n+1).bit_length() - 1) - 1

        compress(t.root, n - d)
        while d > 0:
            d //= 2
            compress(t.root, d)


def main():
    from bstvis.viewer import TreeView
    from random import shuffle
    from bstvis.tree.naive import NaiveBST, perfect_inserter

    t = NaiveBST()
    v = TreeView(t)

    keys = list(range(20))
    shuffle(keys)

    # for i in keys:
    #     t.insert(i)
    perfect_inserter(t, sorted(keys))

    t.view()

    dsw(t, advanced=False)
    t.view()


if __name__ == '__main__':
    main()