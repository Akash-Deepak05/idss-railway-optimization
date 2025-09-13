"""
Enhanced What-If Scenario Output Formatter
Provides beautiful, colorful and human-readable output for scenario simulations
"""

import time
import os
from datetime import datetime

# ANSI Color codes (work in most terminals)
class Colors:
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def disable_if_needed():
        """Disable colors if not supported"""
        if os.name == 'nt':  # Windows
            try:
                # Enable VT100 for Windows 10+
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                # If failed, disable colors
                for attr in dir(Colors):
                    if not attr.startswith('__') and isinstance(getattr(Colors, attr), str):
                        setattr(Colors, attr, '')

class EnhancedDisplay:
    """Enhanced display formatting for scenario results"""
    
    def __init__(self):
        Colors.disable_if_needed()
        
    def display_header(self, title, width=70):
        """Display a beautiful header"""
        print("\n")
        print(f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD} {title.center(width-2)} {Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}{'═' * width}{Colors.RESET}")
        
    def display_subheader(self, subtitle, width=70):
        """Display a sub-header"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{subtitle}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * width}{Colors.RESET}")
    
    def display_scenario_details(self, scenario):
        """Display scenario configuration details"""
        print(f"\n{Colors.BRIGHT_WHITE}{Colors.BOLD}📋 Scenario Configuration:{Colors.RESET}")
        
        # Scenario type icon based on action
        action = scenario.get('action', '').upper()
        if action == 'HOLD':
            icon = "⏸️"
            action_desc = f"{Colors.YELLOW}HOLD{Colors.RESET}"
        elif action == 'REROUTE':
            icon = "🔄"
            action_desc = f"{Colors.MAGENTA}REROUTE{Colors.RESET}"
        else:
            icon = "🔧"
            action_desc = f"{Colors.BLUE}{action}{Colors.RESET}"
        
        print(f"  {icon} {Colors.BOLD}Type:{Colors.RESET} {action_desc}")
        
        # Train with highlighted ID
        train_id = scenario.get('train_id', 'Unknown')
        print(f"  🚂 {Colors.BOLD}Train:{Colors.RESET} {Colors.BRIGHT_GREEN}{train_id}{Colors.RESET}")
        
        # Duration with visual scale
        duration = scenario.get('duration_minutes', 0)
        if duration > 0:
            scale = min(10, duration)
            bar = f"{Colors.YELLOW}{'■' * scale}{Colors.RESET}{'□' * (10-scale)}"
            print(f"  ⏱️  {Colors.BOLD}Duration:{Colors.RESET} {duration} minutes {bar}")
        
        # Additional parameters based on action type
        if action == 'REROUTE' and 'target_node' in scenario:
            print(f"  📍 {Colors.BOLD}Destination:{Colors.RESET} {Colors.CYAN}{scenario['target_node']}{Colors.RESET}")
        
        if 'target_speed' in scenario:
            speed = scenario.get('target_speed', 0)
            print(f"  🏁 {Colors.BOLD}Target Speed:{Colors.RESET} {Colors.BRIGHT_CYAN}{speed} km/h{Colors.RESET}")
    
    def display_impact_results(self, result):
        """Display impact analysis results with visual elements"""
        impact = result.get('impact_analysis', {})
        
        # Main section header
        self.display_subheader("📊 Impact Analysis", 50)
        
        # Delay impact with visual indicator
        delay = impact.get('delay_added_minutes', 0)
        if delay > 0:
            delay_severity = self._get_severity_colors(delay, [5, 10])
            delay_bar = self._generate_bar(delay, 15, color=delay_severity)
            print(f"  ⏱️  {Colors.BOLD}Time Impact:{Colors.RESET} {delay_severity}+{delay:.1f} minutes{Colors.RESET} {delay_bar}")
        else:
            print(f"  ⏱️  {Colors.BOLD}Time Impact:{Colors.RESET} {Colors.GREEN}No significant delay{Colors.RESET}")
        
        # Affected trains
        affected_trains = impact.get('affected_trains', [])
        affected_count = len(affected_trains)
        if affected_count > 0:
            affected_severity = self._get_severity_colors(affected_count, [1, 3])
            print(f"  🚂 {Colors.BOLD}Affected Trains:{Colors.RESET} {affected_severity}{affected_count}{Colors.RESET}")
            
            # List affected trains if any
            if affected_count > 0 and affected_count <= 5:
                for train in affected_trains:
                    print(f"     - {Colors.CYAN}{train}{Colors.RESET}")
        else:
            print(f"  🚂 {Colors.BOLD}Affected Trains:{Colors.RESET} {Colors.GREEN}None{Colors.RESET}")
        
        # Capacity impact
        capacity_impact = impact.get('capacity_impact', 'Unknown')
        capacity_color = {
            'LOW': Colors.GREEN,
            'MODERATE': Colors.YELLOW,
            'HIGH': Colors.RED,
            'SPEED_OPTIMIZED': Colors.BRIGHT_CYAN
        }.get(capacity_impact, Colors.WHITE)
        
        print(f"  📈 {Colors.BOLD}Capacity Impact:{Colors.RESET} {capacity_color}{capacity_impact}{Colors.RESET}")
        
        # Route changes if applicable
        if impact.get('route_change', False):
            distance = impact.get('additional_distance_km', 0)
            print(f"  🛤️  {Colors.BOLD}Route Change:{Colors.RESET} {Colors.MAGENTA}+{distance} km{Colors.RESET}")
        
        # Recovery time
        recovery = impact.get('estimated_recovery_time', 0)
        if recovery > 0:
            print(f"  🔄 {Colors.BOLD}Recovery Time:{Colors.RESET} ~{Colors.YELLOW}{recovery:.1f}{Colors.RESET} minutes")
            
        # Final position and speed from predicted states
        states = result.get('predicted_states', [])
        if states and len(states) > 1:
            final_state = states[-1]
            position = final_state.get('current_node', 'Unknown')
            speed = final_state.get('current_speed', 0)
            
            print(f"  🎯 {Colors.BOLD}Final Position:{Colors.RESET} {Colors.BRIGHT_BLUE}{position}{Colors.RESET}")
            
            # Speed with visual indicator
            if speed > 60:
                speed_color = Colors.GREEN
            elif speed > 30:
                speed_color = Colors.YELLOW
            else:
                speed_color = Colors.RED
                
            print(f"  🏎️  {Colors.BOLD}Final Speed:{Colors.RESET} {speed_color}{speed:.1f} km/h{Colors.RESET}")
    
    def display_risk_assessment(self, impact):
        """Display risk assessment with visual indicators"""
        self.display_subheader("🔍 Risk Assessment", 50)
        
        # Calculate risk level
        delay = impact.get('delay_added_minutes', 0)
        affected = len(impact.get('affected_trains', []))
        
        if delay > 10 or affected > 2:
            risk_level = 'HIGH'
            risk_color = Colors.RED
            risk_bar = f"{Colors.RED}{'■' * 10}{Colors.RESET}"
        elif delay > 5 or affected > 1:
            risk_level = 'MEDIUM'
            risk_color = Colors.YELLOW
            risk_bar = f"{Colors.YELLOW}{'■' * 7}{Colors.RESET}{'□' * 3}"
        else:
            risk_level = 'LOW'
            risk_color = Colors.GREEN
            risk_bar = f"{Colors.GREEN}{'■' * 3}{Colors.RESET}{'□' * 7}"
        
        risk_emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}.get(risk_level, '⚪')
        
        # Print risk level with visual indicator
        print(f"  {risk_emoji} {Colors.BOLD}Overall Risk:{Colors.RESET} {risk_color}{risk_level}{Colors.RESET} {risk_bar}")
        
        # Risk factors
        print(f"  📊 {Colors.BOLD}Risk Factors:{Colors.RESET}")
        
        delay_factor = self._get_severity_colors(delay, [5, 10])
        print(f"     • Time Impact: {delay_factor}{delay:.1f} min{Colors.RESET}")
        
        affected_factor = self._get_severity_colors(affected, [1, 3])
        print(f"     • Affected Trains: {affected_factor}{affected}{Colors.RESET}")
        
        capacity = impact.get('capacity_impact', 'Unknown')
        capacity_color = {
            'LOW': Colors.GREEN,
            'MODERATE': Colors.YELLOW,
            'HIGH': Colors.RED
        }.get(capacity, Colors.WHITE)
        print(f"     • Capacity: {capacity_color}{capacity}{Colors.RESET}")
    
    def display_recommendations(self, scenario, impact):
        """Display AI recommendations with icons and formatting"""
        recommendations = self._generate_recommendations(scenario, impact)
        
        if recommendations:
            self.display_subheader("💡 AI Recommendations", 50)
            
            for i, rec in enumerate(recommendations, 1):
                rec_text, rec_type = rec
                
                # Choose icon based on recommendation type
                icon = {
                    'critical': '🚨',
                    'important': '⚠️',
                    'optimization': '⚙️',
                    'information': 'ℹ️'
                }.get(rec_type, '•')
                
                # Choose color based on type
                color = {
                    'critical': Colors.RED,
                    'important': Colors.YELLOW,
                    'optimization': Colors.BLUE,
                    'information': Colors.CYAN
                }.get(rec_type, Colors.WHITE)
                
                print(f"  {icon} {color}{rec_text}{Colors.RESET}")
    
    def display_scenario_results(self, scenario, result, compact=False):
        """Display complete scenario results with enhanced formatting"""
        if 'error' in result:
            print(f"\n{Colors.RED}❌ Simulation Error: {result['error']}{Colors.RESET}")
            return
            
        # Header with scenario name
        scenario_name = scenario.get('name', f"{scenario.get('action', 'Unknown')} Scenario")
        self.display_header(f"Scenario: {scenario_name}")
        
        # Timestamp for reference
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{Colors.CYAN}Simulation completed at {timestamp}{Colors.RESET}")
        
        # Configuration details
        self.display_scenario_details(scenario)
        
        # Impact analysis results
        impact = result.get('impact_analysis', {})
        self.display_impact_results(result)
        
        # Risk assessment
        self.display_risk_assessment(impact)
        
        # AI recommendations
        self.display_recommendations(scenario, impact)
        
        if not compact:
            # Footer
            print(f"\n{Colors.BRIGHT_BLUE}{'═' * 70}{Colors.RESET}")
            print(f"{Colors.CYAN}Tip: Modify scenario parameters to see different outcomes{Colors.RESET}")
    
    def _get_severity_colors(self, value, thresholds):
        """Get color based on severity thresholds [medium, high]"""
        if value > thresholds[1]:
            return Colors.RED
        elif value > thresholds[0]:
            return Colors.YELLOW
        else:
            return Colors.GREEN
    
    def _generate_bar(self, value, max_length=10, color=None):
        """Generate a visual bar based on value"""
        if not color:
            color = Colors.YELLOW
            
        filled = min(max_length, int(value))
        if filled < 1 and value > 0:
            filled = 1
            
        return f"{color}{'■' * filled}{Colors.RESET}{'□' * (max_length - filled)}"
    
    def _generate_recommendations(self, scenario, impact):
        """Generate recommendations with type classification"""
        recommendations = []
        
        action = scenario.get('action')
        delay = impact.get('delay_added_minutes', 0)
        
        if action == 'HOLD':
            if delay > 10:
                recommendations.append(("Consider alternative routing for following trains", "important"))
                recommendations.append(("Notify passengers of expected delays", "important"))
            recommendations.append(("Monitor signal clearance for early release", "optimization"))
            
        elif action == 'REROUTE':
            recommendations.append(("Verify track availability on alternate route", "important"))
            recommendations.append(("Update passenger information systems", "information"))
            if impact.get('additional_distance_km', 0) > 3:
                recommendations.append(("Consider fuel/energy impact for longer route", "optimization"))
                
        # General recommendations
        if impact.get('capacity_impact') == 'HIGH':
            recommendations.append(("Implement contingency timetable adjustments", "critical"))
            
        return recommendations

# Demo function to show enhanced display
def demo_enhanced_display():
    """Demo function to show the enhanced display capabilities"""
    display = EnhancedDisplay()
    
    # Sample scenario
    scenario = {
        'name': 'Hold T003 for 15 minutes (High Impact Test)',
        'train_id': 'T003',
        'action': 'HOLD',
        'duration_minutes': 15
    }
    
    # Sample result with impact analysis
    result = {
        'impact_analysis': {
            'delay_added_minutes': 15.0,
            'affected_trains': ['T001', 'T004'],
            'capacity_impact': 'MODERATE',
            'estimated_recovery_time': 22.5
        },
        'predicted_states': [
            {'current_node': 'JUN_001', 'current_speed': 60.0},
            {'current_node': 'JUN_001', 'current_speed': 0.0}
        ]
    }
    
    # Display the enhanced output
    display.display_scenario_results(scenario, result)
    
if __name__ == "__main__":
    demo_enhanced_display()