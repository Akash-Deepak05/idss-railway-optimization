"""
KPI Monitoring and Logging System
Tracks operational, financial, and safety metrics as defined in the blueprint
"""

import csv
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class OperationalKPIs:
    """Operational performance indicators"""
    timestamp: str
    total_trains: int
    delayed_trains: int
    on_time_trains: int
    average_delay_minutes: float
    section_throughput_trains_per_hour: float
    punctuality_percentage: float
    asset_utilization_percentage: float

@dataclass
class FinancialKPIs:
    """Financial performance indicators"""
    timestamp: str
    operating_ratio: float  # Operating expenses / Net revenue
    revenue_per_ton_mile: float
    cost_savings_from_optimization: float
    energy_efficiency_improvement: float

@dataclass
class SafetyKPIs:
    """Safety and reliability indicators"""
    timestamp: str
    predictive_maintenance_success_rate: float
    unscheduled_delays_prevented: int
    safety_violations: int
    signal_failures: int
    emergency_braking_events: int

@dataclass
class AIPerformanceKPIs:
    """AI system performance indicators"""
    timestamp: str
    conflicts_predicted: int
    conflicts_accurately_predicted: int
    recommendations_generated: int
    recommendations_accepted: int
    false_positive_rate: float
    prediction_accuracy: float
    recommendation_acceptance_rate: float
    average_response_time_ms: float

class KPILogger:
    """Main KPI logging and monitoring system"""
    
    def __init__(self, data_dir: str = "monitoring_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # CSV files for different KPI categories
        self.operational_file = self.data_dir / "operational_kpis.csv"
        self.financial_file = self.data_dir / "financial_kpis.csv"
        self.safety_file = self.data_dir / "safety_kpis.csv"
        self.ai_performance_file = self.data_dir / "ai_performance_kpis.csv"
        self.raw_events_file = self.data_dir / "raw_events.jsonl"
        
        # Initialize CSV files with headers
        self._initialize_csv_files()
        
        # In-memory storage for current session
        self.current_operational = None
        self.current_financial = None
        self.current_safety = None
        self.current_ai_performance = None
        
        self.session_start = datetime.now()
        
    def _initialize_csv_files(self):
        """Initialize CSV files with appropriate headers"""
        
        # Operational KPIs
        if not self.operational_file.exists():
            with open(self.operational_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'total_trains', 'delayed_trains', 'on_time_trains',
                    'average_delay_minutes', 'section_throughput_trains_per_hour',
                    'punctuality_percentage', 'asset_utilization_percentage'
                ])
                
        # Financial KPIs
        if not self.financial_file.exists():
            with open(self.financial_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'operating_ratio', 'revenue_per_ton_mile',
                    'cost_savings_from_optimization', 'energy_efficiency_improvement'
                ])
                
        # Safety KPIs
        if not self.safety_file.exists():
            with open(self.safety_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'predictive_maintenance_success_rate',
                    'unscheduled_delays_prevented', 'safety_violations',
                    'signal_failures', 'emergency_braking_events'
                ])
                
        # AI Performance KPIs
        if not self.ai_performance_file.exists():
            with open(self.ai_performance_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'conflicts_predicted', 'conflicts_accurately_predicted',
                    'recommendations_generated', 'recommendations_accepted',
                    'false_positive_rate', 'prediction_accuracy',
                    'recommendation_acceptance_rate', 'average_response_time_ms'
                ])
    
    def log_kpis(self, kpi_data: Dict[str, Any]) -> None:
        """Log KPIs from various sources"""
        timestamp = kpi_data.get('timestamp', datetime.now().isoformat())
        
        # Log raw event for debugging
        self._log_raw_event(kpi_data)
        
        # Process operational KPIs
        if 'operational' in kpi_data:
            self._log_operational_kpis(timestamp, kpi_data['operational'])
            
        # Process financial KPIs
        if 'financial' in kpi_data:
            self._log_financial_kpis(timestamp, kpi_data['financial'])
            
        # Process safety KPIs
        if 'safety' in kpi_data:
            self._log_safety_kpis(timestamp, kpi_data['safety'])
            
        # Process AI performance KPIs
        if 'ai_performance' in kpi_data:
            self._log_ai_performance_kpis(timestamp, kpi_data['ai_performance'])
            
        # Process operator feedback
        if 'operator_feedback' in kpi_data:
            self._process_operator_feedback(timestamp, kpi_data['operator_feedback'])
    
    def _log_raw_event(self, event_data: Dict[str, Any]) -> None:
        """Log raw event data for detailed analysis"""
        with open(self.raw_events_file, 'a') as f:
            f.write(json.dumps(event_data) + '\n')
    
    def _log_operational_kpis(self, timestamp: str, data: Dict[str, Any]) -> None:
        """Log operational performance indicators"""
        total_trains = data.get('total_trains', 0)
        delayed_trains = data.get('delayed_trains', 0)
        on_time_trains = max(0, total_trains - delayed_trains)
        
        operational_kpis = OperationalKPIs(
            timestamp=timestamp,
            total_trains=total_trains,
            delayed_trains=delayed_trains,
            on_time_trains=on_time_trains,
            average_delay_minutes=data.get('average_delay_minutes', 0.0),
            section_throughput_trains_per_hour=data.get('throughput_trains_per_hour', 0.0),
            punctuality_percentage=(on_time_trains / total_trains * 100) if total_trains > 0 else 100.0,
            asset_utilization_percentage=data.get('asset_utilization_percentage', 75.0)  # Mock
        )
        
        self.current_operational = operational_kpis
        
        # Write to CSV
        with open(self.operational_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                operational_kpis.timestamp,
                operational_kpis.total_trains,
                operational_kpis.delayed_trains,
                operational_kpis.on_time_trains,
                operational_kpis.average_delay_minutes,
                operational_kpis.section_throughput_trains_per_hour,
                operational_kpis.punctuality_percentage,
                operational_kpis.asset_utilization_percentage
            ])
    
    def _log_financial_kpis(self, timestamp: str, data: Dict[str, Any]) -> None:
        """Log financial performance indicators"""
        financial_kpis = FinancialKPIs(
            timestamp=timestamp,
            operating_ratio=data.get('operating_ratio', 0.95),  # Mock baseline
            revenue_per_ton_mile=data.get('revenue_per_ton_mile', 0.04),  # Mock
            cost_savings_from_optimization=data.get('cost_savings', 0.0),
            energy_efficiency_improvement=data.get('energy_efficiency_improvement', 0.0)
        )
        
        self.current_financial = financial_kpis
        
        # Write to CSV
        with open(self.financial_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                financial_kpis.timestamp,
                financial_kpis.operating_ratio,
                financial_kpis.revenue_per_ton_mile,
                financial_kpis.cost_savings_from_optimization,
                financial_kpis.energy_efficiency_improvement
            ])
    
    def _log_safety_kpis(self, timestamp: str, data: Dict[str, Any]) -> None:
        """Log safety and reliability indicators"""
        safety_kpis = SafetyKPIs(
            timestamp=timestamp,
            predictive_maintenance_success_rate=data.get('predictive_maintenance_success_rate', 0.90),
            unscheduled_delays_prevented=data.get('unscheduled_delays_prevented', 0),
            safety_violations=data.get('safety_violations', 0),
            signal_failures=data.get('signal_failures', 0),
            emergency_braking_events=data.get('emergency_braking_events', 0)
        )
        
        self.current_safety = safety_kpis
        
        # Write to CSV
        with open(self.safety_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                safety_kpis.timestamp,
                safety_kpis.predictive_maintenance_success_rate,
                safety_kpis.unscheduled_delays_prevented,
                safety_kpis.safety_violations,
                safety_kpis.signal_failures,
                safety_kpis.emergency_braking_events
            ])
    
    def _log_ai_performance_kpis(self, timestamp: str, data: Dict[str, Any]) -> None:
        """Log AI system performance indicators"""
        conflicts_predicted = data.get('conflicts_predicted', 0)
        recommendations_generated = data.get('recommendations_generated', 0)
        
        ai_performance_kpis = AIPerformanceKPIs(
            timestamp=timestamp,
            conflicts_predicted=conflicts_predicted,
            conflicts_accurately_predicted=data.get('conflicts_accurately_predicted', 
                                                   int(conflicts_predicted * 0.85)),  # Mock 85% accuracy
            recommendations_generated=recommendations_generated,
            recommendations_accepted=data.get('recommendations_accepted', 0),
            false_positive_rate=data.get('false_positive_rate', 0.15),
            prediction_accuracy=data.get('prediction_accuracy', 0.85),
            recommendation_acceptance_rate=self._calculate_recommendation_acceptance_rate(data),
            average_response_time_ms=data.get('average_response_time_ms', 250.0)
        )
        
        self.current_ai_performance = ai_performance_kpis
        
        # Write to CSV
        with open(self.ai_performance_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                ai_performance_kpis.timestamp,
                ai_performance_kpis.conflicts_predicted,
                ai_performance_kpis.conflicts_accurately_predicted,
                ai_performance_kpis.recommendations_generated,
                ai_performance_kpis.recommendations_accepted,
                ai_performance_kpis.false_positive_rate,
                ai_performance_kpis.prediction_accuracy,
                ai_performance_kpis.recommendation_acceptance_rate,
                ai_performance_kpis.average_response_time_ms
            ])
    
    def _calculate_recommendation_acceptance_rate(self, data: Dict[str, Any]) -> float:
        """Calculate acceptance rate for recommendations"""
        generated = data.get('recommendations_generated', 0)
        accepted = data.get('recommendations_accepted', 0)
        return (accepted / generated) if generated > 0 else 0.0
    
    def _process_operator_feedback(self, timestamp: str, feedback_data: Dict[str, Any]) -> None:
        """Process operator feedback for KPI calculation"""
        # This would update acceptance rates and other metrics
        # For now, just log the feedback
        logger.info(f"Operator feedback processed: {feedback_data}")
    
    def get_current_kpis(self) -> Dict[str, Any]:
        """Get current KPI snapshot"""
        return {
            "timestamp": datetime.now().isoformat(),
            "session_duration_minutes": (datetime.now() - self.session_start).total_seconds() / 60,
            "operational": asdict(self.current_operational) if self.current_operational else None,
            "financial": asdict(self.current_financial) if self.current_financial else None,
            "safety": asdict(self.current_safety) if self.current_safety else None,
            "ai_performance": asdict(self.current_ai_performance) if self.current_ai_performance else None
        }
    
    def generate_kpi_report(self, hours_back: int = 24) -> Dict[str, Any]:
        """Generate comprehensive KPI report"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        report = {
            "report_period": f"Last {hours_back} hours",
            "generated_at": datetime.now().isoformat(),
            "summary": {}
        }
        
        # Analyze operational KPIs
        if self.operational_file.exists():
            df = pd.read_csv(self.operational_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            recent_data = df[df['timestamp'] >= cutoff_time]
            
            if not recent_data.empty:
                report["operational_summary"] = {
                    "average_delay_minutes": recent_data['average_delay_minutes'].mean(),
                    "best_punctuality": recent_data['punctuality_percentage'].max(),
                    "worst_punctuality": recent_data['punctuality_percentage'].min(),
                    "total_trains_processed": recent_data['total_trains'].sum(),
                    "peak_throughput": recent_data['section_throughput_trains_per_hour'].max()
                }
        
        # Analyze AI performance
        if self.ai_performance_file.exists():
            df = pd.read_csv(self.ai_performance_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            recent_data = df[df['timestamp'] >= cutoff_time]
            
            if not recent_data.empty:
                report["ai_performance_summary"] = {
                    "total_conflicts_predicted": recent_data['conflicts_predicted'].sum(),
                    "average_prediction_accuracy": recent_data['prediction_accuracy'].mean(),
                    "total_recommendations": recent_data['recommendations_generated'].sum(),
                    "average_acceptance_rate": recent_data['recommendation_acceptance_rate'].mean(),
                    "average_response_time": recent_data['average_response_time_ms'].mean()
                }
        
        return report
    
    def export_data(self, format: str = "csv", hours_back: Optional[int] = None) -> List[str]:
        """Export KPI data in specified format"""
        exported_files = []
        
        if format.lower() == "csv":
            # CSV files are already available
            exported_files = [
                str(self.operational_file),
                str(self.financial_file),
                str(self.safety_file),
                str(self.ai_performance_file)
            ]
        elif format.lower() == "json":
            # Export as JSON
            json_file = self.data_dir / f"kpi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "operational": self._read_csv_to_dict(self.operational_file, hours_back),
                "financial": self._read_csv_to_dict(self.financial_file, hours_back),
                "safety": self._read_csv_to_dict(self.safety_file, hours_back),
                "ai_performance": self._read_csv_to_dict(self.ai_performance_file, hours_back)
            }
            
            with open(json_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            exported_files.append(str(json_file))
        
        return exported_files
    
    def _read_csv_to_dict(self, csv_file: Path, hours_back: Optional[int] = None) -> List[Dict]:
        """Read CSV file and convert to list of dictionaries"""
        if not csv_file.exists():
            return []
        
        df = pd.read_csv(csv_file)
        
        if hours_back:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[df['timestamp'] >= cutoff_time]
        
        return df.to_dict('records')

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create KPI logger
    kpi_logger = KPILogger("test_monitoring_data")
    
    # Log sample operational KPIs
    sample_operational = {
        'timestamp': datetime.now().isoformat(),
        'operational': {
            'total_trains': 4,
            'delayed_trains': 1,
            'average_delay_minutes': 3.2,
            'throughput_trains_per_hour': 8,
        },
        'ai_performance': {
            'conflicts_predicted': 2,
            'recommendations_generated': 3,
            'recommendations_accepted': 2,
            'prediction_accuracy': 0.87,
            'average_response_time_ms': 245
        }
    }
    
    kpi_logger.log_kpis(sample_operational)
    
    # Get current KPIs
    current = kpi_logger.get_current_kpis()
    print("Current KPIs:")
    print(json.dumps(current, indent=2, default=str))
    
    # Generate report
    report = kpi_logger.generate_kpi_report(hours_back=1)
    print("\nKPI Report:")
    print(json.dumps(report, indent=2, default=str))
    
    # Export data
    exported = kpi_logger.export_data("json")
    print(f"\nExported files: {exported}")
