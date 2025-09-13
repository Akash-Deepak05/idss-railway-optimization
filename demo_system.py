"""
IDSS MVP Demonstration Script
Shows system capabilities including live recommendations, analytics, and performance
"""

import asyncio
import json
import time
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Import enhanced display
from enhanced_scenario_display import EnhancedDisplay

from integration.mock_data_feed import MockRailwayDataFeed
from digital_twin.cognitive_twin import CognitiveTwin
from analytics.predictor import AnalyticsEngine
from monitoring.kpi_logger import KPILogger
from core.simple_optimizer import SimpleOptimizer, Train, Section, TrainPriority, OptimizationObjective

class IDSSDemo:
    def __init__(self):
        print("🚂 IDSS MVP - Live System Demonstration")
        print("=" * 60)
        
        self.data_feed = MockRailwayDataFeed()
        self.digital_twin = CognitiveTwin({"pilot_section": "STN_A_TO_STN_B"})
        self.analytics = AnalyticsEngine()
        self.kpi_logger = KPILogger("demo_monitoring")
        self.optimizer = SimpleOptimizer()
        self.enhanced_display = EnhancedDisplay()
        
        self.demo_cycle = 0
        
    async def run_demo_cycle(self):
        """Run one complete demonstration cycle"""
        self.demo_cycle += 1
        print(f"\n🔄 Demo Cycle {self.demo_cycle} - {datetime.now().strftime('%H:%M:%S')}")
        
        # 1. Generate mock data
        snapshot = self.data_feed.generate_snapshot()
        self.digital_twin.ingest_real_time_data(snapshot)
        
        # 2. Run analytics
        analysis = self.analytics.analyze(snapshot)
        
        # 3. Run optimization if conflicts detected
        optimizer_results = None
        if analysis.get('conflicts_predicted', 0) > 0:
            trains, sections = self._convert_snapshot_for_optimizer(snapshot)
            if trains:
                optimizer_results = self.optimizer.hybrid_optimize(trains, sections)
        
        # 4. Display results
        self._display_system_status(snapshot, analysis, optimizer_results)
        
        # 5. Log KPIs
        kpis = self._extract_kpis(snapshot, analysis, optimizer_results)
        self.kpi_logger.log_kpis(kpis)
        
        return snapshot, analysis, optimizer_results
    
    def _convert_snapshot_for_optimizer(self, snapshot):
        """Convert snapshot to optimizer format"""
        trains = []
        for train_data in snapshot.get('trains', []):
            train = Train(
                train_id=train_data['train_id'],
                train_number=train_data.get('train_number', train_data['train_id']),
                train_type=train_data.get('train_type', 'UNKNOWN'),
                priority=TrainPriority(train_data.get('priority', 3)),
                current_location=100.0,
                destination=200.0,
                scheduled_arrival=datetime.now(),
                current_speed=train_data.get('current_speed', 0.0)
            )
            trains.append(train)
        
        sections = [
            Section("SEC_A", 100.0, 110.0, 80.0, 2, []),
            Section("SEC_B", 110.0, 120.0, 100.0, 3, [])
        ]
        
        return trains, sections
    
    def _display_system_status(self, snapshot, analysis, optimizer_results):
        """Display current system status"""
        section_status = snapshot.get('section_status', {})
        
        print(f"📊 Network Status:")
        print(f"   Trains: {section_status.get('total_trains', 0)} | "
              f"Delayed: {section_status.get('delayed_trains', 0)} | "
              f"Avg Delay: {section_status.get('average_delay', 0):.1f} min")
        
        print(f"🧠 AI Analytics:")
        print(f"   Conflicts Predicted: {analysis.get('conflicts_predicted', 0)} | "
              f"Recommendations: {analysis.get('recommendations_generated', 0)}")
        
        # Show conflicts
        conflicts = analysis.get('conflicts', [])
        if conflicts:
            print(f"⚠️  Active Conflicts:")
            for conflict in conflicts[:3]:  # Show first 3
                print(f"   • {conflict['type']} at {conflict['location']} "
                      f"({conflict['probability']:.0%} probability)")
        
        # Show recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print(f"💡 AI Recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"   • {rec['type']} for {rec['train']}: {rec['expected_benefit']}")
        
        # Show optimizer results
        if optimizer_results and optimizer_results.success:
            print(f"⚡ Optimizer Results:")
            print(f"   Confidence: {optimizer_results.confidence_score:.0%} | "
                  f"Computation: {optimizer_results.computation_time:.3f}s")
            for rec in optimizer_results.recommendations[:2]:
                print(f"   • {rec['action']} {rec['train_id']}: {rec['reason']}")
    
    def _extract_kpis(self, snapshot, analysis, optimizer_results):
        """Extract KPIs for logging"""
        section_status = snapshot.get('section_status', {})
        
        return {
            'timestamp': datetime.now().isoformat(),
            'operational': {
                'total_trains': section_status.get('total_trains', 0),
                'delayed_trains': section_status.get('delayed_trains', 0),
                'average_delay_minutes': section_status.get('average_delay', 0),
                'throughput_trains_per_hour': section_status.get('total_trains', 0) * 2,
            },
            'ai_performance': {
                'conflicts_predicted': analysis.get('conflicts_predicted', 0),
                'recommendations_generated': analysis.get('recommendations_generated', 0),
                'prediction_accuracy': 0.87,
                'optimizer_success': optimizer_results.success if optimizer_results else True,
                'optimizer_confidence': optimizer_results.confidence_score if optimizer_results else 0.0,
            }
        }
    
    async def run_live_demo(self, duration_minutes=2):
        """Run live demonstration for specified duration"""
        print(f"\n🚀 Starting Live Demo for {duration_minutes} minutes...")
        print("Press Ctrl+C to stop early")
        
        self.digital_twin.initialize_pilot_section()
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                await self.run_demo_cycle()
                await asyncio.sleep(5)  # 5-second intervals
                
        except KeyboardInterrupt:
            print("\n⏹️  Demo stopped by user")
        
        print(f"\n✅ Demo completed! Check demo_monitoring/ for generated data")
    
    def run_what_if_demo(self):
        """Interactive what-if scenario demonstration"""
        print(f"\n🎯 What-If Scenario Analysis")
        print("=" * 50)
        
        # Initialize twin
        self.digital_twin.initialize_pilot_section()
        
        # Generate sample data
        snapshot = self.data_feed.generate_snapshot()
        self.digital_twin.ingest_real_time_data(snapshot)
        
        # Show current network status
        self._display_network_status(snapshot)
        
        # Interactive scenario selection
        selected_train = None
        while True:
            try:
                print(f"\n🔧 What-If Scenario Options:")
                print(f"1. Select/Change Train (Currently: {selected_train or 'None'})")
                print(f"2. Hold Train at Current Position")
                print(f"3. Reroute Train to Different Station")
                print(f"4. Change Train Speed")
                print(f"5. Run Pre-defined Scenarios")
                print(f"6. Exit What-If Analysis")
                
                choice = input("\nSelect option (1-6): ").strip()
                
                if choice == '1':
                    selected_train = self._select_train(snapshot)
                elif choice == '2' and selected_train:
                    self._run_hold_scenario(selected_train)
                elif choice == '3' and selected_train:
                    self._run_reroute_scenario(selected_train)
                elif choice == '4' and selected_train:
                    self._run_speed_scenario(selected_train)
                elif choice == '5':
                    self._run_predefined_scenarios()
                elif choice == '6':
                    break
                else:
                    if not selected_train and choice in ['2', '3', '4']:
                        print("❌ Please select a train first (Option 1)")
                    else:
                        print("❌ Invalid choice. Please try again.")
                        
            except KeyboardInterrupt:
                print("\n👋 Exiting what-if analysis...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _display_network_status(self, snapshot):
        """Display current network status for context"""
        print(f"\n📊 Current Network Status:")
        print(f"   {'=' * 30}")
        
        trains = snapshot.get('trains', [])
        print(f"   📍 Active Trains: {len(trains)}")
        
        for i, train in enumerate(trains, 1):
            status = "🟢 On-time" if train.get('delay_minutes', 0) <= 2 else f"🔴 Delayed {train.get('delay_minutes', 0)}min"
            print(f"     {i}. {train['train_id']} - {status} @ {train.get('current_node', 'Unknown')}")
        
        signals = snapshot.get('signals', [])
        print(f"   🚦 Signal Status: {len([s for s in signals if s['aspect'] != 'GREEN'])} restricted")
        
    def _select_train(self, snapshot):
        """Allow user to select a train for scenarios"""
        trains = snapshot.get('trains', [])
        if not trains:
            print("❌ No trains available for simulation")
            return None
            
        print(f"\n🚂 Available Trains:")
        for i, train in enumerate(trains, 1):
            speed = train.get('current_speed', 0)
            location = train.get('current_node', 'Unknown')
            delay = train.get('delay_minutes', 0)
            delay_text = f"({delay}min delay)" if delay > 0 else "(on-time)"
            print(f"   {i}. {train['train_id']} - {speed} km/h @ {location} {delay_text}")
            
        while True:
            try:
                choice = input(f"\nSelect train (1-{len(trains)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(trains):
                    selected = trains[idx]['train_id']
                    print(f"✅ Selected train: {selected}")
                    return selected
                else:
                    print(f"❌ Please enter a number between 1 and {len(trains)}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                return None
    
    def _run_hold_scenario(self, train_id):
        """Run hold scenario with user input"""
        print(f"\n⏸️  Hold Scenario for {train_id}")
        print(f"   {'=' * 35}")
        
        try:
            duration = int(input("Enter hold duration in minutes (1-60): "))
            if duration < 1 or duration > 60:
                print("❌ Duration must be between 1-60 minutes")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
            
        scenario = {
            'name': f'Hold {train_id} for {duration} minutes',
            'train_id': train_id,
            'action': 'HOLD',
            'duration_minutes': duration
        }
        
        result = self.digital_twin.run_what_if_simulation(scenario)
        self._display_scenario_results(scenario, result)
    
    def _run_reroute_scenario(self, train_id):
        """Run reroute scenario with user input"""
        print(f"\n🔄 Reroute Scenario for {train_id}")
        print(f"   {'=' * 38}")
        
        stations = ['STN_A', 'STN_B', 'JUN_001']
        print("\nAvailable destinations:")
        for i, station in enumerate(stations, 1):
            print(f"   {i}. {station}")
            
        try:
            choice = int(input(f"\nSelect destination (1-{len(stations)}): "))
            if choice < 1 or choice > len(stations):
                print(f"❌ Please enter a number between 1 and {len(stations)}")
                return
            target = stations[choice - 1]
        except ValueError:
            print("❌ Please enter a valid number")
            return
            
        scenario = {
            'name': f'Reroute {train_id} to {target}',
            'train_id': train_id,
            'action': 'REROUTE', 
            'target_node': target,
            'duration_minutes': 30
        }
        
        result = self.digital_twin.run_what_if_simulation(scenario)
        self._display_scenario_results(scenario, result)
    
    def _run_speed_scenario(self, train_id):
        """Run speed change scenario"""
        print(f"\n🏃 Speed Change Scenario for {train_id}")
        print(f"   {'=' * 42}")
        
        try:
            speed = int(input("Enter new target speed (20-120 km/h): "))
            if speed < 20 or speed > 120:
                print("❌ Speed must be between 20-120 km/h")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
            
        # For demo purposes, simulate speed change as a hold with modified impact
        scenario = {
            'name': f'Change {train_id} speed to {speed} km/h',
            'train_id': train_id,
            'action': 'HOLD',  # Simulate as brief hold for speed adjustment
            'duration_minutes': 2,
            'target_speed': speed
        }
        
        result = self.digital_twin.run_what_if_simulation(scenario)
        # Modify result for speed change context
        if 'impact_analysis' in result:
            result['impact_analysis']['delay_added_minutes'] = max(0, (80 - speed) / 40)  # Speed-dependent delay
            result['impact_analysis']['capacity_impact'] = 'SPEED_OPTIMIZED'
            
        self._display_scenario_results(scenario, result)
    
    def _run_predefined_scenarios(self):
        """Run pre-defined scenarios for quick demo"""
        print(f"\n📋 Pre-defined Scenarios")
        print(f"   {'=' * 25}")
        
        scenarios = [
            {
                'name': 'Emergency: Hold all freight trains', 
                'train_id': 'T003',
                'action': 'HOLD',
                'duration_minutes': 15
            },
            {
                'name': 'Optimization: Reroute express via bypass',
                'train_id': 'T001',
                'action': 'REROUTE',
                'target_node': 'STN_B',
                'duration_minutes': 25
            },
            {
                'name': 'Signal failure: Hold approaching trains',
                'train_id': 'T002', 
                'action': 'HOLD',
                'duration_minutes': 8
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. 📋 {scenario['name']}")
            result = self.digital_twin.run_what_if_simulation(scenario)
            self._display_scenario_results(scenario, result, compact=True)
    
    def _display_scenario_results(self, scenario, result, compact=False):
        """Display scenario results using enhanced formatting"""
        self.enhanced_display.display_scenario_results(scenario, result, compact)
    

async def main():
    """Main demo execution"""
    demo = IDSSDemo()
    
    print("Select demonstration mode:")
    print("1. Live System Demo (2 minutes)")
    print("2. What-If Scenarios Demo")
    print("3. Both")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
    except:
        choice = "3"  # Default to both
    
    if choice in ["1", "3"]:
        await demo.run_live_demo(2)
    
    if choice in ["2", "3"]:
        demo.run_what_if_demo()
    
    print(f"\n🎉 Demonstration Complete!")

if __name__ == "__main__":
    asyncio.run(main())
