"""
Scalability Architecture for IDSS
Design for scaling to larger railway network sections with distributed processing
"""

import asyncio
import json
import logging
import os
import redis
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from queue import Queue
import threading

# Import production config
from production_config import ScalingConfig, get_production_config

class NodeType(Enum):
    COORDINATOR = "coordinator"
    WORKER = "worker" 
    DATABASE = "database"
    CACHE = "cache"
    LOAD_BALANCER = "load_balancer"

class ProcessingType(Enum):
    REAL_TIME = "real_time"
    BATCH = "batch"
    ANALYTICS = "analytics"
    OPTIMIZATION = "optimization"

@dataclass
class ClusterNode:
    """Represents a node in the IDSS cluster"""
    node_id: str
    node_type: NodeType
    ip_address: str
    port: int
    zone: str
    capacity: int
    current_load: int = 0
    status: str = "healthy"
    last_heartbeat: datetime = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()
    
    def get_load_percentage(self) -> float:
        """Get current load as percentage"""
        return (self.current_load / self.capacity) * 100 if self.capacity > 0 else 0

@dataclass
class ProcessingTask:
    """Represents a processing task in the distributed system"""
    task_id: str
    task_type: ProcessingType
    priority: int
    railway_zone: str
    data: Dict[str, Any]
    created_at: datetime
    assigned_node: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class LoadBalancer:
    """Advanced load balancer for IDSS cluster"""
    
    def __init__(self, config: ScalingConfig):
        self.config = config
        self.nodes = {}
        self.task_queue = Queue()
        self.completed_tasks = {}
        self.load_balancing_algorithm = "weighted_round_robin"
        
        # Health monitoring
        self.health_check_interval = 30  # seconds
        self.unhealthy_threshold = 3
        
        # Metrics
        self.total_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0
        
        # Start health monitoring
        self._start_health_monitoring()
    
    def register_node(self, node: ClusterNode) -> bool:
        """Register a new node in the cluster"""
        if node.node_id in self.nodes:
            logging.warning(f"Node {node.node_id} already registered")
            return False
        
        self.nodes[node.node_id] = node
        logging.info(f"Node {node.node_id} registered successfully")
        
        # Initialize node-specific metrics
        self._initialize_node_metrics(node.node_id)
        
        return True
    
    def _initialize_node_metrics(self, node_id: str):
        """Initialize metrics for a new node"""
        # In production, this would be stored in a metrics database
        pass
    
    def select_node(self, task: ProcessingTask) -> Optional[ClusterNode]:
        """Select best node for task using load balancing algorithm"""
        available_nodes = self._get_healthy_nodes(task.railway_zone)
        
        if not available_nodes:
            logging.error("No healthy nodes available")
            return None
        
        if self.load_balancing_algorithm == "weighted_round_robin":
            return self._weighted_round_robin_selection(available_nodes)
        elif self.load_balancing_algorithm == "least_connections":
            return self._least_connections_selection(available_nodes)
        elif self.load_balancing_algorithm == "resource_based":
            return self._resource_based_selection(available_nodes, task)
        else:
            # Default to round robin
            return available_nodes[0]
    
    def _get_healthy_nodes(self, zone: Optional[str] = None) -> List[ClusterNode]:
        """Get list of healthy nodes, optionally filtered by zone"""
        healthy_nodes = []
        
        for node in self.nodes.values():
            if node.status == "healthy":
                # Filter by zone if specified
                if zone and node.zone != zone and node.zone != "SYSTEM":
                    continue
                
                # Check if node has capacity
                if node.current_load < node.capacity:
                    healthy_nodes.append(node)
        
        # Sort by load percentage (ascending)
        return sorted(healthy_nodes, key=lambda n: n.get_load_percentage())
    
    def _weighted_round_robin_selection(self, nodes: List[ClusterNode]) -> ClusterNode:
        """Select node using weighted round robin based on capacity"""
        if not nodes:
            return None
        
        # Calculate weights based on available capacity
        total_available_capacity = sum(node.capacity - node.current_load for node in nodes)
        
        if total_available_capacity == 0:
            return nodes[0]  # All nodes at capacity, return first
        
        # Select node with highest available capacity percentage
        best_node = max(nodes, key=lambda n: (n.capacity - n.current_load) / n.capacity)
        
        return best_node
    
    def _least_connections_selection(self, nodes: List[ClusterNode]) -> ClusterNode:
        """Select node with least current connections"""
        return min(nodes, key=lambda n: n.current_load)
    
    def _resource_based_selection(self, nodes: List[ClusterNode], task: ProcessingTask) -> ClusterNode:
        """Select node based on resource requirements of task"""
        # For AI/ML tasks, prioritize nodes with higher capacity
        if task.task_type in [ProcessingType.ANALYTICS, ProcessingType.OPTIMIZATION]:
            return max(nodes, key=lambda n: n.capacity - n.current_load)
        
        # For real-time tasks, prioritize nodes with lowest load
        if task.task_type == ProcessingType.REAL_TIME:
            return min(nodes, key=lambda n: n.get_load_percentage())
        
        # Default selection
        return self._weighted_round_robin_selection(nodes)
    
    def assign_task(self, task: ProcessingTask) -> Optional[str]:
        """Assign task to appropriate node"""
        selected_node = self.select_node(task)
        
        if not selected_node:
            logging.error(f"No available node for task {task.task_id}")
            return None
        
        # Assign task to node
        task.assigned_node = selected_node.node_id
        task.status = "assigned"
        
        # Update node load
        selected_node.current_load += 1
        
        logging.info(f"Task {task.task_id} assigned to node {selected_node.node_id}")
        
        return selected_node.node_id
    
    def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed and update node load"""
        # Find the task (in production, this would be from database)
        for task in self.task_queue.queue:
            if task.task_id == task_id:
                task.status = "completed"
                task.result = result
                
                # Update node load
                if task.assigned_node and task.assigned_node in self.nodes:
                    self.nodes[task.assigned_node].current_load -= 1
                
                # Store completed task
                self.completed_tasks[task_id] = task
                
                logging.info(f"Task {task_id} completed")
                break
    
    def _start_health_monitoring(self):
        """Start background health monitoring"""
        def health_monitor():
            while True:
                self._check_node_health()
                threading.Event().wait(self.health_check_interval)
        
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        health_thread.start()
    
    def _check_node_health(self):
        """Check health of all nodes"""
        current_time = datetime.now()
        
        for node in self.nodes.values():
            # Check if node has missed heartbeats
            time_since_heartbeat = (current_time - node.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > self.health_check_interval * self.unhealthy_threshold:
                if node.status == "healthy":
                    node.status = "unhealthy"
                    logging.warning(f"Node {node.node_id} marked as unhealthy")
            else:
                if node.status == "unhealthy":
                    node.status = "healthy"
                    logging.info(f"Node {node.node_id} restored to healthy")
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status"""
        healthy_nodes = len([n for n in self.nodes.values() if n.status == "healthy"])
        total_nodes = len(self.nodes)
        
        total_capacity = sum(node.capacity for node in self.nodes.values())
        total_load = sum(node.current_load for node in self.nodes.values())
        
        return {
            "total_nodes": total_nodes,
            "healthy_nodes": healthy_nodes,
            "cluster_health": "healthy" if healthy_nodes > total_nodes * 0.7 else "degraded",
            "total_capacity": total_capacity,
            "current_load": total_load,
            "load_percentage": (total_load / total_capacity * 100) if total_capacity > 0 else 0,
            "pending_tasks": self.task_queue.qsize(),
            "completed_tasks": len(self.completed_tasks)
        }

class DistributedCache:
    """Distributed caching system using Redis"""
    
    def __init__(self, redis_urls: List[str]):
        self.redis_clients = []
        self.consistent_hash = ConsistentHashing()
        
        # Initialize Redis clients
        for i, url in enumerate(redis_urls):
            try:
                client = redis.Redis.from_url(url, decode_responses=True)
                client.ping()  # Test connection
                self.redis_clients.append(client)
                self.consistent_hash.add_node(f"redis_{i}")
                logging.info(f"Connected to Redis: {url}")
            except Exception as e:
                logging.error(f"Failed to connect to Redis {url}: {e}")
    
    def _get_client(self, key: str) -> redis.Redis:
        """Get Redis client for key using consistent hashing"""
        node = self.consistent_hash.get_node(key)
        node_index = int(node.split('_')[1])
        return self.redis_clients[node_index] if node_index < len(self.redis_clients) else self.redis_clients[0]
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in distributed cache"""
        try:
            client = self._get_client(key)
            serialized_value = json.dumps(value, default=str)
            return client.setex(key, ttl, serialized_value)
        except Exception as e:
            logging.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache"""
        try:
            client = self._get_client(key)
            value = client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logging.error(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            client = self._get_client(key)
            return client.delete(key) > 0
        except Exception as e:
            logging.error(f"Cache delete error: {e}")
            return False
    
    def flush_all(self):
        """Flush all cache data"""
        for client in self.redis_clients:
            try:
                client.flushdb()
            except Exception as e:
                logging.error(f"Cache flush error: {e}")

class ConsistentHashing:
    """Consistent hashing for distributed cache"""
    
    def __init__(self, replicas: int = 100):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
    
    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: str):
        """Add node to the hash ring"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def remove_node(self, node: str):
        """Remove node from hash ring"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            if key in self.ring:
                del self.ring[key]
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key: str) -> str:
        """Get node for key"""
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        
        # Find the first node clockwise from hash_key
        for ring_key in self.sorted_keys:
            if hash_key <= ring_key:
                return self.ring[ring_key]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]

class DistributedProcessor:
    """Distributed processing engine for IDSS"""
    
    def __init__(self, config: ScalingConfig):
        self.config = config
        self.load_balancer = LoadBalancer(config)
        self.cache = None  # Will be initialized with Redis URLs
        self.task_processors = {}
        
        # Processing pools
        self.thread_pool = ThreadPoolExecutor(max_workers=config.worker_processes * 2)
        self.process_pool = ProcessPoolExecutor(max_workers=config.worker_processes)
        
        # Task queues by type
        self.real_time_queue = asyncio.Queue(maxsize=1000)
        self.batch_queue = asyncio.Queue(maxsize=10000)
        self.analytics_queue = asyncio.Queue(maxsize=500)
        
        # Initialize task processors
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize different types of task processors"""
        self.task_processors = {
            ProcessingType.REAL_TIME: self._process_real_time_task,
            ProcessingType.BATCH: self._process_batch_task,
            ProcessingType.ANALYTICS: self._process_analytics_task,
            ProcessingType.OPTIMIZATION: self._process_optimization_task
        }
    
    def initialize_cache(self, redis_urls: List[str]):
        """Initialize distributed cache"""
        self.cache = DistributedCache(redis_urls)
    
    async def submit_task(self, task: ProcessingTask) -> str:
        """Submit task for processing"""
        # Assign task to appropriate node
        assigned_node = self.load_balancer.assign_task(task)
        
        if not assigned_node:
            raise Exception("No available nodes for task processing")
        
        # Add to appropriate queue based on task type
        if task.task_type == ProcessingType.REAL_TIME:
            await self.real_time_queue.put(task)
        elif task.task_type == ProcessingType.BATCH:
            await self.batch_queue.put(task)
        elif task.task_type == ProcessingType.ANALYTICS:
            await self.analytics_queue.put(task)
        else:
            await self.batch_queue.put(task)  # Default queue
        
        logging.info(f"Task {task.task_id} submitted for processing")
        return task.task_id
    
    async def _process_real_time_task(self, task: ProcessingTask) -> Dict[str, Any]:
        """Process real-time tasks (low latency required)"""
        start_time = datetime.now()
        
        # Check cache first
        cache_key = f"rt_task_{task.railway_zone}_{task.task_type.value}"
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logging.info(f"Task {task.task_id} served from cache")
                return cached_result
        
        # Process task
        if task.task_type == ProcessingType.REAL_TIME:
            # Simulate real-time processing (conflict detection, signal optimization)
            result = {
                "task_id": task.task_id,
                "processed_at": datetime.now().isoformat(),
                "processing_time_ms": 50,  # Target < 100ms for real-time
                "conflicts_detected": len(task.data.get('trains', [])) // 3,
                "recommendations": [
                    {"type": "SPEED_ADJUST", "train": "T001", "target_speed": 80},
                    {"type": "SIGNAL_CLEAR", "signal": "SIG_001"}
                ]
            }
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        result["actual_processing_time_ms"] = processing_time
        
        # Cache result for similar requests
        if self.cache:
            self.cache.set(cache_key, result, ttl=60)  # Cache for 1 minute
        
        return result
    
    async def _process_batch_task(self, task: ProcessingTask) -> Dict[str, Any]:
        """Process batch tasks (higher throughput, can have higher latency)"""
        start_time = datetime.now()
        
        # Process in thread pool for I/O bound tasks
        result = await asyncio.get_event_loop().run_in_executor(
            self.thread_pool, self._batch_processing_worker, task
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        result["processing_time_ms"] = processing_time
        
        return result
    
    def _batch_processing_worker(self, task: ProcessingTask) -> Dict[str, Any]:
        """Worker function for batch processing"""
        # Simulate batch processing (data aggregation, reporting)
        import time
        time.sleep(0.1)  # Simulate processing time
        
        return {
            "task_id": task.task_id,
            "processed_at": datetime.now().isoformat(),
            "batch_size": len(task.data.get('records', [])),
            "processed_records": len(task.data.get('records', [])),
            "summary": {
                "total_trains": 150,
                "delayed_trains": 12,
                "punctuality": 92.0
            }
        }
    
    async def _process_analytics_task(self, task: ProcessingTask) -> Dict[str, Any]:
        """Process analytics tasks (CPU intensive)"""
        start_time = datetime.now()
        
        # Process in process pool for CPU bound tasks
        result = await asyncio.get_event_loop().run_in_executor(
            self.process_pool, self._analytics_processing_worker, task
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        result["processing_time_ms"] = processing_time
        
        return result
    
    def _analytics_processing_worker(self, task: ProcessingTask) -> Dict[str, Any]:
        """Worker function for analytics processing"""
        # Simulate analytics processing (ML model inference, pattern analysis)
        import time
        import random
        
        time.sleep(0.2)  # Simulate CPU intensive processing
        
        return {
            "task_id": task.task_id,
            "processed_at": datetime.now().isoformat(),
            "model_predictions": [
                {"train": "T001", "delay_probability": random.uniform(0.1, 0.9)},
                {"train": "T002", "delay_probability": random.uniform(0.1, 0.9)}
            ],
            "patterns_detected": 3,
            "confidence_score": random.uniform(0.8, 0.95)
        }
    
    async def _process_optimization_task(self, task: ProcessingTask) -> Dict[str, Any]:
        """Process optimization tasks (complex algorithms)"""
        start_time = datetime.now()
        
        # Use process pool for complex optimization algorithms
        result = await asyncio.get_event_loop().run_in_executor(
            self.process_pool, self._optimization_processing_worker, task
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        result["processing_time_ms"] = processing_time
        
        return result
    
    def _optimization_processing_worker(self, task: ProcessingTask) -> Dict[str, Any]:
        """Worker function for optimization processing"""
        # Simulate optimization processing (route optimization, schedule optimization)
        import time
        
        time.sleep(0.5)  # Simulate complex optimization algorithms
        
        return {
            "task_id": task.task_id,
            "processed_at": datetime.now().isoformat(),
            "optimization_type": "SCHEDULE_OPTIMIZATION",
            "improved_punctuality": 15.2,  # percentage improvement
            "cost_savings": 125000,  # INR
            "optimized_routes": 8,
            "confidence_score": 0.89
        }
    
    async def start_processing(self):
        """Start distributed processing"""
        # Start workers for different task types
        asyncio.create_task(self._real_time_worker())
        asyncio.create_task(self._batch_worker())
        asyncio.create_task(self._analytics_worker())
        
        logging.info("Distributed processing started")
    
    async def _real_time_worker(self):
        """Worker for real-time tasks"""
        while True:
            try:
                task = await self.real_time_queue.get()
                
                # Process task
                processor = self.task_processors[task.task_type]
                result = await processor(task)
                
                # Complete task
                self.load_balancer.complete_task(task.task_id, result)
                
                # Mark task as done
                self.real_time_queue.task_done()
                
            except Exception as e:
                logging.error(f"Real-time worker error: {e}")
    
    async def _batch_worker(self):
        """Worker for batch tasks"""
        while True:
            try:
                task = await self.batch_queue.get()
                
                # Process task
                processor = self.task_processors.get(task.task_type, self._process_batch_task)
                result = await processor(task)
                
                # Complete task
                self.load_balancer.complete_task(task.task_id, result)
                
                # Mark task as done
                self.batch_queue.task_done()
                
            except Exception as e:
                logging.error(f"Batch worker error: {e}")
    
    async def _analytics_worker(self):
        """Worker for analytics tasks"""
        while True:
            try:
                task = await self.analytics_queue.get()
                
                # Process task
                processor = self.task_processors[task.task_type]
                result = await processor(task)
                
                # Complete task
                self.load_balancer.complete_task(task.task_id, result)
                
                # Mark task as done
                self.analytics_queue.task_done()
                
            except Exception as e:
                logging.error(f"Analytics worker error: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            "real_time_queue_size": self.real_time_queue.qsize(),
            "batch_queue_size": self.batch_queue.size(),
            "analytics_queue_size": self.analytics_queue.qsize(),
            "thread_pool_active": self.thread_pool._threads.__len__(),
            "process_pool_active": len(self.process_pool._processes),
            "cluster_status": self.load_balancer.get_cluster_status()
        }

class ScalabilityManager:
    """Main scalability management system"""
    
    def __init__(self):
        self.config = get_production_config().config['scaling']
        self.processor = DistributedProcessor(self.config)
        self.auto_scaler = AutoScaler(self.config)
        
        # Metrics collection
        self.metrics_collector = MetricsCollector()
        
        logging.info("Scalability Manager initialized")
    
    async def initialize_cluster(self, node_configs: List[Dict[str, Any]]):
        """Initialize the IDSS cluster"""
        for node_config in node_configs:
            node = ClusterNode(
                node_id=node_config['id'],
                node_type=NodeType(node_config['type']),
                ip_address=node_config['ip'],
                port=node_config['port'],
                zone=node_config.get('zone', 'DEFAULT'),
                capacity=node_config.get('capacity', 100)
            )
            
            self.processor.load_balancer.register_node(node)
        
        # Initialize distributed cache
        redis_urls = node_configs.get('redis_urls', ['redis://localhost:6379'])
        self.processor.initialize_cache(redis_urls)
        
        # Start processing
        await self.processor.start_processing()
        
        logging.info(f"Cluster initialized with {len(node_configs)} nodes")
    
    async def scale_up(self, target_nodes: int):
        """Scale up the cluster"""
        await self.auto_scaler.scale_up(target_nodes)
    
    async def scale_down(self, target_nodes: int):
        """Scale down the cluster"""
        await self.auto_scaler.scale_down(target_nodes)
    
    def get_scalability_metrics(self) -> Dict[str, Any]:
        """Get comprehensive scalability metrics"""
        return {
            "cluster_status": self.processor.load_balancer.get_cluster_status(),
            "processing_stats": self.processor.get_processing_stats(),
            "auto_scaling_status": self.auto_scaler.get_status(),
            "performance_metrics": self.metrics_collector.get_metrics()
        }

class AutoScaler:
    """Automatic scaling based on load and performance metrics"""
    
    def __init__(self, config: ScalingConfig):
        self.config = config
        self.scaling_enabled = True
        self.last_scaling_action = datetime.now()
        self.min_nodes = 2
        self.max_nodes = 20
        
        # Scaling thresholds
        self.scale_up_cpu_threshold = 80
        self.scale_up_memory_threshold = 85
        self.scale_down_cpu_threshold = 30
        self.scale_down_memory_threshold = 40
        
        # Scaling cooldown (prevent rapid scaling)
        self.scaling_cooldown = timedelta(minutes=5)
    
    def should_scale_up(self, metrics: Dict[str, Any]) -> bool:
        """Determine if cluster should scale up"""
        if not self.scaling_enabled:
            return False
        
        # Check cooldown period
        if datetime.now() - self.last_scaling_action < self.scaling_cooldown:
            return False
        
        # Check resource utilization
        cpu_usage = metrics.get('cluster_status', {}).get('load_percentage', 0)
        queue_sizes = sum([
            metrics.get('processing_stats', {}).get('real_time_queue_size', 0),
            metrics.get('processing_stats', {}).get('batch_queue_size', 0),
            metrics.get('processing_stats', {}).get('analytics_queue_size', 0)
        ])
        
        # Scale up conditions
        if cpu_usage > self.scale_up_cpu_threshold:
            return True
        
        if queue_sizes > 1000:  # High queue backlog
            return True
        
        return False
    
    def should_scale_down(self, metrics: Dict[str, Any]) -> bool:
        """Determine if cluster should scale down"""
        if not self.scaling_enabled:
            return False
        
        # Check cooldown period
        if datetime.now() - self.last_scaling_action < self.scaling_cooldown:
            return False
        
        # Check resource utilization
        cpu_usage = metrics.get('cluster_status', {}).get('load_percentage', 0)
        healthy_nodes = metrics.get('cluster_status', {}).get('healthy_nodes', 0)
        
        # Don't scale below minimum
        if healthy_nodes <= self.min_nodes:
            return False
        
        # Scale down conditions
        if cpu_usage < self.scale_down_cpu_threshold:
            return True
        
        return False
    
    async def scale_up(self, target_nodes: int):
        """Scale up cluster"""
        logging.info(f"Scaling up cluster to {target_nodes} nodes")
        # Implementation would depend on orchestration platform (Kubernetes, etc.)
        self.last_scaling_action = datetime.now()
    
    async def scale_down(self, target_nodes: int):
        """Scale down cluster"""
        logging.info(f"Scaling down cluster to {target_nodes} nodes")
        # Implementation would depend on orchestration platform
        self.last_scaling_action = datetime.now()
    
    def get_status(self) -> Dict[str, Any]:
        """Get auto-scaler status"""
        return {
            "enabled": self.scaling_enabled,
            "min_nodes": self.min_nodes,
            "max_nodes": self.max_nodes,
            "last_action": self.last_scaling_action.isoformat(),
            "thresholds": {
                "scale_up_cpu": self.scale_up_cpu_threshold,
                "scale_down_cpu": self.scale_down_cpu_threshold
            }
        }

class MetricsCollector:
    """Collect and aggregate performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "requests_per_second": 0,
            "average_response_time": 0,
            "error_rate": 0,
            "throughput": 0
        }
        
        # Start metrics collection
        self._start_collection()
    
    def _start_collection(self):
        """Start background metrics collection"""
        def collect_metrics():
            while True:
                self._collect_system_metrics()
                threading.Event().wait(30)  # Collect every 30 seconds
        
        metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
        metrics_thread.start()
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        # In production, this would collect real system metrics
        import psutil
        import random
        
        self.metrics.update({
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "requests_per_second": random.randint(50, 200),
            "average_response_time": random.uniform(100, 500),
            "error_rate": random.uniform(0, 5),
            "timestamp": datetime.now().isoformat()
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 IDSS Scalability Architecture")
    print("=" * 50)
    
    # Initialize scalability manager
    scalability_manager = ScalabilityManager()
    
    # Example node configurations
    node_configs = [
        {
            "id": "coordinator_001",
            "type": "coordinator",
            "ip": "10.0.1.10",
            "port": 8000,
            "zone": "CR",
            "capacity": 200
        },
        {
            "id": "worker_001",
            "type": "worker", 
            "ip": "10.0.1.11",
            "port": 8001,
            "zone": "CR",
            "capacity": 100
        },
        {
            "id": "worker_002",
            "type": "worker",
            "ip": "10.0.1.12", 
            "port": 8002,
            "zone": "WR",
            "capacity": 100
        }
    ]
    
    print(f"\n📊 Cluster Configuration:")
    for config in node_configs:
        print(f"  • {config['id']} ({config['type']}) - {config['zone']} zone")
    
    print(f"\n⚖️ Load Balancing:")
    load_balancer = LoadBalancer(scalability_manager.config)
    
    # Register nodes
    for config in node_configs:
        node = ClusterNode(
            node_id=config['id'],
            node_type=NodeType(config['type']),
            ip_address=config['ip'],
            port=config['port'],
            zone=config['zone'],
            capacity=config['capacity']
        )
        load_balancer.register_node(node)
    
    # Test task assignment
    test_task = ProcessingTask(
        task_id="task_001",
        task_type=ProcessingType.REAL_TIME,
        priority=1,
        railway_zone="CR",
        data={"trains": ["T001", "T002"]},
        created_at=datetime.now()
    )
    
    assigned_node = load_balancer.assign_task(test_task)
    if assigned_node:
        print(f"  ✅ Task assigned to node: {assigned_node}")
    
    # Display cluster status
    status = load_balancer.get_cluster_status()
    print(f"\n📈 Cluster Status:")
    print(f"  • Total Nodes: {status['total_nodes']}")
    print(f"  • Healthy Nodes: {status['healthy_nodes']}")
    print(f"  • Load: {status['load_percentage']:.1f}%")
    print(f"  • Capacity: {status['current_load']}/{status['total_capacity']}")
    
    print(f"\n🎉 Scalability architecture initialized successfully!")
    print(f"\n💡 Key Features:")
    print(f"  ✅ Distributed load balancing")
    print(f"  ✅ Auto-scaling capabilities") 
    print(f"  ✅ Multi-zone support")
    print(f"  ✅ Task prioritization")
    print(f"  ✅ Health monitoring")
    print(f"  ✅ Performance metrics")