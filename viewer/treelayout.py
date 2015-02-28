#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines some (binary) tree layout algorithms.
"""

class SimpleBinaryTreeLayout():

    """
    Simple top to bottom binary tree layout halfing the space between siblings
    at every level.

    Args:
        width (int): The width of the viewport in px, default 800.
        height (int): The height of the viewport in px, default 600.
        margin (int): The margin in px, default 20. The center of the nodes are
            placed on the border so it should be greater than the node radius.
    """

    def __init__(self,
                 width=800,
                 height=600,
                 margin=20):
        self.width = width
        self.height = height
        self.margin = margin

        # node_radius seems to act like a additional margin so we don't need
        # it. It is here because it may be necessary in future if we want to
        # take the additional informations next to a node into account.
        self.node_radius = 0

    def layout(self, tree):
        """
        Layout a binary tree, i.e. calculate the position of each node in
        the viewport where the origin is in the top left.

        Args:
            tree (BinaryTree): the tree to layout.

        Returns:
            dict: node -> (x, y) tuple of double - the coordinates of the
                  center of the node.
        """
        pos = {}
        margin = self.margin + self.node_radius

        if tree.root:
            width = self.width - 2 * margin
            height = self.height - 2 * margin

            # the root is displayed at the top center
            y_0 = margin
            x_0 = margin + width/2
            pos[tree.root] = (x_0, y_0)

            # vertical spacing
            tree_depth = tree.height()
            dy = height / tree_depth if tree_depth != 0 else 0

            # horizontal spacing
            def dx(depth):
                """Returns horizontal spacing for given level:"""
                return (width / 2) / (2 ** depth)

            def pos_from_parent(node, depth, parent_pos):
                """Recursive helper to calculate position based on parent and
                depth."""
                if node:
                    y = y_0 + depth * dy

                    if node == node.parent.left:
                        x = parent_pos[0] - dx(depth)
                    else:
                        x = parent_pos[0] + dx(depth)

                    pos[node] = (x, y)

                    pos_from_parent(node.left, depth+1, (x, y))
                    pos_from_parent(node.right, depth+1, (x, y))

            pos_from_parent(tree.root.left, 1, (x_0, y_0))
            pos_from_parent(tree.root.right, 1, (x_0, y_0))

        return pos
