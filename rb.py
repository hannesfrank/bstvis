from bintree import Node
from naive import NaiveBST

RED = 'red'
BLACK = 'black'

class RBNode(Node):
    """
    Representation of a node in a Red Tree, 
    i.e. has key, left/right child and parent
    and additionally color and black-height bh.

    The black-height has to be maintained during rotations.
    """
    def __init__(self, key, 
        data=None, parent=None, left=None, right=None, tree=None,
        color=RED, bh=0):
        """
        root node should have tree set to adjust when rotated
        """
        super().__init__(key, data, parent, left, right, tree)
        self.color = color
        self.bh = bh

    @property
    def grand_parent(self):
        if self.parent:
            return self.parent.parent
        else:
            return None
    
    
    def rotate(self):
        """
        Rotate node with parent if present.
        """
        if self.parent == None:
            return
        
        parent = self.parent

        if parent.parent:
            if parent.parent.left == parent:
                parent.parent.left = self
            elif parent.parent.right == parent:
                parent.parent.right = self
        else:
            # we rotate to root -> change in tree
            self.tree = parent.tree
            self.tree.root = self
            parent.tree = None
        self.parent = parent.parent

        if parent.left == self:
            parent.left = self.right
            if self.right: self.right.parent = parent
            self.right = parent
        elif parent.right == self:
            parent.right = self.left
            if self.left: self.left.parent = parent
            self.left = parent
        parent.parent = self

class RBTree(NaiveBST):
    """
    A balanced BST implementation.

    A Red-Black-Tree uses one bit of extra information:
        node.color = RED|BLACK
    It enforces the following properties to be balanced
    1. The root (and all leaves, i.e. None-pointer) are BLACK.
    2. Every RED node has two BLACK children.
    3. Every root-to-leaf-path has the same number of BLACK nodes.

    Optionally the black-height of a node p 
        bh(p) = #(black nodes in a p-to-leaf-path)
    can be maintained without extra cost.
    """
    def __init__(self):
        super().__init__()
    # drawing reads color attributes so use constants of matplotlib

    # search like NaiveBST

    def insert(self, key, data=None):
        """
        Insert or update data for given key.

        Returns True for insert (key is new) and False for update (key already present).
        """
        if self.root == None:
            self.root = RBNode(key, data, tree=self, color=BLACK)
            self.root.color = BLACK
            self.root.bh = 1
            return True

        p = self.root
        parent = None
        isLeftChild = False

        while p != None:
            if key == p.key:
                p.data = data
                return False
            elif key < p.key:
                parent = p
                p = p.left
                isLeftChild = True
            elif key > p.key:
                parent = p
                p = p.right
                isLeftChild = False

        p = RBNode(key, data, parent)
        if isLeftChild:
            parent.left = p
        else:
            parent.right = p
        p.color = RED
        p.bh = 0
        RBTree._insert_fixup(p)

    def _insert_fixup(p):
        """fix rb-properties"""
        while p.parent and p.parent.color == RED:
            # p.parent.parent exists because p.parent.color == RED
            if p.parent == p.parent.parent.left:
                y = p.parent.parent.right
                if y and y.color == RED:
                    #   gB           p=gR
                    #  / \            / \
                    # qR  yR  -->    qB  yB
                    #  \              \
                    #...pR          ...R
                    p.parent.color = BLACK
                    p.parent.bh += 1
                    y.color = BLACK
                    y.bh += 1
                    p.parent.parent.color = RED
                    p = p.parent.parent
                else:
                    #   gB             gB          qB      
                    #  / \            / \         / \      
                    # qR  yB  -->    qR  yB -->  pR  gR        
                    #  \            /                 \
                    #...pR         pR                  y
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
        
        if not p.parent and p.color == RED:
            p.color = BLACK
            p.bh += 1

    def delete(self, key):
        pass

    def __repr__(self):
        return self.root.__repr__()

    def join(self):
        RBTree._join(self.root)

    def _join(x):
        """
        x is the root of a BST where both subtrees are Red-Black-Trees:
            x
           / \
          T1 T2
        Modify t such that t is a Red-Black-Tree by doing join(T1, t, T2).
        """
        t1 = x.left
        if t1 and t1.color == RED:
            t1.color = BLACK
            t1.bh += 1
        t2 = x.right 
        if t2 and t2.color == RED:
            t2.color = BLACK
            t2.bh += 1

        if t1 == None and t2 == None:
            x.color = BLACK
            x.bh = 1
        elif t1 == None:
            # x
            #  \
            #  t2
            while x.right:
                x.right.rotate()
            x.color = RED
            x.bh = 0
        elif t2 == None:
            while x.left:
                x.left.rotate()
            x.color = RED
            x.bh = 0
        elif t1.bh == t2.bh:
            x.color = BLACK
            x.bh = t1.bh + 1
        elif t1.bh > t2.bh:
            # walk down the right path of t1 to search for the node 
            # with equal blackheight than t2
            # x.right is always t2
            #   /\
            #  /  t (red)
            # /__/_\
            x.color = RED
            x.bh = t2.bh
            while x.left.bh > t2.bh or x.left.color == RED:
                x.left.rotate()
        else:
            x.color = RED
            x.bh = t1.bh
            while x.right.bh > t1.bh or x.right.color == RED:
                x.right.rotate()

        if x.color == RED:
            RBTree._insert_fixup(x)

    def split(self, x):
        # search for x
        p = self.root
        while p != None:
            if p.key == x:
                break
            elif p.key < x:
                p = p.right
            else:
                p = p.left
        else:
            raise KeyError("Key {} not found".format(x))

        while p != self.root:
            if p == p.parent.left:
                #     pp
                #    /  \
                #   p   r_n
                #  / \
                # L   R
                p.rotate()
                RBTree._join(p.right)
            else:
                p.rotate()
                RBTree._join(p.left)



def main():
    import random
    import drawing
    random.seed(0)  # do always the same for testing
    
    tree = RBTree()
    # tv = drawing.TreeView(tree)
    tv = drawing.TreeView(tree, node_attributes=['bh'], animation=True)
    n = 3
    universe = list(range(n))
    random.shuffle(universe)
    for key in universe:
        tree.insert(key)
        # tv.display(pause=0.1)
    tv.display()
    # tree.root.left.right.rotate()
    # tv.display(pause=2)
    # tree.root.right.left.rotate()
    # tv.display(pause=0.3)
    # tree.root.left.rotate()
    # tv.display(pause=1)
    tv.test()
    
def joinTest():
    t1 = RBTree()
    t2 = RBTree()
    
    t = RBTree()
    t.insert(7)

    t1.insert(4)
    t1.insert(2)
    t1.insert(6)
    t1.insert(1)
    t1.insert(3)
    t1.insert(5)
    t2.insert(9)
    t2.insert(8)
    t2.insert(10)

    t.root.left = t1.root
    t1.root.parent = t.root
    t1.root.tree = None
    t.root.right = t2.root
    t2.root.parent = t.root
    t2.root.tree = None


    import treeview
    tv = treeview.TreeView(t)
    tv.view()
    RBTree.join(t)
    tv.view()

if __name__ == '__main__':
    # main()
    joinTest()
    
    # introspection test
    # t = RBTree()
    # t.insert(7)
    # t.insert(2)
    # r = t.root
    # print(r)
    # print(dir(r))
    # print(r.__dict__)
    # print(dir(RBNode))
    # print(RBNode.__dict__)