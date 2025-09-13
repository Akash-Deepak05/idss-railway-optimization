"""
Predictive and Prescriptive Analytics Engine
Moves from reactive to proactive traffic management
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConflictPrediction:
    """Predicted conflict between trains or at infrastructure"""
    conflict_id: str
    conflict_type: str  # HEADWAY, PLATFORM, SIGNAL, JUNCTION
    trains_involved: List[str]
    location: str
    predicted_time: datetime
    probability: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    estimated_delay_minutes: float

@dataclass
class PrescriptiveAction:
    """Recommended action to prevent or resolve conflicts"""
    action_id: str
    action_type: str  # HOLD, REROUTE, SPEED_CHANGE, PRIORITY_OVERRIDE
    target_train: str
    parameters: Dict[str, Any]  # action-specific parameters
    expected_benefit: str
    confidence: float
    urgency: str  # LOW, MEDIUM, HIGH

class ConflictPredictor:
    """AI-powered conflict prediction system"""
    
    def __init__(self, prediction_horizon_minutes: int = 30):
        self.horizon = prediction_horizon_minutes
        self.conflict_history = []
        
    def predict_conflicts(self, snapshot: Dict[str, Any]) -> List[ConflictPrediction]:
        """Predict potential conflicts in the next time horizon"""
        predictions = []
        trains = snapshot.get('trains', [])
        
        # Headway conflicts
        headway_conflicts = self._predict_headway_conflicts(trains)
        predictions.extend(headway_conflicts)
        
        # Platform conflicts
        platform_conflicts = self._predict_platform_conflicts(trains)
        predictions.extend(platform_conflicts)
        
        # Signal conflicts
        signal_conflicts = self._predict_signal_conflicts(trains, snapshot.get('signals', []))
        predictions.extend(signal_conflicts)
        
        return predictions
        
    def _predict_headway_conflicts(self, trains: List[Dict[str, Any]]) -> List[ConflictPrediction]:
        """Predict trains getting too close to each other"""
        conflicts = []
        
        # Group trains by current section/node
        node_groups = {}
        for train in trains:
            node = train.get('current_node', 'UNKNOWN')
            if node not in node_groups:
                node_groups[node] = []
            node_groups[node].append(train)
            
        # Check for potential conflicts in each section
        for node, node_trains in node_groups.items():
            if len(node_trains) > 1:
                # Sort by speed to find fastest approaching slowest
                node_trains.sort(key=lambda t: t.get('current_speed', 0), reverse=True)
                
                for i in range(len(node_trains) - 1):
                    fast_train = node_trains[i]
                    slow_train = node_trains[i + 1]
                    
                    speed_diff = fast_train.get('current_speed', 0) - slow_train.get('current_speed', 0)
                    if speed_diff > 10:  # Fast train catching up
                        # Estimate time to conflict
                        time_to_conflict = 300 / max(speed_diff, 1)  # Simplified calculation
                        probability = min(0.9, speed_diff / 30.0)
                        
                        conflict = ConflictPrediction(
                            conflict_id=f"HEADWAY_{fast_train['train_id']}_{slow_train['train_id']}",
                            conflict_type="HEADWAY",
                            trains_involved=[fast_train['train_id'], slow_train['train_id']],
                            location=node,
                            predicted_time=datetime.now() + timedelta(seconds=time_to_conflict),
                            probability=probability,
                            severity="HIGH" if probability > 0.7 else "MEDIUM",
                            estimated_delay_minutes=max(2.0, speed_diff * 0.2)
                        )
                        conflicts.append(conflict)
                        
        return conflicts
        
    def _predict_platform_conflicts(self, trains: List[Dict[str, Any]]) -> List[ConflictPrediction]:
        """Predict platform occupancy conflicts"""
        conflicts = []
        
        # Find trains at stations
        station_trains = [t for t in trains if t.get('current_node', '').startswith('STN_')]
        
        # Group by station
        stations = {}
        for train in station_trains:
            station = train.get('current_node')
            if station not in stations:
                stations[station] = []
            stations[station].append(train)
            
        # Check for overcrowding
        for station, trains_at_station in stations.items():
            if len(trains_at_station) > 2:  # Assume 2 platform capacity
                conflict = ConflictPrediction(
                    conflict_id=f"PLATFORM_{station}_{len(trains_at_station)}",
                    conflict_type="PLATFORM",
                    trains_involved=[t['train_id'] for t in trains_at_station],
                    location=station,
                    predicted_time=datetime.now() + timedelta(minutes=5),
                    probability=0.8,
                    severity="HIGH",
                    estimated_delay_minutes=5.0 * (len(trains_at_station) - 2)
                )
                conflicts.append(conflict)
                
        return conflicts
        
    def _predict_signal_conflicts(self, trains: List[Dict[str, Any]], 
                                signals: List[Dict[str, Any]]) -> List[ConflictPrediction]:
        """Predict signal-related conflicts"""
        conflicts = []
        
        # Find trains approaching RED signals
        red_signals = [s for s in signals if s.get('aspect') == 'RED']
        
        for signal in red_signals:
            signal_id = signal['signal_id']
            
            # Find trains that might be approaching this signal
            approaching_trains = []
            for train in trains:
                # Simplified: assume train is approaching if speed > 0 and not at station
                current_node = train.get('current_node', '')
                current_speed = train.get('current_speed', 0)
                
                if current_speed > 10 and not current_node.startswith('STN_'):
                    approaching_trains.append(train)
                    
            if approaching_trains:
                # Create conflict prediction for signal approach
                for train in approaching_trains:
                    # Estimate braking distance and time
                    speed_kmh = train.get('current_speed', 0)
                    if speed_kmh > 20:  # Only if significant speed
                        braking_time = speed_kmh / 20  # Simplified: seconds to stop
                        
                        conflict = ConflictPrediction(
                            conflict_id=f"SIGNAL_{signal_id}_{train['train_id']}",
                            conflict_type="SIGNAL",
                            trains_involved=[train['train_id']],
                            location=signal_id,
                            predicted_time=datetime.now() + timedelta(seconds=braking_time),
                            probability=0.6 if speed_kmh > 40 else 0.3,
                            severity="HIGH" if speed_kmh > 60 else "MEDIUM",
                            estimated_delay_minutes=max(1.0, braking_time / 30)
                        )
                        conflicts.append(conflict)
                        
        return conflicts

class PrescriptiveEngine:
    """Generate actionable recommendations to prevent conflicts"""
    
    def __init__(self):
        self.action_history = []
        
    def generate_recommendations(self, 
                               conflicts: List[ConflictPrediction],
                               snapshot: Dict[str, Any]) -> List[PrescriptiveAction]:
        """Generate recommendations to resolve predicted conflicts"""
        recommendations = []
        
        # Sort conflicts by severity and probability
        high_priority_conflicts = sorted(
            conflicts, 
            key=lambda c: (c.probability * self._severity_weight(c.severity)), 
            reverse=True
        )
        
        for conflict in high_priority_conflicts:
            if conflict.probability > 0.5:  # Only act on likely conflicts
                actions = self._recommend_for_conflict(conflict, snapshot)
                recommendations.extend(actions)
                
        return recommendations
        
    def _severity_weight(self, severity: str) -> float:
        """Convert severity to numeric weight"""
        weights = {"LOW": 1.0, "MEDIUM": 2.0, "HIGH": 3.0, "CRITICAL": 4.0}
        return weights.get(severity, 1.0)
        
    def _recommend_for_conflict(self, conflict: ConflictPrediction, 
                              snapshot: Dict[str, Any]) -> List[PrescriptiveAction]:
        """Generate specific recommendations for a conflict"""
        actions = []
        trains = {t['train_id']: t for t in snapshot.get('trains', [])}
        
        if conflict.conflict_type == "HEADWAY":
            # Recommend holding slower train or speeding up faster train
            for train_id in conflict.trains_involved:
                train = trains.get(train_id)
                if train:
                    current_speed = train.get('current_speed', 0)
                    priority = train.get('priority', 3)
                    
                    if priority > 2:  # Lower priority (freight)
                        action = PrescriptiveAction(
                            action_id=f"HOLD_{train_id}_{conflict.conflict_id}",
                            action_type="HOLD",
                            target_train=train_id,
                            parameters={
                                "duration_minutes": min(10, conflict.estimated_delay_minutes * 1.5),
                                "location": conflict.location,
                                "reason": f"Resolve headway conflict with higher priority train"
                            },
                            expected_benefit=f"Prevent {conflict.estimated_delay_minutes:.1f} min delay propagation",
                            confidence=conflict.probability,
                            urgency="HIGH" if conflict.severity == "HIGH" else "MEDIUM"
                        )
                        actions.append(action)
                        
        elif conflict.conflict_type == "PLATFORM":
            # Recommend rerouting or holding lower priority trains
            for train_id in conflict.trains_involved[1:]:  # Skip first (highest priority)
                train = trains.get(train_id)
                if train:
                    action = PrescriptiveAction(
                        action_id=f"HOLD_PLATFORM_{train_id}",
                        action_type="HOLD",
                        target_train=train_id,
                        parameters={
                            "duration_minutes": 5,
                            "location": conflict.location,
                            "reason": "Platform capacity management"
                        },
                        expected_benefit="Prevent platform congestion",
                        confidence=0.8,
                        urgency="MEDIUM"
                    )
                    actions.append(action)
                    
        elif conflict.conflict_type == "SIGNAL":
            # Recommend speed reduction approaching RED signals
            train_id = conflict.trains_involved[0]
            train = trains.get(train_id)
            if train:
                current_speed = train.get('current_speed', 0)
                target_speed = max(20, current_speed * 0.5)  # Reduce to 50% or min 20 km/h
                
                action = PrescriptiveAction(
                    action_id=f"SPEED_REDUCE_{train_id}_{conflict.conflict_id}",
                    action_type="SPEED_CHANGE",
                    target_train=train_id,
                    parameters={
                        "target_speed_kmh": target_speed,
                        "reason": f"Approach RED signal {conflict.location} safely"
                    },
                    expected_benefit="Prevent emergency braking and ensure safe signal approach",
                    confidence=conflict.probability,
                    urgency="HIGH"
                )
                actions.append(action)
                
        return actions

class AnalyticsEngine:
    """Main analytics coordinator"""
    
    def __init__(self):
        self.predictor = ConflictPredictor()
        self.prescriptor = PrescriptiveEngine()
        self.last_analysis = None
        
    def analyze(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Run full predictive + prescriptive analysis"""
        logger.info("Running predictive analysis...")
        
        # Step 1: Predict conflicts
        conflicts = self.predictor.predict_conflicts(snapshot)
        
        # Step 2: Generate recommendations
        recommendations = self.prescriptor.generate_recommendations(conflicts, snapshot)
        
        # Step 3: Format results
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "conflicts_predicted": len(conflicts),
            "recommendations_generated": len(recommendations),
            "conflicts": [
                {
                    "id": c.conflict_id,
                    "type": c.conflict_type,
                    "trains": c.trains_involved,
                    "location": c.location,
                    "probability": round(c.probability, 2),
                    "severity": c.severity,
                    "estimated_delay": round(c.estimated_delay_minutes, 1)
                } for c in conflicts
            ],
            "recommendations": [
                {
                    "id": r.action_id,
                    "type": r.action_type,
                    "train": r.target_train,
                    "parameters": r.parameters,
                    "expected_benefit": r.expected_benefit,
                    "confidence": round(r.confidence, 2),
                    "urgency": r.urgency
                } for r in recommendations
            ],
            "summary": {
                "high_severity_conflicts": len([c for c in conflicts if c.severity == "HIGH"]),
                "urgent_recommendations": len([r for r in recommendations if r.urgency == "HIGH"]),
                "total_predicted_delay": sum(c.estimated_delay_minutes for c in conflicts)
            }
        }
        
        self.last_analysis = analysis_result
        return analysis_result

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Sample snapshot data for testing
    sample_snapshot = {
        "timestamp": datetime.now().isoformat(),
        "trains": [
            {"train_id": "T001", "train_type": "EXPRESS", "priority": 1, "current_node": "SIG_001", "current_speed": 60.0},
            {"train_id": "T002", "train_type": "PASSENGER", "priority": 2, "current_node": "SIG_001", "current_speed": 30.0},
            {"train_id": "T003", "train_type": "FREIGHT", "priority": 3, "current_node": "STN_A", "current_speed": 0.0}
        ],
        "signals": [
            {"signal_id": "SIG_001", "aspect": "RED"},
            {"signal_id": "SIG_002", "aspect": "GREEN"}
        ]
    }
    
    engine = AnalyticsEngine()
    result = engine.analyze(sample_snapshot)
    
    print("Analytics Results:")
    print(f"Conflicts predicted: {result['conflicts_predicted']}")
    print(f"Recommendations: {result['recommendations_generated']}")
    
    print("\nConflicts:")
    for conflict in result['conflicts']:
        print(f"  {conflict['type']} at {conflict['location']}: {conflict['probability']} probability")
        
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  {rec['type']} for {rec['train']}: {rec['expected_benefit']}")
