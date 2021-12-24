################################################################################
# 6.0002 Fall 2021
# Problem Set 1
# Name: Miguel Chacon
# Collaborators: 
# Time: 8 hours

from state import State

##########################################################################################################
## Problem 1
##########################################################################################################

def load_election(filename):
    """
    Reads the contents of a file, with data given in the following tab-separated format:
    State[tab]Democrat_votes[tab]Republican_votes[tab]EC_votes

    Please ignore the first line of the file, which are the column headers, and remember that
    the special character for tab is '\t'

    Parameters:
    filename - the name of the data file as a string

    Returns:
    a list of State instances
    """
    # TODO
    file = open(filename, "r")
    file.readline()
    States = []
    for line in file:
        States.append(State(*line.split()))
    return States


##########################################################################################################
## Problem 2: Helper functions
##########################################################################################################

def election_winner(election):
    """
    Finds the winner of the election based on who has the most amount of EC votes.
    Note: In this simplified representation, all of EC votes from a state go
    to the party with the majority vote.

    Parameters:
    election - a list of State instances

    Returns:
    a tuple, (winner, loser) of the election i.e. ('dem', 'rep') if Democrats won, else ('rep', 'dem')
    """
    # TODO
    dem_ecvotes = 0
    rep_ecvotes = 0
    for state in election:
        # check which party got more votes in the state
        if state.get_winner() == "dem":
            dem_ecvotes += state.get_ecvotes()
        else:
            rep_ecvotes += state.get_ecvotes()
    if dem_ecvotes > rep_ecvotes: 
        return ("dem", "rep")
    else:
        return ("rep", "dem")


def winner_states(election):
    """
    Finds the list of States that were won by the winning candidate (lost by the losing candidate).

    Parameters:
    election - a list of State instances

    Returns:
    A list of State instances won by the winning candidate
    """
    # TODO
    # get the winner of the election
    winner = election_winner(election)[0]
    ns_states = []
    # for every state, check if state's winner is the election winner
    for state in election:
        if state.get_winner() == winner:
            ns_states.append(state)
    
    return ns_states



def ec_votes_to_flip(election, total=538):
    """
    Finds the number of additional EC votes required by the loser to change election outcome.
    Note: A party wins when they earn half the total number of EC votes plus 1.

    Parameters:
    election - a list of State instances
    total - total possible number of EC votes

    Returns:
    int, number of additional EC votes required by the loser to change the election outcome
    """
    # TODO
    winning_states = winner_states(election)
    # collect the electoral votes of the winner
    w_ecvotes = 0
    for state in winning_states:
        w_ecvotes += state.get_ecvotes()

    # get the losers electoral votes
    l_ecvotes = total - w_ecvotes

    return (total//2) + 1 - l_ecvotes
##########################################################################################################
## Problem 3: Brute Force approach
##########################################################################################################

def combinations(L):
    """
    Helper function to generate powerset of all possible combinations
    of items in input list L. E.g., if
    L is [1, 2] it will return a list with elements
    [], [1], [2], and [1,2].

    Parameters:
    L - list of items

    Returns:
    a list of lists that contains all possible
    combinations of the elements of L
    """

    def get_binary_representation(n, num_digits):
        """
        Inner function to get a binary representation of items to add to a subset,
        which combinations() uses to construct and append another item to the powerset.

        Parameters:
        n and num_digits are non-negative ints

        Returns:
            a num_digits str that is a binary representation of n
        """
        result = ''
        while n > 0:
            result = str(n%2) + result
            n = n//2
        if len(result) > num_digits:
            raise ValueError('not enough digits')
        for i in range(num_digits - len(result)):
            result = '0' + result
        return result

    powerset = []
    for i in range(0, 2**len(L)):
        binStr = get_binary_representation(i, len(L))
        subset = []
        for j in range(len(L)):
            if binStr[j] == '1':
                subset.append(L[j])
        powerset.append(subset)
    return powerset

def brute_force_swing_states(winner_states, ec_votes):
    """
    Finds a subset of winner_states that would change an election outcome if
    voters moved into those states, these are our swing states. Iterate over
    all possible move combinations using the helper function combinations(L).
    Return the move combination that minimises the number of voters moved. If
    there exists more than one combination that minimises this, return any one of them.

    Parameters:
    winner_states - a list of State instances that were won by the winner
    ec_votes - int, number of EC votes needed to change the election outcome

    Returns:
    A list of State instances such that the election outcome would change if additional
    voters relocated to those states
    The empty list, if no possible swing states
    """
    # TODO
    # get all combinations of winner_states
    w_combos = combinations(winner_states)

    # dictionary that holds combos of states that can flip the election
    # keys are the margins and the values are the combos of states
    results = dict()
    for combo in w_combos:
        flipped_ecvotes = 0
        total_margins = 0
        for state in combo:
            # first, find the margin needed to flip state
            total_margins += state.get_margin() + 1
            flipped_ecvotes += state.get_ecvotes()
        # add the margin and whether or not the election was flipped to results
        if flipped_ecvotes >= ec_votes:
            results[total_margins] = combo
    # return the combo with smallest change in voters
    return results[ min(results.keys()) ]


##########################################################################################################
## Problem 4: Dynamic Programming
## In this section we will define two functions, move_max_voters and move_min_voters, that
## together will provide a dynamic programming approach to find swing states. This problem
## is analagous to the complementary knapsack problem, you might find Lecture 1 of 6.0002 useful
## for this section of the pset.
##########################################################################################################

def move_max_voters(winner_states, ec_votes):
    """
    Finds the largest number of voters needed to relocate to get at most ec_votes
    for the election loser.

    Analogy to the knapsack problem:
        Given a list of states each with a weight(ec_votes) and value(margin+1),
        determine the states to include in a collection so the total weight(ec_votes)
        is less than or equal to the given limit(ec_votes) and the total value(voters displaced)
        is as large as possible.

    Parameters:
    winner_states - a list of State instances that were won by the winner
    ec_votes - int, the maximum number of EC votes

    Returns:
    A list of State instances such that the maximum number of voters need to be relocated
    to these states in order to get at most ec_votes
    The empty list, if every state has a # EC votes greater than ec_votes
    """
    # returns tuple of max voters and states
    def max_helper(toConsider, avail, memo = {}):
        # if it's already been calculated, return it
        if (len(toConsider), avail) in memo:
            result = memo[(len(toConsider), avail)]
        # base case
        elif toConsider == [] or avail == 0:
            result = (0, ())
        # state has too many ec votes
        elif toConsider[0].get_ecvotes() > avail:
            result = max_helper(toConsider[1:], avail, memo)
        else:
            next_state = toConsider[0]
            # take next state
            ns_voters, ns_states = max_helper(toConsider[1:], avail - next_state.get_ecvotes(), memo)
            ns_voters += next_state.get_margin() + 1

            # do not take next item
            current_voters, current_states = max_helper(toConsider[1:], avail, memo)

            # take the max of the two
            if ns_voters > current_voters:
                result = (ns_voters, ns_states + (next_state,))
            else:
                result = (current_voters, current_states)
        # update memo
        memo[(len(toConsider), avail)] = result
        return result
    
    r = max_helper(winner_states, ec_votes)
    return list(r[1])


def move_min_voters(winner_states, ec_votes_needed):
    """
    Finds a subset of winner_states that would change an election outcome if
    voters moved into those states. Should minimize the number of voters being relocated.
    Only return states that were originally won by the winner (lost by the loser)
    of the election.

    Hint: This problem is simply the complement of move_max_voters. You should call
    move_max_voters with ec_votes set to (#ec votes won by original winner - ec_votes_needed)

    Parameters:
    winner_states - a list of State instances that were won by the winner
    ec_votes_needed - int, number of EC votes needed to change the election outcome

    Returns:
    A list of State instances such that the election outcome would change if additional
    voters relocated to those states (also can be referred to as our swing states)
    The empty list, if no possible swing states
    """
    # TODO
    # get the winning candidate's ec votes
    original_ec_votes = sum([state.get_ecvotes() for state in winner_states])
    # get the states that can't be flipped and remove them from winning states
    removed_states = move_max_voters(winner_states, original_ec_votes - ec_votes_needed)
    results = winner_states.copy()
    for state in removed_states:
        results.remove(state)
    return results

##########################################################################################################
## Problem 5
##########################################################################################################

def relocate_voters(election, swing_states, states_with_pride = ['AL', 'AZ', 'CA', 'TX']):
    """
    Finds a way to shuffle voters in order to flip an election outcome. Moves voters
    from states that were won by the losing candidate (states not in winner_states), to
    each of the states in swing_states. To win a swing state, you must move (margin + 1)
    new voters into that state. Any state that voters are moved from should still be won
    by the loser even after voters are moved. Also finds the number of EC votes gained by
    this rearrangement, as well as the minimum number of voters that need to be moved.
    Note: You cannot move voters out of Alabama, Arizona, California, or Texas.

    Parameters:
    election - a list of State instances representing the election
    swing_states - a list of State instances where people need to move to flip the election outcome
                   (result of move_min_voters or greedy_swing_states)
    states_with_pride - a list of Strings holding the names of states where residents cannot be moved from
                    (default states are AL, AZ, CA, TX)

    Return:
    A tuple that has 3 elements in the following order:
        - an int, the total number of voters moved
        - a dictionary with the following (key, value) mapping:
            - Key: a 2 element tuple of str, (from_state, to_state), the 2 letter State names
            - Value: int, number of people that are being moved
        - an int, the total number of EC votes gained by moving the voters
    None, if it is not possible to sway the election
    """
    # TODO
    # keeps track of voters moved from state to state
    Dict = dict()
    # keeps track of how many states have been overturned
    count = 0

    # dict[state name] = available votes
    lcs = dict()

    # get winning_states
    winning_states = winner_states(election)

    # also remove swing state and states with pride
    for state in election:
        # don't add winning states nor states with pride
        if state.get_name() not in states_with_pride and state not in winning_states:
            lcs[state.get_name()] = state.get_margin() -1

    # for every swing state...
    for i in range(len(swing_states)):
        # see how many votes one needs to flip it
        needed_votes = swing_states[i].get_margin() + 1
        # for every state that the losing candidate won...
        # use available votes from current state until needed votes = 0
        for key in lcs.keys():
            if needed_votes > lcs[key]:
                needed_votes -= lcs[key]
                Dict[(key, swing_states[i].get_name())] = lcs[key]
                lcs[key] = 0
            elif needed_votes == lcs[key]:
                Dict[(key, swing_states[i].get_name())] = needed_votes
                lcs[key], needed_votes = 0
            else:
                lcs[key] -= needed_votes
                Dict[(key, swing_states[i].get_name())] = needed_votes
                needed_votes = 0

            if needed_votes == 0:
                # keep track of swing states to see if election was flipped
                count += 1
                break
    # check if all swing states were flipped to flip general election
    if count != len(swing_states):
        return None
    else:
        votes_moved = sum( [state.get_margin() +1 for state in swing_states] )
        EC_votes_gained = sum( [state.get_ecvotes() for state in swing_states] )
        return (votes_moved, Dict, EC_votes_gained)


if __name__ == "__main__":
    pass
    # Uncomment the following lines to test each of the problems

    # tests Problem 1
    year = 2012
    election = load_election("%s_results.txt" % year)
    print(len(election))
    print(election[0])

    # tests Problem 2
    winner, loser = election_winner(election)
    won_states = winner_states(election)
    names_won_states = [state.get_name() for state in won_states]
    reqd_ec_votes = ec_votes_to_flip(election)
    print("Winner:", winner, "\nLoser:", loser)
    print("States won by the winner: ", names_won_states)
    print("EC votes needed:",reqd_ec_votes, "\n")

    # tests Problem 3
    brute_election = load_election("60002_results.txt")
    brute_won_states = winner_states(brute_election)
    brute_ec_votes_to_flip = ec_votes_to_flip(brute_election, total=14)
    brute_swing = brute_force_swing_states(brute_won_states, brute_ec_votes_to_flip)
    names_brute_swing = [state.get_name() for state in brute_swing]
    voters_brute = sum([state.get_margin()+1 for state in brute_swing])
    ecvotes_brute = sum([state.get_ecvotes() for state in brute_swing])
    print("Brute force swing states results:", names_brute_swing)
    print("Brute force voters displaced:", voters_brute, "for a total of", ecvotes_brute, "Electoral College votes.\n")

    # tests Problem 4: move_max_voters
    print("move_max_voters")
    total_lost = sum(state.get_ecvotes() for state in won_states)
    non_swing_states = move_max_voters(won_states, total_lost-reqd_ec_votes)
    non_swing_states_names = [state.get_name() for state in non_swing_states]
    max_voters_displaced = sum([state.get_margin()+1 for state in non_swing_states])
    max_ec_votes = sum([state.get_ecvotes() for state in non_swing_states])
    print("States with the largest margins (non-swing states):", non_swing_states_names)
    print("Max voters displaced:", max_voters_displaced, "for a total of", max_ec_votes, "Electoral College votes.", "\n")

    # tests Problem 4: move_min_voters
    print("move_min_voters")
    swing_states = move_min_voters(won_states, reqd_ec_votes)
    swing_state_names = [state.get_name() for state in swing_states]
    min_voters_displaced = sum([state.get_margin()+1 for state in swing_states])
    swing_ec_votes = sum([state.get_ecvotes() for state in swing_states])
    print("Complementary knapsack swing states results:", swing_state_names)
    print("Min voters displaced:", min_voters_displaced, "for a total of", swing_ec_votes, "Electoral College votes. \n")

    # tests Problem 5: relocate_voters
    print("relocate_voters")
    flipped_election = relocate_voters(election, swing_states)
    print("Flip election mapping:", flipped_election)