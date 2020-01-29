
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

#num_nodes = 1000
#num_nodes = 100
#num_nodes = 10
num_nodes = 5
#num_nodes = 2
#num_nodes = 1
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """

    # if curr node is a leaf (has untried actions)
    if node.untried_actions:
        return node

    # else recursively traverse_nodes to find a leaf
    else:
        # recursively search children of curr node
        for move in board.legal_actions(state):
            return traverse_nodes(node.child_nodes[move], board, state, identity)




def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """

    # select an untried action
    action = node.untried_actions[0]
    node.untried_actions.remove(action)

    # create a new child with selected action
    new_node = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(state))
    node.child_nodes[action] = new_node

    # return newly created node
    return new_node




def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """

    # randomly play until game completed
    while not board.is_ended(state):
        action = choice(board.legal_actions(state))
        state = board.next_state(state, action)
    
    # return whether the rollout game was a win or loss
    return state


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """

    # increment node visits and wins
    node.visits += 1
    if won:
        node.wins += 1

    # recursively trace backwards until root
    if node.parent != None:
        return
    else:
        return backpropagate(node.parent, won)



def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    #print(root_node.tree_to_string(horizon=3, indent=2))

    for step in range(num_nodes):

        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # ==========
        #  RUN MCTS 
        # ==========

        # SELECT
        # set node to leaf returned by selection
        leaf_node = traverse_nodes(node, board, sampled_game, identity_of_bot)
        
        # EXPAND
        # expand selected leaf by exploring a new action
        new_node = expand_leaf(leaf_node, board, sampled_game)
        sampled_expand = board.next_state(sampled_game, new_node.parent_action)

        # ROLLOUT
        # play rest of the game after new action
        sampled_rollout = rollout(board, sampled_expand)

        # BACKPROPAGATE
        # propagate results of rollout back up the tree
        points_values = board.points_values(sampled_rollout)
        if points_values[identity_of_bot] > 0:
            won = True
        else:
            won = False
        backpropagate(new_node, won)

    
    # ===============
    #  RETURN ACTION 
    # ===============

    # find the best child
    best_node = None
    for i in leaf_node.child_nodes:
        if best_node == None:
            best_node = leaf_node.child_nodes[i]
        elif leaf_node.child_nodes[i].wins > best_node.wins:
            best_node = leaf_node.child_nodes[i]

    # return best child
    return best_node.parent_action