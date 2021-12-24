import copy
import unittest
import ps1

def check_valid_mapping(election, move_voters_result, real_results):
    # case when student returns None
    if move_voters_result is None:
        assert real_results is None, "There is a possible solution here, but you returned None."
        return True

    if real_results is None:
        assert move_voters_result is None, "This election cannot be flipped, but you returned something other than None."
        return True

    voters_moved, voter_map, ec_votes = move_voters_result
    staff_voters_moved, staff_voter_map, staff_ec_votes = real_results
    orig_winner, orig_loser = ps1.election_winner(election)
    election_copy = election[:]

    # check if the numbers line up
    assert (ec_votes == staff_ec_votes), f"The number of ec_votes gained isn't quite right: expected {staff_ec_votes}, got {ec_votes}."
    assert (voters_moved == staff_voters_moved), f"The number of voters_moved isn't quite right: expected {staff_voters_moved}, got {voters_moved}."

    # maps the state to the index in the list allows for easy access
    election_dict = {}
    for state_index in range(len(election_copy)):
        election_dict[election_copy[state_index].get_name()] = state_index

    # make all of the moves suggested in voter_map
    states_with_pride = ['AL', 'AZ', 'CA', 'TX']
    for state_from, state_to in voter_map:
        from_index, to_index = election_dict[state_from], election_dict[state_to]
        from_margin, to_margin = election_copy[from_index].get_margin(), election_copy[to_index].get_margin()
        margin_moved = voter_map[(state_from, state_to)]

        # just flipped a state that was already won
        assert from_margin-margin_moved >= 1, f"Your mapping should not be turning a state won by the original loser into one they now lost or tied, but it turns out it did so for {state_from}."

        assert state_from not in states_with_pride, (f"Your mapping should not have moved voters from state with pride {state_from}, but it turns out it has.")

        #change the results of the election
        election_copy[from_index].subtract_winning_candidate_voters(margin_moved)
        election_copy[to_index].add_losing_candidate_voters(margin_moved)

    # check if after all of the changes are made, the election result has been flipped
    new_winner, new_loser = ps1.election_winner(election_copy)
    assert new_winner == orig_loser, "After making the moves you suggested, your mapping should have flipped the election, but it turns out it has not."
    return True


class TestPS1(unittest.TestCase):
    def test_1_load_election(self):
        parsed_election_600 = ps1.load_election("600_results.txt")
        real_parsed_election_600 = [ps1.State("TX", 1, 2, 530), ps1.State("CA", 4, 5, 3), ps1.State("MA", 7, 8, 5)]
        self.assertIsInstance(parsed_election_600, list, f"load_election should have returned a list, but instead returned an instance of {type(parsed_election_600)}.")
        self.assertEqual(len(parsed_election_600), len(real_parsed_election_600), f"The length of the list returned by load_election should have been {len(real_parsed_election_600)}, but found it returned {len(parsed_election_600)}.")
        self.assertTrue(all(isinstance(st, ps1.State) for st in parsed_election_600), f"All items in the list returned by load_election should have been State instances, but found your output was {parsed_election_600}.")
        for i in range(len(parsed_election_600)):
            self.assertEqual(real_parsed_election_600[i], parsed_election_600[i], f"Expected the element at index {i} of the returned list be `{real_parsed_election_600[i]}`, found it was `{parsed_election_600[i]}`.")

        parsed_election_60001 = ps1.load_election("60001_results.txt")
        real_parsed_election_60001 = [ps1.State("FL", 4, 3, 3), ps1.State("GA", 8, 7, 5), ps1.State("WA", 7, 8, 5), ps1.State("AL", 1, 10, 1)]
        self.assertIsInstance(parsed_election_60001, list, f"load_election should have returned a list, but instead returned an instance of {type(parsed_election_60001)}.")
        self.assertEqual(len(parsed_election_60001), len(real_parsed_election_60001), f"The length of the list returned by load_election should have been {len(real_parsed_election_60001)}, but found it returned {len(parsed_election_60001)}.")
        self.assertTrue(all(isinstance(st, ps1.State) for st in parsed_election_60001), f"All items in the list returned by load_election should have been State instances, but found your output was {parsed_election_60001}.")
        for i in range(len(parsed_election_60001)):
            self.assertEqual(parsed_election_60001[i], real_parsed_election_60001[i], f"Expected the element at index {i} of the returned list be `{real_parsed_election_60001[i]}`, found it was `{parsed_election_60001[i]}`.")

    def test_2a_election_winner(self):
        rep_won = ("rep", "dem")
        dem_won = ("dem", "rep")

        parsed_election_600 = [ps1.State("TX", 2, 1, 100), ps1.State("CA", 1, 2, 1), ps1.State("MA", 1, 2, 2)]
        results_600 = ps1.election_winner(parsed_election_600)
        self.assertEqual(results_600, dem_won, f"For the sample election: expected {dem_won}, got {results_600}. You appear to be tallying number of states won rather than number of EC votes won by a state.")

        parsed_election_60001 = [ps1.State("FL", 4, 3, 3), ps1.State("GA", 8, 7, 5), ps1.State("WA", 7, 8, 5), ps1.State("AL", 1, 10, 1)]
        results_60001 = ps1.election_winner(parsed_election_60001)
        self.assertEqual(results_60001, dem_won, f"For the second sample election: expected {dem_won}, got {results_60001}.")

        results_2020 = ps1.election_winner(ps1.load_election("2020_results.txt"))
        self.assertEqual(results_2020, dem_won, f"For the 2020 election: expected {dem_won}, got {results_2020}.")

        results_2016 = ps1.election_winner(ps1.load_election("2016_results.txt"))
        self.assertEqual(results_2016, rep_won, f"For the 2016 election: expected {rep_won}, got {results_2016}.")

        results_2012 = ps1.election_winner(ps1.load_election("2012_results.txt"))
        self.assertEqual(results_2012, dem_won, f"For the 2012 election: expected {dem_won}, got {results_2012}.")

    def test_2b_winner_states(self):
        real_600 = set(['TX', 'CA', 'MA'])
        results_600 = [state.get_name() for state in ps1.winner_states(ps1.load_election("600_results.txt"))]
        self.assertIsInstance(results_600, list, f"winner_states should have returned a list, but instead returned an instance of {type(results_600)}.")
        self.assertEqual(len(results_600), len(set(results_600)), "winner_states should have returned a list with no duplicates, but found it had duplicates.")
        self.assertEqual(real_600, set(results_600), f"For the sample election: expected {real_600}, got {results_600}.")

        real_60001 = set(['FL', 'GA'])
        results_60001 = [state.get_name() for state in ps1.winner_states(ps1.load_election("60001_results.txt"))]
        self.assertIsInstance(results_60001, list, f"winner_states should have returned a list, but instead returned an instance of {type(results_60001)}.")
        self.assertEqual(len(results_60001), len(set(results_60001)), "winner_states should have returned a list with no duplicates, but found it had duplicates.")
        self.assertEqual(real_60001, set(results_60001), f"For the second sample election: expected {real_60001}, got {results_60001}.")

        real_2020 = set(['AZ', 'CA', 'CO', 'CT', 'DE', 'DC', 'GA', 'HI', 'IL', 'ME', 'MD', 'MA', 'MI', 'MN', 'NV', 'NH', 'NJ', 'NM', 'NY', 'OR', 'PA', 'RI', 'VT', 'VA', 'WA', 'WI'])
        results_2020 = [state.get_name() for state in ps1.winner_states(ps1.load_election("2020_results.txt"))]
        self.assertIsInstance(results_2020, list, f"winner_states should have returned a list, but instead returned an instance of {type(results_2020)}.")
        self.assertEqual(len(results_2020), len(set(results_2020)), "winner_states should have returned a list with no duplicates, but found it had duplicates.")
        self.assertEqual(real_2020, set(results_2020), f"For the 2020 election: expected {real_2020}, got {results_2020}.")

        real_2016 = set(['AL', 'AK', 'AZ', 'AR', 'FL', 'GA', 'ID', 'IN', 'IA', 'KS', 'KY', 'LA', 'MI', 'MS', 'MO', 'MT', 'NE', 'NC', 'ND', 'OH', 'OK', 'PA', 'SC', 'SD', 'TN', 'TX', 'UT', 'WV', 'WI', 'WY'])
        results_2016 = [state.get_name() for state in ps1.winner_states(ps1.load_election("2016_results.txt"))]
        self.assertIsInstance(results_2016, list, f"winner_states should have returned a list, but instead returned an instance of {type(results_2016)}.")
        self.assertEqual(len(results_2016), len(set(results_2016)), "winner_states should have returned a list with no duplicates, but found it had duplicates.")
        self.assertEqual(real_2016, set(results_2016), f"For the 2016 election: expected {real_2016}, got {results_2016}.")

        real_2012 = set(['CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'HI', 'IL', 'IA', 'ME', 'MD', 'MA', 'MI', 'MN', 'NV', 'NH', 'NJ', 'NM', 'NY', 'OH', 'OR', 'PA', 'RI', 'VT', 'VA', 'WA', 'WI'])
        results_2012 = [state.get_name() for state in ps1.winner_states(ps1.load_election("2012_results.txt"))]
        self.assertIsInstance(results_2012, list, f"winner_states should have returned a list, but instead returned an instance of {type(results_2012)}.")
        self.assertEqual(len(results_2012), len(set(results_2012)), "winner_states should have returned a list with no duplicates, but found it had duplicates.")
        self.assertEqual(real_2012, set(results_2012), f"For the 2016 election: expected {real_2012}, got {results_2012}.")

    def test_2c_ec_votes_to_flip(self):
        real_600 = 270
        results_600 = ps1.ec_votes_to_flip(ps1.load_election("600_results.txt"))
        self.assertIsInstance(results_600, int, f"ec_votes_to_flip should have returned an int, but instead returned an instance of {type(results_600)}.")
        self.assertEqual(results_600, real_600, f"For the sample election: expected {real_600}, got {results_600}.")

        real_60001 = 2
        results_60001 = ps1.ec_votes_to_flip(ps1.load_election("60001_results.txt"), total=14)
        self.assertIsInstance(real_60001, int, f"ec_votes_to_flip should have returned an int, but instead returned an instance of {type(real_60001)}.")
        self.assertEqual(results_60001, real_60001, f"For the second sample election: expected {real_60001}, got {results_60001}.")

        real_2020 = 38
        results_2020 = ps1.ec_votes_to_flip(ps1.load_election("2020_results.txt"))
        self.assertIsInstance(results_2020, int, f"ec_votes_to_flip should have returned an int, but instead returned an instance of {type(results_2020)}.")
        self.assertEqual(results_2020, real_2020, f"For the 2020 election: expected {real_2020}, got {results_2020}.")

        real_2016 = 37
        results_2016 = ps1.ec_votes_to_flip(ps1.load_election("2016_results.txt"))
        self.assertIsInstance(results_2016, int, f"ec_votes_to_flip should have returned an int, but instead returned an instance of {type(results_2016)}.")
        self.assertEqual(results_2016, real_2016, f"For the 2016 election: expected {real_2016}, got {results_2016}.")

        real_2012 = 64
        results_2012 = ps1.ec_votes_to_flip(ps1.load_election("2012_results.txt"))
        self.assertIsInstance(results_2012, int, f"ec_votes_to_flip should have returned an int, but instead returned an instance of {type(results_2012)}.")
        self.assertEqual(results_2012, real_2012, f"For the 2012 election: expected {real_2012}, got {results_2012}.")

    def test_3_brute_swing_states(self):
        real_sample = set(['TX'])
        lost_sample = ps1.winner_states(ps1.load_election("600_results.txt"))
        votes_sample = ps1.ec_votes_to_flip(ps1.load_election("600_results.txt"))
        results_sample_list = ps1.brute_force_swing_states(copy.deepcopy(lost_sample), votes_sample)
        results_sample = [state.get_name() for state in results_sample_list]
        self.assertEqual(set(results_sample), real_sample, f"For Sample Results: expected {list(real_sample)}, got {list(results_sample)}. Check that you are handling ties correctly.")

        real_sample_2 = set(['BE'])
        lost_sample_2 = ps1.winner_states(ps1.load_election("60002_results.txt"))
        votes_sample_2 = ps1.ec_votes_to_flip(ps1.load_election("60002_results.txt"), total=14)
        results_sample_2_list = ps1.brute_force_swing_states(copy.deepcopy(lost_sample_2), votes_sample_2)
        results_sample_2 = [state.get_name() for state in results_sample_2_list]
        self.assertEqual(set(results_sample_2), real_sample_2, f"For Given Example Results: expected {list(real_sample)}, got {list(results_sample)}. Test your code using the test cases under 'main' in ps1.py.")

        real_2020 = set(['AZ'])
        lost_2020 = ps1.winner_states(ps1.load_election("2020_results_brute.txt"))
        votes_2020 = ps1.ec_votes_to_flip(ps1.load_election("2020_results_brute.txt"), total=122)
        results_2020_list = ps1.brute_force_swing_states(copy.deepcopy(lost_2020), votes_2020)
        results_2020 = [state.get_name() for state in results_2020_list]
        self.assertEqual(set(results_2020), real_2020, f"For 2020 Results: expected {real_2020}, got {results_2020}.")

        real_2016 = set(['IA'])
        lost_2016 = ps1.winner_states(ps1.load_election("2016_results_brute.txt"))
        votes_2016 = ps1.ec_votes_to_flip(ps1.load_election("2016_results_brute.txt"), total=44)
        results_2016_list = ps1.brute_force_swing_states(copy.deepcopy(lost_2016), votes_2016)
        results_2016 = [state.get_name() for state in results_2016_list]
        self.assertEqual(set(results_2016), real_2016, f"For 2016 Results: expected {real_2016}, got {results_2016}.")

        real_2012 = set(['MI', 'NV', 'NH', 'VT', 'VA'])
        lost_2012 = ps1.winner_states(ps1.load_election("2012_results_brute.txt"))
        votes_2012 = ps1.ec_votes_to_flip(ps1.load_election("2012_results_brute.txt"), total=98)
        results_2012_list = ps1.brute_force_swing_states(copy.deepcopy(lost_2012), votes_2012)
        results_2012 = [state.get_name() for state in results_2012_list]
        self.assertEqual(set(results_2012), real_2012, f"For 2012 Results: expected {real_2012}, got {results_2012}.")

    def test_4a_move_max_voters(self):
        real_sample = set([])
        lost_sample = ps1.winner_states(ps1.load_election("600_results.txt"))
        moved_max_voters_sample = ps1.move_max_voters(lost_sample, 2)
        results_sample = set(state.get_name() for state in moved_max_voters_sample)
        self.assertEqual(set(results_sample), real_sample, f"For Sample Results: expected States {list(real_sample)}, got {list(results_sample)}.")

        real_2020 = set(['CA', 'VA', 'IL', 'OR', 'VT', 'DC', 'WA', 'HI', 'NM', 'MN', 'CO', 'DE', 'MA', 'MI', 'NY', 'ME', 'RI', 'MD', 'NJ', 'CT', 'NH', 'PA'])
        lost_2020 = ps1.winner_states(ps1.load_election("2020_results.txt"))
        votes_reqd_2020 = ps1.ec_votes_to_flip(ps1.load_election("2020_results.txt"))
        lost_votes_2020 = sum(state.get_ecvotes() for state in lost_2020)
        moved_max_voters_2020 = ps1.move_max_voters(lost_2020, lost_votes_2020-votes_reqd_2020)
        results_2020 = set(state.get_name() for state in moved_max_voters_2020)
        self.assertEqual(set(results_2020), real_2020, f"For the 2020 election: expected States {list(real_2020)}, got {list(results_2020)}.")

        real_2016 = set(['NE', 'WV', 'OK', 'KY', 'TN', 'AL', 'AR', 'MO', 'ND', 'IN', 'LA', 'KS', 'WY', 'SD', 'MS', 'UT', 'SC', 'OH', 'TX', 'ID', 'NC', 'MT', 'IA', 'GA', 'FL', 'AZ', 'AK'])
        lost_2016 = ps1.winner_states(ps1.load_election("2016_results.txt"))
        votes_reqd_2016 = ps1.ec_votes_to_flip(ps1.load_election("2016_results.txt"))
        lost_votes_2016 = sum(state.get_ecvotes() for state in lost_2016)
        moved_max_voters_2016 = ps1.move_max_voters(lost_2016, lost_votes_2016-votes_reqd_2016)
        results_2016 = set(state.get_name() for state in moved_max_voters_2016)
        self.assertEqual(set(results_2016), real_2016, f"For the 2016 election: expected States {list(real_2016)}, got {list(results_2016)}.")

        real_2012 = set(['NY', 'MA', 'MD', 'DC', 'WA', 'HI', 'VT', 'NJ', 'CA', 'IL', 'CT', 'RI', 'OR', 'MI', 'MN', 'WI', 'NM', 'ME', 'PA', 'IA', 'DE', 'NV', 'CO'])
        lost_2012 = ps1.winner_states(ps1.load_election("2012_results.txt"))
        votes_reqd_2012 = ps1.ec_votes_to_flip(ps1.load_election("2012_results.txt"))
        lost_votes_2012 = sum(state.get_ecvotes() for state in lost_2012)
        moved_max_voters_2012 = ps1.move_max_voters(lost_2012, lost_votes_2012-votes_reqd_2012)
        results_2012 = set(state.get_name() for state in moved_max_voters_2012)
        self.assertEqual(set(results_2012), real_2012, f"For the 2012 election: expected States {list(real_2012)}, got {list(results_2012)}.")

    def test_4b_move_min_voters(self):
        real_sample = set(['TX'])
        lost_sample = ps1.winner_states(ps1.load_election("600_results.txt"))
        votes_sample = ps1.ec_votes_to_flip(ps1.load_election("600_results.txt"))
        moved_min_voters_sample = ps1.move_min_voters(lost_sample, votes_sample)
        results_sample = set(state.get_name() for state in moved_min_voters_sample)
        self.assertEqual(results_sample, real_sample, f"For Sample Results: expected States {list(real_sample)}, got {list(results_sample)}.")

        real_2020 = set(['AZ', 'WI', 'GA', 'NV'])
        lost_2020 = ps1.winner_states(ps1.load_election("2020_results.txt"))
        votes_2020 = ps1.ec_votes_to_flip(ps1.load_election("2020_results.txt"))
        moved_min_voters_2020 = ps1.move_min_voters(lost_2020,votes_2020)
        results_2020 = set(state.get_name() for state in moved_min_voters_2020)
        self.assertEqual(results_2020, real_2020, f"For the 2020 election: expected States {list(real_2020)}, got {list(results_2020)}.")

        real_2016 = set(['MI', 'PA', 'WI'])
        lost_2016 = ps1.winner_states(ps1.load_election("2016_results.txt"))
        votes_2016 = ps1.ec_votes_to_flip(ps1.load_election("2016_results.txt"))
        moved_min_voters_2016 = ps1.move_min_voters(lost_2016,votes_2016)
        results_2016 = set(state.get_name() for state in moved_min_voters_2016)
        self.assertEqual(results_2016, real_2016, f"For the 2016 election: expected States {list(real_2016)}, got {list(results_2016)}.")

        real_2012 = set(['FL', 'NH', 'OH', 'VA'])
        lost_2012 = ps1.winner_states(ps1.load_election("2012_results.txt"))
        votes_2012 = ps1.ec_votes_to_flip(ps1.load_election("2012_results.txt"))
        moved_min_voters_2012 = ps1.move_min_voters(lost_2012,votes_2012)
        results_2012 = set(state.get_name() for state in moved_min_voters_2012)
        self.assertEqual(results_2012, real_2012, f"For the 2012 election: expected States {list(real_2012)}, got {list(results_2012)}.")

    def test_5_relocate_voters(self):
        real_sample = None
        election_sample = ps1.load_election("600_results.txt")
        lost_states_sample, ec_needed_sample = ps1.winner_states(election_sample), ps1.ec_votes_to_flip(election_sample)
        swing_states_sample = ps1.move_min_voters(copy.deepcopy(lost_states_sample), ec_needed_sample)
        results_sample_dp = ps1.relocate_voters(copy.deepcopy(election_sample), copy.deepcopy(swing_states_sample))
        self.assertTrue(check_valid_mapping(election_sample, results_sample_dp, real_sample), f"Your relocate_voters results did not give the correct result.\nFor the sample election you got {results_sample_dp}\nOne valid solution is {real_sample}.")

        real_2020 = (76518, {('AK', 'AZ'): 10458, ('AK', 'GA'): 11780, ('AK', 'NV'): 13802, ('AR', 'NV'): 19795, ('AR', 'WI'): 20683}, 43)
        election_2020 = ps1.load_election("2020_results.txt")
        lost_states_2020, ec_needed_2020 = ps1.winner_states(election_2020), ps1.ec_votes_to_flip(election_2020)
        swing_states_2020 = ps1.move_min_voters(lost_states_2020, ec_needed_2020)
        results_2020_dp = ps1.relocate_voters(copy.deepcopy(election_2020), copy.deepcopy(swing_states_2020))
        self.assertTrue(check_valid_mapping(election_2020, results_2020_dp, real_2020), f"Your relocate_voters results did not give the correct result.\nFor the 2020 election you got {results_2020_dp}.\nOne valid solution is {real_2020}.")

        real_2016 = (77747, {('CO', 'MI'): 10705, ('CO', 'PA'): 44293, ('CO', 'WI'): 22749}, 46)
        election_2016 = ps1.load_election("2016_results.txt")
        lost_states_2016, ec_needed_2016 = ps1.winner_states(election_2016), ps1.ec_votes_to_flip(election_2016)
        swing_states_2016 = ps1.move_min_voters(copy.deepcopy(lost_states_2016), ec_needed_2016)
        results_2016_dp = ps1.relocate_voters(copy.deepcopy(election_2016), copy.deepcopy(swing_states_2016))
        self.assertTrue(check_valid_mapping(election_2016, results_2016_dp, real_2016), f"Your relocate_voters results did not give the correct result.\nFor the 2016 election you got {results_2016_dp}\nOne valid solution is {real_2016}.")

        real_2012 = (429526, {('AK', 'FL'): 42035, ('AR', 'FL'): 32275, ('AR', 'NH'): 39644, ('AR', 'OH'): 166273, ('AR', 'VA'): 15142, ('GA', 'VA'): 134157}, 64)
        election_2012 = ps1.load_election("2012_results.txt")
        lost_states_2012, ec_needed_2012 = ps1.winner_states(election_2012), ps1.ec_votes_to_flip(election_2012)
        swing_states_2012 = ps1.move_min_voters(copy.deepcopy(lost_states_2012), ec_needed_2012)
        results_2012_dp = ps1.relocate_voters(copy.deepcopy(election_2012), copy.deepcopy(swing_states_2012))
        self.assertTrue(check_valid_mapping(election_2012, results_2012_dp, real_2012), f"Your relocate_voters results did not give the correct result.\nFor the 2012 election you got {results_2012_dp}\nOne valid solution is {real_2012}.")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPS1))
    result = unittest.TextTestRunner(verbosity=2).run(suite)