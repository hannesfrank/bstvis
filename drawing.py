# Modification of Tyler Sanderson <tylerbtbam@gmail.com> PyBST
# GNU General Public License

import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab
import networkx as nx
from collections import deque
from io import StringIO
import time

matplotlib_colors = {
    'red': 'r',
    'black': 'k',
    'white': 'w'
}

class TreeView():
    """
    Display a Binary Tree using matplotlib.

    Simply create a instance from a tree, modify the tree and call display.
    """
    def __init__(self, tree, animation=False):
        self.tree = tree
        
        # plt.ion()
        self.old_coords = None
        self.figure = plt.figure()
        self.animation = animation
    
    def _plot(self):
        """
        to be overwritten
        """
        plot_tree(self.tree)

    def display(self, pause=0):
        plt.axis('off')

        # simple plotting
        # plt.clf()
        # self._plot()
        # plt.draw()
        # plt.pause(pause)

        # animation approach
        if not self.animation:
            plt.clf()
            self._plot()
            plt.xlim([-2,2])
            plt.ylim([-7,1])
            plt.draw()
            if pause > 0:
                plt.pause(pause)
            else:
                plt.show()
        else:
            # TODO animation only works if keys are distinct
            G = nx.Graph()

            nodes = _get_node_list(self.tree)
            edges = _get_edge_list(self.tree)

            labels = {i:str(node.key) for i, (x, y, node) in enumerate(nodes)}

            colors = []
            font_colors = []
            for node in nodes:
                try:
                    colors.append(matplotlib_colors[node[2].color])
                    font_colors.append(matplotlib_colors['white'])
                except AttributeError as e:
                    colors.append(matplotlib_colors['white'])
                    font_colors.append(matplotlib_colors['black'])
            font_colors.append('k') # hotfix in case of 0 nodes

            G.add_edges_from(edges)
            G.add_nodes_from(range(len(nodes)))

            # interpolate between old_coords and coords
            # TODO http://ankurankan.github.io/blog/2013/10/11/plotting-and-animating-networkx-graphs/
            if not self.old_coords:
                coords = [(x,y) for x, y, node in nodes]
                plt.clf()
                nx.draw_networkx(G, pos=coords, labels=labels,
                    node_color=colors, font_color=font_colors[0])
                plt.xlim([-2,2])
                plt.ylim([-7,1])
                plt.draw()
                if pause > 0:
                    plt.pause(pause)
                else:
                    plt.show()
            else:
                pause = max(pause, 0.01)
                anim_duration = min(pause, 0.5)
                FPS = 20
                total_frames = int(max(anim_duration * FPS, 1))

                start = time.time()
                for frame in range(1, total_frames+1):
                    fstart = time.time()
                    f = frame/total_frames

                    coords = []
                    for (x,y,node) in nodes:
                        (ox, oy) = self.old_coords.get(node, (x,y))
                        coords.append((x*f + ox*(1-f), y*f + oy*(1-f)))

                    plt.clf()
                    nx.draw_networkx(G, pos=coords, labels=labels,
                        node_color=colors, font_color=font_colors[0])
                    plt.xlim([-2,2])
                    plt.ylim([-7,1])
                    plt.draw()
                    # TODO check time_to_pause
                    # time_to_pause = max(0.001, anim_duration/total_frames - (time.time() - start))
                    # plt.pause(time_to_pause)

                duration = time.time() - start
                if pause > duration:
                    plt.pause(pause - duration)

            self.old_coords = {node: (x,y) for (x,y,node) in nodes}

    def test(self):
        axes = plt.gca()
        # print(axes.get_children())
        # search nodes
        for obj in axes.get_children():
            if isinstance(obj, mpl.collections.PathCollection):
                print(obj)



def _get_node_list(tree):
    """
    Returns list coordinates and labels for plotting in preorder. 

    Since pyplot or networkx don't have built in
    methods for plotting binary search trees, this somewhat
    choppy method has to be used.
    """

    plot_positions = []
    _get_node_list_from(tree, tree.root, plot_positions=plot_positions, parent_pos=None, gap=1.0)
    return plot_positions

def _get_node_list_from(tree, node, plot_positions, parent_pos, gap):
    """
    Fills plot_positions as list coordinates for plotting in preorder. 

    gap: horizontal distance from node and node's parent.
    To achieve plotting consistency each time we move down the tree
    we half this value.
    """

    # print(node.key if node else "NIL") 
    if node and node == tree.root:
        # TODO simplify/extract root
        plot_positions.append((0,0, node))
        _get_node_list_from(tree, node.left, plot_positions, (0,0), gap)
        _get_node_list_from(tree, node.right, plot_positions, (0,0), gap)
    elif node:
        if node == node.parent.right:
            coord = (parent_pos[0] + gap, parent_pos[1] - 1)
        elif node == node.parent.left:
            coord = (parent_pos[0] - gap, parent_pos[1] - 1)
        plot_positions.append(coord + (node,))

        _get_node_list_from(tree, node.left, plot_positions, coord, gap/2)
        _get_node_list_from(tree, node.right, plot_positions, coord, gap/2)
        

def _get_edge_list(tree):
    """
    Returns list of tuples representing the edges to be drawn.
    """
    return _get_edge_list_from(tree, tree.root, [])

def _get_edge_list_from(tree, node, edges):
    """
    Returns list of tuples representing the edges to be drawn,
    indexing the nodes in preorder.
    """

    if node:
        # the preorder index of a node is equal to the number of edges 
        # already in the list

        preorder_index = len(edges)  # preorder index of root

        if node.left:
            edges.append((preorder_index, preorder_index + 1))
            _get_edge_list_from(tree,node.left,edges)
        if node.right:
            index = len(edges)     # may changed due to left subtree
            edges.append((preorder_index, index + 1))
            _get_edge_list_from(tree,node.right,edges)

    return edges

def plot_tree(tree, figure=None):
    """
    Visualize tree using matplotlibs pyplot.
    """
    G = nx.Graph()

    nodes = _get_node_list(tree)
    edges = _get_edge_list(tree)

    coords = [(x,y) for x, y, node in nodes]
    labels = {i:str(node.key) for i, (x, y, node) in enumerate(nodes)}

    colors = []
    font_colors = []
    for node in nodes:
        try:
            colors.append(matplotlib_colors[node[2].color])
            font_colors.append(matplotlib_colors['white'])
        except AttributeError as e:
            colors.append(matplotlib_colors['white'])
            font_colors.append(matplotlib_colors['black'])
    font_colors.append('k') # hotfix in case of 0 nodes

    G.add_edges_from(edges)
    G.add_nodes_from(range(len(nodes)))

    plt.axis('off')

    # node_shape: one of so^>v<dph8
    # nx.draw_networkx_nodes(G, coords, node_size=400, node_color=colors)   
    # nx.draw_networkx_edges(G, coords)
    # nx.draw_networkx_labels(G, coords, labels, font_color='k')  # TODO color for each label
    nx.draw_networkx(
            G,              # networkx graph
            pos=coords,     # A dictionary (list?) with nodes as keys and positions as values. 
                            # If not specified a spring layout positioning will be computed. 
                            # See networkx.layout for functions that compute node positions.
            # with_labels,    # default=True
                            # Set to True to draw labels on the nodes.
            # ax=figure.axes,             # Matplotlib Axes object, optional
                            # Draw the graph in the specified Matplotlib axes.
            # nodelist=nodes,       # list, optional (default G.nodes())
                            # Draw only specified nodes
            # edgelist=edges,       # list, optional (default=G.edges())
                            # Draw only specified edges
            # node_size,      # scalar or array, optional (default=300)
                            # Size of nodes. If an array is specified it must be the same length 
                            # as nodelist.
            node_color=colors,     # color string, or array of floats, (default=’r’)
                            # Node color. Can be a single color format string, or a sequence of 
                            # colors with the same length as nodelist. If numeric values are 
                            # specified they will be mapped to colors using the cmap and 
                            # vmin, vmax parameters. See matplotlib.scatter for more details.
            # node_shape,     # string, optional (default=’o’)
                            # The shape of the node. Specification is as matplotlib.scatter 
                            # marker, one of ‘so^>v<dph8’.
            # alpha,          # float, optional (default=1.0)
                            # The node transparency
            # cmap,           # Matplotlib colormap, optional (default=None)
                            # Colormap for mapping intensities of nodes
            # vmin, vmax      # float, optional (default=None)
                            # Minimum and maximum for node colormap scaling
            # linewidths,     # [None | scalar | sequence]
                            # Line width of symbol border (default =1.0)
            # width,          # float, optional (default=1.0)
                            # Line width of edges
            # edge_color,     # color string, or array of floats (default=’r’)
                            # Edge color. Can be a single color format string, or a sequence 
                            # of colors with the same length as edgelist. If numeric values 
                            # are specified they will be mapped to colors using the edge_cmap 
                            # and edge_vmin,edge_vmax parameters.
            # edge_cmap,      # Matplotlib colormap, optional (default=None)
                            # Colormap for mapping intensities of edges
            # edge_vmin,      # dge_vmax : floats, optional (default=None)
                            # Minimum and maximum for edge colormap scaling
            # style,          # string, optional (default=’solid’)
                            # Edge line style (solid|dashed|dotted,dashdot)
            labels=labels,         # dictionary, optional (default=None)
                            # Node labels in a dictionary keyed by node of text labels
            # font_size,      # int, optional (default=12)
                            # Font size for text labels
            # TODO draw nodes separately
            font_color=font_colors[0],     # string, optional (default=’k’ black)
                            # Font color string
            # font_weight,    # string, optional (default=’normal’)
                            # Font weight
            # font_family,    # string, optional (default=’sans-serif’)
                            # Font family
            # label,          # string, optional
                            # Label for graph legend
            # hold=True
    )

    # plt.show()
def toGraph(node):
    g.add_node(node.key)
    if node.left: 
        toGraph(node.left)
        g.add_edge(node.key, node.left.key)
    if node.right: 
        toGraph(node.right)
        g.add_edge(node.key, node.right.key)

def pretty_print(tree):
    # http://leetcode.com/2010/09/how-to-pretty-print-binary-tree.html
    pass