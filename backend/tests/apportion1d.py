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
