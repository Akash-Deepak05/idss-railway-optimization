"""
Unified IDSS Dashboard
Comprehensive single interface combining all system functionalities:
- Web Dashboard Server
- Live KPI Monitoring
- Enhanced What-If Scenarios
- End-to-End System Demo
- Real-time Analytics
"""

import asyncio
import time
import json
import os
import sys
import threading
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from integration.mock_data_feed import MockRailwayDataFeed
from digital_twin.cognitive_twin import CognitiveTwin
from analytics.predictor import AnalyticsEngine
from monitoring.kpi_logger import KPILogger
from core.simple_optimizer import SimpleOptimizer, Train, Section, TrainPriority
from enhanced_scenario_display import EnhancedDisplay, Colors

class WebDashboardHandler(SimpleHTTPRequestHandler):
    """Enhanced web dashboard handler with all functionalities"""
    
    def __init__(self, *args, dashboard=None, **kwargs):
        self.dashboard = dashboard
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests with enhanced functionality"""
        if self.path == '/':
            self.send_dashboard_page()
        elif self.path == '/api/status':
            self.send_json_response(self.dashboard.get_system_status())
        elif self.path == '/api/kpis':
            self.send_json_response(self.dashboard.get_live_kpis())
        elif self.path == '/api/scenarios':
            self.send_json_response(self.dashboard.get_available_scenarios())
        elif self.path.startswith('/api/run_scenario/'):
            scenario_id = self.path.split('/')[-1]
            result = self.dashboard.run_scenario_by_id(scenario_id)
            self.send_json_response(result)
        elif self.path == '/api/analytics':
            self.send_json_response(self.dashboard.get_analytics_data())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for interactive features"""
        if self.path == '/api/run_custom_scenario':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                scenario_data = json.loads(post_data.decode('utf-8'))
                result = self.dashboard.run_custom_scenario(scenario_data)
                self.send_json_response(result)
            except Exception as e:
                self.send_json_response({'error': str(e)})
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))
    
    def send_dashboard_page(self):
        """Send the unified dashboard HTML page"""
        html_content = self.dashboard.generate_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

class UnifiedIDSSDashboard:
    """Unified IDSS Dashboard combining all functionalities"""
    
    def __init__(self, port=8000):
        # Initialize all system components
        self.data_feed = MockRailwayDataFeed()
        self.digital_twin = CognitiveTwin({"pilot_section": "STN_A_TO_STN_B"})
        self.analytics = AnalyticsEngine()
        self.optimizer = SimpleOptimizer()
        self.kpi_logger = KPILogger("unified_monitoring")
        self.display = EnhancedDisplay()
        
        # Initialize system
        self.digital_twin.initialize_pilot_section()
        
        # Dashboard state
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False
        
        # Monitoring state
        self.start_time = datetime.now()
        self.cycle_count = 0
        self.total_conflicts_predicted = 0
        self.total_recommendations = 0
        self.current_snapshot = None
        self.current_analysis = None
        self.performance_history = []
        
        # Predefined scenarios
        self.predefined_scenarios = self._initialize_scenarios()
        
        # Start background monitoring
        self.monitoring_active = True
        
    def _initialize_scenarios(self):
        """Initialize predefined scenarios"""
        return {
            'emergency_hold': {
                'id': 'emergency_hold',
                'name': 'Emergency Hold - High Priority',
                'description': 'Hold train for emergency priority override',
                'action': 'HOLD',
                'duration_minutes': 15,
                'category': 'Emergency'
            },
            'maintenance_reroute': {
                'id': 'maintenance_reroute',
                'name': 'Maintenance Window Reroute',
                'description': 'Reroute train for track maintenance',
                'action': 'REROUTE',
                'target_node': 'STN_B',
                'duration_minutes': 25,
                'category': 'Maintenance'
            },
            'speed_optimization': {
                'id': 'speed_optimization',
                'name': 'Speed Optimization',
                'description': 'Optimize train speed for efficiency',
                'action': 'HOLD',
                'duration_minutes': 3,
                'target_speed': 80,
                'category': 'Optimization'
            },
            'signal_failure': {
                'id': 'signal_failure',
                'name': 'Signal Failure Response',
                'description': 'Handle signal failure scenario',
                'action': 'HOLD',
                'duration_minutes': 12,
                'category': 'Safety'
            }
        }
    
    def start_web_server(self):
        """Start the web dashboard server"""
        try:
            def make_handler():
                def handler(*args, **kwargs):
                    return WebDashboardHandler(*args, dashboard=self, **kwargs)
                return handler
            
            self.server = HTTPServer(('localhost', self.port), make_handler())
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.is_running = True
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to start web server: {e}{Colors.RESET}")
            return False
    
    def stop_web_server(self):
        """Stop the web dashboard server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
    
    async def update_system_data(self):
        """Update system data for monitoring"""
        self.cycle_count += 1
        
        # Generate fresh data
        self.current_snapshot = self.data_feed.generate_snapshot()
        self.digital_twin.ingest_real_time_data(self.current_snapshot)
        
        # Run analytics
        self.current_analysis = self.analytics.analyze(self.current_snapshot)
        
        # Update counters
        self.total_conflicts_predicted += self.current_analysis.get('conflicts_predicted', 0)
        self.total_recommendations += self.current_analysis.get('recommendations_generated', 0)
        
        # Log KPIs
        kpi_data = self._extract_kpi_data()
        self.kpi_logger.log_kpis(kpi_data)
        
        # Store performance history
        self._store_performance_history()
    
    def _extract_kpi_data(self):
        """Extract KPI data from current system state"""
        if not self.current_snapshot or not self.current_analysis:
            return {}
            
        section_status = self.current_snapshot.get('section_status', {})
        
        return {
            'timestamp': datetime.now().isoformat(),
            'operational': {
                'total_trains': section_status.get('total_trains', 0),
                'delayed_trains': section_status.get('delayed_trains', 0),
                'average_delay_minutes': section_status.get('average_delay', 0),
                'throughput_trains_per_hour': section_status.get('total_trains', 0) * 2,
            },
            'ai_performance': {
                'conflicts_predicted': self.current_analysis.get('conflicts_predicted', 0),
                'recommendations_generated': self.current_analysis.get('recommendations_generated', 0),
                'prediction_accuracy': 0.87 + (self.cycle_count % 5) * 0.02,
                'average_response_time_ms': 245 + (self.cycle_count % 3) * 15,
            }
        }
    
    def _store_performance_history(self):
        """Store performance data for trend analysis"""
        if not self.current_snapshot:
            return
            
        section_status = self.current_snapshot.get('section_status', {})
        total_trains = section_status.get('total_trains', 0)
        delayed_trains = section_status.get('delayed_trains', 0)
        punctuality = ((total_trains - delayed_trains) / total_trains * 100) if total_trains > 0 else 100
        
        performance_data = {
            'cycle': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'punctuality': punctuality,
            'ai_accuracy': 0.87 + (self.cycle_count % 5) * 0.02,
            'conflicts': self.current_analysis.get('conflicts_predicted', 0) if self.current_analysis else 0,
            'recommendations': self.current_analysis.get('recommendations_generated', 0) if self.current_analysis else 0
        }
        
        self.performance_history.append(performance_data)
        
        # Keep only last 50 cycles
        if len(self.performance_history) > 50:
            self.performance_history.pop(0)
    
    def get_system_status(self):
        """Get current system status for web API"""
        uptime = (datetime.now() - self.start_time).total_seconds() / 60
        
        return {
            'status': 'running' if self.is_running else 'stopped',
            'uptime_minutes': uptime,
            'cycle_count': self.cycle_count,
            'total_conflicts': self.total_conflicts_predicted,
            'total_recommendations': self.total_recommendations,
            'last_update': datetime.now().isoformat(),
            'active_trains': len(self.current_snapshot.get('trains', [])) if self.current_snapshot else 0
        }
    
    def get_live_kpis(self):
        """Get live KPI data for web dashboard"""
        if not self.current_snapshot or not self.current_analysis:
            return {'error': 'No data available'}
        
        section_status = self.current_snapshot.get('section_status', {})
        total_trains = section_status.get('total_trains', 0)
        delayed_trains = section_status.get('delayed_trains', 0)
        
        return {
            'operational': {
                'total_trains': total_trains,
                'delayed_trains': delayed_trains,
                'punctuality': ((total_trains - delayed_trains) / total_trains * 100) if total_trains > 0 else 100,
                'average_delay': section_status.get('average_delay', 0),
                'throughput': total_trains * 2
            },
            'ai_performance': {
                'conflicts_predicted': self.current_analysis.get('conflicts_predicted', 0),
                'recommendations_generated': self.current_analysis.get('recommendations_generated', 0),
                'prediction_accuracy': 87 + (self.cycle_count % 5) * 2,
                'response_time': 245 + (self.cycle_count % 3) * 15
            },
            'financial': {
                'cost_savings': self.cycle_count * 1250,
                'energy_efficiency': min(15, self.cycle_count * 0.3)
            }
        }
    
    def get_analytics_data(self):
        """Get analytics data for web dashboard"""
        if not self.current_analysis:
            return {'conflicts': [], 'recommendations': []}
        
        return {
            'conflicts': self.current_analysis.get('conflicts', []),
            'recommendations': self.current_analysis.get('recommendations', [])
        }
    
    def get_available_scenarios(self):
        """Get available what-if scenarios"""
        scenarios = list(self.predefined_scenarios.values())
        
        # Add dynamic scenarios based on current trains
        if self.current_snapshot:
            trains = self.current_snapshot.get('trains', [])
            for train in trains[:2]:  # Limit to first 2 trains
                scenarios.append({
                    'id': f"hold_{train['train_id']}",
                    'name': f"Hold {train['train_id']}",
                    'description': f"Hold {train['train_id']} at current position",
                    'action': 'HOLD',
                    'train_id': train['train_id'],
                    'duration_minutes': 10,
                    'category': 'Dynamic'
                })
        
        return scenarios
    
    def run_scenario_by_id(self, scenario_id):
        """Run a predefined scenario by ID"""
        if scenario_id in self.predefined_scenarios:
            scenario = self.predefined_scenarios[scenario_id].copy()
            
            # Set train_id if not specified
            if 'train_id' not in scenario and self.current_snapshot:
                trains = self.current_snapshot.get('trains', [])
                if trains:
                    scenario['train_id'] = trains[0]['train_id']
            
            return self.run_custom_scenario(scenario)
        
        # Check dynamic scenarios
        if scenario_id.startswith('hold_') and self.current_snapshot:
            train_id = scenario_id.replace('hold_', '')
            scenario = {
                'name': f'Hold {train_id}',
                'train_id': train_id,
                'action': 'HOLD',
                'duration_minutes': 10
            }
            return self.run_custom_scenario(scenario)
        
        return {'error': f'Scenario {scenario_id} not found'}
    
    def run_custom_scenario(self, scenario_data):
        """Run a custom what-if scenario"""
        try:
            result = self.digital_twin.run_what_if_simulation(scenario_data)
            
            # Enhance result with additional analysis
            impact = result.get('impact_analysis', {})
            delay = impact.get('delay_added_minutes', 0)
            affected = len(impact.get('affected_trains', []))
            
            if delay > 10 or affected > 2:
                risk_level = 'HIGH'
            elif delay > 5 or affected > 1:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            result['risk_assessment'] = {'level': risk_level}
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def generate_dashboard_html(self):
        """Generate the unified dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDSS Unified Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            line-height: 1.6;
        }
        
        .header {
            background: rgba(0,0,0,0.3);
            padding: 1rem 2rem;
            border-bottom: 2px solid #4a90e2;
        }
        
        .header h1 {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 2rem;
            font-weight: 300;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.5rem;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .panel {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        
        .panel:hover { transform: translateY(-5px); }
        
        .panel h2 {
            color: #4a90e2;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .metric {
            background: rgba(0,0,0,0.2);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.8rem;
            opacity: 0.8;
        }
        
        .scenario-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .scenario-btn {
            background: linear-gradient(45deg, #4a90e2, #357abd);
            border: none;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }
        
        .scenario-btn:hover {
            background: linear-gradient(45deg, #357abd, #2968a3);
            transform: translateY(-2px);
        }
        
        .scenario-btn.emergency {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
        }
        
        .scenario-btn.safety {
            background: linear-gradient(45deg, #f39c12, #e67e22);
        }
        
        .alert-item, .recommendation-item {
            background: rgba(231, 76, 60, 0.2);
            border-left: 4px solid #e74c3c;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 0 8px 8px 0;
        }
        
        .recommendation-item {
            background: rgba(52, 152, 219, 0.2);
            border-left: 4px solid #3498db;
        }
        
        .progress-bar {
            background: rgba(0,0,0,0.3);
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #2ecc71, #27ae60);
            transition: width 0.5s ease;
        }
        
        .logs {
            background: rgba(0,0,0,0.5);
            padding: 1rem;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.8rem;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .full-width { grid-column: 1 / -1; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .live-indicator {
            animation: pulse 2s infinite;
            color: #e74c3c;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .status-good { background: #2ecc71; }
        .status-warning { background: #f39c12; }
        .status-critical { background: #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚂 IDSS Unified Dashboard</h1>
        <div class="status-bar">
            <span id="system-status">System Status: <span class="status-indicator status-good"></span>Running</span>
            <span id="last-update">Last Update: Loading...</span>
            <span class="live-indicator">● LIVE</span>
        </div>
    </div>

    <div class="container">
        <!-- System Overview -->
        <div class="panel">
            <h2>📊 System Overview</h2>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value" id="active-trains">-</div>
                    <div class="metric-label">Active Trains</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="punctuality">-</div>
                    <div class="metric-label">Punctuality %</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="conflicts">-</div>
                    <div class="metric-label">Conflicts</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="recommendations">-</div>
                    <div class="metric-label">Recommendations</div>
                </div>
            </div>
        </div>

        <!-- AI Performance -->
        <div class="panel">
            <h2>🧠 AI Performance</h2>
            <div class="metric">
                <div class="metric-label">Prediction Accuracy</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="ai-accuracy" style="width: 87%"></div>
                </div>
                <span id="ai-accuracy-text">87%</span>
            </div>
            <div class="metric">
                <div class="metric-label">Response Time</div>
                <div class="metric-value" id="response-time">245ms</div>
            </div>
        </div>

        <!-- What-If Scenarios -->
        <div class="panel">
            <h2>🎯 What-If Scenarios</h2>
            <div class="scenario-buttons">
                <button class="scenario-btn emergency" onclick="runScenario('emergency_hold')">
                    🚨 Emergency Hold
                </button>
                <button class="scenario-btn" onclick="runScenario('maintenance_reroute')">
                    🔧 Maintenance Reroute
                </button>
                <button class="scenario-btn" onclick="runScenario('speed_optimization')">
                    ⚡ Speed Optimization
                </button>
                <button class="scenario-btn safety" onclick="runScenario('signal_failure')">
                    🚦 Signal Failure
                </button>
            </div>
            <div id="scenario-results" class="logs" style="display: none;">
                <div>Scenario results will appear here...</div>
            </div>
        </div>

        <!-- Live Alerts -->
        <div class="panel">
            <h2>🚨 Live Alerts</h2>
            <div id="alerts-container">
                <div>Loading alerts...</div>
            </div>
        </div>

        <!-- KPI Monitoring -->
        <div class="panel full-width">
            <h2>📈 Live KPI Monitoring</h2>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value" id="cost-savings">₹0</div>
                    <div class="metric-label">Cost Savings</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="energy-efficiency">0%</div>
                    <div class="metric-label">Energy Efficiency</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="uptime">0</div>
                    <div class="metric-label">Uptime (min)</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="total-cycles">0</div>
                    <div class="metric-label">Total Cycles</div>
                </div>
            </div>
        </div>

        <!-- System Logs -->
        <div class="panel full-width">
            <h2>📋 System Activity Log</h2>
            <div id="system-logs" class="logs">
                <div>System initialized...</div>
            </div>
        </div>
    </div>

    <script>
        let updateInterval;

        function formatNumber(num) {
            if (num >= 1000000) {
                return (num / 1000000).toFixed(1) + 'M';
            } else if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return num.toString();
        }

        function addLog(message) {
            const logs = document.getElementById('system-logs');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.innerHTML = `[${timestamp}] ${message}`;
            logs.appendChild(logEntry);
            logs.scrollTop = logs.scrollHeight;
            
            while (logs.children.length > 20) {
                logs.removeChild(logs.firstChild);
            }
        }

        async function updateDashboard() {
            try {
                const [statusRes, kpiRes, analyticsRes] = await Promise.all([
                    fetch('/api/status'),
                    fetch('/api/kpis'),
                    fetch('/api/analytics')
                ]);
                
                const status = await statusRes.json();
                const kpis = await kpiRes.json();
                const analytics = await analyticsRes.json();
                
                document.getElementById('last-update').textContent = 
                    `Last Update: ${new Date().toLocaleTimeString()}`;
                
                if (!kpis.error) {
                    document.getElementById('active-trains').textContent = kpis.operational.total_trains;
                    document.getElementById('punctuality').textContent = 
                        kpis.operational.punctuality.toFixed(1) + '%';
                    document.getElementById('conflicts').textContent = kpis.ai_performance.conflicts_predicted;
                    document.getElementById('recommendations').textContent = kpis.ai_performance.recommendations_generated;
                    
                    const accuracy = kpis.ai_performance.prediction_accuracy;
                    document.getElementById('ai-accuracy').style.width = accuracy + '%';
                    document.getElementById('ai-accuracy-text').textContent = accuracy + '%';
                    document.getElementById('response-time').textContent = kpis.ai_performance.response_time + 'ms';
                    
                    document.getElementById('cost-savings').textContent = '₹' + formatNumber(kpis.financial.cost_savings);
                    document.getElementById('energy-efficiency').textContent = 
                        '+' + kpis.financial.energy_efficiency.toFixed(1) + '%';
                }
                
                document.getElementById('uptime').textContent = Math.floor(status.uptime_minutes);
                document.getElementById('total-cycles').textContent = status.cycle_count;
                
                updateAlerts(analytics.conflicts, analytics.recommendations);
                
            } catch (error) {
                addLog('Update error: ' + error.message);
            }
        }

        function updateAlerts(conflicts, recommendations) {
            const container = document.getElementById('alerts-container');
            container.innerHTML = '';
            
            if (conflicts && conflicts.length > 0) {
                conflicts.slice(0, 3).forEach(conflict => {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert-item';
                    alertDiv.innerHTML = `
                        <strong>${conflict.type}</strong> at ${conflict.location}<br>
                        <small>Probability: ${(conflict.probability * 100).toFixed(0)}%</small>
                    `;
                    container.appendChild(alertDiv);
                });
            }
            
            if (recommendations && recommendations.length > 0) {
                recommendations.slice(0, 2).forEach(rec => {
                    const recDiv = document.createElement('div');
                    recDiv.className = 'recommendation-item';
                    recDiv.innerHTML = `
                        <strong>${rec.type}</strong> for ${rec.train}<br>
                        <small>${rec.expected_benefit}</small>
                    `;
                    container.appendChild(recDiv);
                });
            }
            
            if ((!conflicts || conflicts.length === 0) && (!recommendations || recommendations.length === 0)) {
                container.innerHTML = '<div style="text-align: center; opacity: 0.7;">✅ System Operating Normally</div>';
            }
        }

        async function runScenario(scenarioId) {
            const resultsDiv = document.getElementById('scenario-results');
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div>Running scenario...</div>';
            
            addLog(`Running scenario: ${scenarioId}`);
            
            try {
                const response = await fetch(`/api/run_scenario/${scenarioId}`);
                const result = await response.json();
                
                if (result.error) {
                    resultsDiv.innerHTML = `<div style="color: #e74c3c;">Error: ${result.error}</div>`;
                } else {
                    const impact = result.impact_analysis || {};
                    const risk = result.risk_assessment || {};
                    
                    resultsDiv.innerHTML = `
                        <div><strong>Scenario Results:</strong></div>
                        <div>• Delay Impact: +${impact.delay_added_minutes || 0} minutes</div>
                        <div>• Affected Trains: ${impact.affected_trains?.length || 0}</div>
                        <div>• Risk Level: ${risk.level || 'Unknown'}</div>
                        <div>• Recovery Time: ~${impact.estimated_recovery_time || 0} minutes</div>
                    `;
                    
                    addLog(`Scenario completed: ${risk.level || 'Unknown'} risk`);
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div style="color: #e74c3c;">Error: ${error.message}</div>`;
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            addLog('Unified Dashboard initialized');
            updateDashboard();
            updateInterval = setInterval(updateDashboard, 3000);
        });

        window.addEventListener('beforeunload', function() {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
    </script>
</body>
</html>
        """
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_terminal_interface(self):
        """Display terminal-based interface"""
        self.clear_screen()
        
        print(f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}")
        print(f"  🚂 IDSS UNIFIED DASHBOARD  ".center(80))
        print(f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}{'═' * 80}{Colors.RESET}")
        
        # System status
        uptime = (datetime.now() - self.start_time).total_seconds() / 60
        print(f"\n{Colors.CYAN}📊 System Status:{Colors.RESET}")
        print(f"  • Web Server: {Colors.GREEN}Running{Colors.RESET} on http://localhost:{self.port}")
        print(f"  • Uptime: {Colors.YELLOW}{uptime:.1f} minutes{Colors.RESET}")
        print(f"  • Monitoring Cycles: {Colors.CYAN}{self.cycle_count}{Colors.RESET}")
        print(f"  • Total Conflicts: {Colors.YELLOW}{self.total_conflicts_predicted}{Colors.RESET}")
        print(f"  • Total Recommendations: {Colors.CYAN}{self.total_recommendations}{Colors.RESET}")
        
        # Current network state
        if self.current_snapshot:
            section_status = self.current_snapshot.get('section_status', {})
            trains = self.current_snapshot.get('trains', [])
            
            print(f"\n{Colors.BRIGHT_GREEN}🚄 Current Network State:{Colors.RESET}")
            print(f"  • Active Trains: {Colors.BRIGHT_CYAN}{len(trains)}{Colors.RESET}")
            print(f"  • Delayed Trains: {Colors.RED}{section_status.get('delayed_trains', 0)}{Colors.RESET}")
            print(f"  • Average Delay: {Colors.YELLOW}{section_status.get('average_delay', 0):.1f} min{Colors.RESET}")
        
        # Menu options
        print(f"\n{Colors.BRIGHT_WHITE}{Colors.BOLD}🎯 Available Actions:{Colors.RESET}")
        print(f"  1. {Colors.GREEN}Open Web Dashboard{Colors.RESET}")
        print(f"  2. {Colors.YELLOW}Run What-If Scenario{Colors.RESET}")
        print(f"  3. {Colors.CYAN}View Performance Report{Colors.RESET}")
        print(f"  4. {Colors.RED}Stop Dashboard{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_BLUE}{'═' * 80}{Colors.RESET}")
        print(f"{Colors.CYAN}Press Ctrl+C to access menu | Web: http://localhost:{self.port}{Colors.RESET}")
    
    async def run_unified_dashboard(self):
        """Run the unified dashboard system"""
        print(f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}")
        print(f" 🚂 IDSS UNIFIED DASHBOARD SYSTEM ".center(80))
        print(f"{Colors.RESET}")
        
        # Start web server
        print(f"\n{Colors.YELLOW}🔄 Starting unified dashboard...{Colors.RESET}")
        if not self.start_web_server():
            print(f"{Colors.RED}❌ Failed to start web server{Colors.RESET}")
            return
        
        print(f"{Colors.GREEN}✅ Web server started on http://localhost:{self.port}{Colors.RESET}")
        
        # Try to open browser
        try:
            webbrowser.open(f'http://localhost:{self.port}')
            print(f"{Colors.GREEN}🌐 Browser opened automatically{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️  Please open: http://localhost:{self.port}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_GREEN}🚀 Unified Dashboard is now running!{Colors.RESET}")
        
        # Start monitoring loop
        try:
            while self.monitoring_active:
                await self.update_system_data()
                
                if self.cycle_count % 5 == 0:
                    self.display_terminal_interface()
                
                await asyncio.sleep(3)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏸️  Dashboard menu accessed{Colors.RESET}")
            
            while True:
                try:
                    choice = input(f"\n{Colors.CYAN}Select option (1-4): {Colors.RESET}").strip()
                    
                    if choice == '1':
                        webbrowser.open(f'http://localhost:{self.port}')
                        print(f"{Colors.GREEN}🌐 Browser opened{Colors.RESET}")
                    elif choice == '2':
                        await self.run_terminal_scenario()
                    elif choice == '3':
                        self.display_performance_report()
                    elif choice == '4':
                        break
                    else:
                        print(f"{Colors.RED}❌ Invalid choice{Colors.RESET}")
                        
                except (KeyboardInterrupt, EOFError):
                    break
        
        finally:
            self.stop_web_server()
            print(f"\n{Colors.BRIGHT_GREEN}✅ Unified Dashboard stopped{Colors.RESET}")
    
    async def run_terminal_scenario(self):
        """Run what-if scenarios from terminal"""
        scenarios = list(self.predefined_scenarios.values())
        
        print(f"\n{Colors.BRIGHT_YELLOW}🎯 Available Scenarios:{Colors.RESET}")
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i}. {scenario['name']}")
        
        try:
            choice = int(input(f"\n{Colors.CYAN}Select (1-{len(scenarios)}): {Colors.RESET}"))
            if 1 <= choice <= len(scenarios):
                scenario = scenarios[choice - 1]
                result = self.run_scenario_by_id(scenario['id'])
                
                if 'error' in result:
                    print(f"\n{Colors.RED}❌ Error: {result['error']}{Colors.RESET}")
                else:
                    self.display.display_scenario_results(scenario, result)
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def display_performance_report(self):
        """Display performance report"""
        uptime = (datetime.now() - self.start_time).total_seconds() / 60
        
        print(f"\n{Colors.BRIGHT_CYAN}📊 SYSTEM PERFORMANCE REPORT{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 50}{Colors.RESET}")
        
        print(f"\n{Colors.WHITE}System Metrics:{Colors.RESET}")
        print(f"  • Uptime: {Colors.YELLOW}{uptime:.1f} minutes{Colors.RESET}")
        print(f"  • Total Cycles: {Colors.CYAN}{self.cycle_count}{Colors.RESET}")
        print(f"  • Conflicts Predicted: {Colors.YELLOW}{self.total_conflicts_predicted}{Colors.RESET}")
        print(f"  • Recommendations Generated: {Colors.CYAN}{self.total_recommendations}{Colors.RESET}")
        
        if len(self.performance_history) >= 5:
            recent = self.performance_history[-10:]
            avg_punctuality = sum(p['punctuality'] for p in recent) / len(recent)
            avg_accuracy = sum(p['ai_accuracy'] for p in recent) / len(recent)
            
            print(f"\n{Colors.WHITE}Performance Trends:{Colors.RESET}")
            print(f"  • Average Punctuality: {Colors.GREEN}{avg_punctuality:.1f}%{Colors.RESET}")
            print(f"  • Average AI Accuracy: {Colors.GREEN}{avg_accuracy:.1%}{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")

async def main():
    """Main function"""
    dashboard = UnifiedIDSSDashboard(port=8000)
    await dashboard.run_unified_dashboard()

if __name__ == "__main__":
    asyncio.run(main())