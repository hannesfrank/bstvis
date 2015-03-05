import tkinter
from tkinter import Tk, Button, Canvas
from tkinter.constants import YES, BOTH
import time
import functools
import types
from enum import Enum
from viewer.treelayout import SpaceEfficientBinaryTreeLayout
import sys


class NodeShape(Enum):
    circle = 1
    square = 2


class Viewable(object):

    """
    Inherit from this to get a method to manually view the datastructure.
    """

    def __init__(self):
        super().__init__()
        self._viewer = None

    def view(self, *args, **kwargs):
        if self._viewer:
            self._viewer.view(*args, **kwargs)


class TreeView(object):

    """Viewer for a Binary Trees.

    If your binary tree is a subclass of Viewable you can use
    self.view(**kwargs) to manually invocate a view inside the tree class.

    Note:
        A node must always represent the same key-data-pair and should not
        overwrite default __hash__ to be usable as a dictionary key.
        TODO we could add a uid to each node to identify it.

    Args:
        tree (tree.BinaryTree): A reference to the tree to be viewed.
        node_attributes (list, optional): fields of a Node as string which
            should be viewed next to the node, default [].
        # TODO view_after redesign
        view_after (list of string, optional): the name of all functions of the
            class of t that should invoke view(..) after execution,
            default [].
        width (int, optional): tk-viewport width in px, default 800.
        height (int, optional): tk-viewport height in px, default 600.
        node_radius (int, optional): radius of the nodes of the tree in px,
            default 15.
        node_shape (NodeShape, optional): a function (node) -> NodeShape
            mapping a node to it desired shape, default all circles.
        font_size (int, optional): font_size of node labels in pt, default 12.
        animation (bool, optional): animate between tree snapshots,
            default True.

    Example:
        create a binary search tree
        >>> t = RBTree()

        set up the viewer
        >>> v = TreeView(t, node_attributes=['bh'],
        # TODO view_after redesign
        ...       view_after=['insert', 'delete'])

        execute your algorithm
        >>> t.insert(4)     # invokes view(method='insert(4)')
        >>> t.insert(2)

        and view at special states
        >>> v.view(highlight_nodes=[t.root])    # highlight the root
    """

    def __init__(self, tree,
                 node_attributes=None,
                 view_after=None,
                 width=800, height=600,
                 node_radius=15, node_shape=None,
                 font_size=12,
                 layout_algorithm=None,
                 animation=True):

        self.tree = tree
        self.node_attribute_names = node_attributes if node_attributes else []

        self.width = width
        self.height = height
        self.border = 20
        self.node_radius = node_radius
        if node_shape is not None:
            self.node_shape = node_shape
        else:
            self.node_shape = lambda n: NodeShape.circle

        self.font = ('Verdana', font_size)
        self.small_font = ('Verdana', font_size//2)

        if layout_algorithm is not None:
            self.layout_algorithm = layout_algorithm
        else:
            self.layout_algorithm = SpaceEfficientBinaryTreeLayout

        self.animation = animation
        self.end_pause = False   # controls the display loop
        self.redraw = False      # set to True if redraw is needed
        # TODO cleanly implement pause (continue after delay not button press)
        # TODO implement animation with canvas.move() for performance?
        #   store tk-index for each node

        self._createGUI()
        # Set to True if you want to exit the application via sys.exit(0)
        self.exit = False

        # Each display() creates a snapshot of the tree.
        # A snapshot is a dict with the following data:
        #   - 'nodes': {node: ((x,y), node.__dict__) for all nodes}
        #   - 'root': tree.root
        #   - 'info': the kwargs passed to view(..), e.g. the current method of
        #       the alg
        # The display position of the nodes is saved for animation.
        # TODO do we need an initial snapshot?
        self.snapshots = [self._create_snapshot()]
        self.current_snapshot_index = 0
        # TODO (low priority) do incremental versions :)

        # provide self.view(**kwargs)
        if isinstance(tree, Viewable):
            tree._viewer = self
        # and wrap methods to invoke view
        if view_after is not None:
            self._view_after(view_after)

    def _createGUI(self):
        # main window
        self.window = Tk()
        self.window.bind('<Configure>', self._resize_callback)
        self.canvas = Canvas(self.window, width=self.width, height=self.height,
                             highlightthickness=0)
        self.canvas.pack(expand=YES, fill=BOTH)

        # controls
        self.continue_button = Button(
            self.window, text="Continue", underline=0,
            command=self._continue_callback)
        self.continue_button.pack(side='left')

        # TODO enable/disable buttons
        self.previous_button = Button(
            self.window, text="Prev", underline=0,
            command=self._previous_callback)
        self.previous_button.pack(side='left')

        self.next_button = Button(
            self.window, text="Next", underline=0,
            command=self._next_callback)
        self.next_button.pack(side='left')

        # global shortcuts
        self.window.bind('<Escape>', self._close_callback)
        self.window.bind('<c>', lambda e: self.continue_button.invoke())
        self.window.bind('<p>', lambda e: self.previous_button.invoke())
        self.window.bind('<n>', lambda e: self.next_button.invoke())

    def _continue_callback(self, event=None):
        self.end_pause = True   # exit the event loop

    def _previous_callback(self, event=None):
        self._view(self.current_snapshot_index - 1)

    def _next_callback(self, event=None):
        self._view(self.current_snapshot_index + 1)

    def _close_callback(self, event=None):
        self.window.destroy()      # TODO or use destroy() (quit kills tcl)
        self.exit = True

    def _resize_callback(self, event):
        if self.width != self.canvas.winfo_width():
            self.width = self.canvas.winfo_width()
            self.redraw = True
        if self.height != self.canvas.winfo_height():
            self.height = self.canvas.winfo_height()
            self.redraw = True

    def _create_snapshot(self):
        snapshot = {
            'nodes': {},
            'root': self.tree.root,
            'width': self.width,        # canvas dimensions for scaling
            'height': self.height,
            'info': {}
        }

        # calculate the position in viewport
        pos = self.layout_algorithm(self.width, self.height).layout(self.tree)

        for node, position in pos.items():
            # save other attributes
            snapshot['nodes'][node] = (
                position,
                # TODO is using __dict__ save
                # or is a more advanced solution necessary? e.g.
                #   inspect (see also vars(), dir())
                #   or even use pickle
                node.__dict__.copy(),
                [getattr(node, name) for name in self.node_attribute_names],
                self.node_shape(node)
            )

        return snapshot

    # TODO handle close event:
    #  - exit script or
    #  - reopen on next view()
    def view(self, **kwargs):
        """View the current state of the tree and save it to the history.

        Kwargs:
            highlight (iterable of Node): some nodes to be highlighted.
        """
        snapshot = self._create_snapshot()
        snapshot['info'] = kwargs
        self.snapshots.append(snapshot)

        # display the new snapshot and enter the event loop
        # start = time.time()
        self._view(len(self.snapshots) - 1)
        self._pause_until_continue()
        # duration = time.time() - start
        # if wait:
        #    self._pause_until_continue()
        # elif pause > duration:
        #    time.sleep(pause - duration)

    def _view(self, new_snapshot_index=None):
        if new_snapshot_index is None:
            # redraw
            new_snapshot_index = self.current_snapshot_index
            pass
        elif new_snapshot_index == self.current_snapshot_index \
                or new_snapshot_index < 0 \
                or new_snapshot_index >= len(self.snapshots):
            # nothing new
            return

        old_snapshot = self.snapshots[self.current_snapshot_index]
        new_snapshot = self.snapshots[new_snapshot_index]
        self.current_snapshot_index = new_snapshot_index

        node_colors = {}
        node_label_colors = {}
        node_attributes = {}

        for node, (pos, node_dict, attr, shape) \
                in new_snapshot['nodes'].items():

            node_attributes[node] = attr
            try:
                node_colors[node] = node_dict['color']
                node_label_colors[node] = 'white'
            except KeyError:
                node_colors[node] = 'white'
                node_label_colors[node] = 'black'

        def currentPos(node, f):
            # interpolate between old and new pos of a node in new_snapshot
            # where f is in [0..1]
            nx, ny = new_snapshot['nodes'][node][0]
            # scale to window dimensions
            nx *= self.width/new_snapshot['width']
            ny *= self.height/new_snapshot['height']

            if node in old_snapshot['nodes']:
                ox, oy = old_snapshot['nodes'][node][0]
                ox *= self.width/old_snapshot['width']
                oy *= self.height/old_snapshot['height']
            else:
                ox, oy = nx, ny

            return (nx*f + ox*(1-f), ny*f + oy*(1-f))

        def draw(f=1):
            self.canvas.delete(tkinter.ALL)
            # TODO use self.canvas.move(item, dx, dy)

            # edges
            for node in new_snapshot['nodes']:
                if node != new_snapshot['root']:
                    # has parent
                    # TODO for some trees arrows are required
                    # TODO refactor tango fix
                    if 'is_root' in new_snapshot['nodes'][node][1]:
                        # tango tree quick fix:
                        # highlight preferred paths
                        if new_snapshot['nodes'][node][1]['is_root']:
                            color = 'green'
                            width = 1.0
                            dash = (4, 4)
                        else:
                            color = 'blue'
                            width = 2.0
                            dash = None

                        self.canvas.create_line(
                            currentPos(node, f),
                            currentPos(
                                new_snapshot['nodes'][node][1]['parent'],
                                f),
                            fill=color,
                            width=width,
                            dash=dash
                        )
                    else:
                        # other trees
                        self.canvas.create_line(
                            currentPos(node, f),
                            currentPos(
                                new_snapshot['nodes'][node][1]['parent'], f)
                            )

            # nodes
            for node in new_snapshot['nodes']:
                (x, y) = currentPos(node, f)
                r = self.node_radius
                shape = new_snapshot['nodes'][node][3]

                if shape is NodeShape.circle:
                    self.canvas.create_oval(    # node outline: circle
                        x - r, y - r, x + r, y + r,
                        fill=node_colors[node])
                elif shape is NodeShape.square:
                    self.canvas.create_rectangle(    # node outline: circle
                        x - r, y - r, x + r, y + r,
                        fill=node_colors[node])
                self.canvas.create_text(    # node label: key
                    x, y,
                    text=str(node.key),
                    fill=node_label_colors[node],
                    font=self.font)

                # additional info next to node
                info_space = 5  # TODO setting
                info = "\n".join(
                    "{}: {}".format(name, str(value))
                        for name, value in zip(
                            self.node_attribute_names, node_attributes[node])
                    )

                self.canvas.create_text(
                    x + self.node_radius + info_space, y,
                    text=info,
                    fill="black",
                    font=self.small_font,
                    anchor=tkinter.W)

            # additional info
            # highlight node
            highlight_nodes = new_snapshot['info'].get('highlight_nodes', [])
            arrow_length = 2*self.node_radius   # TODO setting
            for node in highlight_nodes:
                if node in new_snapshot['nodes']:
                    x, y = currentPos(node, f)
                    self.canvas.create_line(    # a arrow to the node
                        x - self.node_radius - arrow_length, y,
                        x - self.node_radius, y,
                        arrow='last',
                        width=2)

            self.canvas.update()

        if self.animation:
            anim_duration = 0.1
            FPS = 30
            total_frames = int(max(anim_duration * FPS, 1))
            start = time.time()

            for frame in range(1, total_frames+1):
                f = frame/total_frames
                draw(f)
                time_to_pause = max(0, anim_duration*f - (time.time() - start))
                time.sleep(time_to_pause)

        else:
            draw()

    def _pause_until_continue(self):
        """A simple event loop."""
        self.end_pause = False
        while not self.end_pause:
            if self.exit:
                sys.exit(0)

            self.window.update()
            time.sleep(0.05)
            if self.redraw:
                self._view()
                self.redraw = False

    # TODO view_after redesign
    def _view_after(self, f):
        """Wrap a function f (of a class) to automatically invoke
        self.view(method=f.__name__) after execution.
        """
        # TODO view_after redesign
        # TODO split drawing and observation in different classes
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)
            self.view(method=f.__name__)
            return res
        wrapper = types.MethodType(wrapper, self.t)
        return wrapper


if __name__ == '__main__':
    from tree.rb import RBTree

    t = RBTree()
    tv = TreeView(t, node_attributes=['bh'],
                  width=1300, height=600, node_radius=8, font_size=8,
                  animation=True)

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
        tv.view(highlight_nodes=[t.root])

    # t.split(6)
    # tv.view()
