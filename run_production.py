#!/usr/bin/env python3
"""
Simple Production Server for IDSS
Indian Railways - AI-Powered Section Throughput Optimization System
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup production logging"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/idss_production.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('IDSS-Production')

def print_startup_info():
    """Print startup information"""
    print("=" * 80)
    print("IDSS - AI-Powered Section Throughput Optimization System")
    print("=" * 80)
    print()
    print("Indian Railways Production Deployment")
    print(f"Zone: {os.getenv('RAILWAY_ZONE', 'CR')}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print()
    print("Server Configuration:")
    print(f"    * Host: {os.getenv('HOST', '0.0.0.0')}")
    print(f"    * Port: {os.getenv('PORT', 8000)}")
    print(f"    * Workers: {os.getenv('WORKERS', 4)}")
    print()
    print("Access Points:")
    print(f"    * Dashboard: http://localhost:{os.getenv('PORT', 8000)}")
    print(f"    * API Docs: http://localhost:{os.getenv('PORT', 8000)}/docs")
    print(f"    * Health Check: http://localhost:{os.getenv('PORT', 8000)}/api/status")
    print()
    print("=" * 80)
    print()

def validate_environment():
    """Validate production environment"""
    required_vars = ['SECRET_KEY', 'JWT_SECRET', 'RAILWAY_ZONE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        return False
    
    return True

def main():
    """Main entry point"""
    logger = setup_logging()
    
    print_startup_info()
    logger.info("IDSS Production Server Starting...")
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    logger.info("Environment validation passed")
    
    # Import and run the unified dashboard
    try:
        logger.info("Starting IDSS Unified Dashboard...")
        
        # Import the unified dashboard module
        sys.path.insert(0, os.getcwd())
        from unified_dashboard import main as dashboard_main
        
        # Run the dashboard
        dashboard_main()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown initiated by user")
    except ImportError as e:
        logger.error(f"Failed to import unified dashboard: {e}")
        logger.info("Trying to run unified_dashboard.py directly...")
        os.system("python unified_dashboard.py")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)
    finally:
        logger.info("IDSS Production Server stopped")

if __name__ == "__main__":
    main()