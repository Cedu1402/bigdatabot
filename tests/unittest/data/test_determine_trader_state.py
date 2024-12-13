import unittest

from data.combine_price_trades import determine_trader_state, TraderState


class TestRunner(unittest.TestCase):
    def test_just_bought(self):
        """Test cases where trader just bought tokens"""
        test_cases = [
            # (net_position, cumulative_position, previous_position, description)
            (1.0, 1.0, 0.0, "first buy"),
            (0.5, 1.5, 1.0, "additional buy"),
            (0.1, 10.0, 9.9, "small buy with large position"),
            (100.0, 100.0, 0.0, "large initial buy"),
        ]

        for net_pos, cum_pos, prev_pos, desc in test_cases:
            with self.subTest(description=desc):
                state = determine_trader_state(net_pos, cum_pos, prev_pos)
                self.assertEqual(state, TraderState.JUST_BOUGHT)

    def test_just_sold(self):
        """Test cases where trader sold some but not all tokens"""
        test_cases = [
            # (net_position, cumulative_position, previous_position, description)
            (-0.5, 0.5, 1.0, "partial sell"),
            (-0.1, 9.9, 10.0, "small sell from large position"),
            (-5.0, 5.0, 10.0, "sell half position"),
            (-0.9, 0.1, 1.0, "sell most but not all"),
        ]

        for net_pos, cum_pos, prev_pos, desc in test_cases:
            with self.subTest(description=desc):
                state = determine_trader_state(net_pos, cum_pos, prev_pos)
                self.assertEqual(state, TraderState.JUST_SOLD)

    def test_nuked(self):
        """Test cases where trader sold entire position"""
        test_cases = [
            # (net_position, cumulative_position, previous_position, description)
            (-1.0, 0.0, 1.0, "exact nuke"),
            (-10.0, 0.0, 10.0, "large position nuke"),
            (-1.0, 0.0, 0.9, "nuke with rounding difference"),
            (-1.1, -0.1, 1.0, "oversold nuke"),
        ]

        for net_pos, cum_pos, prev_pos, desc in test_cases:
            with self.subTest(description=desc):
                state = determine_trader_state(net_pos, cum_pos, prev_pos)
                self.assertEqual(state, TraderState.NUKED)

    def test_still_holds(self):
        """Test cases where trader continues to hold position"""
        test_cases = [
            # (net_position, cumulative_position, previous_position, description)
            (0.0, 1.0, 1.0, "holding steady"),
            (0.0, 10.0, 10.0, "holding large position"),
            (0.0, 0.1, 0.1, "holding small position"),
            (0.0, 5.0, 5.0, "mid-size holding"),
        ]

        for net_pos, cum_pos, prev_pos, desc in test_cases:
            with self.subTest(description=desc):
                state = determine_trader_state(net_pos, cum_pos, prev_pos)
                self.assertEqual(state, TraderState.STILL_HOLDS)

    def test_no_action(self):
        """Test cases where trader has no position or activity"""
        test_cases = [
            # (net_position, cumulative_position, previous_position, description)
            (0.0, 0.0, 0.0, "never traded"),
            (0.0, -0.1, 0.0, "slight negative from rounding"),
            (0.0, 0.0, 1.0, "after position closed"),
        ]

        for net_pos, cum_pos, prev_pos, desc in test_cases:
            with self.subTest(description=desc):
                state = determine_trader_state(net_pos, cum_pos, prev_pos)
                self.assertEqual(state, TraderState.NO_ACTION)

    def test_boundary_conditions(self):
        """Test edge cases and boundary conditions"""
        test_cases = [
            # (net_position, cumulative_position, previous_position, expected_state, description)
            (0.000001, 0.000001, 0.0, TraderState.JUST_BOUGHT, "tiny buy"),
            (-0.000001, 0.999999, 1.0, TraderState.JUST_SOLD, "tiny sell"),
            (-1.0, -0.000001, 1.0, TraderState.NUKED, "nuke with tiny overflow"),
            (0.0, 0.000001, 0.000001, TraderState.STILL_HOLDS, "holding tiny amount"),
            (0.0, 0.0, 0.000001, TraderState.NO_ACTION, "no action after tiny position"),
        ]

        for net_pos, cum_pos, prev_pos, expected, desc in test_cases:
            with self.subTest(description=desc):
                state = determine_trader_state(net_pos, cum_pos, prev_pos)
                self.assertEqual(state, expected)

    def test_invalid_inputs(self):
        """Test handling of invalid or unexpected inputs"""
        test_cases = [
            # (net_position, cumulative_position, previous_position, description)
            (float('nan'), 1.0, 1.0, "NaN net position"),
            (1.0, float('nan'), 1.0, "NaN cumulative position"),
            (1.0, 1.0, float('nan'), "NaN previous position"),
            (float('inf'), 1.0, 1.0, "Infinite net position"),
            (-float('inf'), 1.0, 1.0, "Negative infinite net position"),
        ]

        for net_pos, cum_pos, prev_pos, desc in test_cases:
            with self.subTest(description=desc):
                with self.assertRaises(Exception, msg=f"Should handle {desc}"):
                    determine_trader_state(net_pos, cum_pos, prev_pos)


if __name__ == '__main__':
    unittest.main()
