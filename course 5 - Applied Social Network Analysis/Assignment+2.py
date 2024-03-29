
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.2** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-social-network-analysis/resources/yPcBs) course resource._
# 
# ---

# # Assignment 2 - Network Connectivity
# 
# In this assignment you will go through the process of importing and analyzing an internal email communication network between employees of a mid-sized manufacturing company. 
# Each node represents an employee and each directed edge between two nodes represents an individual email. The left node represents the sender and the right node represents the recipient.

# In[1]:


import networkx as nx

# This line must be commented out when submitting to the autograder
#!head email_network.txt


# ### Question 1
# 
# Using networkx, load up the directed multigraph from `email_network.txt`. Make sure the node names are strings.
# 
# *This function should return a directed multigraph networkx graph.*

# In[2]:


email_network = nx.read_edgelist('email_network.txt', delimiter='\t', create_using=nx.MultiDiGraph(), data=(('time',int),))
def answer_one():
    # Your Code Here
    return email_network


# ### Question 2
# 
# How many employees and emails are represented in the graph from Question 1?
# 
# *This function should return a tuple (#employees, #emails).*

# In[3]:


def answer_two():
        
    # Your Code Here    
    return (len(email_network.nodes()), len(email_network.edges()))

answer_two()


# ### Question 3
# 
# * Part 1. Assume that information in this company can only be exchanged through email.
# 
#     When an employee sends an email to another employee, a communication channel has been created, allowing the sender to provide information to the receiver, but not vice versa. 
# 
#     Based on the emails sent in the data, is it possible for information to go from every employee to every other employee?
# 
# 
# * Part 2. Now assume that a communication channel established by an email allows information to be exchanged both ways. 
# 
#     Based on the emails sent in the data, is it possible for information to go from every employee to every other employee?
# 
# 
# *This function should return a tuple of bools (part1, part2).*

# In[4]:


def answer_three():
        
    # Your Code Here
    ans1 = len(list(nx.strongly_connected_components(email_network))) == 1
    ans2 = len(list(nx.weakly_connected_components(email_network))) == 1
    return (ans1, ans2)

answer_three()


# ### Question 4
# 
# How many nodes are in the largest (in terms of nodes) weakly connected component?
# 
# *This function should return an int.*

# In[5]:


def answer_four():
    # Your Code Here
    return max([len(nl) for nl in nx.weakly_connected_components(email_network)])

answer_four()


# ### Question 5
# 
# How many nodes are in the largest (in terms of nodes) strongly connected component?
# 
# *This function should return an int*

# In[6]:


def answer_five():
        
    # Your Code Here
    return max([len(nl) for nl in nx.strongly_connected_components(email_network)])

answer_five()


# ### Question 6
# 
# Using the NetworkX function strongly_connected_component_subgraphs, find the subgraph of nodes in a largest strongly connected component. 
# Call this graph G_sc.
# 
# *This function should return a networkx MultiDiGraph named G_sc.*

# In[7]:


def answer_six():
    # Your Code Here
    sgs = [(len(sg.nodes()),sg) for sg in nx.strongly_connected_component_subgraphs(email_network)]
    G_sc = max(sgs, key= lambda t: t[0])[1]
    return G_sc

answer_six()


# ### Question 7
# 
# What is the average distance between nodes in G_sc?
# 
# *This function should return a float.*

# In[8]:


G_sc = answer_six()

def answer_seven():
        
    # Your Code Here
    #total_len = 0
    #total_paths = 0
    #for source, targets in nx.all_pairs_shortest_path(G_sc).items():
    #    for target, path in targets.items():
    #        total_len += len(path)-1
    #        total_paths += 1
    #return total_len / total_paths
        
    return nx.average_shortest_path_length(G_sc)

answer_seven()


# ### Question 8
# 
# What is the largest possible distance between two employees in G_sc?
# 
# *This function should return an int.*

# In[9]:


def answer_eight():
    # Your Code Here
    eccs = nx.eccentricity(G_sc)
    return max(eccs.values())

answer_eight()


# ### Question 9
# 
# What is the set of nodes in G_sc with eccentricity equal to the diameter?
# 
# *This function should return a set of the node(s).*

# In[10]:


def answer_nine():
       
    # Your Code Here
    eccs = nx.eccentricity(G_sc)
    diameter = nx.diameter(G_sc, e=eccs)
    
    nodes = set()
    for node, ecc in eccs.items():
        if ecc == diameter:
            nodes.add(node)
    return nodes

answer_nine()


# ### Question 10
# 
# What is the set of node(s) in G_sc with eccentricity equal to the radius?
# 
# *This function should return a set of the node(s).*

# In[11]:


def answer_ten():
        
    # Your Code Here
    eccs = nx.eccentricity(G_sc)
    radius = nx.radius(G_sc, e=eccs)
    
    nodes = set()
    for node, ecc in eccs.items():
        if ecc == radius:
            nodes.add(node)
    return nodes

answer_ten()


# ### Question 11
# 
# Which node in G_sc is connected to the most other nodes by a shortest path of length equal to the diameter of G_sc?
# 
# How many nodes are connected to this node?
# 
# 
# *This function should return a tuple (name of node, number of satisfied connected nodes).*

# In[12]:


def answer_eleven():
        
    import collections
    
    # Your Code Here
    eccs = nx.eccentricity(G_sc)
    diameter = nx.diameter(G_sc, e=eccs)
    
    node_paths = collections.defaultdict(int)

    for source, targets in nx.all_pairs_shortest_path(G_sc).items():
        for target, path in targets.items():
            if len(path)-1 == diameter:
                node_paths[source] += 1

    
    return max(list(node_paths.items()), key=lambda t: t[1])

answer_eleven()


# ### Question 12
# 
# Suppose you want to prevent communication from flowing to the node that you found in the previous question from any node in the center of G_sc, what is the smallest number of nodes you would need to remove from the graph (you're not allowed to remove the node from the previous question or the center nodes)? 
# 
# *This function should return an integer.*

# In[18]:


def answer_twelve():
        
    # Your Code Here
    previous_node = '97'
    centers = nx.center(G_sc)
    
    return nx.node_connectivity(G_sc, s=centers[0], t=previous_node)-2

answer_twelve()


# ### Question 13
# 
# Construct an undirected graph G_un using G_sc (you can ignore the attributes).
# 
# *This function should return a networkx Graph.*

# In[14]:


def answer_thirteen():
    # Your Code Here
    return nx.Graph( G_sc.to_undirected() )

answer_thirteen()


# ### Question 14
# 
# What is the transitivity and average clustering coefficient of graph G_un?
# 
# *This function should return a tuple (transitivity, avg clustering).*

# In[15]:


def answer_fourteen():
        
    # Your Code Here
    G_un = answer_thirteen()
    
    return (nx.transitivity(G_un), nx.average_clustering(G_un))

answer_fourteen()


# In[ ]:




