"""
ICT Confluence Scoring for AXIOM Day Trading

Scores ICT setups based on how many confluence factors are present:
- Order Block (OB): +2
- Fair Value Gap (FVG): +2
- Liquidity Sweep: +2
- Optimal Trade Entry (OTE): +2
- Discount Zone (for longs) / Premium Zone (for shorts): +1
- Change of Character (ChoCh): +1

Maximum score: 10
Minimum score to trade: 3
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class ICTConfluenceScorer:
    """Score ICT setups based on confluence of concepts."""

    def __init__(self):
        self.max_score = 10
        self.min_trading_score = 3

    def score_setup(
        self,
        at_order_block: bool = False,
        in_fvg: bool = False,
        liquidity_sweep: bool = False,
        in_ote_zone: bool = False,
        in_discount_zone: bool = False,
        in_premium_zone: bool = False,
        choch_detected: bool = False,
        direction: str = "LONG"
    ) -> Tuple[int, List[str]]:
        """
        Calculate ICT confluence score for a setup.

        Args:
            at_order_block: Price at unmitigated Order Block
            in_fvg: Price inside unfilled Fair Value Gap
            liquidity_sweep: Recent liquidity sweep detected
            in_ote_zone: Price in Optimal Trade Entry zone (62-79% retrace)
            in_discount_zone: Price in discount zone (below 50% equilibrium)
            in_premium_zone: Price in premium zone (above 50% equilibrium)
            choch_detected: Change of Character detected on 5min
            direction: "LONG" or "SHORT"

        Returns:
            Tuple of (score: int, factors: List[str])
        """
        score = 0
        factors = []

        # Order Block: +2
        if at_order_block:
            score += 2
            factors.append("OB")

        # Fair Value Gap: +2
        if in_fvg:
            score += 2
            factors.append("FVG")

        # Liquidity Sweep: +2
        if liquidity_sweep:
            score += 2
            factors.append("Sweep")

        # Optimal Trade Entry (OTE): +2
        if in_ote_zone:
            score += 2
            factors.append("OTE")

        # Discount Zone (longs) or Premium Zone (shorts): +1
        if direction.upper() == "LONG" and in_discount_zone:
            score += 1
            factors.append("Discount")
        elif direction.upper() == "SHORT" and in_premium_zone:
            score += 1
            factors.append("Premium")

        # Change of Character: +1 (highest priority signal)
        if choch_detected:
            score += 1
            factors.append("ChoCh")

        # Cap at max score
        score = min(score, self.max_score)

        logger.debug(f"ICT Confluence Score: {score}/10 | Factors: {' + '.join(factors)}")

        return score, factors

    def is_tradable(self, score: int) -> bool:
        """
        Determine if setup meets minimum confluence threshold.

        Args:
            score: ICT confluence score (0-10)

        Returns:
            bool: True if score >= minimum trading threshold
        """
        return score >= self.min_trading_score

    def get_factor_string(self, factors: List[str]) -> str:
        """
        Format factor list into readable string.

        Args:
            factors: List of factor abbreviations

        Returns:
            Formatted string like "OB + FVG + OTE"
        """
        return " + ".join(factors) if factors else "None"


# Initialize global scorer
ict_scorer = ICTConfluenceScorer()


def calculate_ict_score(
    setup_data: Dict,
    direction: str = "LONG"
) -> Tuple[int, List[str]]:
    """
    Convenience function to calculate ICT score from setup dictionary.

    Args:
        setup_data: Dictionary with ICT context from chart
        direction: "LONG" or "SHORT"

    Returns:
        Tuple of (score, factors)

    Example setup_data:
    {
        "at_order_block": True,
        "in_fvg": False,
        "liquidity_sweep": True,
        "in_ote_zone": True,
        "in_discount_zone": False,
        "in_premium_zone": False,
        "choch_detected": False
    }
    """
    return ict_scorer.score_setup(
        at_order_block=setup_data.get("at_order_block", False),
        in_fvg=setup_data.get("in_fvg", False),
        liquidity_sweep=setup_data.get("liquidity_sweep", False),
        in_ote_zone=setup_data.get("in_ote_zone", False),
        in_discount_zone=setup_data.get("in_discount_zone", False),
        in_premium_zone=setup_data.get("in_premium_zone", False),
        choch_detected=setup_data.get("choch_detected", False),
        direction=direction
    )
