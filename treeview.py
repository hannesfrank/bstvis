from tkinter import Tk, Button, Canvas, ALL
import time
import functools

class Displayable(object):
    """Inherit from this to get a method to manually display the datastructure."""
    def __init__(self):
        super().__init__()
        self._viewer = None

    def display(*args, **kwargs):
        if self._viewer:
            self._viewer.display(*args, **kwargs)

class TreeView:
    """Viewer for a Binary Trees."""
    def __init__(self,
        tree, 
        width=800, 
        height=600, 
        node_radius=15,
        font_size=12,
        animation=True):

        self.tree = tree

        self.width = width
        self.height = height
        self.node_radius = node_radius
        self.font = ('Verdana', font_size)
        
        # the old positions for animation
        self.animation = animation
        if animation:
            self.old_node_pos = self._node_positions()    
        self.endPause = False

        # TODO implement animation with canvas.move() for performance?
        # store tk-index for each node
        # self.node_items = {}    

        self.window = Tk()
        self.canvas = Canvas(self.window, width=width, height=height)
        self.canvas.pack()

        self.continue_button = Button(self.window, text="Continue", 
            command=self._continue_callback)
        self.continue_button.pack()


    # TODO handle close event:
    #  - exit script or
    #  - reopen on next display()
    def display(self, pause=0):
        if self.animation:
            wait = pause == 0
            # pause = max(pause, 0.2)
            # anim_duration = min(pause, 0.5)
            anim_duration = max(0.2, min(pause, 0.5))
            FPS = 30
            total_frames = int(max(anim_duration * FPS, 1))

            node_pos = self._node_positions()
            color = {}
            font_color = {}

            for node in node_pos:
                try:
                    color[node] = node.color
                    font_color[node] = 'white'
                except AttributeError as e:
                    color[node] = 'white'
                    font_color[node] = 'black'

            def currentPos(node, f):
                # interpolate between old_coords and coords
                (x, y) = node_pos[node]         
                (ox, oy) = self.old_node_pos.get(node, (x,y))
                return (x*f + ox*(1-f), y*f + oy*(1-f))

            start = time.time()
            for frame in range(1, total_frames+1):
                # TODO use self.canvas.move(item, dx, dy)
                self.canvas.delete(ALL)
    
                fstart = time.time()
                f = frame/total_frames

                # draw edges
                for node in node_pos:
                    if node != self.tree.root:
                        # has parent
                        self.canvas.create_line(currentPos(node, f), 
                            currentPos(node.parent, f))

                # draw nodes
                for node in node_pos:
                    (x,y) = currentPos(node, f)
                    self.canvas.create_oval(
                        x - self.node_radius, y - self.node_radius, 
                        x + self.node_radius, y + self.node_radius,
                        fill=color[node])
                    self.canvas.create_text(
                        x, y,
                        text=str(node.key),
                        fill=font_color[node],
                        font=self.font)
                    self.canvas.create_text(
                        x + 2*self.node_radius, y,
                        text=str(node.bh),
                        fill="black",
                        font=self.font)

                self.canvas.update()
                time_to_pause = max(0, anim_duration*frame/total_frames - (time.time() - start))
                time.sleep(time_to_pause)

            duration = time.time() - start
            if wait:
                self._pause_until_continue()
            elif pause > duration:
                time.sleep(pause - duration)

            self.old_node_pos = node_pos
 
        else:
            node_pos = self._node_positions()

            self.canvas.delete(ALL)

            # draw edges
            for node in node_pos:
                if node != self.tree.root:
                    # has parent
                    self.canvas.create_line(node_pos[node], node_pos[node.parent])

            # draw nodes
            for node, (x,y) in node_pos.items():
                try:
                    color = node.color
                    font_color = 'white'
                except AttributeError as e:
                    color = 'white'
                    font_color = 'black'

                self.canvas.create_oval(
                    x - self.node_radius, y - self.node_radius, 
                    x + self.node_radius, y + self.node_radius,
                    fill=color)
                self.canvas.create_text(
                    x, y,
                    text=str(node.key),
                    fill=font_color,
                    font=self.font)
                self.canvas.create_text(
                    x + 2*self.node_radius, y,
                    text=str(node.bh),
                    fill="black",
                    font=self.font)

            self.canvas.update()
            if pause == 0:
                self._pause_until_continue()
            else:
                time.sleep(pause)


    def _continue_callback(self):
        self.endPause = True

    def _pause_until_continue(self):
        self.endPause = False
        while not self.endPause:
            self.window.update()
            time.sleep(0.05)

 
    def _node_positions(self):
        """
        returns a dict: node -> width x height
        """
        pos = {}

        if self.tree.root:
            border = 20
            w = self.width - 2 * (border + self.node_radius)
            h = self.height - 2 * (border + self.node_radius)

            d = self.tree.height()
            y_0 = border + self.node_radius

            # TODO handle d == 0
            if d == 0:
                dy = 0
            else:
                dy = h/d        # TODO h//d
            x_0 = border + self.node_radius + w/2       # TODO h//2 ??

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
    tv = TreeView(t, width=1300, height=600, node_radius=8, font_size=8, animation=True)

    import random
    random.seed(0)

    # universe = list(range(50))
    # random.shuffle(universe)
    # for i in universe:
    #     t.insert(i)
    #     # tv.display(pause=0.5)
    #     tv.display()
    
    universe = list(range(20))
    random.shuffle(universe)
    for i in universe:
        t.insert(i)
        # tv.display()

    t.split(6, tv=tv)
    tv.display()
