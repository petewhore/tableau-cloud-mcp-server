"""
Tableau Cloud MCP Server - Autonomous Optimization Engine
Provides intelligent, automated optimization of Tableau content and operations
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    PERFORMANCE = "performance"
    USAGE = "usage"
    GOVERNANCE = "governance"
    COST = "cost"
    SECURITY = "security"

class OptimizationPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class OptimizationAction:
    """Represents an optimization action to be taken"""
    action_id: str
    action_type: OptimizationType
    priority: OptimizationPriority
    title: str
    description: str
    target_content_id: Optional[str]
    estimated_impact: float  # 0-1 scale
    estimated_effort: str  # low, medium, high
    auto_executable: bool
    preconditions: List[str]
    steps: List[str]
    rollback_plan: List[str]
    success_metrics: List[str]
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    status: str = "pending"  # pending, scheduled, executing, completed, failed, cancelled

@dataclass
class OptimizationResult:
    """Result of an optimization action"""
    action_id: str
    success: bool
    impact_achieved: float
    execution_time: timedelta
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    logs: List[str]
    errors: List[str]
    recommendations: List[str]

class PerformanceOptimizer:
    """Handles performance-related optimizations"""
    
    def __init__(self, tableau_client=None):
        self.tableau_client = tableau_client
        self.performance_thresholds = {
            'extract_refresh_time': 300,  # 5 minutes
            'view_load_time': 10,  # 10 seconds
            'data_freshness': 24,  # 24 hours
            'concurrent_users': 50
        }
    
    async def analyze_performance_issues(self, content_metrics: Dict) -> List[OptimizationAction]:
        """Analyze and create performance optimization actions"""
        actions = []
        
        for content_id, metrics in content_metrics.items():
            performance_score = _get_metric_value(metrics, 'performance_score', 1.0)
            
            if performance_score < 0.3:
                # Critical performance issue
                actions.append(self._create_extract_optimization_action(content_id, metrics))
                actions.append(self._create_calculation_optimization_action(content_id, metrics))
            
            elif performance_score < 0.6:
                # Moderate performance issue
                actions.append(self._create_data_source_optimization_action(content_id, metrics))
        
        return actions
    
    def _create_extract_optimization_action(self, content_id: str, metrics: Dict) -> OptimizationAction:
        """Create extract optimization action"""
        return OptimizationAction(
            action_id=f"extract_opt_{content_id}_{int(datetime.now().timestamp())}",
            action_type=OptimizationType.PERFORMANCE,
            priority=OptimizationPriority.HIGH,
            title="Optimize Data Extract",
            description=f"Optimize data extract for improved performance on {content_id}",
            target_content_id=content_id,
            estimated_impact=0.7,
            estimated_effort="medium",
            auto_executable=True,
            preconditions=[
                "Extract refresh is not currently running",
                "No active users viewing the content",
                "Sufficient storage space available"
            ],
            steps=[
                "Analyze current extract structure and size",
                "Identify unused fields and filters",
                "Create optimized extract with only necessary data",
                "Schedule incremental refresh if applicable",
                "Validate extract functionality"
            ],
            rollback_plan=[
                "Restore previous extract backup",
                "Reset refresh schedule to original",
                "Notify users of any temporary issues"
            ],
            success_metrics=[
                "Extract size reduction > 20%",
                "Refresh time improvement > 30%",
                "View load time improvement > 25%"
            ],
            created_at=datetime.now()
        )
    
    def _create_calculation_optimization_action(self, content_id: str, metrics: Dict) -> OptimizationAction:
        """Create calculation optimization action"""
        return OptimizationAction(
            action_id=f"calc_opt_{content_id}_{int(datetime.now().timestamp())}",
            action_type=OptimizationType.PERFORMANCE,
            priority=OptimizationPriority.MEDIUM,
            title="Optimize Workbook Calculations",
            description=f"Optimize complex calculations in workbook {content_id}",
            target_content_id=content_id,
            estimated_impact=0.5,
            estimated_effort="high",
            auto_executable=False,  # Requires manual review
            preconditions=[
                "Workbook is not currently being edited",
                "Performance baseline has been established"
            ],
            steps=[
                "Download and analyze workbook",
                "Identify complex and inefficient calculations",
                "Suggest optimization alternatives",
                "Create performance test plan",
                "Implement optimized calculations"
            ],
            rollback_plan=[
                "Restore original workbook version",
                "Document calculation changes made"
            ],
            success_metrics=[
                "Query execution time improvement > 40%",
                "Reduced server CPU usage > 20%",
                "Maintained calculation accuracy"
            ],
            created_at=datetime.now()
        )
    
    def _create_data_source_optimization_action(self, content_id: str, metrics: Dict) -> OptimizationAction:
        """Create data source optimization action"""
        return OptimizationAction(
            action_id=f"ds_opt_{content_id}_{int(datetime.now().timestamp())}",
            action_type=OptimizationType.PERFORMANCE,
            priority=OptimizationPriority.MEDIUM,
            title="Optimize Data Source Connection",
            description=f"Optimize data source configuration for {content_id}",
            target_content_id=content_id,
            estimated_impact=0.4,
            estimated_effort="low",
            auto_executable=True,
            preconditions=[
                "Data source is accessible",
                "No dependent workbooks are being refreshed"
            ],
            steps=[
                "Analyze data source connection settings",
                "Review and optimize connection pooling",
                "Implement connection caching if beneficial",
                "Update refresh schedules for optimal times",
                "Test connection performance"
            ],
            rollback_plan=[
                "Restore original connection settings",
                "Reset refresh schedules"
            ],
            success_metrics=[
                "Connection establishment time < 5 seconds",
                "Reduced connection failures > 90%",
                "Improved concurrent user support"
            ],
            created_at=datetime.now()
        )

class UsageOptimizer:
    """Handles usage-related optimizations"""
    
    def __init__(self):
        self.usage_thresholds = {
            'min_views_per_month': 10,
            'inactive_days': 90,
            'duplicate_similarity': 0.8
        }
    
    async def analyze_usage_patterns(self, content_metrics: Dict) -> List[OptimizationAction]:
        """Analyze usage patterns and create optimization actions"""
        actions = []
        
        # Identify unused content
        unused_actions = self._identify_unused_content(content_metrics)
        actions.extend(unused_actions)
        
        # Identify duplicate content
        duplicate_actions = self._identify_duplicate_content(content_metrics)
        actions.extend(duplicate_actions)
        
        # Identify optimization opportunities
        promotion_actions = self._identify_promotion_opportunities(content_metrics)
        actions.extend(promotion_actions)
        
        return actions
    
    def _identify_unused_content(self, content_metrics: Dict) -> List[OptimizationAction]:
        """Identify and create actions for unused content"""
        actions = []
        
        for content_id, metrics in content_metrics.items():
            view_count = _get_metric_value(metrics, 'view_count', 0)
            last_accessed = _get_metric_value(metrics, 'last_accessed', None)
            
            days_since_access = 0
            if last_accessed:
                days_since_access = (datetime.now() - last_accessed).days
            
            if view_count < 5 and days_since_access > 90:
                actions.append(OptimizationAction(
                    action_id=f"archive_{content_id}_{int(datetime.now().timestamp())}",
                    action_type=OptimizationType.USAGE,
                    priority=OptimizationPriority.LOW,
                    title="Archive Unused Content",
                    description=f"Archive rarely used content {content_id}",
                    target_content_id=content_id,
                    estimated_impact=0.2,
                    estimated_effort="low",
                    auto_executable=False,  # Requires approval
                    preconditions=[
                        "Content owner approval obtained",
                        "No scheduled dependencies"
                    ],
                    steps=[
                        "Notify content owner of archival plan",
                        "Export content for backup",
                        "Move to archive project/folder",
                        "Update content permissions",
                        "Document archival reason"
                    ],
                    rollback_plan=[
                        "Restore from archive",
                        "Reset original permissions",
                        "Notify users of restoration"
                    ],
                    success_metrics=[
                        "Storage space freed",
                        "Reduced maintenance overhead",
                        "No user complaints within 30 days"
                    ],
                    created_at=datetime.now()
                ))
        
        return actions
    
    def _identify_duplicate_content(self, content_metrics: Dict) -> List[OptimizationAction]:
        """Identify potential duplicate content"""
        actions = []
        
        # Simplified duplicate detection logic
        # In production, this would use more sophisticated analysis
        content_titles = {}
        for content_id, metrics in content_metrics.items():
            title = _get_metric_value(metrics, 'title', '').lower()
            if title in content_titles:
                # Potential duplicate found
                original_id = content_titles[title]
                actions.append(OptimizationAction(
                    action_id=f"merge_dup_{content_id}_{int(datetime.now().timestamp())}",
                    action_type=OptimizationType.USAGE,
                    priority=OptimizationPriority.MEDIUM,
                    title="Consolidate Duplicate Content",
                    description=f"Merge duplicate content {content_id} with {original_id}",
                    target_content_id=content_id,
                    estimated_impact=0.6,
                    estimated_effort="medium",
                    auto_executable=False,
                    preconditions=[
                        "Content comparison completed",
                        "Stakeholder approval obtained",
                        "Migration plan approved"
                    ],
                    steps=[
                        "Compare content functionality and usage",
                        "Identify best version to keep",
                        "Migrate users and dependencies",
                        "Archive redundant content",
                        "Update documentation and links"
                    ],
                    rollback_plan=[
                        "Restore archived content",
                        "Revert user migrations",
                        "Reset original permissions"
                    ],
                    success_metrics=[
                        "Reduced content count",
                        "Maintained user satisfaction",
                        "Simplified maintenance"
                    ],
                    created_at=datetime.now()
                ))
            else:
                content_titles[title] = content_id
        
        return actions
    
    def _identify_promotion_opportunities(self, content_metrics: Dict) -> List[OptimizationAction]:
        """Identify content that should be promoted"""
        actions = []
        
        for content_id, metrics in content_metrics.items():
            engagement = _get_metric_value(metrics, 'user_engagement', 0)
            quality_score = _get_metric_value(metrics, 'quality_score', 0)
            
            if engagement > 0.8 and quality_score > 0.7:
                actions.append(OptimizationAction(
                    action_id=f"promote_{content_id}_{int(datetime.now().timestamp())}",
                    action_type=OptimizationType.USAGE,
                    priority=OptimizationPriority.LOW,
                    title="Promote High-Quality Content",
                    description=f"Promote high-engagement content {content_id}",
                    target_content_id=content_id,
                    estimated_impact=0.5,
                    estimated_effort="low",
                    auto_executable=True,
                    preconditions=[
                        "Content meets quality standards",
                        "Appropriate permissions configured"
                    ],
                    steps=[
                        "Add to featured content collection",
                        "Share in relevant user groups",
                        "Add to recommendation system",
                        "Update content tags and metadata",
                        "Schedule promotion communications"
                    ],
                    rollback_plan=[
                        "Remove from featured collection",
                        "Reset promotion settings"
                    ],
                    success_metrics=[
                        "Increased view count > 50%",
                        "Higher user satisfaction scores",
                        "Improved content discoverability"
                    ],
                    created_at=datetime.now()
                ))
        
        return actions

class GovernanceOptimizer:
    """Handles governance-related optimizations"""
    
    def __init__(self):
        self.governance_standards = {
            'required_tags': ['department', 'data_source', 'refresh_frequency'],
            'max_permission_groups': 10,
            'naming_convention_pattern': r'^[A-Z][a-zA-Z0-9_-]*$'
        }
    
    async def analyze_governance_compliance(self, content_data: List[Dict]) -> List[OptimizationAction]:
        """Analyze governance compliance and create improvement actions"""
        actions = []
        
        for item in content_data:
            # Check metadata compliance
            metadata_action = self._check_metadata_compliance(item)
            if metadata_action:
                actions.append(metadata_action)
            
            # Check permission complexity
            permission_action = self._check_permission_complexity(item)
            if permission_action:
                actions.append(permission_action)
            
            # Check naming conventions
            naming_action = self._check_naming_conventions(item)
            if naming_action:
                actions.append(naming_action)
        
        return actions
    
    def _check_metadata_compliance(self, item: Dict) -> Optional[OptimizationAction]:
        """Check if content has required metadata"""
        content_id = item.get('id', '')
        tags = item.get('tags', [])
        description = item.get('description', '')
        
        missing_requirements = []
        if not description:
            missing_requirements.append("description")
        if len(tags) < 2:
            missing_requirements.append("sufficient tags")
        
        if missing_requirements:
            return OptimizationAction(
                action_id=f"metadata_{content_id}_{int(datetime.now().timestamp())}",
                action_type=OptimizationType.GOVERNANCE,
                priority=OptimizationPriority.MEDIUM,
                title="Improve Content Metadata",
                description=f"Add missing metadata to {content_id}",
                target_content_id=content_id,
                estimated_impact=0.4,
                estimated_effort="low",
                auto_executable=False,
                preconditions=[
                    "Content owner identified",
                    "Metadata standards defined"
                ],
                steps=[
                    "Contact content owner for information",
                    "Add comprehensive description",
                    "Apply appropriate tags and categories",
                    "Set data lineage information",
                    "Validate metadata completeness"
                ],
                rollback_plan=[
                    "Revert to original metadata",
                    "Document changes made"
                ],
                success_metrics=[
                    "All required metadata fields populated",
                    "Improved content discoverability",
                    "Compliance score > 90%"
                ],
                created_at=datetime.now()
            )
        
        return None
    
    def _check_permission_complexity(self, item: Dict) -> Optional[OptimizationAction]:
        """Check for overly complex permissions"""
        content_id = item.get('id', '')
        # Simulated permission complexity check
        permission_count = hash(content_id) % 15  # Simulate permission count
        
        if permission_count > 10:
            return OptimizationAction(
                action_id=f"perms_{content_id}_{int(datetime.now().timestamp())}",
                action_type=OptimizationType.GOVERNANCE,
                priority=OptimizationPriority.HIGH,
                title="Simplify Content Permissions",
                description=f"Reduce permission complexity for {content_id}",
                target_content_id=content_id,
                estimated_impact=0.6,
                estimated_effort="medium",
                auto_executable=False,
                preconditions=[
                    "Permission audit completed",
                    "Stakeholder approval for changes"
                ],
                steps=[
                    "Audit current permission structure",
                    "Identify redundant or conflicting permissions",
                    "Consolidate into role-based groups",
                    "Test permission changes in staging",
                    "Apply optimized permissions"
                ],
                rollback_plan=[
                    "Restore original permission structure",
                    "Verify user access maintained"
                ],
                success_metrics=[
                    "Permission groups reduced by > 50%",
                    "Maintained appropriate access controls",
                    "Simplified administration overhead"
                ],
                created_at=datetime.now()
            )
        
        return None
    
    def _check_naming_conventions(self, item: Dict) -> Optional[OptimizationAction]:
        """Check naming convention compliance"""
        content_id = item.get('id', '')
        name = item.get('name', '')
        
        # Simple naming convention check
        if not name or len(name) < 3 or ' ' in name[:1]:
            return OptimizationAction(
                action_id=f"naming_{content_id}_{int(datetime.now().timestamp())}",
                action_type=OptimizationType.GOVERNANCE,
                priority=OptimizationPriority.LOW,
                title="Update Naming Convention",
                description=f"Fix naming convention for {content_id}",
                target_content_id=content_id,
                estimated_impact=0.3,
                estimated_effort="low",
                auto_executable=False,
                preconditions=[
                    "New name approved by content owner",
                    "No conflicting names exist"
                ],
                steps=[
                    "Generate suggested compliant names",
                    "Get approval from content owner",
                    "Update content name",
                    "Update any references or links",
                    "Notify users of name change"
                ],
                rollback_plan=[
                    "Revert to original name",
                    "Update references back"
                ],
                success_metrics=[
                    "Name follows naming convention",
                    "No broken references",
                    "User adoption of new name"
                ],
                created_at=datetime.now()
            )
        
        return None

def _get_metric_value(metrics, key: str, default=None):
    """Helper function to get value from metrics object or dict"""
    if hasattr(metrics, key):
        return getattr(metrics, key, default)
    elif hasattr(metrics, 'get'):
        return metrics.get(key, default)
    else:
        return default

class AutonomousOptimizer:
    """Main autonomous optimization engine"""
    
    def __init__(self, tableau_client=None):
        self.tableau_client = tableau_client
        self.performance_optimizer = PerformanceOptimizer(tableau_client)
        self.usage_optimizer = UsageOptimizer()
        self.governance_optimizer = GovernanceOptimizer()
        
        self.optimization_queue: List[OptimizationAction] = []
        self.execution_history: List[OptimizationResult] = []
        self.max_concurrent_optimizations = 3
        self.optimization_enabled = True
    
    async def run_optimization_cycle(self, content_data: List[Dict], content_metrics: Dict) -> Dict[str, Any]:
        """Run a complete optimization cycle"""
        if not self.optimization_enabled:
            return {"status": "disabled", "message": "Optimization engine is disabled"}
        
        cycle_results = {
            'cycle_id': f"opt_cycle_{int(datetime.now().timestamp())}",
            'started_at': datetime.now().isoformat(),
            'actions_identified': 0,
            'actions_executed': 0,
            'actions_successful': 0,
            'impact_achieved': 0.0,
            'optimizations': []
        }
        
        logger.info("Starting optimization cycle")
        
        # Identify optimization opportunities
        all_actions = await self._identify_optimization_opportunities(content_data, content_metrics)
        cycle_results['actions_identified'] = len(all_actions)
        
        # Prioritize and filter actions
        prioritized_actions = self._prioritize_actions(all_actions)
        
        # Execute auto-executable actions
        execution_results = await self._execute_optimizations(prioritized_actions)
        
        cycle_results['actions_executed'] = len(execution_results)
        cycle_results['actions_successful'] = sum(1 for r in execution_results if r.success)
        cycle_results['impact_achieved'] = sum(r.impact_achieved for r in execution_results)
        cycle_results['optimizations'] = [asdict(r) for r in execution_results]
        cycle_results['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"Optimization cycle completed: {cycle_results['actions_successful']}/{cycle_results['actions_executed']} successful")
        
        return cycle_results
    
    async def _identify_optimization_opportunities(self, content_data: List[Dict], 
                                                 content_metrics: Dict) -> List[OptimizationAction]:
        """Identify all optimization opportunities"""
        all_actions = []
        
        # Performance optimizations
        perf_actions = await self.performance_optimizer.analyze_performance_issues(content_metrics)
        all_actions.extend(perf_actions)
        
        # Usage optimizations
        usage_actions = await self.usage_optimizer.analyze_usage_patterns(content_metrics)
        all_actions.extend(usage_actions)
        
        # Governance optimizations
        gov_actions = await self.governance_optimizer.analyze_governance_compliance(content_data)
        all_actions.extend(gov_actions)
        
        return all_actions
    
    def _prioritize_actions(self, actions: List[OptimizationAction]) -> List[OptimizationAction]:
        """Prioritize optimization actions"""
        # Sort by priority and estimated impact
        priority_weights = {
            OptimizationPriority.CRITICAL: 4,
            OptimizationPriority.HIGH: 3,
            OptimizationPriority.MEDIUM: 2,
            OptimizationPriority.LOW: 1
        }
        
        def action_score(action):
            priority_score = priority_weights.get(action.priority, 1)
            impact_score = action.estimated_impact
            return priority_score * 10 + impact_score
        
        return sorted(actions, key=action_score, reverse=True)
    
    async def _execute_optimizations(self, actions: List[OptimizationAction]) -> List[OptimizationResult]:
        """Execute optimization actions"""
        results = []
        executing_count = 0
        
        for action in actions:
            # Limit concurrent executions
            if executing_count >= self.max_concurrent_optimizations:
                break
            
            # Only execute auto-executable actions
            if not action.auto_executable:
                continue
            
            # Check preconditions
            if not await self._check_preconditions(action):
                continue
            
            executing_count += 1
            result = await self._execute_single_optimization(action)
            results.append(result)
            
            # Store in history
            self.execution_history.append(result)
        
        return results
    
    async def _check_preconditions(self, action: OptimizationAction) -> bool:
        """Check if action preconditions are met"""
        # Simplified precondition checking
        # In production, this would verify actual system states
        return True
    
    async def _execute_single_optimization(self, action: OptimizationAction) -> OptimizationResult:
        """Execute a single optimization action"""
        start_time = datetime.now()
        logs = []
        errors = []
        success = False
        impact_achieved = 0.0
        
        try:
            logs.append(f"Starting optimization: {action.title}")
            
            # Simulate optimization execution based on type
            if action.action_type == OptimizationType.PERFORMANCE:
                success, impact_achieved = await self._execute_performance_optimization(action, logs)
            elif action.action_type == OptimizationType.USAGE:
                success, impact_achieved = await self._execute_usage_optimization(action, logs)
            elif action.action_type == OptimizationType.GOVERNANCE:
                success, impact_achieved = await self._execute_governance_optimization(action, logs)
            
            if success:
                logs.append(f"Optimization completed successfully")
                action.status = "completed"
                action.executed_at = datetime.now()
            else:
                logs.append(f"Optimization failed")
                action.status = "failed"
        
        except Exception as e:
            errors.append(f"Execution error: {str(e)}")
            success = False
            action.status = "failed"
        
        execution_time = datetime.now() - start_time
        
        return OptimizationResult(
            action_id=action.action_id,
            success=success,
            impact_achieved=impact_achieved,
            execution_time=execution_time,
            metrics_before={},  # Would capture actual metrics
            metrics_after={},   # Would capture actual metrics
            logs=logs,
            errors=errors,
            recommendations=[]
        )
    
    async def _execute_performance_optimization(self, action: OptimizationAction, 
                                              logs: List[str]) -> Tuple[bool, float]:
        """Execute performance optimization"""
        logs.append("Analyzing performance metrics")
        await asyncio.sleep(0.1)  # Simulate work
        
        logs.append("Applying performance optimizations")
        await asyncio.sleep(0.2)  # Simulate work
        
        # Simulate success with some probability
        import random
        success = random.random() > 0.2  # 80% success rate
        impact = action.estimated_impact * (0.7 + random.random() * 0.3) if success else 0
        
        return success, impact
    
    async def _execute_usage_optimization(self, action: OptimizationAction, 
                                        logs: List[str]) -> Tuple[bool, float]:
        """Execute usage optimization"""
        logs.append("Analyzing usage patterns")
        await asyncio.sleep(0.1)
        
        logs.append("Implementing usage optimizations")
        await asyncio.sleep(0.15)
        
        import random
        success = random.random() > 0.15  # 85% success rate
        impact = action.estimated_impact * (0.8 + random.random() * 0.2) if success else 0
        
        return success, impact
    
    async def _execute_governance_optimization(self, action: OptimizationAction, 
                                             logs: List[str]) -> Tuple[bool, float]:
        """Execute governance optimization"""
        logs.append("Checking governance compliance")
        await asyncio.sleep(0.05)
        
        logs.append("Applying governance improvements")
        await asyncio.sleep(0.1)
        
        import random
        success = random.random() > 0.1  # 90% success rate
        impact = action.estimated_impact * (0.6 + random.random() * 0.4) if success else 0
        
        return success, impact
    
    async def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            'enabled': self.optimization_enabled,
            'queue_size': len(self.optimization_queue),
            'history_count': len(self.execution_history),
            'last_cycle': self.execution_history[-1].action_id if self.execution_history else None,
            'total_impact_achieved': sum(r.impact_achieved for r in self.execution_history),
            'success_rate': len([r for r in self.execution_history if r.success]) / max(1, len(self.execution_history))
        }
    
    def enable_optimization(self):
        """Enable autonomous optimization"""
        self.optimization_enabled = True
        logger.info("Autonomous optimization enabled")
    
    def disable_optimization(self):
        """Disable autonomous optimization"""
        self.optimization_enabled = False
        logger.info("Autonomous optimization disabled")
    
    async def schedule_optimization(self, action: OptimizationAction, scheduled_time: datetime):
        """Schedule an optimization for later execution"""
        action.scheduled_for = scheduled_time
        action.status = "scheduled"
        self.optimization_queue.append(action)
        logger.info(f"Optimization {action.action_id} scheduled for {scheduled_time}")
    
    async def cancel_optimization(self, action_id: str) -> bool:
        """Cancel a scheduled optimization"""
        for action in self.optimization_queue:
            if action.action_id == action_id:
                action.status = "cancelled"
                self.optimization_queue.remove(action)
                logger.info(f"Optimization {action_id} cancelled")
                return True
        return False