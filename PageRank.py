import sys
import random
import networkx as nx
import numpy as np
import sys

# TEAM MEBMERS:
# - Bartosz Pliszka
# - Krzysztof Marcinkiewicz
# - Utku Yoztyurk





 #FIRST PART OF CODE did -  Utku Yoztyurk
 #opening file, defining variables in PageRank function and preparing it (before the loops)
 #and one of the matrix reduction to constant (S * x_k)
 #Also priting of the results
 


# first of all we set important variables 
# m is a teleportation probability
# and random seed for stability of results since random surfer is random
m = 0.15
random.seed(43)

# Then we open the file typed in a command line, read it with the networkx library and assign it to the variable graph
fh=open(sys.argv[1], 'rb')
graph = nx.read_adjlist(
    fh,
    create_using=nx.DiGraph(),
    comments='#',
    nodetype=int)
fh.close()

# Then we define our PageRank function
def PageRank(graph, m):
    '''
        INPUT : The function takes two inputs:
                 - graph - which is given graph with pages
                 - m - which is probability of teleporting.
        FUNCIONALITY: The function ranks the 'importance' of the pages in given graph based on a PageRank algorithm.
                      and prints top 10 pages along with their scores.
        OUTPUT: The function gives one output which is top 10 pages as a list
    '''

    # Firstly we take our graph and transofrm it into zero-based integer indices in order to use them with NumPy arrays as indices
    original_nodes = list(graph.nodes())
    node_map = {node: i for i, node in enumerate(original_nodes)}
    G = nx.relabel_nodes(graph, node_map)

    # Then we takes required for future atributes like number of nodes, reversed graph
    number_of_nodes = G.number_of_nodes()
    reversed_graph = G.reverse(copy=True)

    # We create a branching array and provide it number of links going out of every node
    branching = np.zeros(number_of_nodes, dtype=int)
    for i in range(number_of_nodes):
        branching[i] = G.out_degree(i)

    # With branching we can get all the nodes that dont have any links further
    dang_nodes = [i for i in range(number_of_nodes) if branching[i] == 0]

    # We put starting value for our ranking matrix and we divide the rank even between all nodes at start
    x_k = np.full(number_of_nodes, 1.0/number_of_nodes)

    # We set variables iterations and top_10_prev which we will use in the loop
    iterations = 0
    top_10_prev = []
    
    # just for better looking print output
    print('PAGE RANK SIMULATION')
    print('=========================')


 #SECOND PART OF CODE DID - Bartosz Pliszka
 #Doing outer and inner loops, reduction of (1-m) * D * x_k part and checking if the results are stabilized enough to end the loop.


#WE are starting the outerloop
    while True:

        # SO every time we iterate we count the iterations ( needed for output )
        iterations+=1
        # We set next ranking matrix as a empty ( we will fill it later )
        x_k_plus_1 = np.empty(number_of_nodes)

        # This is the (1-m) * D * x_k part
        # since its the same we can compute it once in the outer loop
        dang_sum = np.sum(x_k[dang_nodes])
        dang_contr = (1-m) * dang_sum / number_of_nodes

        # This is m * (S * x_k) part
        # because if we multiplike inside of the bracket and using fact that all x_k gives 1
        # we get that S*x_k = 1/n
        teleport_contr = m / number_of_nodes

        # now we start the inner loop
        for i in range(number_of_nodes):
            # we add our contributions from teleporting and dangling
            rank_i = teleport_contr
            rank_i += dang_contr
            link_contr = 0
            
            #here we start another loop to compute link contribution
            # as written in exercise we use reversed greaph to get all the backlinks
            for j in reversed_graph.successors(i):
                # for nodes with links ( so not dangling links )
                if branching[j] > 0:
                    # we get the rank of the item and divide it by number of links from that one ( splitted given rank)
                    link_contr += x_k[j] / branching[j]
            
            # we add this contribution
            rank_i += (1-m) * link_contr
            # and set each array value with the rank
            x_k_plus_1[i] = rank_i


        # Here we check current top 10 nodes in order to check if they change
        # When they stop changing between interations we can say they stabilized
        # and that means we can stop the function
        top_10_indices = np.argsort(x_k_plus_1)[-10:][::-1]
        top_10_current = list(top_10_indices)
        if top_10_current == top_10_prev:
            print(f"TOP 10 stabilized after {iterations} iterations")
            print('\n')
            break

        # if it is not stabilized yet we prepare variables for the next iterations
        top_10_prev = top_10_current
        x_k = x_k_plus_1


    # If the outerloop is broken and our code is done we can get our final_ranks into our original graph and sort it
    final_rank = {original_nodes[i]: x_k[i] for i in range(number_of_nodes)}
    sorted_ranks = sorted(final_rank.items(), key=lambda item: item[1], reverse=True)

    # at the end we print in a nice looking way
    print(f"{'Rank':<5} | {'Node ID':<10} | {'Score':<20}")
    for i, (node, rank) in enumerate(sorted_ranks[:10]):
        print(f"{i+1:<5} | {node:<10} | {rank:<20.10f}")
    print('\n')

    # here we take the top10 as a list ( to use it in a random surfer function )
    top_10_node_ids = [node for (node, rank) in sorted_ranks[:10]]
    return top_10_node_ids


#THis part was done by Krzysztof Marcinkiewicz
#Random surfer function from the begining to the printing

def random_surfer(Graph, m, target_top_10):
    '''
        INPUT : The function takes three inputs: 
                - graph - which is given graph with pages
                - m - which is probability of teleporting.
                - target_top_10 - whichc is top10 nodes from PageRank algorithm. We use it to check how many steps random surfer
                                  needs to get similar results
        FUNCIONALITY: The function goes randomly through the pages by the links. It can teleport with probability eaither when there
                      are no links or randomly with probability m. At the end funciton prints top10 result and counter of visits and
                      probability of stepping into particular page. The results whould be similar to PageRank results,
        OUTPUT: The function doesnt return anythink
    '''

    # Printing for better looking output
    print('RANDOM SURFER SIMULATION')
    print('=========================')

    # we create a list of all nodes
    all_nodes = list(Graph.nodes())
    # and take one randomly as a starting one
    current_node = random.choice(all_nodes)
    # we create a dictonary with nodes and number of visits
    visit_counts = {}

    # we map all the successors for all nodes in our nodes list
    successor_map = {node: list(Graph.successors(node)) for node in all_nodes}

    # set steps and top10 variable which we will have in our loop
    steps = 0
    top_10_prev = []

    # start main loop
    while True:

        # every iteration of loop we add 1 step and add 1 to our visit counter 
        steps+=1
        visit_counts[current_node] = visit_counts.get(current_node, 0 ) + 1

        # here we can use the succesor map and take neighbours of the current node
        out_neighbors = successor_map[current_node]


        # here we move to another page
        # with probability of teleporting m random surfer can teleport
        # if there are no links from current node random surfer teleports
        # if none of 2 above happen our surfer randomly goes with one of the links to another node
        prob = random.random()
        if prob < m or not out_neighbors:
            next_node = random.choice(all_nodes)
        else:
            next_node = random.choice(out_neighbors)
        # and we set this new node to a current node
        current_node = next_node


        # here we check if the loop should stop ( we wait until random surfer would get similar results as PageRank)
        # We check every 1000 steps for faster running time
        if steps % 1000 == 0 and steps > 1000:

            # we sort the current items and get the list of top 10
            sorted_items = sorted(visit_counts.items(), key=lambda item: item[1], reverse=True)
            current_top_10 = [node for (node, count) in sorted_items[:10]]

            # if the result of PageRank ad RandomSurfer match we break the loop
            if current_top_10 == target_top_10:
                print(f"TOP 10 matched PageRank after {steps:,} steps. (Checked every better 1000 steps for running time)")
                print('However, random surfer is random, so this is the value for random seed = 43')
                print('\n')
                break


    # Here we just print the results of RandomSurfer
    print(f"{'Rank':<5} | {'Node ID':<12} | {'Count':<20} | {'Probability':<28}")
    for i, (node, count) in enumerate(sorted_items[:10]):
        probability = count / steps
        rank = i+1
        print(f"{rank:<5} | {node:<12} | {count:<20,} | {probability:<28}")



# Here we just call the functions and use the returned top10 of PageRank as a parameter in randomSurfer
random_surfer(graph, m, PageRank(graph, m))
