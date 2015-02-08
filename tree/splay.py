from bintree import Node
from naive import NaiveBST


class SplayTree(NaiveBST):

    """
    An unbalanced Binary Search Tree Implementation.

    No augumented data.
    """

    def __init__(self):
        super(SplayTree, self).__init__()

    def search(self, key):
        p = self.root
        while p is None:
            if p.key == key:
                break
            elif p.key < key:
                p = p.right
            else:
                p = p.left
        else:   # no break
            raise KeyError("Key {} not found".format(key))

        self._splay(p)

        # now p is the root
        return p.data

    def _splay(self, p):
        while p.parent is not None:
            # splay until root
            if p.parent.parent is None:
                # zig: one step left
                p.rotate()
            elif p == p.parent.left and p.parent == p.grand_parent.left or \
                    p == p.parent.right and p.parent == p.grand_parent.right:
                # zig zig
                p.parent.rotate()
                p.rotate()
            elif p == p.parent.left and p.parent == p.grand_parent.right or \
                    p == p.parent.right and p.parent == p.grand_parent.left:
                # zig zag
                p.rotate()
                p.rotate()

    def insert(self, key, data=None):
        """
        Insert or update data for given key.

        Returns True for insert (key is new) and
        False for update (key already present).
        """
        # quick & dirty
        if self.root is None:
            self.root = Node(key, data, tree=self)
            return True

        p = self.root
        parent = None
        isLeftChild = False

        while p is not None:
            if key == p.key:
                p.data = data
                self._splay(p)
                return False
            elif key < p.key:
                parent = p
                p = p.left
                isLeftChild = True
            elif key > p.key:
                parent = p
                p = p.right
                isLeftChild = False

        p = Node(key, data, parent)
        if isLeftChild:
            parent.left = p
        else:
            parent.right = p
        self._splay(p)
        return True

    def delete(self, key):
        pass

    def __repr__(self):
        return self.root.__repr__()

    def preorder(self):
        return self.root.preorder()


def main():
    import random
    import drawing
    random.seed(0)  # do always the same for testing

    tree = SplayTree()
    tv = drawing.TreeView(tree)
    n = 16
    universe = list(range(n))
    random.shuffle(universe)
    for key in universe:
        tv.display(0.1)
        tree.insert(key)

    tv.display(0.1)
    print(tree.search(4))
    tv.display(0.1)

if __name__ == '__main__':
    main()
