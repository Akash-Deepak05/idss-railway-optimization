"""
Mock Data Integration Feed
Simulates real-time data from railway systems for MVP demo
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class MockTrain:
    train_id: str
    train_number: str
    train_type: str
    priority: int
    current_node: str
    current_speed: float
    target_speed: float
    scheduled_arrival: datetime
    delay_minutes: float = 0.0
    
@dataclass
class MockSignal:
    signal_id: str
    current_aspect: str
    last_change: datetime
    failure_probability: float = 0.01

class MockRailwayDataFeed:
    """Generates realistic mock data for pilot section"""
    
    def __init__(self):
        self.trains = self._initialize_mock_trains()
        self.signals = self._initialize_mock_signals()
        self.nodes = ["STN_A", "SIG_001", "JUN_001", "SIG_002", "STN_B"]
        self.running = False
        
    def _initialize_mock_trains(self) -> List[MockTrain]:
        """Create initial train fleet"""
        base_time = datetime.now()
        return [
            MockTrain("T001", "12345", "EXPRESS", 1, "STN_A", 0.0, 80.0, base_time + timedelta(minutes=30)),
            MockTrain("T002", "56789", "PASSENGER", 2, "SIG_001", 45.0, 60.0, base_time + timedelta(minutes=25)),
            MockTrain("T003", "99999", "FREIGHT", 3, "JUN_001", 30.0, 50.0, base_time + timedelta(minutes=45), delay_minutes=5.0),
            MockTrain("T004", "11111", "PASSENGER", 2, "STN_B", 0.0, 70.0, base_time + timedelta(minutes=20))
        ]
        
    def _initialize_mock_signals(self) -> List[MockSignal]:
        """Create initial signal states"""
        return [
            MockSignal("SIG_001", "YELLOW", datetime.now()),
            MockSignal("SIG_002", "GREEN", datetime.now())
        ]
        
    def _simulate_train_movement(self, train: MockTrain) -> None:
        """Simulate realistic train movement"""
        # Random speed variations
        speed_variation = random.uniform(-5.0, 5.0)
        train.current_speed = max(0, min(train.target_speed + speed_variation, 120.0))
        
        # Simulate delays
        if random.random() < 0.1:  # 10% chance of new delay
            additional_delay = random.uniform(0.5, 3.0)
            train.delay_minutes += additional_delay
            logger.info(f"Train {train.train_id} experienced {additional_delay:.1f} min delay")
            
        # Move between nodes occasionally
        if random.random() < 0.3:  # 30% chance of node change
            current_idx = self.nodes.index(train.current_node) if train.current_node in self.nodes else 0
            if current_idx < len(self.nodes) - 1:
                train.current_node = self.nodes[current_idx + 1]
                logger.info(f"Train {train.train_id} moved to {train.current_node}")
                
    def _simulate_signal_changes(self, signal: MockSignal) -> None:
        """Simulate signal aspect changes"""
        aspects = ["RED", "YELLOW", "GREEN", "DOUBLE_YELLOW"]
        
        # Change signal aspect occasionally
        if random.random() < 0.2:  # 20% chance
            signal.current_aspect = random.choice(aspects)
            signal.last_change = datetime.now()
            
        # Simulate failures
        if random.random() < signal.failure_probability:
            signal.current_aspect = "RED"  # Default to safe
            logger.warning(f"Signal {signal.signal_id} failure - set to RED")
            
    def generate_snapshot(self) -> Dict[str, Any]:
        """Generate current system snapshot"""
        # Update train positions and signals
        for train in self.trains:
            self._simulate_train_movement(train)
            
        for signal in self.signals:
            self._simulate_signal_changes(signal)
            
        # Format data for digital twin
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "trains": [
                {
                    "train_id": train.train_id,
                    "train_number": train.train_number,
                    "train_type": train.train_type,
                    "priority": train.priority,
                    "current_node": train.current_node,
                    "current_speed": round(train.current_speed, 1),
                    "target_speed": train.target_speed,
                    "scheduled_arrival": train.scheduled_arrival.isoformat(),
                    "delay_minutes": round(train.delay_minutes, 1)
                } for train in self.trains
            ],
            "signals": [
                {
                    "signal_id": signal.signal_id,
                    "aspect": signal.current_aspect,
                    "last_change": signal.last_change.isoformat()
                } for signal in self.signals
            ],
            "section_status": {
                "total_trains": len(self.trains),
                "delayed_trains": len([t for t in self.trains if t.delay_minutes > 0]),
                "average_delay": round(sum(t.delay_minutes for t in self.trains) / len(self.trains), 1)
            }
        }
        
        return snapshot
        
    async def start_feed(self, callback_func, interval_seconds: float = 1.0):
        """Start continuous data feed"""
        logger.info(f"Starting mock data feed with {interval_seconds}s interval")
        self.running = True
        
        try:
            while self.running:
                snapshot = self.generate_snapshot()
                await callback_func(snapshot)
                await asyncio.sleep(interval_seconds)
        except Exception as e:
            logger.error(f"Error in data feed: {e}")
        finally:
            logger.info("Mock data feed stopped")
            
    def stop_feed(self):
        """Stop the data feed"""
        self.running = False

# Example usage and testing
async def print_snapshot(snapshot: Dict[str, Any]):
    """Example callback function"""
    print(f"Snapshot at {snapshot['timestamp'][:19]}:")
    print(f"  Trains: {snapshot['section_status']['total_trains']}")
    print(f"  Delayed: {snapshot['section_status']['delayed_trains']}")
    print(f"  Avg Delay: {snapshot['section_status']['average_delay']} min")
    
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    feed = MockRailwayDataFeed()
    
    print("Starting mock railway data feed...")
    print("Press Ctrl+C to stop")
    
    try:
        asyncio.run(feed.start_feed(print_snapshot, 2.0))
    except KeyboardInterrupt:
        print("\nStopping feed...")
        feed.stop_feed()
