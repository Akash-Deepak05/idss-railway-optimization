"""
Simplified IDSS Optimizer (without OR-Tools for Windows compatibility)
Uses basic heuristics instead of CP-SAT for MVP demonstration
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TrainPriority(Enum):
    MAIL_EXPRESS = 1
    PASSENGER = 2  
    FREIGHT = 3
    MAINTENANCE = 4

class OptimizationObjective(Enum):
    MINIMIZE_DELAY = "minimize_total_delay"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"

@dataclass
class Train:
    train_id: str
    train_number: str
    train_type: str
    priority: TrainPriority
    current_location: float
    destination: float
    scheduled_arrival: datetime
    current_speed: float = 0.0
    max_speed: float = 100.0

@dataclass
class Section:
    section_id: str
    start_km: float
    end_km: float
    max_speed: float
    capacity: int
    current_occupancy: List[str]

@dataclass
class OptimizationResult:
    success: bool
    objective_value: float
    recommendations: List[Dict[str, Any]]
    explanation: str
    confidence_score: float
    computation_time: float

class SimpleOptimizer:
    """Simplified optimizer using heuristics"""
    
    def __init__(self, objective: OptimizationObjective = OptimizationObjective.MINIMIZE_DELAY):
        self.objective = objective
        
    def hybrid_optimize(self, trains: List[Train], sections: List[Section]) -> OptimizationResult:
        """Simple heuristic optimization"""
        start_time = datetime.now()
        recommendations = []
        
        # Sort trains by priority
        priority_trains = sorted(trains, key=lambda t: t.priority.value)
        
        for train in priority_trains:
            # Simple heuristic rules
            recommendation = self._generate_recommendation(train, trains, sections)
            if recommendation:
                recommendations.append(recommendation)
        
        computation_time = (datetime.now() - start_time).total_seconds()
        
        return OptimizationResult(
            success=True,
            objective_value=len(recommendations),
            recommendations=recommendations,
            explanation=f"Heuristic optimization generated {len(recommendations)} recommendations",
            confidence_score=0.75,
            computation_time=computation_time
        )
    
    def _generate_recommendation(self, train: Train, all_trains: List[Train], sections: List[Section]) -> Dict[str, Any]:
        """Generate recommendation for a specific train"""
        
        # Check if train has low priority and others are nearby
        if train.priority.value > 2:  # Lower priority (freight)
            nearby_trains = [t for t in all_trains if t.train_id != train.train_id and 
                           abs(t.current_location - train.current_location) < 10.0]
            
            if any(t.priority.value < train.priority.value for t in nearby_trains):
                return {
                    'train_id': train.train_id,
                    'action': 'HOLD',
                    'duration_minutes': 5,
                    'reason': 'Lower priority - give way to higher priority trains',
                    'priority_impact': train.priority.value
                }
        
        # Check for speed adjustment
        if train.current_speed > 60:
            return {
                'train_id': train.train_id,
                'action': 'SPEED_CHANGE',
                'duration_minutes': 0,
                'target_speed': 50,
                'reason': 'Speed optimization for safety',
                'priority_impact': train.priority.value
            }
        
        return None

# Example usage
if __name__ == "__main__":
    trains = [
        Train("T001", "12345", "EXPRESS", TrainPriority.MAIL_EXPRESS, 100.0, 200.0, datetime.now()),
        Train("T002", "56789", "PASSENGER", TrainPriority.PASSENGER, 110.0, 200.0, datetime.now()),
        Train("T003", "99999", "FREIGHT", TrainPriority.FREIGHT, 105.0, 200.0, datetime.now())
    ]
    
    sections = [
        Section("SEC001", 90.0, 120.0, 80.0, 2, ["T001", "T002"])
    ]
    
    optimizer = SimpleOptimizer()
    result = optimizer.hybrid_optimize(trains, sections)
    
    print(f"Success: {result.success}")
    print(f"Recommendations: {len(result.recommendations)}")
    for rec in result.recommendations:
        print(f"  {rec['action']} for {rec['train_id']}: {rec['reason']}")
