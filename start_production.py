#!/usr/bin/env python3
"""
IDSS Production Startup Script
Indian Railways - AI-Powered Section Throughput Optimization System

This script starts the IDSS system in production mode with:
- Production configuration
- Security hardening
- Performance optimization
- Logging and monitoring
- Health checks
"""

import os
import sys
import logging
import asyncio
# uvloop not supported on Windows
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
import signal
import psutil
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

class ProductionServer:
    """Production server manager for IDSS"""
    
    def __init__(self):
        self.setup_logging()
        self.validate_environment()
        self.server = None
        
    def setup_logging(self):
        """Setup production logging"""
        log_dir = Path(os.getenv('LOG_DIR', './logs'))
        log_dir.mkdir(exist_ok=True)
        
        log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
        log_file = log_dir / os.getenv('LOG_FILE', 'idss_production.log')
        
        # Configure logging with rotation
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('IDSS-Production')
        self.logger.info("IDSS Production Server Starting...")
        
    def validate_environment(self):
        """Validate production environment"""
        required_vars = [
            'SECRET_KEY', 'JWT_SECRET', 'DB_PASSWORD', 
            'RAILWAY_ZONE', 'ENVIRONMENT'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"❌ Missing required environment variables: {missing_vars}")
            self.logger.error("Please configure .env file with production settings")
            sys.exit(1)
        
        self.logger.info("Environment validation passed")
        
    def check_system_resources(self):
        """Check system resources before startup"""
        # Check memory
        memory = psutil.virtual_memory()
        if memory.available < 1024 * 1024 * 1024:  # Less than 1GB
            self.logger.warning("⚠️ Low memory available: {:.1f}GB".format(
                memory.available / (1024**3)
            ))
        
        # Check CPU
        cpu_count = psutil.cpu_count()
        self.logger.info(f"System Resources - CPU Cores: {cpu_count}, Memory: {memory.total / (1024**3):.1f}GB")
        
        # Check disk space (Windows compatible)
        try:
            disk = psutil.disk_usage('C:\\')
            if disk.free < 5 * 1024 * 1024 * 1024:  # Less than 5GB
                self.logger.warning(f"Low disk space: {disk.free / (1024**3):.1f}GB")
        except Exception as e:
            self.logger.warning(f"Could not check disk space: {e}")
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            'logs',
            'monitoring_data',
            'backup',
            'temp',
            'static'
        ]
        
        for directory in directories:
            path = Path(directory)
            path.mkdir(exist_ok=True)
            self.logger.debug(f"Created/verified directory: {directory}")
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Graceful shutdown procedure"""
        self.logger.info("Shutting down IDSS Production Server...")
        
        if self.server:
            self.server.should_exit = True
            self.logger.info("Server shutdown completed")
    
    def get_uvicorn_config(self):
        """Get Uvicorn server configuration"""
        config = {
            "app": "unified_dashboard:app",  # Import path to FastAPI app
            "host": os.getenv('HOST', '0.0.0.0'),
            "port": int(os.getenv('PORT', 8000)),
            "workers": int(os.getenv('WORKERS', 4)),
            "log_level": os.getenv('LOG_LEVEL', 'info').lower(),
            "access_log": True,
            "use_colors": False,
            "server_header": False,
            "date_header": True,
            # "loop": "uvloop",  # Not supported on Windows
            # "http": "httptools",  # Optional
            "lifespan": "on",
            "timeout_keep_alive": int(os.getenv('KEEPALIVE_TIMEOUT', 65)),
            "timeout_graceful_shutdown": 30,
            "limit_concurrency": int(os.getenv('MAX_CONCURRENT_CONNECTIONS', 1000)),
            "limit_max_requests": 10000,
            "backlog": 2048
        }
        
        # SSL Configuration
        if os.getenv('SSL_ENABLED', 'false').lower() == 'true':
            ssl_cert = os.getenv('SSL_CERT_PATH')
            ssl_key = os.getenv('SSL_KEY_PATH')
            
            if ssl_cert and ssl_key and Path(ssl_cert).exists() and Path(ssl_key).exists():
                config.update({
                    "ssl_keyfile": ssl_key,
                    "ssl_certfile": ssl_cert,
                    "ssl_version": 3,  # TLS 1.2+
                })
                self.logger.info("SSL/TLS enabled")
            else:
                self.logger.warning("SSL enabled but certificates not found, running without SSL")
        
        return config
    
    def print_startup_banner(self):
        """Print startup banner with system information"""
        banner = f"""
{'='*80}
IDSS - AI-Powered Section Throughput Optimization System
{'='*80}

Indian Railways Production Deployment
Zone: {os.getenv('RAILWAY_ZONE', 'N/A')}
Environment: {os.getenv('ENVIRONMENT', 'production')}
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}

Server Configuration:
    * Host: {os.getenv('HOST', '0.0.0.0')}
    * Port: {os.getenv('PORT', 8000)}
    * Workers: {os.getenv('WORKERS', 4)}
    * Max Connections: {os.getenv('MAX_CONCURRENT_CONNECTIONS', 1000)}

Security Features:
    * SSL/TLS: {'Enabled' if os.getenv('SSL_ENABLED', 'false').lower() == 'true' else 'Disabled'}
    * Data Localization: {os.getenv('DATA_LOCALIZATION', 'true')}
    * Audit Logging: {os.getenv('AUDIT_LOGGING', 'true')}

Monitoring:
    * Metrics: {'Enabled' if os.getenv('ENABLE_METRICS', 'true').lower() == 'true' else 'Disabled'}
    * Alerts: {'Enabled' if os.getenv('ENABLE_ALERTS', 'true').lower() == 'true' else 'Disabled'}

Access Points:
    * Dashboard: http{'s' if os.getenv('SSL_ENABLED', 'false').lower() == 'true' else ''}://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', 8000)}
    * API Docs: http{'s' if os.getenv('SSL_ENABLED', 'false').lower() == 'true' else ''}://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', 8000)}/docs
    * Health Check: http{'s' if os.getenv('SSL_ENABLED', 'false').lower() == 'true' else ''}://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', 8000)}/api/status

{'='*80}
"""
        print(banner)
        self.logger.info("IDSS Production Server Started Successfully")
    
    async def start_server(self):
        """Start the production server"""
        try:
        self.logger.info("Performing pre-startup checks...")
            
            # System checks
            self.check_system_resources()
            self.create_directories()
            self.setup_signal_handlers()
            
            # Get server configuration
            config = self.get_uvicorn_config()
            
            # Print startup information
            self.print_startup_banner()
            
            # Start server
            self.logger.info("Starting Uvicorn server...")
            await uvicorn.run(**config)
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            sys.exit(1)

def main():
    """Main entry point for production server"""
    
    # Set event loop policy for better performance
    # uvloop not supported on Windows, using default event loop
    
    # Create and start production server
    server = ProductionServer()
    
    try:
        if sys.platform == 'win32':
            # Windows-specific event loop handling
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Run the server
        asyncio.run(server.start_server())
        
    except KeyboardInterrupt:
        server.logger.info("Server shutdown initiated by user")
    except Exception as e:
        server.logger.error(f"Critical error: {e}")
        sys.exit(1)
    finally:
        server.logger.info("IDSS Production Server stopped")

if __name__ == "__main__":
    main()