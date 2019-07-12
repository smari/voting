# coding:utf-8
from unittest import TestCase
import logging

import solution_util

class TestExistanceCheck(TestCase):

    def setUp(self):
        pass

    def test_solution_does_not_exist(self):
        #Arrange
        votes = [[10,  0],
                 [ 0, 20]]
        prior = [[0,0],
                 [0,0]]
        row_sums =      [2,
                         2]
        col_sums = [1,3]

        #Act
        exists = solution_util.solution_exists(votes, row_sums, col_sums, prior)

        #Assert
        self.assertFalse(exists)

    def test_solution_exists(self):
        #Arrange
        votes = [[10,  0],
                 [ 0, 20]]
        prior = [[0,0],
                 [0,0]]
        row_sums =      [2,
                         2]
        col_sums = [2,2]

        #Act
        exists = solution_util.solution_exists(votes, row_sums, col_sums, prior)

        #Assert
        self.assertTrue(exists)
