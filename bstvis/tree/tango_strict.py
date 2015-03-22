#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a implementation of Tango Trees as described in
"Dynamic Optimality - Almost" by ERIK D. DEMAINE, DION HARMON,
JOHN IACONO, AND MIHAI PATRASCU.


It trys to use the proposed strict model, i.e. using only one pointer p at
all times and allowing only the following unit-cost operations
 - go left  (p = p.left)
 - go right (p = p.right)
 - go up    (p = p.parent)
 - rotate with parent (p.rotate())
on it.

Furthermore the access algorithm is not allowed to save extra data.

The choice of the next operation is a function only of the data of the node
currently pointed to.
You can write data after each operation on the node pointed by p.
The data should have constant size so it can be read and written in constant
time (in the RAM model).

The access algorithm's goal is to set p to the node with the desired key.

In general it has the following structure:

    def search(key):
        p = root
        p.search_key = key

        while True:
            data = p.getData()  # returning p and all fields of p
            operation, data = access_algorithm(data)
            if operation == RIGHT:
                p = p.right
            elif operation == LEFT:
                p = p.left
            elif operation == UP:
                p = p.parent
            elif operation == ROTATE:
                p.rotate()
            else:
                break
            p.setData(data)

        return p.data

where access_algorithm is a function mapping a node's data to an operation and
the data to write after the operation.


Implementation note
-------------------
A (sane) programm can (?) be transformed to a function of the required form by
saving the state of the programm in the node. This includes the line you are at
and all local variables.

So you are model-conform if you use only constant space and no additional
pointers.

TODO Proof this :)


Implementation note
-------------------
You can still use statements like

    if p.parent.right.color == RED:
        ..

because they can be rewritten as:

    # go to node
    key = self.key
    p = p.parent

    p = p.right

    # retrieve the value
    val = p.color

    # go back
    p = p.parent

    p = p.left
    if p.key != key:
        # we should have chosen the right child
        p = p.parent
        p = p.right

    if val == RED:
        ..

This uses only extra space proportional to the length of the code which
is constant.

Implementation note
-------------------
You can even use aliases if you do not modify p before using the alias.

    pp = p.parent
    pp.color = BLACK    // OK - you could substitute pp with p.parent
    p = p.right
    // pp.color = RED   // ERROR - pp is now p.parent.parent
"""

from .bintree import BinaryTree
from .rb import RBNode, RED, BLACK
from .naive import perfect_inserter


def is_root_or_None(node):
    """
    Returns True if node is None or the root of a new auxiliary tree,
    otherwise False.
    """
    return node is None or node.is_root


class TangoNode(RBNode):

    """
    Attributes:
        key
        data
        parent
        left
        right
        tree
        color: inherited from RBTree (to balance auxiliary tree).
        bh: Black-Height from RBTree (concatenate).
        depth (int): depth of node in the perfect BST P (constant over time).
        min_depth (int): The minimum depth of all nodes in auxiliary tree.
        max_depth (int): The maximum depth of all nodes in auxiliary tree.
        is_root (bool): True if this node is the root of an auxiliary tree.
    """

    def __init__(self, key,
                 data=None, parent=None, left=None, right=None, tree=None,
                 color=BLACK, bh=1,
                 depth=0, is_root=True):

        super().__init__(key, data, parent, left, right, tree, color, bh)

        self.depth = depth
        # Infer min_depth and max depth from left and right children
        # and own depth.
        self._update_depths()

        self.is_root = is_root

    def _update_depths(self):
        """
        Infer (recursivly defined) min_depth and max_depth from children.

        *_depth = *(self.depth, self.left.*_depth, self.right.*_depth)
        where * = min or max
        """

        self.min_depth = self.depth
        self.max_depth = self.depth

        if not is_root_or_None(self.left):
            self.min_depth = min(self.min_depth, self.left.min_depth)
            self.max_depth = max(self.max_depth, self.left.max_depth)

        if not is_root_or_None(self.right):
            self.min_depth = min(self.min_depth, self.right.min_depth)
            self.max_depth = max(self.max_depth, self.right.max_depth)

    def rotate(self):
        """
        Rotate node with parent if present. Do nothing if there is no parent.

        This specialized version preserves the tree of tree representation and
        the recursivly defined attributes bh, min_depth and max_depth.

             p := self.parent     self
            /  \                  /  \
          self  C       -->      A    p     (and symmetric case)
          /  \                       / \
         A    B                     B   C
        """
        # Rotate only when not root of auxTree
        # TODO Do we ever need to catch this?
        # if self.is_root:
        #     return

        # ### Start of rotation primitive ###
        # We can only rotate if there is a parent
        if not self.parent:
            return

        # As this is one of the primitive operations we are allowed to use
        # multiple pointers for convenience here.
        parent = self.parent

        # If p has a parent replace its pointer to p with self.
        if parent.parent:
            if parent.parent.left == parent:
                parent.parent.left = self
            elif parent.parent.right == parent:
                parent.parent.right = self
        # If p has no parent we rotate to root and we have to update
        # the tree reference.
        else:
            self.tree = parent.tree
            self.tree.root = self
            parent.tree = None

        self.parent = parent.parent

        # Case 1:
        #     p
        #    /
        #  self
        if parent.left == self:
            parent.left = self.right
            if self.right:
                self.right.parent = parent
            self.right = parent

        # Case 2:
        #  p
        #   \
        #  self
        elif parent.right == self:
            parent.right = self.left
            if self.left:
                self.left.parent = parent
            self.left = parent
        parent.parent = self
        # ### End of rotation primitive ###

        # The following updates do not belong to the rotation primitive but
        # have to be performed after each rotation so they are included in the
        # function.

        # Swap root flag since we may have rotated to a auxiliary tree root.
        # Implementation detail:
        #   To use only one pointer we could remember which case we executed
        #   above and swap with the respective child of self,
        #   i.e. Case 1 -> parent := self.right, Case 2 -> parent := self.left
        self.is_root, parent.is_root = parent.is_root, self.is_root

        # We also update the recursivly defined min/max depth of old parent
        # and self.
        parent._update_depths()
        self._update_depths()

    # The following methods are only used as node_attributes for TreeView.
    @property
    def ir(self):   # is_root
        return self.is_root

    @property
    def d(self):
        return self.depth

    @property
    def min_d(self):
        return self.min_depth

    @property
    def max_d(self):
        return self.max_depth


class TangoTree(BinaryTree):

    """
    Tango Trees are a class of O(log log n)-competetive binary search trees.
    They only support searches.

    Args:
        keys (list): The static universe of keys.
    """

    def __init__(self, keys):
        super().__init__()

        if not keys:
            raise AttributeError("No keys given")

        # We want to use insert() to construct the initial tree.
        # After that we disable insert() by setting constructed to True.
        self.constructed = False

        # Create perfect tree P (using insert()).
        # TODO This is only a O(n log n) solution.
        perfect_inserter(self, sorted(keys))
        self.constructed = True

        # Set min_depth and max_depth of each node.
        def fix_depth(node, depth=0):
            # d = min_d = max_d because each node forms its own auxiliary tree
            # You could also invoke _update_depths() on each node.
            if node:
                fix_depth(node.left, depth + 1)
                fix_depth(node.right, depth + 1)
                node.depth = node.min_depth = node.max_depth = depth

        fix_depth(self.root)

    def insert(self, key, data=None):
        """A naive insert function only used to construct the tree."""
        if self.constructed:
            raise NotImplementedError(
                "Original Tango Trees do not support insert")

        if self.root is None:
            self.root = TangoNode(key, tree=self)
            return

        p = self.root
        parent = None
        is_left_child = False

        while p is not None:
            if key < p.key:
                parent = p
                p = p.left
                is_left_child = True
            elif key > p.key:
                parent = p
                p = p.right
                is_left_child = False

        p = TangoNode(key, parent=parent)
        if is_left_child:
            parent.left = p
        else:
            parent.right = p

    def search(self, key):
        """
        Search for key in the tree.

        The search is only defined for accesses, i.e. keys that are actually
        in the tree.

        Returns:
            The reference p of a node with p.key == key.
        """

        # Start at the root.
        p = self.root

        # We do a normal BST walk.
        while True:
            if p.key < key:
                p = p.right
            elif p.key > key:
                p = p.left
            else:
                break

            # If we visit a marked node we have to modifiy the preferred paths
            # 1 Cut auxiliary tree containing the parent of p at p.min_depth-1.
            #       into a top and a bottom path.
            # 2 Join the top path with auxiliary tree rooted at p.
            if p.is_root:
                depth = p.min_depth - 1
                p = p.parent

                p = self._cut(p, depth)

                # p is now the root of the top path.
                # Go down to the bottom path to join again.
                p = self._aux_search(key, p)
                # We are now at a leaf of the top path so go down one more.
                if p.key < key:
                    p = p.right
                elif p.key > key:
                    p = p.left
                else:
                    raise Exception("??")

                p = self._join(p)

        # The while loop has terminated so p.key == key.
        # If the searched node was a root we are now at the root again
        # so we make sure that p.key = key again
        # TODO Test if this breaks something again.
        # if p.key != key:
        #     p = self._aux_search(key, p)

        # Finally set the preferred child of the access p to left.
        # 1 cut its auxiliary tree at depth p.depth
        # 2 join with preceding marked node
        print("final cut&join")
        p = self._cut(p, p.depth)

        # Go down to node again.
        p = self._aux_search(key, p)

        # The paper says: "join the resulting top path with the auxiliary tree
        # rooted at the preceding marked node"
        #
        # So we try to find the predecessor of p.
        # Case 1: The predecessor is an ancestor of p, i.e. p has no
        #         left child (and we would go up).
        #   Then this predecessor is already included in the auxiliary tree,
        #   i.e. (*)
        #       - the preferred child of p in P is already set to left or
        #       - p has no children in P and the predecessor of p in P is also
        #         above
        # Case 2: p has a left child
        #   Find the first root on the way to predecessor.
        #   Case 2.1 if you find a root: join it
        #   Case 2.2 if not: (*)

        if p.left is None:
            # Case 1
            pass
        else:
            p = p.left

            # Go to predecessor but stop at a root.
            while not p.is_root and p.right is not None:
                p = p.right

            # The loop exited because:
            if p.is_root:
                # Case 2.1: p.is_root: join it.
                p = self._join(p)
            else:
                # Case 2.2: p.right is None: predecessor is already included.
                pass

        # Search for p again to return pointer/data
        p = self._aux_go_to_root(p)
        p = self._aux_search(key, p)
        print("Search: Found", p.key)
        return p

    def _aux_search(self, key, root):
        """
        Search key in the auxiliary tree with the given root.

        Returns:
            Either the node with the given key or
            the leaf where the search ends.
        """
        # Do an ordinary search until the next node would be a root or None.
        p = root
        while p.key != key:
            if p.key < key:
                if not is_root_or_None(p.right):
                    p = p.right
                else:
                    # print("\taux_search of {} in {} ended in leaf {}".format(
                    #     key, root.key, p.key))
                    # self.view(highlight_nodes=[p])
                    return p
            elif p.key > key:
                if not is_root_or_None(p.left):
                    p = p.left
                else:
                    # print("\taux_search of {} in {} ended in leaf {}".format(
                    #     key, root.key, p.key))
                    # self.view(highlight_nodes=[p])
                    return p

        # print("\taux_search of {} in {} successful".format(
        #     key, root.key))
        # self.view(highlight_nodes=[p])
        return p

    def _aux_go_to_root(self, p):
        """
        Returns the root of the auxiliary tree containing p.
        """
        if p is None:
            return None

        while not p.is_root:
            p = p.parent
        # print("\tgoing up to", p.key)
        # self.view(highlight_nodes=[p])
        return p

    def _aux_concatenate(self, p):
        """
        p is the root of a subtree t where both childs are roots of
        red-black trees:
            p
           / \
          T1 T2
        Modify t such that t is a red-black tree by doing
        concatenate(T1, p, T2).

        Returns:
            The (new) root of the concatenated tree.
        """
        # See also RBTree._concatenate().

        t1 = p.left     # just an alias for readability
        if t1 and t1.color == RED:
            t1.color = BLACK
            t1.bh += 1
        t2 = p.right    # just an alias for readability
        if t2 and t2.color == RED:
            t2.color = BLACK
            t2.bh += 1

        # To return the root after concatenation we want to save its parent's
        # key so we can go up to it after the rotations and the rb_fixup().
        parent_key = p.parent.key if p.parent else None

        # There are 4 cases: t1 and t2 can both exist or not.

        # Case 1: both subtrees are empty
        if is_root_or_None(t1) and is_root_or_None(t2):
            # There is nothing to do. Just restore the RB properties.
            root_key = p.key

            p.color = BLACK
            p.bh = 1

        # Case 2: t1 is empty (and t2 not)
        # p         t2
        #  \  -->  /_\
        #  t2     p
        elif is_root_or_None(t1):
            # Insert p into t2.
            # This can also be done simply by rotating it down.
            root_key = p.right.key

            while not is_root_or_None(p.right):
                p.right.rotate()

            # We set the color of p to RED as if it was inserted and invoke
            # insert_fixup() later.
            p.color = RED
            p.bh = 0

        # Case 3: t2 is empty (and t1 not) - symmetric to case 2
        #   p      t1
        #  /  ->  /_\
        # t1         p
        elif is_root_or_None(t2):
            root_key = p.left.key

            while not is_root_or_None(p.left):
                p.left.rotate()

            p.color = RED
            p.bh = 0

        # Case 4: t1 and t2 are present
            #   p
            #  / \
            # t1 t2
        # Case 4.1: t1 and t2 have equal black-height
        elif t1.bh == t2.bh:
            root_key = p.key

            p.color = BLACK
            p.bh = t1.bh + 1

        # Case 4.2: t1 has larger black-height
        elif t1.bh > t2.bh:
            # Make t2 part of t1
            # Rotate down the right path of t1 to search for the node
            # with equal blackheight as t2 (and maximum depth).
            # p.right is always t2.
            #   /\
            #  /  t (red)
            # /__/_\
            root_key = p.left.key

            p.color = RED
            p.bh = t2.bh
            while p.left.bh > t2.bh or p.left.color == RED:
                p.left.rotate()

        # Case 4.3: t2 has larger black-height - symmetric to case 4.2
        else:
            # symmetric to Case 4.2
            root_key = p.right.key

            p.color = RED
            p.bh = t1.bh
            while p.right.bh > t1.bh or p.right.color == RED:
                p.right.rotate()

        # fix RB properties
        if p.color == RED:
            p = TangoTree._insert_fixup(p)
            # p moves only up as it does if we go to root.

        # go up to (new) root
        if parent_key == None:
            # go to real root
            while p.parent:
                p = p.parent
        else:
            while p.parent.key != parent_key:
                p = p.parent

        # print("\tconcatenated")
        # self.view(highlight_nodes=[p])
        return p

    def _insert_fixup(p):
        """
        Fix RB properties.

        Returns:
            The node where fixup stops.
        """
        while not p.is_root and p.parent.color == RED:
            # p.parent.parent exists because p.parent.color == RED
            if p.parent == p.parent.parent.left:
                y = p.parent.parent.right       # NOTE: y is just an alias
                if y and y.color == RED:
                    #   gB           p=gR
                    #  / \            / \
                    # qR  yR  -->    qB  yB
                    #  \              \
                    # ..pR           ..R
                    p.parent.color = BLACK
                    p.parent.bh += 1
                    y.color = BLACK
                    y.bh += 1
                    p.parent.parent.color = RED
                    p = p.parent.parent
                else:
                    #   gB             gB          pB
                    #  / \            / \         / \
                    # qR  yB  -->    pR  yB -->  qR  gR
                    #  \            /                 \
                    # ..pR         qR                  y
                    if p == p.parent.right:
                        p.rotate()
                        p = p.left
                    p.parent.color = BLACK
                    p.parent.bh += 1
                    p.parent.parent.color = RED
                    p.parent.parent.bh -= 1
                    p.parent.rotate()
            else:
                # analog left <-> right
                y = p.parent.parent.left
                if y and y.color == RED:
                    p.parent.color = BLACK
                    p.parent.bh += 1
                    y.color = BLACK
                    y.bh += 1
                    p.parent.parent.color = RED
                    p = p.parent.parent
                else:
                    if p == p.parent.left:
                        p.rotate()
                        p = p.right
                    p.parent.color = BLACK
                    p.parent.bh += 1
                    p.parent.parent.color = RED
                    p.parent.parent.bh -= 1
                    p.parent.rotate()

        # if not p.parent and p.color == RED:
        if p.is_root and p.color == RED:
            p.color = BLACK
            p.bh += 1

        return p

    def _aux_split(self, p, root_key=None):
        """
        Reorder the auxiliary tree containing p such that p is at the root.

        You can also specify a root_key to mark the root of a subtree which is
        a red-black tree but not a auxiliary tree.

        Note: The resulting tree is not a red-black tree any more but
              p's children are.

        Note: The runtime is logarithmic (the runtimes of the concatenates
              add up nicely).

        Returns:
            The root p.
        """
        # See also RBTree.split()

        found_root_key = False
        if root_key is not None and p.key == root_key:
            return p

        while not p.is_root and not found_root_key:
            if root_key and p.parent.key == root_key:
                found_root_key = True

            if p == p.parent.left:
                #     pp           p
                #    /  \         / \
                #   p    R'  ->  L   pp
                #  / \              / \
                # L   R            R   R'
                p.rotate()
                p = self._aux_concatenate(p.right)
            else:
                p.rotate()
                p = self._aux_concatenate(p.left)

            p = p.parent

        # print("\tsplit")
        # self.view(highlight_nodes=[p])
        return p

    def _cut(self, p, d):
        """
        Cut the auxiliary tree containing p into two auxiliary trees, one
        containing all nodes with depth <= d and one with depths > d.

        Returns:
            The root of the top path.
        """
        # TODO explain cutting
        print("Cut at", p.key, "depth", d)
        p = self._aux_go_to_root(p)

        # l .. smalles node with depth > d
        #      found by walking left while max_depth > d
        # r .. biggest node with depth > d
        #      found by walking right while max_depth > d
        # l_pre .. predecessor of l
        # r_suc .. successor of r

        if p.max_depth <= d:
            # There is no l and no r, i.e. the interval is empty
            # we can return
            return p

        # Find l.
        #  - if there is a left child and its max_depth is > d:
        #       go left
        #  - if there is no left child and the current node has depth > d:
        #       return this node
        #  - if there is no left child and the current node has depth <= d:
        #       go right (this right child has to have max_depth > d)
        while True:
            if not is_root_or_None(p.left) and p.left.max_depth > d:
                # we can go left
                p = p.left

            # The following two cases can be combined when the case above is
            # already covered:
            # elif is_root_or_None(p.left) and p.depth > d:
                # can not go left and node has desired depth -> found it
            # elif (not is_root_or_None(p.left) and p.left.max_depth <= d
            #       and p.depth > d):
                # this is the minimal node with depth > d,
                # all smaller nodes have depth <= d

            # The minimal node is found.
            elif p.depth > d:
                break

            # We may have to go right if p.depth <= d and left is nothing.
            elif p.depth <= d and (
                    (not is_root_or_None(p.left) and p.left.max_depth <= d) or
                    is_root_or_None(p.left)):
                p = p.right
            else:
                raise Exception('ERROR: Case not covered')

        # Find predecessor of l.
        p, l_pre_exists = self._find_predecessor(p)

        # To find the node where to concatenate we also save the key.
        l_pre_key = p.key if l_pre_exists else None

        # Split if predecessor exists.
        if l_pre_exists:
            # Do splitting. Result:
            p = self._aux_split(p)
            subtree_root_key = p.right.key if p.right else None
            # Result:
            #   l_pre = p
            #    / \
            #   /   *.key == subtree_root_key
            #  /\   /\
            # /B \ /C \  <-  r may be in C.
            # ---- ----
        else:
            # Go back to root.
            p = self._aux_go_to_root(p)
            subtree_root_key = p.key
            # Result:
            #   p.key = subtree_root_key
            #  / \
            # / C \  <-  r may be in C.
            # -----

        # Find r (symmetric to finding l).
        while True:
            if not is_root_or_None(p.right) and p.right.max_depth > d:
                p = p.right

            # The minimal node is found.
            elif p.depth > d:
                break

            # We may have to go left if p.depth <= d and right is nothing.
            elif p.depth <= d and (
                    (not is_root_or_None(p.right) and p.right.max_depth <= d) or
                    is_root_or_None(p.right)):
                p = p.left
            else:
                raise Exception('ERROR: Case not covered')

        # Find successor of r.
        p, r_suc_exists = self._find_successor(p)

        # Split if Successor exists.
        if r_suc_exists:
            p = self._aux_split(p, subtree_root_key)

            # Result
            #       l_pre
            #      / \
            #     /   r_suc = p
            #    /\    /  \
            #   /B \  /\  /\
            #   ---- /D \/E \
            #        --------
            p = p.left

        # else:
        # l_pre
        #   \
        #   /\
        #  /D \
        #  ----

        # Mark root of D as new auxiliary tree.
        self._aux_set_root_mark(p, True)

        if r_suc_exists:
            p = p.parent
            p = self._aux_concatenate(p)

        if l_pre_exists:
            # Go back up to node with key l_pre_key.
            while p.key != l_pre_key:
                p = p.parent
            p = self._aux_concatenate(p)

        print("\tCut end.")
        self.view(highlight_nodes=[p])

        return p

    def _aux_split_l(self, p, l_pre):
        """
        Split at l_pre if present where l_pre is either p or None

        Case 1: l_pre is not None
            Do splitting. Result:

                l_pre = p
                 / \
                /   *.key == subtree_root_key
               /\   /\
              /B \ /Cr\
              ---- ----

        Case 2: l_pre is None
            No splitting.

                p.key = subtree_root_key
               / \
              /Cr \
              -----

        Returns:
            p, subtree_root_key
        """
        if l_pre is not None:
            p = self._aux_split(l_pre)
            print("Split l")
            self.view(highlight_nodes=[p])
            # we need to mark the right child as root since we want to
            # use split later
            #
            # TODO how to use split on right subtree properly
            #   1 specify pseudo root
            #   2 temporary mark right child as root

            # proper splitting
            subtree_root_key = p.right.key if p.right else None
        else:
            p = self._aux_go_to_root(p)
            print("l_pre is None: no left split")
            self.view(highlight_nodes=[p])
            subtree_root_key = p.key
        return (p, subtree_root_key)

    def _aux_split_r(self, p, r_suc, subtree_root_key):
        """
        TODO ? Split at r_suc where r_suc is either p or None.

        Returns:
            p
        """
        if r_suc is not None:
            p = self._aux_split(r_suc, subtree_root_key)
            print("Split r")
            self.view(highlight_nodes=[p])
            # Result
            #       l_pre
            #      / \
            #     /   r_suc = p
            #    /\    /  \
            #   /B \  /\  /\
            #   ---- /D \/E \
            #        --------
            p = p.left      # TODO check None
            print("Interval splitted")
            self.view(highlight_nodes=[p])
            return p
        else:
            # l_pre
            #   \
            #   /\
            #  /D \
            #  ----
            p = p.right
            print("Interval splitted (else)")
            self.view(highlight_nodes=[p])
            return p

    def _join(self, p):
        """
        Join the auxiliary tree t containing p with the auxiliary tree
        containing the parent of the root of t.

        Returns:
            The root of the joined auxiliary tree.
        """
        print("Join at", p.key)
        self.view(highlight_nodes=[p])

        # Normalize p. We are now at the root of an bottom path.
        p = self._aux_go_to_root(p)

        # Save the root of the bottom to find its predecessor/successor
        # in top path.
        root_key = p.key

        # Go up to the top path.
        p = p.parent

        # If we search this auxiliary tree for root_key we find
        # l_pre < root_key < r_suc (l_pre or r_suc may be None).

        # Case 1: Found l_pre.
        #  p = l_pre
        #   \
        #   root
        if p.key < root_key:
            l_pre_key = p.key

            p = self._aux_split(p)
            subtree_root_key = p.right.key if p.right else None

            p, r_suc_exists = self._find_successor(p)

            if r_suc_exists:
                p = self._aux_split(p, subtree_root_key)
                p = p.left
            else:
                p = p.right

            # Unmark instead of mark as in split.
            p = self._aux_set_root_mark(p, False)

            # Concatenate right if present.
            if r_suc_exists:
                p = p.parent
                p = self._aux_concatenate(p)

            # Concatenate left.
            while p.key != l_pre_key:
                p = p.parent
            p = self._aux_concatenate(p)

        # Case 2: Found r_suc (symmetric to case 1).
        #   p = r_suc
        #  /
        # root
        else:
            r_suc_key = p.key

            p = self._aux_split(p)
            subtree_root_key = p.left.key if p.left else None

            p, l_pre_exists = self._find_predecessor(p)

            if l_pre_exists:
                p = self._aux_split(p, subtree_root_key)
                p = p.right
            else:
                p = p.left

            # Unmark instead of mark as in split.
            p = self._aux_set_root_mark(p, False)

            # Concatenate left if present.
            if l_pre_exists:
                p = p.parent
                p = self._aux_concatenate(p)

            # Concatenate right.
            while p.key != r_suc_key:
                p = p.parent
            p = self._aux_concatenate(p)

        print("\tJoin end.")
        self.view(highlight_nodes=[p])

        return p

    def _aux_set_root_mark(self, p, mark):
        """
        Set p.is_root to mark and updates min_depth and max_depth of ancestors.

        Returns:
            p
        """
        p.is_root = mark
        # This adds or removes nodes from the subtree p.parents auxiliary tree
        # so we have to update all recursively defined attributes.
        if p.parent:
            # save the key to go back to it
            p_key = p.key

            # update the depths
            p = p.parent
            p = self._aux_update_depths(p)

            # go back
            if p.key > p_key:
                p = p.left
            else:
                p = p.right


        print("\tSet root to", mark)
        self.view(highlight_nodes=[p])

        return p

    def _aux_update_depths(self, p):
        """
        Update the min_depth and max_depth of p and its ancestors in auxiliary
        tree.

        This is be needed if you mark or unmark a node thus changing an
        auxiliary tree.

        Returns:
            The argument p.
        """
        p._update_depths()
        p_key = p.key

        while not p.is_root:
            p = p.parent
            p._update_depths()

        # go down to the saved key again
        p = self._aux_search(p_key, p)

        return p

    # The methods _find_predecessor(self, p) and _find_successor(self, p)
    # do not return p.
    def _find_predecessor(self, p):
        """
        Returns the predecessor of a node in an auxiliary tree if it exists,
        otherwise p itself.

        Returns:
            (pred, True) if pred is the predecessor of p, otherwise
            (p, False) if there is no predecessor.
        """
        # Case 1: left subtree is not empty
        #   the maximum node of the left subtree is the predecessor
        if not is_root_or_None(p.left):
            # if left child exists go left and then all the way right
            p = p.left
            while not is_root_or_None(p.right):
                p = p.right
            return p, True

        # Case 2: left subtree is empty
        #   go up until we come from a right child
        #   this parent is the predecessor
        # Case 3: no parent (and left subtree) exists
        #   there is no predecessor
        p_key = p.key
        while True:
            if p.is_root:
                # Case 3: no predecessor
                # We have to go back to p
                p = self._aux_search(p_key, p)
                return p, False
            if p == p.parent.right:
                return p.parent, True
            else:
                p = p.parent    # go up

    def _find_successor(self, p):
        """
        Returns the successor of a node in an auxiliary tree if it exists,
        otherwise p itself.

        Returns:
            (succ, True) if succ is the successor of p, otherwise
            (p, False) if there is no successor.
        """
        # This is symmetric with _find_predecessor swapping left and right.

        # Case 1: right subtree is not empty
        #   the maximum node of the right subtree is the successor
        if not is_root_or_None(p.right):
            # if right child exists go right and then all the way left
            p = p.right
            while not is_root_or_None(p.left):
                p = p.left
            return p, True

        # Case 2: right subtree is empty
        #   go up until we come from a left child
        #   this parent is the successor
        # Case 3: no parent (and right subtree) exists
        #   there is no successor
        p_key = p.key
        while True:
            if p.is_root:
                # Case 3: no successor
                # We have to go back to p
                p = self._aux_search(p_key, p)
                return p, False
            if p == p.parent.left:
                return p.parent, True
            else:
                p = p.parent    # go up


from bstvis.viewer import NodeShape


def node_shape(node):
    if node.is_root:
        return NodeShape.square
    else:
        return NodeShape.circle


def main():
    from bstvis.viewer import TreeView

    t = TangoTree(range(12))
    tv = TreeView(t,
                  node_attributes=['d', 'min_d', 'max_d', 'bh'], width=800,
                  node_shape=node_shape)
    tv.view()
    # t.search(4)
    # t.search(10)

    t.search(0)
    t.search(2)
    t.search(4)
    t.search(6)
    t.search(8)
    t.search(11)
    tv.view()


def sample_tree():
    # manually setup a sample tree
    universe = range(1, 16)
    t = TangoTree(universe)
    nodes = dict()

    #                  key, data, pare, left,    right,     tree, color, bh,d, ir
    nodes[1] = TangoNode(1, None, None, None,     None,     None, BLACK, 1, 3, True)

    nodes[7] = TangoNode(7, None, None, None,     None,     None, BLACK, 1, 3, True)

    nodes[5] = TangoNode(5, None, None, None,     None,     None, RED,   0, 3, False)
    nodes[6] = TangoNode(6, None, None, nodes[5], nodes[7], None, BLACK, 1, 2, True)

    nodes[9] = TangoNode(9, None, None, None,     None,     None, BLACK, 1, 3, True)

    nodes[10] = TangoNode(10, None, None, nodes[9], None,   None, RED,   0, 2, False)
    nodes[11] = TangoNode(11, None, None, nodes[10], None,  None, BLACK, 1, 3, True)

    nodes[13] = TangoNode(13, None, None, None,   None,     None, BLACK, 1, 3, True)

    nodes[12] = TangoNode(12, None, None, nodes[11], nodes[13], None, RED, 0, 1, False)
    nodes[15] = TangoNode(15, None, None, None,   None,     None, RED,   0, 3, False)
    nodes[14] = TangoNode(14, None, None, nodes[12], nodes[15], None, BLACK, 1, 2, True)

    nodes[3] = TangoNode(3, None, None, None,     None,     None, RED,   0, 3, False)
    nodes[2] = TangoNode(2, None, None, nodes[1], nodes[3], None, BLACK, 1, 2, False)
    nodes[8] = TangoNode(8, None, None, nodes[6], nodes[14], None, BLACK, 1, 0, False)
    nodes[4] = TangoNode(4, None, None, nodes[2], nodes[8], None, BLACK, 2, 1, True)

    t.root = nodes[4]

    from bstvis.util import set_parents
    set_parents(t)

    from bstvis.viewer import TreeView
    tv = TreeView(t,
                  node_attributes=['d', 'min_d', 'max_d'], width=800,
                  node_shape=node_shape)
    tv.view()
    t.search(9)
    tv.view()


if __name__ == '__main__':
    sample_tree()
    # main()
