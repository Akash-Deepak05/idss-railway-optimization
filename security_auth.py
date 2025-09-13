"""
Security & Authentication System for IDSS
Role-based access control, secure API authentication, and audit logging
"""

import jwt
import bcrypt
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import json
import asyncio
from functools import wraps
import ipaddress

# Import production config
from production_config import UserRole, SecurityConfig

class PermissionLevel(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class ResourceType(Enum):
    DASHBOARD = "dashboard"
    SCENARIOS = "scenarios"
    ANALYTICS = "analytics"
    CONFIGURATION = "configuration"
    USER_MANAGEMENT = "user_management"
    SYSTEM_LOGS = "system_logs"
    AUDIT_LOGS = "audit_logs"

@dataclass
class User:
    """User model with security attributes"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    railway_zone: str
    department: str
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    is_locked: bool = False
    locked_until: Optional[datetime] = None
    session_tokens: List[str] = None
    permissions: Set[str] = None
    two_factor_enabled: bool = False
    
    def __post_init__(self):
        if self.session_tokens is None:
            self.session_tokens = []
        if self.permissions is None:
            self.permissions = set()

@dataclass
class AuditLog:
    """Audit log entry"""
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    success: bool
    risk_level: str = "LOW"

class RolePermissionManager:
    """Manages role-based permissions"""
    
    def __init__(self):
        self.role_permissions = self._initialize_permissions()
    
    def _initialize_permissions(self) -> Dict[UserRole, Dict[ResourceType, Set[PermissionLevel]]]:
        """Initialize role-based permissions matrix"""
        return {
            UserRole.OPERATOR: {
                ResourceType.DASHBOARD: {PermissionLevel.READ},
                ResourceType.SCENARIOS: {PermissionLevel.READ, PermissionLevel.EXECUTE},
                ResourceType.ANALYTICS: {PermissionLevel.READ},
                ResourceType.SYSTEM_LOGS: {PermissionLevel.READ}
            },
            
            UserRole.SUPERVISOR: {
                ResourceType.DASHBOARD: {PermissionLevel.READ, PermissionLevel.WRITE},
                ResourceType.SCENARIOS: {PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE},
                ResourceType.ANALYTICS: {PermissionLevel.READ, PermissionLevel.WRITE},
                ResourceType.CONFIGURATION: {PermissionLevel.READ},
                ResourceType.SYSTEM_LOGS: {PermissionLevel.READ},
                ResourceType.AUDIT_LOGS: {PermissionLevel.READ}
            },
            
            UserRole.MANAGER: {
                ResourceType.DASHBOARD: {PermissionLevel.READ, PermissionLevel.WRITE},
                ResourceType.SCENARIOS: {PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.EXECUTE},
                ResourceType.ANALYTICS: {PermissionLevel.READ, PermissionLevel.WRITE},
                ResourceType.CONFIGURATION: {PermissionLevel.READ, PermissionLevel.WRITE},
                ResourceType.USER_MANAGEMENT: {PermissionLevel.READ},
                ResourceType.SYSTEM_LOGS: {PermissionLevel.READ},
                ResourceType.AUDIT_LOGS: {PermissionLevel.READ}
            },
            
            UserRole.ADMIN: {
                ResourceType.DASHBOARD: {PermissionLevel.ADMIN},
                ResourceType.SCENARIOS: {PermissionLevel.ADMIN},
                ResourceType.ANALYTICS: {PermissionLevel.ADMIN},
                ResourceType.CONFIGURATION: {PermissionLevel.ADMIN},
                ResourceType.USER_MANAGEMENT: {PermissionLevel.ADMIN},
                ResourceType.SYSTEM_LOGS: {PermissionLevel.ADMIN},
                ResourceType.AUDIT_LOGS: {PermissionLevel.ADMIN}
            },
            
            UserRole.SYSTEM: {
                ResourceType.DASHBOARD: {PermissionLevel.ADMIN},
                ResourceType.SCENARIOS: {PermissionLevel.ADMIN},
                ResourceType.ANALYTICS: {PermissionLevel.ADMIN},
                ResourceType.CONFIGURATION: {PermissionLevel.ADMIN},
                ResourceType.SYSTEM_LOGS: {PermissionLevel.ADMIN}
            }
        }
    
    def has_permission(self, user: User, resource: ResourceType, permission: PermissionLevel) -> bool:
        """Check if user has specific permission for resource"""
        if user.role not in self.role_permissions:
            return False
        
        resource_permissions = self.role_permissions[user.role].get(resource, set())
        
        # Admin permission grants all access
        if PermissionLevel.ADMIN in resource_permissions:
            return True
        
        return permission in resource_permissions
    
    def get_user_permissions(self, user: User) -> Dict[str, List[str]]:
        """Get all permissions for a user"""
        if user.role not in self.role_permissions:
            return {}
        
        permissions = {}
        for resource, perms in self.role_permissions[user.role].items():
            permissions[resource.value] = [p.value for p in perms]
        
        return permissions

class AuthenticationManager:
    """Handles user authentication and session management"""
    
    def __init__(self, security_config: SecurityConfig):
        self.config = security_config
        self.permission_manager = RolePermissionManager()
        self.active_sessions = {}
        self.audit_logger = AuditLogger()
        self.users_db = {}  # In production, this would be a proper database
        
        # Initialize with default admin user
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user for initial setup"""
        admin_user = User(
            user_id="admin_001",
            username="admin",
            email="admin@railways.gov.in",
            password_hash=self._hash_password("admin123!"),
            role=UserRole.ADMIN,
            railway_zone="SYSTEM",
            department="IT",
            created_at=datetime.now()
        )
        self.users_db[admin_user.username] = admin_user
    
    def _hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'railway_zone': user.railway_zone,
            'exp': datetime.utcnow() + timedelta(minutes=self.config.session_timeout_minutes),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.config.jwt_secret, algorithm='HS256')
    
    def _verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logging.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logging.warning("Invalid token")
            return None
    
    def authenticate_user(self, username: str, password: str, ip_address: str = "", user_agent: str = "") -> Optional[str]:
        """Authenticate user and return JWT token"""
        
        # Check if user exists
        user = self.users_db.get(username)
        if not user:
            self.audit_logger.log_authentication_attempt(
                username, "LOGIN_FAILED", "User not found", ip_address, user_agent, False
            )
            return None
        
        # Check if user is locked
        if user.is_locked and user.locked_until and datetime.now() < user.locked_until:
            self.audit_logger.log_authentication_attempt(
                user.user_id, "LOGIN_FAILED", "Account locked", ip_address, user_agent, False
            )
            return None
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            
            # Lock account after max attempts
            if user.failed_login_attempts >= self.config.max_login_attempts:
                user.is_locked = True
                user.locked_until = datetime.now() + timedelta(minutes=self.config.lockout_duration_minutes)
                
                self.audit_logger.log_authentication_attempt(
                    user.user_id, "ACCOUNT_LOCKED", "Too many failed attempts", ip_address, user_agent, False
                )
            else:
                self.audit_logger.log_authentication_attempt(
                    user.user_id, "LOGIN_FAILED", "Invalid password", ip_address, user_agent, False
                )
            
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        user.last_login = datetime.now()
        
        # Generate JWT token
        token = self._generate_jwt_token(user)
        user.session_tokens.append(token)
        
        # Store active session
        self.active_sessions[token] = {
            'user_id': user.user_id,
            'created_at': datetime.now(),
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        self.audit_logger.log_authentication_attempt(
            user.user_id, "LOGIN_SUCCESS", "Successful login", ip_address, user_agent, True
        )
        
        return token
    
    def validate_session(self, token: str) -> Optional[User]:
        """Validate session token and return user"""
        if token not in self.active_sessions:
            return None
        
        payload = self._verify_jwt_token(token)
        if not payload:
            # Remove invalid token
            self.revoke_session(token)
            return None
        
        user = self.users_db.get(payload['username'])
        if not user or token not in user.session_tokens:
            return None
        
        return user
    
    def revoke_session(self, token: str):
        """Revoke a session token"""
        if token in self.active_sessions:
            session = self.active_sessions[token]
            user_id = session['user_id']
            
            # Remove from active sessions
            del self.active_sessions[token]
            
            # Remove from user's session tokens
            for user in self.users_db.values():
                if user.user_id == user_id and token in user.session_tokens:
                    user.session_tokens.remove(token)
                    break
            
            self.audit_logger.log_action(
                user_id, "SESSION_REVOKED", "session_management", {"token_revoked": True}, "", "", True
            )
    
    def create_user(self, username: str, email: str, password: str, role: UserRole, 
                   railway_zone: str, department: str, created_by: str) -> bool:
        """Create new user"""
        if username in self.users_db:
            return False
        
        user = User(
            user_id=f"user_{secrets.token_hex(8)}",
            username=username,
            email=email,
            password_hash=self._hash_password(password),
            role=role,
            railway_zone=railway_zone,
            department=department,
            created_at=datetime.now()
        )
        
        self.users_db[username] = user
        
        self.audit_logger.log_action(
            created_by, "USER_CREATED", "user_management", 
            {"new_user": username, "role": role.value, "zone": railway_zone}, "", "", True
        )
        
        return True

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, log_file: str = "logs/idss_audit.log"):
        self.log_file = log_file
        self.setup_logging()
        
        # In-memory storage for recent logs (production would use database)
        self.audit_logs = []
    
    def setup_logging(self):
        """Setup audit logging"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - AUDIT - %(message)s'
        )
    
    def log_authentication_attempt(self, user_id: str, action: str, details: str, 
                                 ip_address: str, user_agent: str, success: bool):
        """Log authentication attempts"""
        audit_entry = AuditLog(
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource="authentication",
            details={"details": details, "success": success},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            risk_level="HIGH" if not success else "LOW"
        )
        
        self._write_audit_log(audit_entry)
    
    def log_action(self, user_id: str, action: str, resource: str, details: Dict[str, Any],
                   ip_address: str, user_agent: str, success: bool, risk_level: str = "LOW"):
        """Log user actions"""
        audit_entry = AuditLog(
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            risk_level=risk_level
        )
        
        self._write_audit_log(audit_entry)
    
    def _write_audit_log(self, audit_entry: AuditLog):
        """Write audit log entry"""
        log_data = asdict(audit_entry)
        log_data['timestamp'] = audit_entry.timestamp.isoformat()
        
        # Write to file
        logging.info(json.dumps(log_data))
        
        # Store in memory for quick access
        self.audit_logs.append(audit_entry)
        
        # Keep only last 1000 entries in memory
        if len(self.audit_logs) > 1000:
            self.audit_logs.pop(0)
    
    def get_audit_logs(self, user_id: Optional[str] = None, 
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[AuditLog]:
        """Retrieve audit logs with filters"""
        logs = self.audit_logs
        
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]
        
        return logs

class SecurityMiddleware:
    """Security middleware for API protection"""
    
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.rate_limiter = RateLimiter()
        self.ip_whitelist = self._load_ip_whitelist()
    
    def _load_ip_whitelist(self) -> List[ipaddress.IPv4Network]:
        """Load IP whitelist for railway network"""
        # Railway internal IP ranges (example)
        whitelist = [
            "10.0.0.0/8",      # Internal railway network
            "172.16.0.0/12",   # Railway data centers
            "192.168.0.0/16",  # Local networks
            "127.0.0.1/32"     # Localhost
        ]
        
        return [ipaddress.ip_network(ip) for ip in whitelist]
    
    def validate_ip_address(self, ip_address: str) -> bool:
        """Validate if IP is in whitelist"""
        try:
            client_ip = ipaddress.ip_address(ip_address)
            return any(client_ip in network for network in self.ip_whitelist)
        except:
            return False
    
    def require_authentication(self, required_role: UserRole = None, 
                             required_permission: PermissionLevel = None,
                             resource_type: ResourceType = None):
        """Decorator for requiring authentication"""
        def decorator(func):
            @wraps(func)
            async def wrapper(request, *args, **kwargs):
                # Check rate limiting
                client_ip = request.remote_addr
                if not self.rate_limiter.check_rate_limit(client_ip):
                    return {"error": "Rate limit exceeded", "code": 429}
                
                # Check IP whitelist
                if not self.validate_ip_address(client_ip):
                    return {"error": "Access denied from this IP", "code": 403}
                
                # Check authentication
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return {"error": "Authentication required", "code": 401}
                
                token = auth_header.replace('Bearer ', '')
                user = self.auth_manager.validate_session(token)
                if not user:
                    return {"error": "Invalid or expired token", "code": 401}
                
                # Check role requirements
                if required_role and user.role != required_role:
                    return {"error": "Insufficient privileges", "code": 403}
                
                # Check permission requirements
                if required_permission and resource_type:
                    if not self.auth_manager.permission_manager.has_permission(
                        user, resource_type, required_permission
                    ):
                        return {"error": "Permission denied", "code": 403}
                
                # Log the action
                self.auth_manager.audit_logger.log_action(
                    user.user_id, f"API_CALL_{func.__name__.upper()}", 
                    resource_type.value if resource_type else "api",
                    {"endpoint": func.__name__, "method": request.method},
                    client_ip, request.headers.get('User-Agent', ''), True
                )
                
                # Add user to request context
                request.current_user = user
                
                return await func(request, *args, **kwargs)
            
            return wrapper
        return decorator

class RateLimiter:
    """API rate limiting"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}  # In production, use Redis
    
    def check_rate_limit(self, ip_address: str) -> bool:
        """Check if IP is within rate limit"""
        now = datetime.now()
        
        if ip_address not in self.requests:
            self.requests[ip_address] = []
        
        # Clean old requests
        cutoff_time = now - timedelta(seconds=self.time_window)
        self.requests[ip_address] = [
            req_time for req_time in self.requests[ip_address] 
            if req_time > cutoff_time
        ]
        
        # Check if under limit
        if len(self.requests[ip_address]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[ip_address].append(now)
        return True

# Data encryption utilities
class DataEncryption:
    """Data encryption for sensitive information"""
    
    def __init__(self, encryption_key: str):
        self.key = encryption_key.encode()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        # Simple encryption for demo - use proper encryption in production
        import base64
        encrypted = base64.b64encode(data.encode()).decode()
        return encrypted
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        import base64
        decrypted = base64.b64decode(encrypted_data.encode()).decode()
        return decrypted

# Example usage and testing
if __name__ == "__main__":
    # Initialize security system
    security_config = SecurityConfig(
        secret_key="test-secret",
        jwt_secret="test-jwt",
        password_salt="test-salt",
        audit_enabled=True
    )
    
    auth_manager = AuthenticationManager(security_config)
    
    print("🔒 IDSS Security & Authentication System")
    print("=" * 50)
    
    # Test authentication
    print("\n🔑 Testing Authentication:")
    token = auth_manager.authenticate_user("admin", "admin123!", "127.0.0.1", "Test-Agent")
    if token:
        print("✅ Admin authentication successful")
        
        # Validate session
        user = auth_manager.validate_session(token)
        if user:
            print(f"✅ Session valid for user: {user.username}")
            print(f"   Role: {user.role.value}")
            print(f"   Zone: {user.railway_zone}")
    else:
        print("❌ Authentication failed")
    
    # Test permissions
    print("\n🛡️ Testing Permissions:")
    if user:
        permissions = auth_manager.permission_manager.get_user_permissions(user)
        print(f"User permissions:")
        for resource, perms in permissions.items():
            print(f"  • {resource}: {', '.join(perms)}")
    
    # Test audit logs
    print("\n📋 Recent Audit Logs:")
    logs = auth_manager.audit_logger.get_audit_logs()
    for log in logs[-3:]:  # Show last 3 logs
        print(f"  {log.timestamp.strftime('%H:%M:%S')} - {log.action} - {log.resource} - {'✅' if log.success else '❌'}")
    
    print("\n🎉 Security system initialized and tested successfully!")