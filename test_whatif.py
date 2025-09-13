#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced what-if scenario system
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from demo_system import IDSSDemo

def test_whatif_scenarios():
    """Test the what-if scenarios with enhanced formatting"""
    print("🎯 Testing Enhanced What-If Scenarios")
    print("=" * 50)
    
    # Initialize demo system
    demo = IDSSDemo()
    
    # Initialize the digital twin and generate sample data
    demo.digital_twin.initialize_pilot_section()
    snapshot = demo.data_feed.generate_snapshot()
    demo.digital_twin.ingest_real_time_data(snapshot)
    
    # Display network status
    demo._display_network_status(snapshot)
    
    # Test different scenario types
    scenarios = [
        {
            'name': 'Hold T003 for 15 minutes (High Impact Test)',
            'train_id': 'T003',
            'action': 'HOLD',
            'duration_minutes': 15
        },
        {
            'name': 'Reroute T001 to alternate station',
            'train_id': 'T001',
            'action': 'REROUTE',
            'target_node': 'STN_B',
            'duration_minutes': 25
        },
        {
            'name': 'Speed optimization for T002',
            'train_id': 'T002', 
            'action': 'HOLD',  # Simulated as speed adjustment
            'duration_minutes': 3,
            'target_speed': 60  # Custom field for speed scenarios
        }
    ]
    
    print(f"\n🧪 Running {len(scenarios)} test scenarios...")
    print(f"{'=' * 55}")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🔬 Test {i}/3: {scenario['name']}")
        print(f"   {'─' * 45}")
        
        # Run the simulation
        result = demo.digital_twin.run_what_if_simulation(scenario)
        
        # Display results with enhanced formatting
        demo._display_scenario_results(scenario, result, compact=False)
        
        # Add separator between scenarios
        if i < len(scenarios):
            print(f"\n   {'·' * 50}")

if __name__ == "__main__":
    test_whatif_scenarios()
    print(f"\n✅ What-If Scenario Testing Complete!")
    print(f"\n🎉 Key improvements implemented:")
    print(f"   • Train selection persistence (fixed disappearing bug)")  
    print(f"   • User-friendly output formatting (no more raw JSON)")
    print(f"   • Interactive scenario builder with input validation")
    print(f"   • Risk assessment and recommendations")
    print(f"   • Comprehensive impact analysis display")
