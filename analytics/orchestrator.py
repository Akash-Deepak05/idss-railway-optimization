"""
Analytics orchestrator: predictive (conflict risk) + prescriptive (recommendations)
Runs on a cadence, querying the digital twin, invoking the hybrid optimizer,
then publishing recommendations for the HMI and logging KPIs.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

from MVP_IDSS_digital_twin import twin_handle

logger = logging.getLogger(__name__)

class RecommendationBus:
    """In-memory bus for recommendations (replace with Kafka in prod)"""
    def __init__(self):
        self._latest: List[Dict[str, Any]] = []
        self._last_updated: str = datetime.now().isoformat()
    
    def publish(self, recs: List[Dict[str, Any]]):
        self._latest = recs
        self._last_updated = datetime.now().isoformat()
    
    def get(self) -> Dict[str, Any]:
        return {"recommendations": self._latest, "last_updated": self._last_updated}

rec_bus = RecommendationBus()

async def run_prescriptive_loop(optimize_func, interval_seconds: int = 30):
    """Main analytics loop: pull snapshot, optimize, publish"""
    logger.info(f"Starting prescriptive loop on {interval_seconds}s interval")
    while True:
        try:
            snapshot = twin_handle.get_network_snapshot()
            trains, sections = optimize_func.prepare_inputs(snapshot)
            result = optimize_func.optimize(trains, sections)
            rec_bus.publish(result.recommendations)
        except Exception as e:
            logger.error(f"Analytics loop error: {e}")
        finally:
            await asyncio.sleep(interval_seconds)

