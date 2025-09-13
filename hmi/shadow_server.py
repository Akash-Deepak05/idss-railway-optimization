"""
Shadow-Mode HMI Server
FastAPI-based web interface for controllers to view AI recommendations
Includes Explainable AI (XAI) features for trust building
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json
import logging
from datetime import datetime
import uvicorn

# Import our MVP components (adjust paths as needed)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from integration.mock_data_feed import MockRailwayDataFeed
from digital_twin.cognitive_twin import CognitiveTwin
from analytics.predictor import AnalyticsEngine
from monitoring.kpi_logger import KPILogger

logger = logging.getLogger(__name__)

# Pydantic models for API
class FeedbackRequest(BaseModel):
    recommendation_id: str
    action: str  # "ACCEPT", "IGNORE", "MODIFY"
    reason: Optional[str] = None
    operator_id: Optional[str] = "controller_1"
    comments: Optional[str] = None

class WhatIfRequest(BaseModel):
    scenario_name: str
    train_id: str
    action: str  # "HOLD", "REROUTE", "SPEED_CHANGE"
    parameters: Dict[str, Any]

# Global state (in production, use proper state management)
class MVPState:
    def __init__(self):
        self.data_feed = MockRailwayDataFeed()
        self.digital_twin = CognitiveTwin({"pilot_section": "STN_A_TO_STN_B"})
        self.analytics = AnalyticsEngine()
        self.kpi_logger = KPILogger()
        self.current_snapshot = {}
        self.current_analysis = {}
        self.feedback_log = []
        self.is_initialized = False

mvp_state = MVPState()

# FastAPI app setup
app = FastAPI(
    title="IDSS Shadow Mode HMI",
    description="Intelligent Decision Support System - Shadow Mode Interface",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system on startup
@app.on_event("startup")
async def startup_event():
    """Initialize all MVP components"""
    logger.info("Initializing MVP IDSS system...")
    
    # Initialize digital twin
    mvp_state.digital_twin.initialize_pilot_section()
    
    # Start background data ingestion
    asyncio.create_task(start_data_ingestion())
    
    # Start analytics loop
    asyncio.create_task(start_analytics_loop())
    
    mvp_state.is_initialized = True
    logger.info("MVP IDSS system initialized successfully")

async def start_data_ingestion():
    """Background task for data ingestion"""
    async def process_snapshot(snapshot):
        mvp_state.current_snapshot = snapshot
        mvp_state.digital_twin.ingest_real_time_data(snapshot)
        
    await mvp_state.data_feed.start_feed(process_snapshot, 2.0)

async def start_analytics_loop():
    """Background analytics processing"""
    while True:
        try:
            if mvp_state.current_snapshot:
                analysis = mvp_state.analytics.analyze(mvp_state.current_snapshot)
                mvp_state.current_analysis = analysis
                
                # Log KPIs
                kpis = extract_kpis_from_analysis(analysis, mvp_state.current_snapshot)
                mvp_state.kpi_logger.log_kpis(kpis)
                
        except Exception as e:
            logger.error(f"Analytics loop error: {e}")
            
        await asyncio.sleep(30)  # Run every 30 seconds

def extract_kpis_from_analysis(analysis: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Extract KPIs from analysis for monitoring"""
    section_status = snapshot.get('section_status', {})
    summary = analysis.get('summary', {})
    
    return {
        'timestamp': datetime.now().isoformat(),
        'operational': {
            'total_trains': section_status.get('total_trains', 0),
            'delayed_trains': section_status.get('delayed_trains', 0),
            'average_delay_minutes': section_status.get('average_delay', 0),
            'throughput_trains_per_hour': section_status.get('total_trains', 0) * 2,  # Estimated
        },
        'ai_performance': {
            'conflicts_predicted': analysis.get('conflicts_predicted', 0),
            'recommendations_generated': analysis.get('recommendations_generated', 0),
            'high_severity_conflicts': summary.get('high_severity_conflicts', 0),
            'urgent_recommendations': summary.get('urgent_recommendations', 0),
        },
        'system_health': {
            'data_freshness_seconds': 2,  # Mock feed interval
            'twin_update_count': mvp_state.digital_twin.update_count,
            'analysis_success': True
        }
    }

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard HTML"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IDSS Shadow Mode - Railway Traffic Control</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .metric { text-align: center; }
            .metric-value { font-size: 2em; font-weight: bold; color: #3498db; }
            .metric-label { color: #666; }
            .recommendation { border-left: 4px solid #e74c3c; padding: 15px; margin: 10px 0; background: #fff5f5; }
            .recommendation.medium { border-left-color: #f39c12; background: #fffaf0; }
            .recommendation.low { border-left-color: #27ae60; background: #f0fff4; }
            .conflict { border-left: 4px solid #e74c3c; padding: 15px; margin: 10px 0; background: #fff5f5; }
            .btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #2980b9; }
            .btn.accept { background: #27ae60; }
            .btn.ignore { background: #95a5a6; }
            .explanation { background: #ecf0f1; padding: 15px; border-radius: 4px; margin: 10px 0; font-size: 0.9em; }
            .loading { text-align: center; color: #666; }
            .timestamp { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚂 IDSS Shadow Mode - Railway Traffic Control Dashboard</h1>
                <p>AI-powered recommendations for optimal train scheduling</p>
                <p class="timestamp">Last updated: <span id="lastUpdate">Loading...</span></p>
            </div>
            
            <div class="status-grid">
                <div class="card metric">
                    <div class="metric-value" id="totalTrains">-</div>
                    <div class="metric-label">Total Trains</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="delayedTrains">-</div>
                    <div class="metric-label">Delayed Trains</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="avgDelay">-</div>
                    <div class="metric-label">Avg Delay (min)</div>
                </div>
                <div class="card metric">
                    <div class="metric-value" id="conflictsPredicted">-</div>
                    <div class="metric-label">Conflicts Predicted</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🔮 AI Predictions & Conflicts</h2>
                <div id="conflictsContainer">
                    <div class="loading">Loading conflict predictions...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>💡 AI Recommendations</h2>
                <div id="recommendationsContainer">
                    <div class="loading">Loading recommendations...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 What-If Simulation</h2>
                <div>
                    <select id="trainSelect">
                        <option value="">Select Train...</option>
                    </select>
                    <select id="actionSelect">
                        <option value="">Select Action...</option>
                        <option value="HOLD">Hold Train</option>
                        <option value="REROUTE">Reroute Train</option>
                    </select>
                    <input type="number" id="durationInput" placeholder="Duration (minutes)" min="1" max="60">
                    <button class="btn" onclick="runWhatIf()">Run Simulation</button>
                </div>
                <div id="simulationResult"></div>
            </div>
        </div>
        
        <script>
            let currentData = {};
            
            async function fetchData() {
                try {
                    const snapshot = await fetch('/api/snapshot').then(r => r.json());
                    const analysis = await fetch('/api/analysis').then(r => r.json());
                    
                    currentData = { snapshot, analysis };
                    updateDashboard();
                    updateTrainSelect();
                } catch (error) {
                    console.error('Error fetching data:', error);
                }
            }
            
            function updateDashboard() {
                const { snapshot, analysis } = currentData;
                
                if (snapshot && snapshot.section_status) {
                    document.getElementById('totalTrains').textContent = snapshot.section_status.total_trains || 0;
                    document.getElementById('delayedTrains').textContent = snapshot.section_status.delayed_trains || 0;
                    document.getElementById('avgDelay').textContent = (snapshot.section_status.average_delay || 0).toFixed(1);
                    document.getElementById('lastUpdate').textContent = new Date(snapshot.timestamp).toLocaleTimeString();
                }
                
                if (analysis) {
                    document.getElementById('conflictsPredicted').textContent = analysis.conflicts_predicted || 0;
                    updateConflicts(analysis.conflicts || []);
                    updateRecommendations(analysis.recommendations || []);
                }
            }
            
            function updateConflicts(conflicts) {
                const container = document.getElementById('conflictsContainer');
                if (conflicts.length === 0) {
                    container.innerHTML = '<p>✅ No conflicts predicted in the next 30 minutes</p>';
                    return;
                }
                
                container.innerHTML = conflicts.map(conflict => `
                    <div class="conflict">
                        <h4>⚠️ ${conflict.type} Conflict (${(conflict.probability * 100).toFixed(0)}% probability)</h4>
                        <p><strong>Location:</strong> ${conflict.location}</p>
                        <p><strong>Trains:</strong> ${conflict.trains.join(', ')}</p>
                        <p><strong>Estimated Delay:</strong> ${conflict.estimated_delay} minutes</p>
                        <p><strong>Severity:</strong> ${conflict.severity}</p>
                    </div>
                `).join('');
            }
            
            function updateRecommendations(recommendations) {
                const container = document.getElementById('recommendationsContainer');
                if (recommendations.length === 0) {
                    container.innerHTML = '<p>✅ No immediate actions required</p>';
                    return;
                }
                
                container.innerHTML = recommendations.map((rec, index) => `
                    <div class="recommendation ${rec.urgency.toLowerCase()}">
                        <h4>📋 ${rec.type} - Train ${rec.train}</h4>
                        <p><strong>Expected Benefit:</strong> ${rec.expected_benefit}</p>
                        <p><strong>Confidence:</strong> ${(rec.confidence * 100).toFixed(0)}%</p>
                        <p><strong>Urgency:</strong> ${rec.urgency}</p>
                        
                        <div class="explanation">
                            <strong>🧠 AI Explanation:</strong><br>
                            ${JSON.stringify(rec.parameters, null, 2).replace(/[{}]/g, '').replace(/"/g, '').replace(/,/g, '<br>')}
                        </div>
                        
                        <button class="btn accept" onclick="provideFeedback('${rec.id}', 'ACCEPT')">✅ Accept</button>
                        <button class="btn ignore" onclick="provideFeedback('${rec.id}', 'IGNORE')">❌ Ignore</button>
                        <button class="btn" onclick="explainMore('${rec.id}')">🤔 Explain More</button>
                    </div>
                `).join('');
            }
            
            function updateTrainSelect() {
                const select = document.getElementById('trainSelect');
                if (currentData.snapshot && currentData.snapshot.trains) {
                    select.innerHTML = '<option value="">Select Train...</option>' + 
                        currentData.snapshot.trains.map(train => 
                            `<option value="${train.train_id}">${train.train_number} (${train.train_type})</option>`
                        ).join('');
                }
            }
            
            async function provideFeedback(recId, action) {
                const reason = prompt(`Why are you choosing to ${action} this recommendation?`);
                try {
                    await fetch('/api/feedback', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            recommendation_id: recId,
                            action: action,
                            reason: reason
                        })
                    });
                    alert(`Feedback recorded: ${action}`);
                } catch (error) {
                    alert('Error recording feedback');
                }
            }
            
            async function explainMore(recId) {
                try {
                    const explanation = await fetch(`/api/explain/${recId}`).then(r => r.json());
                    alert(`Detailed Explanation:\\n${explanation.explanation}`);
                } catch (error) {
                    alert('Error getting explanation');
                }
            }
            
            async function runWhatIf() {
                const trainId = document.getElementById('trainSelect').value;
                const action = document.getElementById('actionSelect').value;
                const duration = document.getElementById('durationInput').value;
                
                if (!trainId || !action) {
                    alert('Please select train and action');
                    return;
                }
                
                try {
                    const result = await fetch('/api/what-if', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            scenario_name: `${action} ${trainId}`,
                            train_id: trainId,
                            action: action,
                            parameters: { duration_minutes: parseInt(duration) || 10 }
                        })
                    }).then(r => r.json());
                    
                    document.getElementById('simulationResult').innerHTML = `
                        <h4>Simulation Result:</h4>
                        <pre>${JSON.stringify(result, null, 2)}</pre>
                    `;
                } catch (error) {
                    alert('Error running simulation');
                }
            }
            
            // Start data fetching
            fetchData();
            setInterval(fetchData, 5000);  // Update every 5 seconds
        </script>
    </body>
    </html>
    """)

@app.get("/api/snapshot")
async def get_snapshot():
    """Get current network snapshot"""
    if not mvp_state.is_initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return mvp_state.current_snapshot

@app.get("/api/analysis")
async def get_analysis():
    """Get current AI analysis and recommendations"""
    if not mvp_state.is_initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return mvp_state.current_analysis

@app.get("/api/twin-status")
async def get_twin_status():
    """Get digital twin status"""
    if not mvp_state.is_initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return mvp_state.digital_twin.get_network_snapshot()

@app.post("/api/feedback")
async def record_feedback(feedback: FeedbackRequest):
    """Record operator feedback on recommendations"""
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "recommendation_id": feedback.recommendation_id,
        "action": feedback.action,
        "reason": feedback.reason,
        "operator_id": feedback.operator_id,
        "comments": feedback.comments
    }
    
    mvp_state.feedback_log.append(feedback_entry)
    logger.info(f"Feedback recorded: {feedback.action} for {feedback.recommendation_id}")
    
    # Update KPI metrics
    kpi_update = {
        'timestamp': datetime.now().isoformat(),
        'operator_feedback': {
            'recommendation_id': feedback.recommendation_id,
            'action': feedback.action,
            'acceptance_rate': calculate_acceptance_rate()
        }
    }
    mvp_state.kpi_logger.log_kpis(kpi_update)
    
    return {"status": "success", "message": "Feedback recorded"}

@app.get("/api/explain/{recommendation_id}")
async def explain_recommendation(recommendation_id: str):
    """Provide detailed explanation for a specific recommendation (XAI)"""
    
    # Find the recommendation in current analysis
    current_recs = mvp_state.current_analysis.get('recommendations', [])
    recommendation = next((r for r in current_recs if r.get('id') == recommendation_id), None)
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Generate detailed explanation
    explanation = {
        "recommendation_id": recommendation_id,
        "explanation": generate_detailed_explanation(recommendation),
        "confidence_breakdown": {
            "model_confidence": recommendation.get('confidence', 0),
            "data_quality": 0.9,  # Mock
            "historical_accuracy": 0.85,  # Mock
            "complexity_factor": 0.7  # Mock
        },
        "alternative_actions": generate_alternatives(recommendation),
        "risk_assessment": assess_recommendation_risks(recommendation)
    }
    
    return explanation

@app.post("/api/what-if")
async def run_what_if_simulation(request: WhatIfRequest):
    """Run what-if simulation scenario"""
    scenario = {
        "name": request.scenario_name,
        "train_id": request.train_id,
        "action": request.action,
        **request.parameters
    }
    
    result = mvp_state.digital_twin.run_what_if_simulation(scenario)
    return result

@app.get("/api/kpis")
async def get_kpis():
    """Get current KPI metrics"""
    return mvp_state.kpi_logger.get_current_kpis()

@app.get("/api/feedback-log")
async def get_feedback_log():
    """Get operator feedback history"""
    return {
        "feedback_entries": mvp_state.feedback_log[-50:],  # Last 50 entries
        "summary": {
            "total_feedback": len(mvp_state.feedback_log),
            "acceptance_rate": calculate_acceptance_rate(),
            "most_recent": mvp_state.feedback_log[-1] if mvp_state.feedback_log else None
        }
    }

# Helper functions

def calculate_acceptance_rate() -> float:
    """Calculate recommendation acceptance rate"""
    if not mvp_state.feedback_log:
        return 0.0
    
    accepted = len([f for f in mvp_state.feedback_log if f.get('action') == 'ACCEPT'])
    total = len(mvp_state.feedback_log)
    return round(accepted / total, 2) if total > 0 else 0.0

def generate_detailed_explanation(recommendation: Dict[str, Any]) -> str:
    """Generate detailed XAI explanation"""
    rec_type = recommendation.get('type', 'UNKNOWN')
    train = recommendation.get('train', 'UNKNOWN')
    confidence = recommendation.get('confidence', 0)
    
    explanations = {
        'HOLD': f"""
        The AI recommends holding train {train} based on:
        1. Conflict prediction models detected potential headway violation
        2. Current section occupancy exceeds optimal capacity
        3. Higher priority trains need right-of-way access
        4. Holding prevents cascading delays (confidence: {confidence:.0%})
        
        Decision factors:
        - Train priority: Lower priority allows holding
        - Current speed: Safe to hold without emergency braking
        - Section capacity: Temporary hold reduces congestion
        - Downstream impact: Minimal effect on schedule adherence
        """,
        'SPEED_CHANGE': f"""
        Speed adjustment recommended for train {train} because:
        1. Signal aspect analysis shows RED signal ahead
        2. Braking distance calculation indicates potential overrun
        3. Gradual speed reduction prevents emergency braking
        4. Maintains safety margins while optimizing flow
        
        Technical factors:
        - Current speed vs. safe approach speed differential
        - Track gradient and braking performance curves
        - Signal interlocking protection requirements
        - Passenger comfort and operational safety
        """,
        'REROUTE': f"""
        Rerouting train {train} recommended due to:
        1. Primary route showing persistent conflicts
        2. Alternative route available with better timing
        3. Resource optimization across network
        4. Reduces overall system delay
        """
    }
    
    return explanations.get(rec_type, f"AI recommendation for {rec_type} action on train {train} based on current system analysis.")

def generate_alternatives(recommendation: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate alternative actions"""
    return [
        {"action": "WAIT", "description": "Monitor situation for 5 more minutes"},
        {"action": "MANUAL_OVERRIDE", "description": "Controller takes manual control"},
        {"action": "PRIORITY_BOOST", "description": "Temporarily increase train priority"}
    ]

def assess_recommendation_risks(recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """Assess risks of following recommendation"""
    return {
        "safety_risk": "LOW",
        "schedule_impact": "MEDIUM",
        "passenger_comfort": "LOW",
        "operational_complexity": "LOW",
        "reversibility": "HIGH"
    }

# Run the server
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting IDSS Shadow Mode HMI Server...")
    print("Dashboard available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
