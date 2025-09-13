"""
Cognitive Digital Twin - MVP Implementation
Virtual replica of pilot railway section with real-time data synchronization
Based on blueprint requirements for scenario analysis and what-if simulations
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import networkx as nx
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class Node:
    """Railway network node (stations, signals, junctions)"""
    node_id: str
    node_type: str  # STATION, SIGNAL, JUNCTION
    km_post: float
    station_code: Optional[str] = None
    coordinates: Tuple[float, float] = (0.0, 0.0)

@dataclass  
class Edge:
    """Railway track segment between nodes"""
    edge_id: str
    from_node: str
    to_node: str
    length_m: float
    gradient: float = 0.0  # percentage grade
    curvature: float = 0.0  # degrees per km
    max_speed: float = 100.0  # km/h
    track_condition: str = "GOOD"  # GOOD, FAIR, POOR, CRITICAL

@dataclass
class Signal:
    """Railway signal with interlocking logic"""
    signal_id: str
    node_id: str
    signal_type: str  # HOME, STARTER, DISTANT, SHUNT, AUTOMATIC
    current_aspect: str = "RED"  # RED, YELLOW, GREEN, DOUBLE_YELLOW
    interlocking_zone: str = ""
    failure_status: bool = False
    maintenance_mode: bool = False

@dataclass
class BlockSection:
    """Track circuit or axle counter block"""
    block_id: str
    start_node: str
    end_node: str
    length_m: float
    occupied_by: Optional[str] = None  # train_id if occupied
    last_cleared: Optional[datetime] = None

@dataclass
class TrainState:
    """Real-time train state in digital twin"""
    train_id: str
    current_node: str
    current_edge: Optional[str] = None
    position_on_edge: float = 0.0  # meters from start of edge
    current_speed: float = 0.0
    target_speed: float = 0.0
    acceleration: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)

class PhysicsEngine:
    """Train dynamics simulation engine"""
    
    def __init__(self):
        self.gravity = 9.81  # m/s²
        self.air_resistance_coefficient = 0.3
        
    def calculate_max_acceleration(self, train_weight_tons: float, power_kw: float) -> float:
        """Calculate maximum acceleration based on train characteristics"""
        weight_kg = train_weight_tons * 1000
        force_n = (power_kw * 1000) / 10  # Simplified traction calculation
        max_accel = force_n / weight_kg
        return min(max_accel, 1.0)  # Cap at 1 m/s² for safety
    
    def calculate_braking_distance(self, current_speed_kmh: float, 
                                 target_speed_kmh: float, 
                                 gradient: float = 0.0) -> float:
        """Calculate braking distance considering gradient"""
        v1 = current_speed_kmh / 3.6  # Convert to m/s
        v2 = target_speed_kmh / 3.6
        
        # Emergency braking deceleration (conservative)
        decel_base = 0.8  # m/s²
        gradient_factor = self.gravity * (gradient / 100.0)
        effective_decel = decel_base + gradient_factor
        
        if effective_decel <= 0:
            return float('inf')  # Cannot brake on steep downgrade
            
        distance = (v1*v1 - v2*v2) / (2 * effective_decel)
        return max(0, distance)

class TopologyService:
    """Railway network topology management"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.signals: Dict[str, Signal] = {}
        self.blocks: Dict[str, BlockSection] = {}
        
    def add_node(self, node: Node) -> None:
        """Add node to network topology"""
        self.nodes[node.node_id] = node
        self.graph.add_node(node.node_id, **node.__dict__)
        
    def add_edge(self, edge: Edge) -> None:
        """Add edge to network topology"""
        self.edges[edge.edge_id] = edge
        edge_attrs = edge.__dict__.copy()
        self.graph.add_edge(edge.from_node, edge.to_node, **edge_attrs)
        
    def find_route(self, start_node: str, end_node: str) -> List[str]:
        """Find shortest path between nodes"""
        try:
            return nx.shortest_path(self.graph, start_node, end_node, weight='length_m')
        except nx.NetworkXNoPath:
            return []
            
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighboring nodes"""
        return list(self.graph.neighbors(node_id))
        
    def calculate_section_capacity(self, start_node: str, end_node: str) -> int:
        """Calculate theoretical capacity of a section"""
        route = self.find_route(start_node, end_node)
        if not route:
            return 0
            
        # Count block sections in route
        block_count = 0
        for i in range(len(route) - 1):
            for block in self.blocks.values():
                if block.start_node == route[i] and block.end_node == route[i+1]:
                    block_count += 1
                    
        # Capacity = number of blocks (simplified)
        return max(1, block_count)

class StateManager:
    """Manages real-time state of all network assets"""
    
    def __init__(self):
        self.train_states: Dict[str, TrainState] = {}
        self.signal_states: Dict[str, Signal] = {}
        self.block_states: Dict[str, BlockSection] = {}
        self.last_sync: datetime = datetime.now()
        self._lock = threading.Lock()
        
    def update_train_state(self, train_id: str, state: TrainState) -> None:
        """Update train state with thread safety"""
        with self._lock:
            self.train_states[train_id] = state
            self.last_sync = datetime.now()
            
    def update_signal_state(self, signal_id: str, aspect: str) -> None:
        """Update signal aspect"""
        with self._lock:
            if signal_id in self.signal_states:
                self.signal_states[signal_id].current_aspect = aspect
                
    def get_section_occupancy(self, start_node: str, end_node: str) -> List[str]:
        """Get list of trains in a section"""
        with self._lock:
            occupying_trains = []
            for train_id, state in self.train_states.items():
                # Simplified: check if train is between start and end nodes
                # In real implementation, would use proper topology checking
                occupying_trains.append(train_id)
            return occupying_trains

class SimulationEngine:
    """Discrete event simulation for what-if analysis"""
    
    def __init__(self, topology: TopologyService, physics: PhysicsEngine):
        self.topology = topology
        self.physics = physics
        self.current_time = datetime.now()
        self.time_step = 5.0  # seconds
        self.is_running = False
        
    def simulate_train_movement(self, train_id: str, train_state: TrainState,
                              target_node: str, duration_minutes: int) -> List[TrainState]:
        """Simulate train movement over time"""
        states = [train_state]
        current_state = train_state
        
        # Find route to target
        route = self.topology.find_route(current_state.current_node, target_node)
        if not route:
            logger.warning(f"No route found from {current_state.current_node} to {target_node}")
            return states
            
        # Simulate movement along route
        simulation_steps = int((duration_minutes * 60) / self.time_step)
        
        for step in range(simulation_steps):
            # Calculate next position based on current speed and acceleration
            next_state = self._calculate_next_state(current_state, route)
            next_state.last_update = self.current_time + timedelta(seconds=step * self.time_step)
            states.append(next_state)
            current_state = next_state
            
        return states
        
    def _calculate_next_state(self, current_state: TrainState, route: List[str]) -> TrainState:
        """Calculate next train state based on physics"""
        next_state = TrainState(
            train_id=current_state.train_id,
            current_node=current_state.current_node,
            current_edge=current_state.current_edge,
            position_on_edge=current_state.position_on_edge,
            current_speed=current_state.current_speed,
            target_speed=current_state.target_speed,
            acceleration=current_state.acceleration
        )
        
        # Simplified physics integration
        dt = self.time_step
        
        # Update speed
        next_state.current_speed += current_state.acceleration * dt
        next_state.current_speed = max(0, min(next_state.current_speed, 120))  # Cap speed
        
        # Update position
        distance_traveled = next_state.current_speed * (dt / 3.6)  # Convert km/h to m/s
        next_state.position_on_edge += distance_traveled
        
        # Check if reached next node
        if current_state.current_edge and current_state.current_edge in self.topology.edges:
            edge = self.topology.edges[current_state.current_edge]
            if next_state.position_on_edge >= edge.length_m:
                # Move to next node
                next_state.current_node = edge.to_node
                next_state.current_edge = None
                next_state.position_on_edge = 0.0
                
        return next_state

class CognitiveTwin:
    """Main digital twin orchestrator"""
    
    def __init__(self, pilot_section_config: Dict[str, Any]):
        self.config = pilot_section_config
        self.topology = TopologyService()
        self.state_manager = StateManager()
        self.physics = PhysicsEngine()
        self.simulation = SimulationEngine(self.topology, self.physics)
        self.is_initialized = False
        
        # Performance tracking
        self.update_count = 0
        self.last_performance_check = datetime.now()
        
    def initialize_pilot_section(self) -> None:
        """Initialize the pilot section topology and assets"""
        logger.info("Initializing pilot section digital twin")
        
        # Create sample topology for demo (replace with real data)
        self._create_sample_topology()
        
        # Initialize state managers
        self._initialize_signals()
        self._initialize_blocks()
        
        self.is_initialized = True
        logger.info("Pilot section initialization complete")
        
    def _create_sample_topology(self) -> None:
        """Create sample railway topology for MVP demo"""
        # Nodes
        nodes = [
            Node("STN_A", "STATION", 100.0, "STN_A", (77.5946, 12.9716)),
            Node("SIG_001", "SIGNAL", 105.0),
            Node("JUN_001", "JUNCTION", 110.0),
            Node("SIG_002", "SIGNAL", 115.0),
            Node("STN_B", "STATION", 120.0, "STN_B", (77.6413, 12.9141))
        ]
        
        for node in nodes:
            self.topology.add_node(node)
            
        # Edges
        edges = [
            Edge("E001", "STN_A", "SIG_001", 5000, 0.5, 2.0, 80.0),
            Edge("E002", "SIG_001", "JUN_001", 5000, -0.2, 1.0, 100.0),
            Edge("E003", "JUN_001", "SIG_002", 5000, 0.0, 0.0, 120.0),
            Edge("E004", "SIG_002", "STN_B", 5000, -1.0, 3.0, 80.0)
        ]
        
        for edge in edges:
            self.topology.add_edge(edge)
            
    def _initialize_signals(self) -> None:
        """Initialize signal states"""
        signals = [
            Signal("SIG_001", "SIG_001", "HOME", "RED", "ZONE_1"),
            Signal("SIG_002", "SIG_002", "STARTER", "GREEN", "ZONE_2")
        ]
        
        for signal in signals:
            self.topology.signals[signal.signal_id] = signal
            self.state_manager.signal_states[signal.signal_id] = signal
            
    def _initialize_blocks(self) -> None:
        """Initialize block sections"""
        blocks = [
            BlockSection("BLK_001", "STN_A", "SIG_001", 5000),
            BlockSection("BLK_002", "SIG_001", "JUN_001", 5000),
            BlockSection("BLK_003", "JUN_001", "SIG_002", 5000),
            BlockSection("BLK_004", "SIG_002", "STN_B", 5000)
        ]
        
        for block in blocks:
            self.topology.blocks[block.block_id] = block
            self.state_manager.block_states[block.block_id] = block
            
    def ingest_real_time_data(self, data: Dict[str, Any]) -> None:
        """Ingest real-time data from railway systems"""
        if not self.is_initialized:
            logger.warning("Digital twin not initialized")
            return
            
        # Process train positions
        if 'trains' in data:
            for train_data in data['trains']:
                train_state = TrainState(
                    train_id=train_data['train_id'],
                    current_node=train_data.get('current_node', 'UNKNOWN'),
                    current_speed=train_data.get('current_speed', 0.0),
                    target_speed=train_data.get('target_speed', 0.0)
                )
                self.state_manager.update_train_state(train_data['train_id'], train_state)
                
        # Process signal updates
        if 'signals' in data:
            for signal_data in data['signals']:
                self.state_manager.update_signal_state(
                    signal_data['signal_id'], 
                    signal_data['aspect']
                )
                
        self.update_count += 1
        
    def run_what_if_simulation(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run what-if simulation for scenario analysis"""
        logger.info(f"Running what-if simulation: {scenario.get('name', 'Unnamed')}")
        
        # Extract scenario parameters
        train_id = scenario.get('train_id')
        action = scenario.get('action')  # HOLD, REROUTE, SPEED_CHANGE
        duration = scenario.get('duration_minutes', 30)
        
        # Get current train state
        if train_id not in self.state_manager.train_states:
            return {'error': f'Train {train_id} not found in current state'}
            
        current_state = self.state_manager.train_states[train_id]
        
        # Run simulation
        if action == 'HOLD':
            # Simulate holding train at current position
            hold_states = self._simulate_hold(current_state, duration)
            return {
                'scenario': scenario,
                'predicted_states': [state.__dict__ for state in hold_states],
                'impact_analysis': self._analyze_hold_impact(train_id, duration)
            }
        elif action == 'REROUTE':
            # Simulate rerouting
            target_node = scenario.get('target_node', 'STN_B')
            reroute_states = self.simulation.simulate_train_movement(
                train_id, current_state, target_node, duration
            )
            return {
                'scenario': scenario,
                'predicted_states': [state.__dict__ for state in reroute_states],
                'impact_analysis': self._analyze_reroute_impact(train_id, target_node)
            }
        else:
            return {'error': f'Unsupported action: {action}'}
            
    def _simulate_hold(self, train_state: TrainState, hold_minutes: int) -> List[TrainState]:
        """Simulate holding a train at current position"""
        held_states = []
        
        for minute in range(hold_minutes + 1):
            held_state = TrainState(
                train_id=train_state.train_id,
                current_node=train_state.current_node,
                current_edge=train_state.current_edge,
                position_on_edge=train_state.position_on_edge,
                current_speed=0.0,  # Held at zero speed
                target_speed=0.0,
                acceleration=0.0,
                last_update=datetime.now() + timedelta(minutes=minute)
            )
            held_states.append(held_state)
            
        return held_states
        
    def _analyze_hold_impact(self, train_id: str, hold_minutes: int) -> Dict[str, Any]:
        """Analyze impact of holding a train"""
        return {
            'delay_added_minutes': hold_minutes,
            'affected_trains': [],  # Would analyze downstream impacts
            'capacity_impact': 'MODERATE',
            'estimated_recovery_time': hold_minutes * 1.5
        }
        
    def _analyze_reroute_impact(self, train_id: str, target_node: str) -> Dict[str, Any]:
        """Analyze impact of rerouting a train"""
        return {
            'route_change': True,
            'additional_distance_km': 2.5,  # Estimated
            'time_impact_minutes': 8,
            'capacity_freed': ['BLK_001', 'BLK_002']
        }
        
    def get_network_snapshot(self) -> Dict[str, Any]:
        """Get current state snapshot of entire network"""
        return {
            'timestamp': datetime.now().isoformat(),
            'trains': {tid: state.__dict__ for tid, state in self.state_manager.train_states.items()},
            'signals': {sid: signal.__dict__ for sid, signal in self.state_manager.signal_states.items()},
            'blocks': {bid: block.__dict__ for bid, block in self.state_manager.block_states.items()},
            'performance_metrics': {
                'update_count': self.update_count,
                'last_sync': self.state_manager.last_sync.isoformat(),
                'topology_nodes': len(self.topology.nodes),
                'topology_edges': len(self.topology.edges)
            }
        }
        
    def validate_against_real_world(self, real_data: Dict[str, Any]) -> Dict[str, float]:
        """Validate digital twin accuracy against real-world data"""
        validation_metrics = {}
        
        # Compare train positions
        if 'trains' in real_data:
            position_errors = []
            for train_data in real_data['trains']:
                train_id = train_data['train_id']
                if train_id in self.state_manager.train_states:
                    predicted_pos = self.state_manager.train_states[train_id].position_on_edge
                    actual_pos = train_data.get('actual_position_m', 0)
                    error = abs(predicted_pos - actual_pos)
                    position_errors.append(error)
                    
            if position_errors:
                validation_metrics['mean_position_error_m'] = np.mean(position_errors)
                validation_metrics['max_position_error_m'] = np.max(position_errors)
                
        # Compare timing predictions
        # Would include arrival time accuracy, clearance time accuracy, etc.
        
        return validation_metrics

# Example usage and testing
if __name__ == "__main__":
    # Initialize digital twin
    config = {
        'pilot_section': 'STN_A_TO_STN_B',
        'update_frequency': 5,  # seconds
        'validation_threshold': 60  # seconds
    }
    
    twin = CognitiveTwin(config)
    twin.initialize_pilot_section()
    
    # Simulate real-time data ingestion
    sample_data = {
        'trains': [
            {'train_id': 'T001', 'current_node': 'STN_A', 'current_speed': 45.0, 'target_speed': 80.0},
            {'train_id': 'T002', 'current_node': 'JUN_001', 'current_speed': 60.0, 'target_speed': 60.0}
        ],
        'signals': [
            {'signal_id': 'SIG_001', 'aspect': 'YELLOW'},
            {'signal_id': 'SIG_002', 'aspect': 'GREEN'}
        ]
    }
    
    twin.ingest_real_time_data(sample_data)
    
    # Run what-if simulation
    scenario = {
        'name': 'Hold T001 for 10 minutes',
        'train_id': 'T001',
        'action': 'HOLD',
        'duration_minutes': 10
    }
    
    result = twin.run_what_if_simulation(scenario)
    print("What-if simulation result:")
    print(json.dumps(result, indent=2, default=str))
    
    # Get network snapshot
    snapshot = twin.get_network_snapshot()
    print(f"\nNetwork snapshot at {snapshot['timestamp']}:")
    print(f"Trains tracked: {len(snapshot['trains'])}")
    print(f"Signals monitored: {len(snapshot['signals'])}")
    print(f"Update count: {snapshot['performance_metrics']['update_count']}")
