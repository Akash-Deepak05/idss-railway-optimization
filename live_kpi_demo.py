"""
Live KPI Monitoring Dashboard Demo
Real-time visualization of operational, financial, safety, and AI performance metrics
"""

import asyncio
import time
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from integration.mock_data_feed import MockRailwayDataFeed
from digital_twin.cognitive_twin import CognitiveTwin
from analytics.predictor import AnalyticsEngine
from monitoring.kpi_logger import KPILogger
from enhanced_scenario_display import EnhancedDisplay, Colors

class LiveKPIDashboard:
    """Live KPI monitoring dashboard with real-time updates"""
    
    def __init__(self):
        self.data_feed = MockRailwayDataFeed()
        self.digital_twin = CognitiveTwin({"pilot_section": "STN_A_TO_STN_B"})
        self.analytics = AnalyticsEngine()
        self.kpi_logger = KPILogger("live_monitoring")
        self.display = EnhancedDisplay()
        
        # Initialize system
        self.digital_twin.initialize_pilot_section()
        
        # KPI tracking
        self.session_start = datetime.now()
        self.cycle_count = 0
        self.total_conflicts_predicted = 0
        self.total_recommendations = 0
        
        # Performance history for trends
        self.performance_history = []
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_dashboard_header(self):
        """Display the main dashboard header"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60
        
        print(f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}")
        print(f"  🚂 IDSS LIVE KPI MONITORING DASHBOARD  ".center(80))
        print(f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}{'═' * 80}{Colors.RESET}")
        
        print(f"{Colors.CYAN}📅 Current Time: {current_time}")
        print(f"⏱️  Session Duration: {session_duration:.1f} minutes")
        print(f"🔄 Monitoring Cycle: #{self.cycle_count}{Colors.RESET}\n")
    
    def display_operational_kpis(self, snapshot: Dict[str, Any], analysis: Dict[str, Any]):
        """Display operational performance indicators"""
        print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}🚄 OPERATIONAL PERFORMANCE{Colors.RESET}")
        print(f"{Colors.GREEN}{'─' * 50}{Colors.RESET}")
        
        # Extract data from snapshot
        section_status = snapshot.get('section_status', {})
        total_trains = section_status.get('total_trains', 0)
        delayed_trains = section_status.get('delayed_trains', 0)
        on_time_trains = max(0, total_trains - delayed_trains)
        avg_delay = section_status.get('average_delay', 0)
        throughput = total_trains * 2  # Mock throughput calculation
        
        # Calculate punctuality
        punctuality = (on_time_trains / total_trains * 100) if total_trains > 0 else 100
        
        # Display metrics with visual indicators
        print(f"  🚂 {Colors.BOLD}Active Trains:{Colors.RESET} {Colors.BRIGHT_CYAN}{total_trains}{Colors.RESET}")
        
        # On-time vs delayed with color coding
        if delayed_trains == 0:
            status_color = Colors.GREEN
            status_text = "All On-Time ✅"
        elif delayed_trains <= total_trains * 0.2:  # Less than 20% delayed
            status_color = Colors.YELLOW
            status_text = f"{on_time_trains} On-Time, {delayed_trains} Delayed"
        else:
            status_color = Colors.RED
            status_text = f"{on_time_trains} On-Time, {delayed_trains} Delayed"
        
        print(f"  📊 {Colors.BOLD}Train Status:{Colors.RESET} {status_color}{status_text}{Colors.RESET}")
        
        # Average delay with visual indicator
        if avg_delay <= 2:
            delay_color = Colors.GREEN
        elif avg_delay <= 5:
            delay_color = Colors.YELLOW
        else:
            delay_color = Colors.RED
        
        print(f"  ⏰ {Colors.BOLD}Avg Delay:{Colors.RESET} {delay_color}{avg_delay:.1f} minutes{Colors.RESET}")
        
        # Punctuality percentage with bar
        punctuality_bar = self._generate_percentage_bar(punctuality)
        punctuality_color = self._get_performance_color(punctuality, 95, 85)
        print(f"  🎯 {Colors.BOLD}Punctuality:{Colors.RESET} {punctuality_color}{punctuality:.1f}%{Colors.RESET} {punctuality_bar}")
        
        # Throughput
        print(f"  📈 {Colors.BOLD}Throughput:{Colors.RESET} {Colors.BRIGHT_CYAN}{throughput:.1f}{Colors.RESET} trains/hour")
        
        # Asset utilization (mock)
        asset_util = max(60, min(95, 75 + (total_trains - 3) * 5))
        util_bar = self._generate_percentage_bar(asset_util)
        util_color = self._get_performance_color(asset_util, 80, 60)
        print(f"  🏭 {Colors.BOLD}Asset Utilization:{Colors.RESET} {util_color}{asset_util:.1f}%{Colors.RESET} {util_bar}")
    
    def display_ai_performance_kpis(self, analysis: Dict[str, Any]):
        """Display AI system performance indicators"""
        print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}🧠 AI SYSTEM PERFORMANCE{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'─' * 50}{Colors.RESET}")
        
        conflicts_predicted = analysis.get('conflicts_predicted', 0)
        recommendations_generated = analysis.get('recommendations_generated', 0)
        
        # Update session totals
        self.total_conflicts_predicted += conflicts_predicted
        self.total_recommendations += recommendations_generated
        
        # Current cycle performance
        print(f"  🎯 {Colors.BOLD}Conflicts Predicted:{Colors.RESET} {Colors.BRIGHT_YELLOW}{conflicts_predicted}{Colors.RESET}")
        print(f"  💡 {Colors.BOLD}Recommendations Generated:{Colors.RESET} {Colors.BRIGHT_CYAN}{recommendations_generated}{Colors.RESET}")
        
        # Session totals
        print(f"  📊 {Colors.BOLD}Session Totals:{Colors.RESET}")
        print(f"     • Total Conflicts: {Colors.YELLOW}{self.total_conflicts_predicted}{Colors.RESET}")
        print(f"     • Total Recommendations: {Colors.CYAN}{self.total_recommendations}{Colors.RESET}")
        
        # AI Performance Metrics
        prediction_accuracy = 0.87 + (self.cycle_count % 5) * 0.02  # Mock variation
        response_time = 245 + (self.cycle_count % 3) * 15  # Mock variation
        acceptance_rate = 0.78 + (self.cycle_count % 4) * 0.03  # Mock variation
        
        # Prediction accuracy
        accuracy_bar = self._generate_percentage_bar(prediction_accuracy * 100)
        accuracy_color = self._get_performance_color(prediction_accuracy * 100, 85, 75)
        print(f"  🔍 {Colors.BOLD}Prediction Accuracy:{Colors.RESET} {accuracy_color}{prediction_accuracy:.1%}{Colors.RESET} {accuracy_bar}")
        
        # Response time
        if response_time <= 200:
            response_color = Colors.GREEN
        elif response_time <= 300:
            response_color = Colors.YELLOW
        else:
            response_color = Colors.RED
        print(f"  ⚡ {Colors.BOLD}Response Time:{Colors.RESET} {response_color}{response_time:.0f}ms{Colors.RESET}")
        
        # Recommendation acceptance rate
        acceptance_bar = self._generate_percentage_bar(acceptance_rate * 100)
        acceptance_color = self._get_performance_color(acceptance_rate * 100, 80, 70)
        print(f"  ✅ {Colors.BOLD}Acceptance Rate:{Colors.RESET} {acceptance_color}{acceptance_rate:.1%}{Colors.RESET} {acceptance_bar}")
    
    def display_safety_kpis(self):
        """Display safety and reliability indicators"""
        print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}🛡️  SAFETY & RELIABILITY{Colors.RESET}")
        print(f"{Colors.RED}{'─' * 50}{Colors.RESET}")
        
        # Mock safety metrics
        maintenance_success = 0.92 + (self.cycle_count % 3) * 0.01
        delays_prevented = self.cycle_count // 3
        safety_violations = max(0, (self.cycle_count - 10) // 15)  # Occasional violations after cycle 10
        signal_failures = max(0, (self.cycle_count - 8) // 12)
        
        # Predictive maintenance success rate
        maintenance_bar = self._generate_percentage_bar(maintenance_success * 100)
        maintenance_color = self._get_performance_color(maintenance_success * 100, 90, 80)
        print(f"  🔧 {Colors.BOLD}Predictive Maintenance:{Colors.RESET} {maintenance_color}{maintenance_success:.1%}{Colors.RESET} {maintenance_bar}")
        
        # Delays prevented
        if delays_prevented > 0:
            print(f"  ⏸️  {Colors.BOLD}Delays Prevented:{Colors.RESET} {Colors.GREEN}{delays_prevented}{Colors.RESET} incidents")
        else:
            print(f"  ⏸️  {Colors.BOLD}Delays Prevented:{Colors.RESET} {Colors.CYAN}0{Colors.RESET} incidents (monitoring...)")
        
        # Safety violations
        if safety_violations == 0:
            print(f"  🛡️  {Colors.BOLD}Safety Violations:{Colors.RESET} {Colors.GREEN}None{Colors.RESET} ✅")
        else:
            print(f"  🛡️  {Colors.BOLD}Safety Violations:{Colors.RESET} {Colors.RED}{safety_violations}{Colors.RESET} ⚠️")
        
        # Signal failures
        if signal_failures == 0:
            print(f"  🚦 {Colors.BOLD}Signal Status:{Colors.RESET} {Colors.GREEN}All Operational{Colors.RESET} ✅")
        else:
            print(f"  🚦 {Colors.BOLD}Signal Failures:{Colors.RESET} {Colors.RED}{signal_failures}{Colors.RESET} ⚠️")
    
    def display_financial_kpis(self):
        """Display financial performance indicators"""
        print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}💰 FINANCIAL PERFORMANCE{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─' * 50}{Colors.RESET}")
        
        # Mock financial metrics
        operating_ratio = max(0.85, 0.95 - (self.cycle_count * 0.002))  # Improving over time
        cost_savings = self.cycle_count * 1250 + (self.total_recommendations * 350)  # Mock savings
        energy_efficiency = min(15, self.cycle_count * 0.3)  # Mock efficiency improvement
        
        # Operating ratio (lower is better)
        ratio_color = Colors.GREEN if operating_ratio <= 0.90 else Colors.YELLOW if operating_ratio <= 0.95 else Colors.RED
        print(f"  📊 {Colors.BOLD}Operating Ratio:{Colors.RESET} {ratio_color}{operating_ratio:.3f}{Colors.RESET}")
        
        # Cost savings
        print(f"  💵 {Colors.BOLD}Cost Savings:{Colors.RESET} {Colors.GREEN}₹{cost_savings:,.0f}{Colors.RESET} (session)")
        
        # Energy efficiency improvement
        if energy_efficiency > 0:
            efficiency_bar = self._generate_bar(energy_efficiency, 15)
            print(f"  ⚡ {Colors.BOLD}Energy Efficiency:{Colors.RESET} {Colors.GREEN}+{energy_efficiency:.1f}%{Colors.RESET} {efficiency_bar}")
        else:
            print(f"  ⚡ {Colors.BOLD}Energy Efficiency:{Colors.RESET} {Colors.CYAN}Baseline{Colors.RESET} (measuring...)")
        
        # Revenue impact
        revenue_impact = cost_savings * 0.15  # Mock revenue correlation
        print(f"  📈 {Colors.BOLD}Revenue Impact:{Colors.RESET} {Colors.GREEN}+₹{revenue_impact:,.0f}{Colors.RESET}")
    
    def display_live_alerts(self, analysis: Dict[str, Any]):
        """Display live system alerts and recommendations"""
        print(f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD} 🚨 LIVE ALERTS & RECOMMENDATIONS {Colors.RESET}")
        print(f"{Colors.BRIGHT_RED}{'═' * 50}{Colors.RESET}")
        
        conflicts = analysis.get('conflicts', [])
        recommendations = analysis.get('recommendations', [])
        
        if conflicts:
            print(f"\n  {Colors.RED}{Colors.BOLD}⚠️  Active Conflicts:{Colors.RESET}")
            for i, conflict in enumerate(conflicts[:3], 1):
                probability = conflict.get('probability', 0.5)
                prob_color = Colors.RED if probability > 0.8 else Colors.YELLOW if probability > 0.5 else Colors.GREEN
                print(f"    {i}. {conflict['type']} at {conflict['location']}")
                print(f"       Probability: {prob_color}{probability:.0%}{Colors.RESET}")
        
        if recommendations:
            print(f"\n  {Colors.CYAN}{Colors.BOLD}💡 AI Recommendations:{Colors.RESET}")
            for i, rec in enumerate(recommendations[:3], 1):
                rec_type = rec.get('type', 'Unknown')
                train = rec.get('train', 'Unknown')
                benefit = rec.get('expected_benefit', 'Improved flow')
                
                print(f"    {i}. {Colors.BRIGHT_CYAN}{rec_type}{Colors.RESET} for {Colors.GREEN}{train}{Colors.RESET}")
                print(f"       Expected: {Colors.YELLOW}{benefit}{Colors.RESET}")
        
        if not conflicts and not recommendations:
            print(f"  {Colors.GREEN}✅ System Operating Normally{Colors.RESET}")
            print(f"  {Colors.CYAN}🔍 Continuous monitoring active...{Colors.RESET}")
    
    def display_trend_analysis(self):
        """Display performance trends"""
        if len(self.performance_history) < 3:
            return
            
        print(f"\n{Colors.BRIGHT_BLUE}{Colors.BOLD}📊 PERFORMANCE TRENDS{Colors.RESET}")
        print(f"{Colors.BLUE}{'─' * 50}{Colors.RESET}")
        
        # Analyze last 5 cycles
        recent_history = self.performance_history[-5:]
        
        # Punctuality trend
        punctuality_trend = [cycle.get('punctuality', 0) for cycle in recent_history]
        if len(punctuality_trend) >= 2:
            trend_direction = "📈" if punctuality_trend[-1] > punctuality_trend[-2] else "📉"
            avg_punctuality = sum(punctuality_trend) / len(punctuality_trend)
            print(f"  🎯 {Colors.BOLD}Punctuality Trend:{Colors.RESET} {trend_direction} {avg_punctuality:.1f}% avg")
        
        # AI Performance trend
        ai_accuracy_trend = [cycle.get('ai_accuracy', 0) for cycle in recent_history]
        if len(ai_accuracy_trend) >= 2:
            trend_direction = "📈" if ai_accuracy_trend[-1] > ai_accuracy_trend[-2] else "📉"
            avg_accuracy = sum(ai_accuracy_trend) / len(ai_accuracy_trend)
            print(f"  🧠 {Colors.BOLD}AI Accuracy Trend:{Colors.RESET} {trend_direction} {avg_accuracy:.1%} avg")
    
    def _generate_percentage_bar(self, percentage: float, width: int = 10) -> str:
        """Generate a visual percentage bar"""
        filled = int(percentage / 10)  # Scale to 0-10
        filled = max(0, min(width, filled))
        
        if percentage >= 90:
            color = Colors.GREEN
        elif percentage >= 70:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        return f"{color}{'■' * filled}{Colors.RESET}{'□' * (width - filled)}"
    
    def _generate_bar(self, value: float, max_value: float, width: int = 10) -> str:
        """Generate a visual bar for arbitrary values"""
        filled = int((value / max_value) * width)
        filled = max(0, min(width, filled))
        
        return f"{Colors.GREEN}{'■' * filled}{Colors.RESET}{'□' * (width - filled)}"
    
    def _get_performance_color(self, value: float, good_threshold: float, ok_threshold: float) -> str:
        """Get color based on performance thresholds"""
        if value >= good_threshold:
            return Colors.GREEN
        elif value >= ok_threshold:
            return Colors.YELLOW
        else:
            return Colors.RED
    
    async def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        self.cycle_count += 1
        
        # Generate fresh data
        snapshot = self.data_feed.generate_snapshot()
        self.digital_twin.ingest_real_time_data(snapshot)
        
        # Run analytics
        analysis = self.analytics.analyze(snapshot)
        
        # Log KPIs
        kpi_data = self._extract_kpi_data(snapshot, analysis)
        self.kpi_logger.log_kpis(kpi_data)
        
        # Store performance history
        self._store_performance_history(snapshot, analysis)
        
        # Clear screen and display dashboard
        self.clear_screen()
        self.display_dashboard_header()
        self.display_operational_kpis(snapshot, analysis)
        self.display_ai_performance_kpis(analysis)
        self.display_safety_kpis()
        self.display_financial_kpis()
        self.display_live_alerts(analysis)
        self.display_trend_analysis()
        
        # Footer
        print(f"\n{Colors.BRIGHT_BLUE}{'═' * 80}{Colors.RESET}")
        print(f"{Colors.CYAN}⏱️  Next update in 3 seconds... (Press Ctrl+C to stop){Colors.RESET}")
    
    def _extract_kpi_data(self, snapshot: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract KPI data from snapshot and analysis"""
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
                'prediction_accuracy': 0.87 + (self.cycle_count % 5) * 0.02,
                'average_response_time_ms': 245 + (self.cycle_count % 3) * 15,
            },
            'financial': {
                'cost_savings': self.cycle_count * 1250,
                'energy_efficiency_improvement': min(15, self.cycle_count * 0.3),
            },
            'safety': {
                'predictive_maintenance_success_rate': 0.92,
                'unscheduled_delays_prevented': self.cycle_count // 3,
                'safety_violations': max(0, (self.cycle_count - 10) // 15),
                'signal_failures': max(0, (self.cycle_count - 8) // 12),
            }
        }
    
    def _store_performance_history(self, snapshot: Dict[str, Any], analysis: Dict[str, Any]):
        """Store performance data for trend analysis"""
        section_status = snapshot.get('section_status', {})
        total_trains = section_status.get('total_trains', 0)
        delayed_trains = section_status.get('delayed_trains', 0)
        punctuality = ((total_trains - delayed_trains) / total_trains * 100) if total_trains > 0 else 100
        
        performance_data = {
            'cycle': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'punctuality': punctuality,
            'ai_accuracy': 0.87 + (self.cycle_count % 5) * 0.02,
            'conflicts': analysis.get('conflicts_predicted', 0),
            'recommendations': analysis.get('recommendations_generated', 0)
        }
        
        self.performance_history.append(performance_data)
        
        # Keep only last 20 cycles
        if len(self.performance_history) > 20:
            self.performance_history.pop(0)
    
    async def run_live_demo(self, duration_minutes: int = 5):
        """Run the live KPI monitoring demo"""
        print(f"\n{Colors.BG_GREEN}{Colors.WHITE}{Colors.BOLD}")
        print(f"🚀 Starting Live KPI Monitoring Demo ({duration_minutes} minutes)".center(80))
        print(f"{Colors.RESET}")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                await self.run_monitoring_cycle()
                await asyncio.sleep(3)  # Update every 3 seconds
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⏹️  Demo stopped by user{Colors.RESET}")
        
        # Final summary
        self._display_session_summary()
    
    def _display_session_summary(self):
        """Display session summary"""
        duration = (datetime.now() - self.session_start).total_seconds() / 60
        
        print(f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}")
        print(f" 📋 SESSION SUMMARY ".center(80))
        print(f"{Colors.RESET}")
        
        print(f"{Colors.BRIGHT_CYAN}⏱️  Session Duration: {duration:.1f} minutes{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}🔄 Total Cycles: {self.cycle_count}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}🎯 Total Conflicts Predicted: {self.total_conflicts_predicted}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}💡 Total Recommendations: {self.total_recommendations}{Colors.RESET}")
        
        # Export final report
        try:
            exported_files = self.kpi_logger.export_data("json", hours_back=1)
            if exported_files:
                print(f"\n{Colors.GREEN}📁 KPI data exported to:{Colors.RESET}")
                for file in exported_files:
                    print(f"   • {Colors.CYAN}{file}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Note: Could not export data ({e}){Colors.RESET}")
        
        print(f"\n{Colors.GREEN}✅ Live KPI Monitoring Demo Complete!{Colors.RESET}")

async def main():
    """Main function to run the live KPI demo"""
    dashboard = LiveKPIDashboard()
    
    print("🚂 IDSS Live KPI Monitoring Dashboard")
    print("=====================================")
    print()
    print("This demo will show:")
    print("• Real-time operational metrics")
    print("• AI system performance indicators")
    print("• Safety and reliability monitoring")
    print("• Financial performance tracking")
    print("• Live alerts and recommendations")
    print("• Performance trend analysis")
    print()
    
    try:
        duration = input("Enter demo duration in minutes (default 3): ").strip()
        duration = int(duration) if duration else 3
    except:
        duration = 3
    
    await dashboard.run_live_demo(duration)

if __name__ == "__main__":
    asyncio.run(main())