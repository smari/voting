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
