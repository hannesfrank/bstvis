from tkinter import Tk, Button, Canvas
import tkinter
import time
import functools

class Viewable(object):
    """Inherit from this to get a method to manually view the datastructure.
    """
    def __init__(self):
        super().__init__()
        self._viewer = None

    def view(*args, **kwargs):
        if self._viewer:
            self._viewer.view(*args, **kwargs)

class TreeView:
    """Viewer for a Binary Trees.

    If your binary tree is a subclass of Viewable you can use 
    self.view(**kwargs) to manually invocate a view.
    
    Note: 
        A node must always represent the same key-data-pair and should not 
        overwrite default __hash__ to be usable as a dictionary key.
        TODO we could add a uid to each node to identify it.

    Args:
        tree (BinaryTree): A reference to the tree to be viewed.

    Kwargs:
        node_attributes (list, optional): fields of a Node as string which 
            should be viewed next to the node, default [].
        width (int, optional): tk-viewport width in px, default 800.
        height (int, optional): tk-viewport height in px, default 600.
        node_radius (int, optional): radius of the nodes of the tree in px, 
            default 15.
        font_size (int, optional): font_size of node labels in pt, default 12.
        animation (bool, optional): animate between tree snapshots, 
            default True.
    """

    def __init__(self, tree,
        node_attributes=None,
        width=800, height=600, 
        node_radius=15, font_size=12,
        animation=True):
    
        self.tree = tree
        self.node_attributes = node_attributes if node_attributes else []

        self.width = width
        self.height = height
        self.border = 20
        self.node_radius = node_radius
        self.font = ('Verdana', font_size)
        
        self.animation = animation
        self.end_pause = False   # controls the display loop
        # TODO cleanly implement pause (continue after delay not button press)
        # TODO implement animation with canvas.move() for performance?
        #   store tk-index for each node
        
        self._createGUI()

        # Each display() creates a snapshot of the tree.
        # A snapshot is a dict with the following data:
        #   - 'nodes': {node: ((x,y), node.__dict__) for all nodes}
        #   - 'root': tree.root
        #   - 'info': the kwargs passed to view(..), e.g. the current method of 
        #       the alg
        # The display position of the nodes is saved for animation.
        self.snapshots = [self._create_snapshot()]
        self.current_snapshot_index = 0 
        # TODO (low priority) do incremental versions :)

    def _createGUI(self):
        # main window
        self.window = Tk()
        self.canvas = Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()

        # controls
        self.continue_button = Button(self.window, text="Continue", 
            command=self._continue_callback)
        self.continue_button.pack()
        
        # TODO enable/disable buttons
        self.previous_button = Button(self.window, text="Prev", 
            command=self._previous_callback)
        self.previous_button.pack()
        
        self.next_button = Button(self.window, text="Next", 
            command=self._next_callback)
        self.next_button.pack()

    def _continue_callback(self):
        self.end_pause = True   # exit the event loop

    def _previous_callback(self):
        self._view(self.current_snapshot_index - 1)
    
    def _next_callback(self):
        self._view(self.current_snapshot_index + 1)

    def _create_snapshot(self):
        snapshot = {
            'nodes': {},
            'root': self.tree.root
        }

        # calculate the position in viewport
        pos = self._layout_tree()

        for node, p in pos.items():
            # save other attributes
            snapshot['nodes'][node] = (
                p, 
                # TODO is using __dict__ save or is a more advanced solution with
                # inspect (see also vars(), dir())
                # or even use pickle
                node.__dict__.copy()
            )

        return snapshot
            
    def _layout_tree(self):
        """Layout a binary tree, i.e. calculate the position of each node in
        the viewport.

        Returns:
            dict: node -> width x height
        """
        pos = {}

        if self.tree.root:
            w = self.width - 2 * (self.border + self.node_radius)
            h = self.height - 2 * (self.border + self.node_radius)

            d = self.tree.height()
            y_0 = self.border + self.node_radius
            x_0 = self.border + self.node_radius + w/2
            # TODO do we have to use integer division to get int coordinates?
            dy = h/d if d != 0 else 0

            pos[self.tree.root] = (x_0, y_0)
            
            def f(node, depth, parent_pos):
                if node:
                    y = y_0 + depth*dy
                    if node == node.parent.left:
                        x = parent_pos[0] - (w/2)/(2**depth)
                    else:
                        x = parent_pos[0] + (w/2)/(2**depth)
                    pos[node] = (x,y)
                    f(node.left, depth+1, (x,y))
                    f(node.right, depth+1, (x,y))

            f(self.tree.root.left, 1, (x_0, y_0))
            f(self.tree.root.right, 1, (x_0, y_0))
        return pos


    # TODO handle close event:
    #  - exit script or
    #  - reopen on next view()
    def view(self, **kwargs):
        snapshot = self._create_snapshot()
        snapshot['info'] = kwargs
        self.snapshots.append(snapshot)
        
        # display the new snapshot and enter the event loop
        #start = time.time()
        self._view(len(self.snapshots) - 1)
        self._pause_until_continue()
        #duration = time.time() - start
        #if wait:
        #    self._pause_until_continue()
        #elif pause > duration:
        #    time.sleep(pause - duration)

    def _view(self, new_snapshot_index):
        if new_snapshot_index == self.current_snapshot_index \
            or new_snapshot_index < 0 \
            or new_snapshot_index >= len(self.snapshots):
            return

        old_snapshot = self.snapshots[self.current_snapshot_index]
        new_snapshot = self.snapshots[new_snapshot_index]
        self.current_snapshot_index = new_snapshot_index

        node_colors = {}
        node_label_colors = {}

        for node, (pos, attr) in new_snapshot['nodes'].items():
            try:
                node_colors[node] = attr['color']
                node_label_colors[node] = 'white'
            except AttributeError as e:
                node_colors[node] = 'white'
                node_label_colors[node] = 'black'
        
        def currentPos(node, f):
            # interpolate between old and new pos of a node in new_snapshot
            # where f is in [0..1]
            nx, ny = new_snapshot['nodes'][node][0]
            if node in old_snapshot['nodes']:
                ox, oy = old_snapshot['nodes'][node][0]
            else:
                ox, oy = nx, ny

            return (nx*f + ox*(1-f), ny*f + oy*(1-f))

        def draw_edges(f=1):
            for node in new_snapshot['nodes']:
                if node != new_snapshot['root']:
                    # has parent
                    # TODO for some trees arrows are required
                    self.canvas.create_line(currentPos(node, f), 
                        currentPos(new_snapshot['nodes'][node][1]['parent'], f))

        def draw_nodes(f=1):
            for node in new_snapshot['nodes']:
                (x,y) = currentPos(node, f)
                self.canvas.create_oval(    # node outline: circle
                    x - self.node_radius, y - self.node_radius, 
                    x + self.node_radius, y + self.node_radius,
                    fill=node_colors[node])
                self.canvas.create_text(    # node label: key
                    x, y,
                    text=str(node.key),
                    fill=node_label_colors[node],
                    font=self.font)
                # additional info next to node
                info = "\n".join(
                    "{}: {}".format(a, str(getattr(node, a))) 
                        for a in self.node_attributes
                    )
                self.canvas.create_text(    
                    x + 2*self.node_radius, y,
                    text=info,
                    fill="black",
                    font=self.font,
                    anchor=tkinter.W)

        if self.animation:
            anim_duration = 0.5
            FPS = 30
            total_frames = int(max(anim_duration * FPS, 1))
            start = time.time()
        
            for frame in range(1, total_frames+1):
                f = frame/total_frames

                # TODO use self.canvas.move(item, dx, dy)
                self.canvas.delete(tkinter.ALL)

                draw_edges(f)   # render edges below nodes
                draw_nodes(f)

                self.canvas.update()

                time_to_pause = max(0, anim_duration*f - (time.time() - start))
                time.sleep(time_to_pause)
 
        else:
            self.canvas.delete(tkinter.ALL)

            draw_edges()
            draw_nodes()

            self.canvas.update()

    def _pause_until_continue(self):
        """A simple event loop."""
        self.end_pause = False
        while not self.end_pause:
            self.window.update()
            time.sleep(0.05)

    def display_after(self, f):
        # TODO modify class
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)
            self.display()
            return res


if __name__ == '__main__':
    from rb import RBTree

    t = RBTree()
    tv = TreeView(t, node_attributes=['bh'],
        width=1300, height=600, node_radius=8, font_size=8, animation=True)

    import random
    random.seed(0)

    # universe = list(range(50))
    # random.shuffle(universe)
    # for i in universe:
    #     t.insert(i)
    #     # tv.view(pause=0.5)
    #     tv.view()
    
    universe = list(range(20))
    random.shuffle(universe)
    for i in universe:
        t.insert(i)
        tv.view()

    #t.split(6)
    #tv.view()
