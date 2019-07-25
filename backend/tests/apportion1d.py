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
                full=[1]
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
