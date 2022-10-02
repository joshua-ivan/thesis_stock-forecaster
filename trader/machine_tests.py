from trader.machine import MachineInvestor
from trader.position import Position
from unittest.mock import Mock, call
from datetime import datetime
import unittest


class MachineInvestorTests(unittest.TestCase):
    def test_new_open_position(self):
        mi = MachineInvestor(start_date='2022-08-22', end_date='2022-08-23')
        mi.new_open_position('MOCK', sentiment=-1, forecast=1, price=5, position_datetime='2022-08-23 09:30:00-04:00')
        mi.new_open_position('MOCK', sentiment=0, forecast=1, price=5, position_datetime='2022-08-23 09:31:00-04:00')
        mi.new_open_position('MOCK', sentiment=1, forecast=1, price=5, position_datetime='2022-08-23 09:32:00-04:00')
        mi.new_open_position('MOCK', sentiment=-1, forecast=0, price=5, position_datetime='2022-08-23 09:33:00-04:00')
        mi.new_open_position('MOCK', sentiment=0, forecast=0, price=5, position_datetime='2022-08-23 09:34:00-04:00')
        mi.new_open_position('MOCK', sentiment=1, forecast=0, price=5, position_datetime='2022-08-23 09:35:00-04:00')
        mi.new_open_position('MOCK', sentiment=-1, forecast=-1, price=5, position_datetime='2022-08-23 09:36:00-04:00')
        mi.new_open_position('MOCK', sentiment=0, forecast=-1, price=5, position_datetime='2022-08-23 09:37:00-04:00')
        mi.new_open_position('MOCK', sentiment=1, forecast=-1, price=5, position_datetime='2022-08-23 09:38:00-04:00')

        expected_positions = [
            Position('MOCK', 'LONG', 2000, 5, '2022-08-23 09:30:00-04:00'),
            Position('MOCK', 'SHORT', 2000, 5, '2022-08-23 09:38:00-04:00')
        ]
        for i in range(0, len(expected_positions)):
            self.assertEqual(mi.open_positions[i], expected_positions[i])

    def test_run_simulation(self):
        mi = MachineInvestor(start_date='2022-08-15', end_date='2022-08-20')
        # mi.run_simulation()
