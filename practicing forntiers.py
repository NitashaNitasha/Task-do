
'''
• Start with a frontier that contains the initial state.

• Start with an empty explored set.

repeat :
    1.	If the frontier is empty,
        o	Stop. There is no solution to the problem.
    2.	Remove a node from the frontier. This is the node that will be considered.
    3.	If the node contains the goal state,
        o	Return the solution. Stop.
        Else,
            * Expand the node (find all the new nodes that could be reached from this node), and add resulting nodes to the frontier.
            * Add the current node to the explored set.
'''

class Node():
    def __int__(self , state, parent, action, cost=None):
        self.state = state
        self.parent = parent
        self.action = action
        # self.cost = cost


class SimpleFrontier:
    '''
    functions related to a frontier entity
    '''
    def __init__(self):
        self.Frontier = []
    def add(self,node):
        self.Frontier.append(node)
    def contains_state(self,state):
        return any(node.state==state for node in self.Frontier)
    def empty(self):
        return self.Frontier==[]

class StackFrontier(SimpleFrontier):
    '''
    last element removed for a DFS approach
    '''
    def remove(self,node):
        if(self.empty()):raise Exception('Empty Frontier')
        else:
            node=self.Frontier[-1]
            self.Frontier=self.Frontier[:-1]
            return node


class QueueFrontier(StackFrontier):
    '''
    first element removed for a BFS approach
    '''
    def remove(self,node):
        if(self.empty()):raise Exception('Empty Frontier')
        else:
            node=self.Frontier[0]
            self.Frontier=self.Frontier[1:]
            return node

class Maze():
    def __init__(self,initial_state,h,w):
        # with open(filename) as f:
        #     content=f.read()
        # if 'p' not in content:
        #     raise Exception('No Starting position')
        # if 'm' not in content:
        #     raise Exception('No Starting position')
        self.height = h
        self.width = w

    def Solve(self):
        self.explored()