from bintree import BinaryTree, Node

class NaiveBST(BinaryTree):
    """
    An unbalanced Binary Search Tree Implementation.

    No augumented data.
    """
    def __init__(self):
        super().__init__()
        self.root = None

    def _search(self, key):
        p = self.root
        while p != None:
            if p.key == key:
                return p.data
            elif p.key < key:
                p = p.right
            else:
                p = p.left
        raise KeyError("Key {} not found".format(key))
        return p

    def search(self, key):
        p = self._search(key)
        return p.data

    def search_functional(self, key):
        def accessAlgorithm(searchTarget):
            # the access algorithms choice for the next operation depends on
            # - the key to search (global information)
            # - the current key (local)
            # - augumenting attributes of the node
            # availible Operations
            # - move to parent/left/right
            # - rotate
            # and write augumenting information on entering (exiting?) node
            def moveLeft(p):
                return p.left
            def moveRight(p):
                return p.right
            def moveUp(p):
                return p.parent
            def rotate(p):
                p.rotate()
                return p
            
            def alg(p):
                # you can read p.* but not p.*.*
                # you can also write p.info etc. but p.key is fixed and the pointers
                # can only be modified with rotations
                # you must execute one of the above operations or return
                if p == None:
                    raise KeyError("Key {} not found".format(searchTarget))
                elif p.key == searchTarget:
                    return p
                elif p.key < searchTarget:
                    p = moveRight(p)
                    return alg(p)
                elif p.key > searchTarget:
                    p = moveLeft(p)
                    return alg(p)
            return alg

        alg = accessAlgorithm(key)
        p = self.root   # pointer is always initialized to root node
        p = alg(p)      # run algorithm

        return p.data       

    def insert(self, key, data=None):
        """
        Insert or update data for given key.

        Returns True for insert (key is new) and False for update (key already present).
        """
        # TODO quick and dirty implementation
        if self.root == None:
            self.root = Node(key, data, tree=self)
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

        p = Node(key, data, parent)
        if isLeftChild:
            parent.left = p
        else:
            parent.right = p
        return True

    def delete(self, key):
        pass

    def __repr__(self):
        return self.root.__repr__()

    def preorder(self):
        return self.root.preorder()


def usage():
    import random
    random.seed(0)  # do always the same for testing

    # tree = NaiveBST()
    # print(tree)
    # print()
    
    # tree.insert(2)
    # print(tree)
    # print()

    # tree.insert(1)
    # print(tree)
    # print()

    # tree.insert(3)
    # print(tree)
    # print()

    # print("Random insertions")
    # import random
    # tree = NaiveBST()
    # for i in range(10):
    #   n = random.randint(1,20)
    #   print("insert", n)
    #   tree.insert(n)
    #   print(tree, end="\n\n")

    tree = NaiveBST()
    n = 16
    universe = list(range(n))
    random.shuffle(universe)
    for key in universe:
        tree.insert(key)
    # print(tree)
    # print(tree.preorder())

    node5 = tree.root.left
    node5.rotate()
    print(tree)
    # print(' '.join([str(key) for key in tree.preorder()]))
    
    # tree.show()
    import drawing
    
    # tv = drawing.TreeView(tree)
    # tv.display()
    # tree.root.right.rotate()
    # tv.display()
    print(tree.search_functional(4))

def join():
    t = NaiveBST()
    
    t.insert(7)
    t.insert(4)
    t.insert(2)
    t.insert(6)
    t.insert(1)
    t.insert(3)
    t.insert(5)
    t.insert(9)
    t.insert(8)
    t.insert(10)

    import drawing
    tv = drawing.TreeView(t)
    tv.display(pause=1)
    
    p = t.root
    p.left.rotate()
    tv.display(pause=1)
    p.left.rotate()
    tv.display(pause=1)

def dsw_algorithm(t, v):
    p = t.root
    n = 0   # number of nodes
    if not p:
        return
    v.view(highlight_nodes=[p])

    # phase 1: make a right leaning chain/linked list
    # go to leaf
    while p.right:
        p = p.right
        v.view(highlight_nodes=[p])
    # go up and rotate all left childs until at root
    while True:
        while p.left:
            p.left.rotate()
            v.view(highlight_nodes=[p])

        if p.parent:
            p = p.parent
            n += 1
            v.view(highlight_nodes=[p])
        else:
            break
    # phase 2: 
    n += 1

    x = 1       # discrete log
    while 2*x < n:
        x *= 1
        

def dsw_algorithm_vis():
    from functionaltree.treeview import TreeView
    t = NaiveBST()
    v = TreeView(t)
    keys = range(10)
    keys = [4, 2, 6, 1, 3, 5, 7]
    for i in keys:
        t.insert(i)
    v.view()
    
    dsw_algorithm(t,v)
    v.view()
    # while p.right and p.right.right:
    #     p = p.right
    #     p.rotate()
    #     p = p.right
    #     v.view()


    # while p.parent and p.parent.parent:
    #     p.rotate()
    #     p = p.parent
    #     v.view()


def main():
    # usage()
    # join()
    dsw_algorithm_vis()

if __name__ == '__main__':
    main()