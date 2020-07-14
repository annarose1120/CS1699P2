#represents a relationship between two people(nodes)
#relationship goes from left to right (subject to object)
#Ex. if the relationship is parent, left is the parent of right
class Edge:
  def __init__(self, id, node1, node2):
    self.relationshipIdentifier = id
    self.left = node1
    self.right = node2

#represents a person
class Node:
  def __init__(self, name):
    self.name = name

#represents a social network represented as a graph
#graph is stored as a mapping of nodes to a list of edges
class Graph:
    def __init__(self):
        self.graph = {}

    #prints the status of the graph
    def printGraph(self):
        for key in self.graph:
            print("{}|\t".format(key.name), end = "")
            for edge in self.graph[key]:
                print("({}, {}, {})".format(edge.relationshipIdentifier, edge.left.name, edge.right.name), end = "")
            print("\n")

    #add a new edge to the graph
    #indicates that node1 is has relationship <relationshipIdentifier> with node2
    #and node2 has relationship -<relationshipIdentifier> with node1
    def addEdge(self, relationshipIdentifier, node1, node2):
        #update node 1's edge list
        if node1 in self.graph:
            edges = self.graph[node1]
        else:
            edges = []
        edges.append(Edge(relationshipIdentifier, node1, node2))
        self.graph[node1] = edges

        #update node2's edge list
        if node2 in self.graph:
            edges = self.graph[node2]
        else:
            edges = []
        edges.append(Edge(relationshipIdentifier, node1, node2))
        self.graph[node2] = edges

    #tests whether source is connected with destination using sequence of relationships in edgeTypes
    # e.g. if edgeTypes holds ['parent', 'sibling'], tests if destination is source's parent's sibling
    def hasRelationship(self, edgeTypes, source, destination):
        if type(source) is not Node or type(destination) is not Node:
            raise TypeError("hasRelationship method in class Graph must be passed Node objects for source and destination")

        #if neither source nor destination is connected to any other nodes (e.g. no relationships), return early
        if source not in self.graph:
            return False
        if destination not in self.graph:
            return False

        for edge in self.graph[source]:
            #see if edge connects source with another node with relationship edgeTypes[0]
            if edgeTypes[0].find("-") != -1:
                #if relationship in edgeTypes[0] has a preceding -, relationship must go from source to another node
                if edgeTypes[0][1:] == edge.relationshipIdentifier and edge.left.name == source.name:
                    #if we are on the last edge in the list, check if destination node matches
                    if len(edgeTypes) == 1:
                        if(edge.right.name == destination.name):
                            return True
                    else:
                        #recursion- we have connected source with one node, try to connect next node
                        result = self.hasRelationship(edgeTypes[1:], edge.right, destination)
                        if result:
                            return result
            else:
                #if no preceding - in edgeTypes[0], relationship must go from another node to source
                if edgeTypes[0] == edge.relationshipIdentifier and edge.right.name == source.name:
                    #if we are on the last edge in the list, check if destination node matches
                    if len(edgeTypes) == 1:
                        if(edge.left.name == destination.name):
                            return True
                    else:
                        #recursion- we have connected source with one node, try to connect next node
                        result = self.hasRelationship(edgeTypes[1:], edge.left, destination)
                        if result:
                            return result
        return False
