"""
Main IDSS MVP Orchestrator
Wires all components together for end-to-end shadow-mode demonstration
Non-invasive AI layer that integrates with existing railway systems
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import MVP components
from integration.mock_data_feed import MockRailwayDataFeed
from digital_twin.cognitive_twin import CognitiveTwin
from analytics.predictor import AnalyticsEngine
from monitoring.kpi_logger import KPILogger
from core.idss_optimizer import HybridOptimizer, Train, Section, TrainPriority, OptimizationObjective

logger = logging.getLogger(__name__)

class IDSSOrchestrator:
    """Main orchestrator for the MVP IDSS system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        
        # Initialize components
        self.data_feed = MockRailwayDataFeed()
        self.digital_twin = CognitiveTwin(self.config.get('digital_twin', {}))
        self.analytics_engine = AnalyticsEngine()
        self.kpi_logger = KPILogger(self.config.get('monitoring_dir', 'monitoring_data'))
        self.optimizer = HybridOptimizer(OptimizationObjective.MINIMIZE_DELAY)
        
        # System state
        self.is_running = False
        self.current_snapshot = {}
        self.current_analysis = {}
        self.recommendations = []
        
        logger.info("IDSS Orchestrator initialized")
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for MVP"""
        return {
            'digital_twin': {
                'pilot_section': 'STN_A_TO_STN_B',
                'update_frequency': 5,
                'validation_threshold': 60
            },
            'analytics': {
                'prediction_horizon_minutes': 30,
                'recommendation_interval_seconds': 30
            },
            'monitoring_dir': str(project_root / 'monitoring_data'),
            'data_feed_interval': 2.0
        }
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing IDSS MVP system...")
        
        # Initialize digital twin
        self.digital_twin.initialize_pilot_section()
        
        # Create initial KPI entries
        initial_kpis = {
            'timestamp': datetime.now().isoformat(),
            'system_health': {
                'initialization_success': True,
                'components_loaded': 5,
                'data_sources_connected': 1
            }
        }
        self.kpi_logger.log_kpis(initial_kpis)
        
        logger.info("IDSS MVP system initialized successfully")
    
    async def start_system(self):
        """Start the complete IDSS system"""
        await self.initialize()
        
        self.is_running = True
        
        # Start background tasks
        data_task = asyncio.create_task(self._data_ingestion_loop())
        analytics_task = asyncio.create_task(self._analytics_loop())
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("IDSS MVP system started - all background tasks running")
        
        try:
            # Run until interrupted
            await asyncio.gather(data_task, analytics_task, monitoring_task)
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"System error: {e}")
        finally:
            await self.shutdown()
    
    async def _data_ingestion_loop(self):
        """Background data ingestion from mock feed"""
        async def process_snapshot(snapshot):
            self.current_snapshot = snapshot
            
            # Ingest into digital twin
            self.digital_twin.ingest_real_time_data(snapshot)
            
            logger.debug(f"Processed snapshot with {len(snapshot.get('trains', []))} trains")
        
        try:
            await self.data_feed.start_feed(
                process_snapshot, 
                self.config['data_feed_interval']
            )
        except Exception as e:
            logger.error(f"Data ingestion error: {e}")
    
    async def _analytics_loop(self):
        """Background analytics processing"""
        interval = self.config['analytics']['recommendation_interval_seconds']
        
        while self.is_running:
            try:
                if self.current_snapshot:
                    # Run predictive analytics
                    analysis = self.analytics_engine.analyze(self.current_snapshot)
                    self.current_analysis = analysis
                    
                    # Generate optimizer recommendations for high-priority conflicts
                    if analysis.get('conflicts_predicted', 0) > 0:
                        optimizer_recs = await self._run_optimizer_recommendations()
                        
                        # Merge with analytics recommendations
                        all_recommendations = analysis.get('recommendations', []) + optimizer_recs
                        self.recommendations = all_recommendations
                        
                        # Update analysis with optimizer results
                        self.current_analysis['total_recommendations'] = len(all_recommendations)
                        self.current_analysis['optimizer_contributions'] = len(optimizer_recs)
                    
                    logger.info(f"Analytics cycle: {analysis.get('conflicts_predicted', 0)} conflicts, "
                              f"{analysis.get('recommendations_generated', 0)} recommendations")
                
            except Exception as e:
                logger.error(f"Analytics loop error: {e}")
            
            await asyncio.sleep(interval)
    
    async def _run_optimizer_recommendations(self) -> list:
        """Run hybrid optimizer for additional recommendations"""
        try:
            # Convert current snapshot to optimizer format
            trains, sections = self._convert_snapshot_for_optimizer()
            
            if trains and sections:
                # Run optimization
                result = self.optimizer.hybrid_optimize(trains, sections)
                
                if result.success:
                    # Convert optimizer recommendations to standard format
                    optimizer_recs = []
                    for rec in result.recommendations:
                        optimizer_rec = {
                            'id': f"OPT_{rec['train_id']}_{datetime.now().strftime('%H%M%S')}",
                            'type': rec['action'],
                            'train': rec['train_id'],
                            'parameters': rec,
                            'expected_benefit': f"Hybrid AI-OR optimization: {result.explanation}",
                            'confidence': result.confidence_score,
                            'urgency': 'HIGH' if rec.get('duration_minutes', 0) > 5 else 'MEDIUM',
                            'source': 'HYBRID_OPTIMIZER'
                        }
                        optimizer_recs.append(optimizer_rec)
                    
                    return optimizer_recs
        
        except Exception as e:
            logger.error(f"Optimizer error: {e}")
        
        return []
    
    def _convert_snapshot_for_optimizer(self):
        """Convert snapshot data to optimizer input format"""
        trains = []
        sections = []
        
        snapshot_trains = self.current_snapshot.get('trains', [])
        
        for train_data in snapshot_trains:
            train = Train(
                train_id=train_data['train_id'],
                train_number=train_data.get('train_number', train_data['train_id']),
                train_type=train_data.get('train_type', 'UNKNOWN'),
                priority=TrainPriority(train_data.get('priority', 3)),
                current_location=100.0,  # Mock km post
                destination=200.0,  # Mock destination
                scheduled_arrival=datetime.now(),
                current_speed=train_data.get('current_speed', 0.0),
                max_speed=80.0
            )
            trains.append(train)
        
        # Create mock sections for optimizer
        sections = [
            Section("SEC_A", 100.0, 110.0, 80.0, 2, []),
            Section("SEC_B", 110.0, 120.0, 100.0, 3, [])
        ]
        
        return trains, sections
    
    async def _monitoring_loop(self):
        """Background KPI monitoring"""
        while self.is_running:
            try:
                # Extract and log KPIs
                kpis = self._extract_current_kpis()
                self.kpi_logger.log_kpis(kpis)
                
                # Log system health
                system_health = {
                    'timestamp': datetime.now().isoformat(),
                    'system_health': {
                        'data_freshness_seconds': 2,
                        'twin_updates': self.digital_twin.update_count,
                        'recommendations_active': len(self.recommendations),
                        'system_running': self.is_running
                    }
                }
                self.kpi_logger.log_kpis(system_health)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            await asyncio.sleep(30)  # Monitor every 30 seconds
    
    def _extract_current_kpis(self) -> Dict[str, Any]:
        """Extract KPIs from current system state"""
        section_status = self.current_snapshot.get('section_status', {})
        analysis_summary = self.current_analysis.get('summary', {})
        
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
                'recommendations_generated': len(self.recommendations),
                'high_severity_conflicts': analysis_summary.get('high_severity_conflicts', 0),
                'urgent_recommendations': analysis_summary.get('urgent_recommendations', 0),
                'prediction_accuracy': 0.87,  # Mock - would be calculated from historical data
                'average_response_time_ms': 280  # Mock
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Shutting down IDSS MVP system...")
        
        self.is_running = False
        self.data_feed.stop_feed()
        
        # Generate final report
        final_report = self.kpi_logger.generate_kpi_report(hours_back=24)
        
        # Export data
        exported_files = self.kpi_logger.export_data("json")
        
        logger.info(f"System shutdown complete. Data exported to: {exported_files}")
        logger.info(f"Final KPI report generated: {len(final_report)} categories")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status for API endpoints"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_running': self.is_running,
            'components_status': {
                'data_feed': 'RUNNING' if self.is_running else 'STOPPED',
                'digital_twin': 'INITIALIZED' if self.digital_twin.is_initialized else 'NOT_READY',
                'analytics': 'ACTIVE',
                'monitoring': 'LOGGING'
            },
            'current_metrics': {
                'trains_tracked': len(self.current_snapshot.get('trains', [])),
                'conflicts_predicted': self.current_analysis.get('conflicts_predicted', 0),
                'active_recommendations': len(self.recommendations),
                'kpi_records_logged': 'continuous'
            },
            'twin_performance': self.digital_twin.get_network_snapshot().get('performance_metrics', {}),
            'latest_recommendations': self.recommendations[-5:] if self.recommendations else []
        }

# Main entry point
async def main():
    """Main entry point for standalone execution"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('idss_mvp.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("="*60)
    logger.info("IDSS MVP - Indian Railways AI-Powered Traffic Optimization")
    logger.info("Phase I: Shadow Mode Demonstration")
    logger.info("="*60)
    
    # Create and start orchestrator
    orchestrator = IDSSOrchestrator()
    
    try:
        await orchestrator.start_system()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        logger.info("IDSS MVP demonstration completed")

if __name__ == "__main__":
    asyncio.run(main())
