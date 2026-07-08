"""Real-time World Cup transportation and transit coordination service.

This module provides data models and status monitoring feeds for public transit,
buses, and shuttle coordinates servicing the target World Cup 2026 stadiums.
"""

import random  # nosec
from typing import Dict, Any, List


class TransportService:
    """Manages match-day transport schedule timelines and shuttle updates."""

    @staticmethod
    def get_transit_status(stadium: str, seed_value: int = 12) -> List[Dict[str, Any]]:
        """Generates real-time transit routes coordinates and capacities.

        Args:
            stadium: The name of the target stadium.
            seed_value: Seed value to maintain status trends.

        Returns:
            A list of dictionary objects representing transit statuses.
        """
        random.seed(hash(stadium) + seed_value)

        # Base transit routes per stadium
        stadium_routes = {
            "MetLife Stadium": [
                {"type": "Train", "route": "Meadowlands Rail Link", "icon": "🚇", "frequency": "Every 6 mins"},
                {"type": "Bus", "route": "Port Authority Express Shuttle", "icon": "🚌", "frequency": "Every 10 mins"},
                {"type": "Parking", "route": "Lot E Park & Ride Shuttle", "icon": "🚐", "frequency": "Every 5 mins"}
            ],
            "Estadio Azteca": [
                {"type": "Light Rail", "route": "Tren Ligero (Tasqueña Line)", "icon": "🚇", "frequency": "Every 8 mins"},
                {"type": "Taxi", "route": "Tlalpan Official Drop-off Area", "icon": "🚕", "frequency": "Continuous"},
                {"type": "Parking", "route": "Calzada de Tlalpan Shuttle", "icon": "🚐", "frequency": "Every 10 mins"}
            ],
            "BC Place": [
                {"type": "SkyTrain", "route": "Expo Line (Stadium Station)", "icon": "🚇", "frequency": "Every 4 mins"},
                {"type": "Bus", "route": "Georgia St Routes (2, 17, 22)", "icon": "🚌", "frequency": "Every 12 mins"},
                {"type": "Bicycle", "route": "Gate F Free Valet Parking", "icon": "🚲", "frequency": "N/A"}
            ]
        }

        routes = stadium_routes.get(stadium, [])
        for r in routes:
            # Randomly perturb transit status based on seed
            status_roll = random.random()
            if status_roll > 0.8:
                r["status"] = "Delayed"
                r["delay"] = f"{random.randint(10, 25)} mins"
                r["color"] = "#ff4b4b"  # Red
            elif status_roll > 0.5:
                r["status"] = "Congested"
                r["delay"] = f"{random.randint(5, 10)} mins"
                r["color"] = "#ffa500"  # Orange
            else:
                r["status"] = "On Schedule"
                r["delay"] = "None"
                r["color"] = "#00c853"  # Green

        return routes
