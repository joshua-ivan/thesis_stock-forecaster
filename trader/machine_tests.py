from trader.machine import MachineInvestor
from trader.position import Position
from unittest.mock import Mock, call
from datetime import datetime
import unittest


class MachineInvestorTests(unittest.TestCase):
    def test_check_open_positions(self):
        mock_fetcher = Mock()
        mi = MachineInvestor(start_date='2022-08-15', end_date='2022-08-16', pf=mock_fetcher)
        mi.close_position = Mock()
        mi.open_positions = [
            Position('MOCK', 'SHORT', quantity=5, price=1000.00, date_time='2022-08-15 10:00:00-04:00'),
            Position('MOCK', 'SHORT', quantity=5, price=1000.00, date_time='2022-08-15 11:00:00-04:00'),
            Position('MOCK', 'SHORT', quantity=5, price=1000.00, date_time='2022-08-15 12:00:00-04:00'),
            Position('MOCK', 'LONG', quantity=5, price=1000.00, date_time='2022-08-15 13:00:00-04:00'),
            Position('MOCK', 'LONG', quantity=5, price=1000.00, date_time='2022-08-15 14:00:00-04:00'),
            Position('MOCK', 'LONG', quantity=5, price=1000.00, date_time='2022-08-15 15:00:00-04:00')
        ]
        mock_fetcher.get_price.side_effect = iter([2000.00, 1000.00, 500.00, 500.00, 1000.00, 2000.00])

        mi.check_open_positions('2022-08-15 16:00:00-04:00')
        mi.close_position.assert_has_calls([
            call(5000, 5), call(-2500, 3), call(2500, 2), call(-5000, 0)
        ])

    def test_close_position(self):
        mi = MachineInvestor(start_date='2022-08-15', end_date='2022-08-16')
        mi.open_positions = [
            Position('MOCK', 'SHORT', 5, 10000.00, '2022-08-15 10:00:00-04:00'),
            Position('MOCK', 'LONG', 5, 1000.00, '2022-08-15 11:00:00-04:00')
        ]

        expected_values = [49500.00, 45000.00]
        for i in range(0, len(expected_values)):
            opening_value = mi.open_positions[0].quantity * mi.open_positions[0].price
            closing_value = mi.open_positions[0].quantity * 100.00
            position = mi.open_positions[0]

            raw_profit = 0.0
            if position.leverage_type == 'SHORT':
                raw_profit = opening_value - closing_value
            elif position.leverage_type == 'LONG':
                raw_profit = closing_value - opening_value

            mi.close_position(raw_profit, 0)
            self.assertEqual(mi.portfolio_value, expected_values[i])

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
        mi = MachineInvestor(start_date='2022-09-07', end_date='2022-09-08')
        mi.run_simulation()
