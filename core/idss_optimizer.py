"""
Intelligent Decision Support System (IDSS) - Core Optimizer
Hybrid AI-OR framework for train scheduling optimization
Based on the blueprint's Phase I requirements
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# OR dependencies
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

# AI/ML dependencies  
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

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
    current_location: float  # km post
    destination: float       # km post
    scheduled_arrival: datetime
    actual_arrival: Optional[datetime] = None
    current_speed: float = 0.0
    max_speed: float = 100.0
    length_m: float = 500.0
    weight_tons: float = 1000.0

@dataclass
class Section:
    section_id: str
    start_km: float
    end_km: float
    max_speed: float
    capacity: int  # max trains
    current_occupancy: List[str]  # train_ids

@dataclass
class OptimizationResult:
    success: bool
    objective_value: float
    recommendations: List[Dict[str, Any]]
    explanation: str
    confidence_score: float
    computation_time: float

class AIPredictor(nn.Module):
    """Neural network for predicting delay propagation and conflict probability"""
    
    def __init__(self, input_size=20, hidden_size=64):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, 2)  # [delay_minutes, conflict_probability]
        )
        
    def forward(self, x):
        return self.network(x)

class HybridOptimizer:
    """Core IDSS optimizer combining AI prediction with OR optimization"""
    
    def __init__(self, objective: OptimizationObjective = OptimizationObjective.MINIMIZE_DELAY):
        self.objective = objective
        self.ai_predictor = AIPredictor()
        self.delay_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, trains: List[Train], sections: List[Section]) -> np.ndarray:
        """Extract features for AI models"""
        features = []
        
        for train in trains:
            # Train-specific features
            delay_minutes = 0
            if train.actual_arrival and train.scheduled_arrival:
                delay_minutes = (train.actual_arrival - train.scheduled_arrival).total_seconds() / 60
            
            # Section occupancy features
            current_section_occupancy = 0
            for section in sections:
                if section.start_km <= train.current_location <= section.end_km:
                    current_section_occupancy = len(section.current_occupancy) / section.capacity
                    break
            
            train_features = [
                train.priority.value,
                train.current_speed / train.max_speed,  # normalized speed
                delay_minutes,
                current_section_occupancy,
                train.length_m / 1000.0,  # normalized length
                train.weight_tons / 10000.0,  # normalized weight
            ]
            features.extend(train_features)
        
        # Pad or truncate to fixed size
        target_size = 20
        if len(features) < target_size:
            features.extend([0.0] * (target_size - len(features)))
        else:
            features = features[:target_size]
            
        return np.array(features).reshape(1, -1)

    def predict_conflicts(self, trains: List[Train], sections: List[Section]) -> Dict[str, float]:
        """AI-powered conflict prediction"""
        if not self.is_trained:
            # Use rule-based heuristics for initial predictions
            conflicts = {}
            for train in trains:
                # Simple heuristic: higher probability if train is delayed and in congested section
                delay_factor = 0.0
                if train.actual_arrival and train.scheduled_arrival:
                    delay_minutes = (train.actual_arrival - train.scheduled_arrival).total_seconds() / 60
                    delay_factor = min(delay_minutes / 30.0, 1.0)  # normalize to [0,1]
                
                # Section congestion factor
                congestion_factor = 0.0
                for section in sections:
                    if section.start_km <= train.current_location <= section.end_km:
                        congestion_factor = len(section.current_occupancy) / section.capacity
                        break
                
                conflict_probability = min((delay_factor + congestion_factor) / 2.0, 1.0)
                conflicts[train.train_id] = conflict_probability
                
            return conflicts
        
        # Use trained AI model
        features = self.extract_features(trains, sections)
        with torch.no_grad():
            prediction = self.ai_predictor(torch.FloatTensor(features))
            delay_pred, conflict_prob = prediction[0]
            
        return {train.train_id: float(conflict_prob) for train in trains}

    def or_optimize_schedule(self, trains: List[Train], sections: List[Section], 
                           time_horizon: int = 60) -> OptimizationResult:
        """Operations Research optimization using CP-SAT"""
        start_time = datetime.now()
        
        # Create CP model
        model = cp_model.CpModel()
        
        # Decision variables: train departure times (in minutes from now)
        departure_vars = {}
        for train in trains:
            # Allow departures from now to time_horizon minutes
            departure_vars[train.train_id] = model.NewIntVar(0, time_horizon, f'departure_{train.train_id}')
        
        # Constraints
        recommendations = []
        
        # Priority constraints: higher priority trains get preference
        priority_trains = sorted(trains, key=lambda t: t.priority.value)
        for i, train1 in enumerate(priority_trains):
            for train2 in priority_trains[i+1:]:
                # If trains are in same section, enforce separation
                if self._trains_in_same_section(train1, train2, sections):
                    min_separation = 5  # 5 minutes minimum headway
                    model.Add(departure_vars[train2.train_id] >= 
                             departure_vars[train1.train_id] + min_separation)
        
        # Capacity constraints
        for section in sections:
            section_trains = [t for t in trains 
                            if section.start_km <= t.current_location <= section.end_km]
            if len(section_trains) > section.capacity:
                # Delay some trains to respect capacity
                excess_trains = section_trains[section.capacity:]
                for train in excess_trains:
                    model.Add(departure_vars[train.train_id] >= 10)  # Hold for 10+ minutes
        
        # Objective function
        if self.objective == OptimizationObjective.MINIMIZE_DELAY:
            # Minimize total delay
            delay_expr = []
            for train in trains:
                # Estimate delay based on departure time
                estimated_delay = departure_vars[train.train_id]
                delay_expr.append(estimated_delay)
            model.Minimize(sum(delay_expr))
        else:
            # Maximize throughput (minimize total departure time spread)
            max_departure = model.NewIntVar(0, time_horizon, 'max_departure')
            for train in trains:
                model.AddMaxEquality(max_departure, [departure_vars[train.train_id]])
            model.Minimize(max_departure)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0  # Real-time constraint
        status = solver.Solve(model)
        
        computation_time = (datetime.now() - start_time).total_seconds()
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract recommendations
            for train in trains:
                departure_delay = solver.Value(departure_vars[train.train_id])
                if departure_delay > 0:
                    recommendations.append({
                        'train_id': train.train_id,
                        'action': 'HOLD',
                        'duration_minutes': departure_delay,
                        'reason': f'Optimize {self.objective.value}',
                        'priority_impact': train.priority.value
                    })
                else:
                    recommendations.append({
                        'train_id': train.train_id,
                        'action': 'PROCEED',
                        'duration_minutes': 0,
                        'reason': 'No delays required',
                        'priority_impact': train.priority.value
                    })
            
            return OptimizationResult(
                success=True,
                objective_value=solver.ObjectiveValue(),
                recommendations=recommendations,
                explanation=f"OR optimization for {len(trains)} trains completed successfully",
                confidence_score=0.9 if status == cp_model.OPTIMAL else 0.7,
                computation_time=computation_time
            )
        else:
            return OptimizationResult(
                success=False,
                objective_value=float('inf'),
                recommendations=[],
                explanation="OR optimization failed to find feasible solution",
                confidence_score=0.0,
                computation_time=computation_time
            )

    def _trains_in_same_section(self, train1: Train, train2: Train, sections: List[Section]) -> bool:
        """Check if two trains are in the same section"""
        for section in sections:
            if (section.start_km <= train1.current_location <= section.end_km and
                section.start_km <= train2.current_location <= section.end_km):
                return True
        return False

    def hybrid_optimize(self, trains: List[Train], sections: List[Section]) -> OptimizationResult:
        """Main hybrid optimization combining AI prediction with OR optimization"""
        logger.info(f"Starting hybrid optimization for {len(trains)} trains")
        
        # Step 1: AI-based conflict prediction
        conflicts = self.predict_conflicts(trains, sections)
        
        # Step 2: OR optimization with AI insights
        or_result = self.or_optimize_schedule(trains, sections)
        
        if not or_result.success:
            return or_result
        
        # Step 3: AI refinement of OR solution
        refined_recommendations = []
        for rec in or_result.recommendations:
            train_id = rec['train_id']
            conflict_prob = conflicts.get(train_id, 0.0)
            
            # Adjust recommendations based on conflict probability
            if conflict_prob > 0.7 and rec['action'] == 'PROCEED':
                # High conflict risk - convert to HOLD
                refined_rec = rec.copy()
                refined_rec['action'] = 'HOLD'
                refined_rec['duration_minutes'] = max(5, int(conflict_prob * 15))
                refined_rec['reason'] = f"AI detected high conflict risk ({conflict_prob:.2f})"
                refined_recommendations.append(refined_rec)
            elif conflict_prob < 0.3 and rec['action'] == 'HOLD':
                # Low conflict risk - reduce hold time
                refined_rec = rec.copy()
                refined_rec['duration_minutes'] = max(0, rec['duration_minutes'] - 5)
                refined_rec['reason'] = f"AI reduced hold time due to low conflict risk ({conflict_prob:.2f})"
                refined_recommendations.append(refined_rec)
            else:
                refined_recommendations.append(rec)
        
        return OptimizationResult(
            success=True,
            objective_value=or_result.objective_value,
            recommendations=refined_recommendations,
            explanation=f"Hybrid AI-OR optimization: {len(conflicts)} conflicts analyzed, {len(refined_recommendations)} recommendations",
            confidence_score=min(0.95, or_result.confidence_score + 0.1),  # Slight boost for hybrid
            computation_time=or_result.computation_time
        )

    def explain_recommendation(self, recommendation: Dict[str, Any], trains: List[Train]) -> str:
        """Generate explanation for XAI compliance"""
        train_id = recommendation['train_id']
        action = recommendation['action']
        
        train = next((t for t in trains if t.train_id == train_id), None)
        if not train:
            return "Train not found"
        
        explanation_parts = [
            f"Train {train.train_number} ({train.train_type})",
            f"Priority: {train.priority.name}",
            f"Current location: {train.current_location:.1f} km",
            f"Action: {action}"
        ]
        
        if action == 'HOLD':
            duration = recommendation['duration_minutes']
            explanation_parts.append(f"Hold duration: {duration} minutes")
        
        explanation_parts.append(f"Reason: {recommendation['reason']}")
        
        return " | ".join(explanation_parts)

# Example usage and testing
if __name__ == "__main__":
    # Create sample data
    trains = [
        Train("T001", "12345", "EXPRESS", TrainPriority.MAIL_EXPRESS, 100.0, 200.0, datetime.now()),
        Train("T002", "56789", "PASSENGER", TrainPriority.PASSENGER, 110.0, 200.0, datetime.now()),
        Train("T003", "99999", "FREIGHT", TrainPriority.FREIGHT, 105.0, 200.0, datetime.now() - timedelta(minutes=15))
    ]
    
    sections = [
        Section("SEC001", 90.0, 120.0, 80.0, 2, ["T001", "T002"]),
        Section("SEC002", 120.0, 150.0, 100.0, 3, [])
    ]
    
    # Test optimization
    optimizer = HybridOptimizer(OptimizationObjective.MINIMIZE_DELAY)
    result = optimizer.hybrid_optimize(trains, sections)
    
    print(f"Optimization Success: {result.success}")
    print(f"Objective Value: {result.objective_value}")
    print(f"Computation Time: {result.computation_time:.2f}s")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Explanation: {result.explanation}")
    
    print("\nRecommendations:")
    for rec in result.recommendations:
        explanation = optimizer.explain_recommendation(rec, trains)
        print(f"  {explanation}")
