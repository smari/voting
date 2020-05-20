import unittest

import division_rules
import apportion

class TestElection(unittest.TestCase):

    def test_valid(self):
        #Arrange
        votes    = [1852,2196,7800,1812,1756,1508,4662,1552]
        priors   = [   1,   1,   4,   1,   1,   0,   2,   0]
        expected = [   1,   1,   5,   1,   1,   0,   2,   0]

        #Act
        results, _ = apportion.apportion1d(
            v_votes=votes,
            num_total_seats=11,
            prior_allocations=priors,
            divisor_gen=division_rules.dhondt_gen,
        )

        #Assert
        self.assertEqual(expected, results)

    def test_quota(self):
        #Arrange
        votes     = [135,129, 36]
        expected3 = [  1,  1,  1]
        expected4 = [  2,  2,  0]

        #Act
        results3, _, _, _ = apportion.apportion1d_general(
            num_total_seats=3,
            v_votes=votes,
            rule=division_rules.hare,
            type_of_rule="Quota",
            prior_allocations=[],
        )
        results4, _, _, _ = apportion.apportion1d_general(
            num_total_seats=4,
            v_votes=votes,
            rule=division_rules.hare,
            type_of_rule="Quota",
            prior_allocations=[],
        )

        #Assert
        self.assertEqual(expected3, results3)
        self.assertEqual(expected4, results4)

    def test_seat_generator_quota(self):
        #Arrange
        votes = [135,129,36]
        repetitions = 2 # Make sure the process is repeatable

        #Act
        seats, seat_gen, last_in, next_in = apportion.apportion1d_general(
            v_votes=votes,
            num_total_seats=3,
            prior_allocations=[],
            rule=division_rules.hare,
            type_of_rule="Quota"
        )

        #Assert
        self.assertEqual(seats, [1,1,1])
        self.assertEqual(last_in, {'idx': 2, 'active_votes': 36})
        self.assertEqual(next_in, {'idx': 0, 'active_votes': 35})
        for i in range(repetitions):
            seat = seat_gen()
            self.assertEqual(next(seat), {'idx': 0, 'active_votes': 135})
            self.assertEqual(next(seat), {'idx': 1, 'active_votes': 129})
            self.assertEqual(next(seat), {'idx': 2, 'active_votes':  36})
            #note that the quota is based on there being only 3 seats,
            #but if we were to continue, the sequence would go on as follows:
            self.assertEqual(next(seat), {'idx': 0, 'active_votes':  35})
            self.assertEqual(next(seat), {'idx': 1, 'active_votes':  29})

    def test_seat_generator_div(self):
        #Arrange
        votes = [135,129,36]
        repetitions = 2 # Make sure the process is repeatable

        #Act
        seats, seat_gen, last_in, next_in = apportion.apportion1d_general(
            v_votes=votes,
            num_total_seats=3,
            prior_allocations=[],
            rule=division_rules.dhondt_gen,
            type_of_rule="Division"
        )

        #Assert
        self.assertEqual(seats, [2,1,0])
        self.assertEqual(last_in, {'idx': 0, 'active_votes': 67.5})
        self.assertEqual(next_in, {'idx': 1, 'active_votes': 64.5})
        for i in range(repetitions):
            seat = seat_gen()
            self.assertEqual(next(seat), {'idx': 0, 'active_votes': 135})
            self.assertEqual(next(seat), {'idx': 1, 'active_votes': 129})
            self.assertEqual(next(seat), {'idx': 0, 'active_votes':  67.5})
            #the sequence continues beyond the specified 3 seats as follows:
            self.assertEqual(next(seat), {'idx': 1, 'active_votes':  64.5})
            self.assertEqual(next(seat), {'idx': 0, 'active_votes':  45})
            self.assertEqual(next(seat), {'idx': 1, 'active_votes':  43})
            self.assertEqual(next(seat), {'idx': 2, 'active_votes':  36})
            self.assertEqual(next(seat), {'idx': 0, 'active_votes':  33.75})
            self.assertEqual(next(seat), {'idx': 1, 'active_votes':  32.25})
            self.assertEqual(next(seat), {'idx': 0, 'active_votes':  27})

    def test_seat_generator_div_with_prior(self):
        #Arrange
        votes = [135,129,36]
        repetitions = 2 # Make sure the process is repeatable

        #Act
        seats, seat_gen, last_in, next_in = apportion.apportion1d_general(
            v_votes=votes,
            num_total_seats=6,
            prior_allocations=[2,1,0],
            rule=division_rules.dhondt_gen,
            type_of_rule="Division"
        )

        #Assert
        self.assertEqual(seats, [3,3,0])
        self.assertEqual(last_in, {'idx': 1, 'active_votes': 43})
        self.assertEqual(next_in, {'idx': 2, 'active_votes': 36})
        for i in range(repetitions):
            seat = seat_gen()
            self.assertEqual(next(seat), {'idx': 1, 'active_votes': 64.5})
            self.assertEqual(next(seat), {'idx': 0, 'active_votes': 45})
            self.assertEqual(next(seat), {'idx': 1, 'active_votes': 43})
            #the sequence continues beyond the specified 3 seats as follows:
            self.assertEqual(next(seat), {'idx': 2, 'active_votes': 36})
            self.assertEqual(next(seat), {'idx': 0, 'active_votes': 33.75})
            self.assertEqual(next(seat), {'idx': 1, 'active_votes': 32.25})
            self.assertEqual(next(seat), {'idx': 0, 'active_votes': 27})
