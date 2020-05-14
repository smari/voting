import unittest

import division_rules
import apportion

class TestElection(unittest.TestCase):

    def test_invalid(self):
        with self.assertRaises(ValueError):
            apportion.apportion1d(
                v_votes=[0,10],
                num_total_seats=1,
                prior_allocations=[0,0],
                divisor_gen=division_rules.dhondt_gen,
                invalid=[1]
            )

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
        results3, _, _ = apportion.apportion1d_by_quota(
            num_total_seats=3,
            v_votes=votes,
            quota_rule=division_rules.hare,
            prior_allocations=[],
        )
        results4, _, _ = apportion.apportion1d_by_quota(
            num_total_seats=4,
            v_votes=votes,
            quota_rule=division_rules.hare,
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
        seats, seat_gen, _, _ = apportion.apportion1d_general(
            v_votes=votes,
            num_total_seats=3,
            prior_allocations=[],
            rule=division_rules.hare,
            type_of_rule="Quota"
        )
        seat = [[],[]]
        for i in range(repetitions):
            gen = seat_gen()
            for j in range(3):
                seat[i].append(next(gen))

        #Assert
        self.assertEqual(seats, [1,1,1])
        for i in range(repetitions):
            self.assertEqual(seat[i][0], {'idx': 0, 'active_votes': 135})
            self.assertEqual(seat[i][1], {'idx': 1, 'active_votes': 129})
            self.assertEqual(seat[i][2], {'idx': 2, 'active_votes':  36})

    def test_seat_generator_div(self):
        #Arrange
        votes = [135,129,36]
        repetitions = 2 # Make sure the process is repeatable

        #Act
        seats, seat_gen, _, _ = apportion.apportion1d_general(
            v_votes=votes,
            num_total_seats=3,
            prior_allocations=[],
            rule=division_rules.dhondt_gen,
            type_of_rule="Division"
        )
        seat = [[],[]]
        for i in range(repetitions):
            gen = seat_gen()
            for j in range(10):
                seat[i].append(next(gen))

        #Assert
        self.assertEqual(seats, [2,1,0])
        for i in range(repetitions):
            self.assertEqual(seat[i][0], {'idx': 0, 'active_votes': 135})
            self.assertEqual(seat[i][1], {'idx': 1, 'active_votes': 129})
            self.assertEqual(seat[i][2], {'idx': 0, 'active_votes':  67.5})
            self.assertEqual(seat[i][3], {'idx': 1, 'active_votes':  64.5})
            self.assertEqual(seat[i][4], {'idx': 0, 'active_votes':  45})
            self.assertEqual(seat[i][5], {'idx': 1, 'active_votes':  43})
            self.assertEqual(seat[i][6], {'idx': 2, 'active_votes':  36})
            self.assertEqual(seat[i][7], {'idx': 0, 'active_votes':  33.75})
            self.assertEqual(seat[i][8], {'idx': 1, 'active_votes':  32.25})
            self.assertEqual(seat[i][9], {'idx': 0, 'active_votes':  27})
