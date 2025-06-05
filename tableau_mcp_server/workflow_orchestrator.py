"""
Workflow Orchestration Engine for Tableau MCP Server

Handles complex multi-step operations with safety checks, progress tracking,
and intelligent error recovery.
"""

import json
import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from .extended_tableau_client import ExtendedTableauCloudClient

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class OperationType(Enum):
    """Types of operations for risk assessment."""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    PUBLISH = "publish"
    REFRESH = "refresh"


@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    id: str
    description: str
    tool_name: str
    arguments: Dict[str, Any]
    operation_type: OperationType
    dependencies: List[str] = None
    rollback_info: Dict[str, Any] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Any = None
    error: str = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class WorkflowPlan:
    """Complete workflow execution plan."""
    id: str
    title: str
    description: str
    steps: List[WorkflowStep]
    estimated_duration: Optional[int] = None
    risk_level: str = "low"
    requires_confirmation: bool = False
    rollback_supported: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def has_destructive_operations(self) -> bool:
        """Check if workflow contains potentially destructive operations."""
        destructive_ops = {OperationType.DELETE, OperationType.MOVE}
        return any(step.operation_type in destructive_ops for step in self.steps)
    
    @property
    def total_steps(self) -> int:
        """Total number of steps in workflow."""
        return len(self.steps)
    
    @property
    def completed_steps(self) -> int:
        """Number of completed steps."""
        return len([s for s in self.steps if s.status == WorkflowStatus.COMPLETED])


class WorkflowIntentParser:
    """Parses natural language requests into structured workflows."""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm
        self.workflow_templates = self._load_workflow_templates()
    
    async def parse_workflow_intent(self, user_request: str) -> WorkflowPlan:
        """Parse a natural language request into a structured workflow."""
        
        # Try to match against known workflow patterns
        template_match = await self._match_workflow_template(user_request)
        
        if template_match:
            return await self._instantiate_template(template_match, user_request)
        
        # Use LLM for complex parsing if available
        if self.llm:
            return await self._llm_parse_workflow(user_request)
        
        # Fall back to pattern-based parsing
        return await self._pattern_parse_workflow(user_request)
    
    async def _llm_parse_workflow(self, user_request: str) -> WorkflowPlan:
        """Use LLM to parse complex workflow requests."""
        # This would use the LLM to understand complex requests
        # For now, fall back to pattern parsing
        return await self._pattern_parse_workflow(user_request)
    
    async def _pattern_parse_workflow(self, user_request: str) -> WorkflowPlan:
        """Simple pattern-based workflow parsing for fallback."""
        request_lower = user_request.lower()
        
        # Create a simple workflow based on keywords
        if any(word in request_lower for word in ["list", "show", "find", "search"]):
            # Read-only operation
            steps = [
                WorkflowStep(
                    id="search_content",
                    description=f"Search for content based on: {user_request}",
                    tool_name="search_workbooks",
                    arguments={"name": ""},
                    operation_type=OperationType.READ
                )
            ]
            
            return WorkflowPlan(
                id=str(uuid.uuid4()),
                title="Content Search",
                description=f"Search operation: {user_request}",
                steps=steps,
                estimated_duration=2,
                risk_level="low",
                requires_confirmation=False
            )
        
        else:
            # Complex operation - create a generic workflow
            steps = [
                WorkflowStep(
                    id="analyze_request",
                    description=f"Analyze request: {user_request}",
                    tool_name="analyze_usage_patterns", 
                    arguments={"request": user_request},
                    operation_type=OperationType.READ
                ),
                WorkflowStep(
                    id="execute_action",
                    description="Execute the requested action",
                    tool_name="request_user_confirmation",
                    arguments={"action": "generic", "items": []},
                    operation_type=OperationType.UPDATE,
                    dependencies=["analyze_request"]
                )
            ]
            
            return WorkflowPlan(
                id=str(uuid.uuid4()),
                title="Generic Workflow",
                description=f"Process request: {user_request}",
                steps=steps,
                estimated_duration=10,
                risk_level="medium",
                requires_confirmation=True
            )
    
    async def _match_workflow_template(self, request: str) -> Optional[Dict]:
        """Match request against known workflow templates."""
        request_lower = request.lower()
        
        # Content cleanup workflow
        cleanup_patterns = [
            "clean up", "cleanup", "archive old", "remove unused", 
            "organize content", "tidy up"
        ]
        if any(pattern in request_lower for pattern in cleanup_patterns):
            return {
                "template": "content_cleanup",
                "project": self._extract_project_name(request),
                "criteria": self._extract_cleanup_criteria(request)
            }
        
        # User migration workflow
        migration_patterns = [
            "migrate", "transfer", "move user", "reassign", 
            "user leaving", "offboard"
        ]
        if any(pattern in request_lower for pattern in migration_patterns):
            return {
                "template": "user_migration",
                "user": self._extract_username(request),
                "target_user": self._extract_target_user(request)
            }
        
        # Permission audit workflow
        audit_patterns = [
            "audit", "review permissions", "check access", 
            "security review", "compliance check"
        ]
        if any(pattern in request_lower for pattern in audit_patterns):
            return {
                "template": "permission_audit",
                "scope": self._extract_audit_scope(request)
            }
        
        return None
    
    async def _instantiate_template(self, template_match: Dict, request: str) -> WorkflowPlan:
        """Create workflow plan from template."""
        template_type = template_match["template"]
        
        if template_type == "content_cleanup":
            return await self._create_cleanup_workflow(template_match, request)
        elif template_type == "user_migration":
            return await self._create_migration_workflow(template_match, request)
        elif template_type == "permission_audit":
            return await self._create_audit_workflow(template_match, request)
        
        raise ValueError(f"Unknown template type: {template_type}")
    
    async def _create_audit_workflow(self, template_match: Dict, request: str) -> WorkflowPlan:
        """Create permission audit workflow."""
        scope = template_match.get("scope", {"target": "all"})
        
        steps = [
            WorkflowStep(
                id="identify_content",
                description="Identify content for audit",
                tool_name="search_workbooks",
                arguments={"project_name": "all"},
                operation_type=OperationType.READ
            ),
            WorkflowStep(
                id="analyze_permissions",
                description="Analyze current permissions",
                tool_name="list_content_permissions",
                arguments={"content_type": "workbook"},
                operation_type=OperationType.READ,
                dependencies=["identify_content"]
            )
        ]
        
        return WorkflowPlan(
            id=str(uuid.uuid4()),
            title="Permission Audit",
            description=f"Audit permissions: {request}",
            steps=steps,
            estimated_duration=20,
            risk_level="low",
            requires_confirmation=False
        )
    
    async def _create_cleanup_workflow(self, template_match: Dict, request: str) -> WorkflowPlan:
        """Create content cleanup workflow."""
        project = template_match.get("project", "all projects")
        
        steps = [
            WorkflowStep(
                id="analyze_content",
                description=f"Analyze content in {project} for cleanup opportunities",
                tool_name="search_workbooks",
                arguments={"project_name": project} if project != "all projects" else {},
                operation_type=OperationType.READ
            ),
            WorkflowStep(
                id="identify_candidates",
                description="Identify unused or old content for archival",
                tool_name="analyze_usage_patterns",
                arguments={"days_threshold": 90},
                operation_type=OperationType.READ,
                dependencies=["analyze_content"]
            ),
            WorkflowStep(
                id="confirm_archival",
                description="Confirm content to be archived",
                tool_name="request_user_confirmation",
                arguments={"action": "archive", "items": "{{identified_candidates}}"},
                operation_type=OperationType.READ,
                dependencies=["identify_candidates"]
            ),
            WorkflowStep(
                id="archive_content",
                description="Move selected content to Archive project",
                tool_name="bulk_move_content",
                arguments={"target_project": "Archive", "items": "{{confirmed_items}}"},
                operation_type=OperationType.MOVE,
                dependencies=["confirm_archival"],
                rollback_info={"action": "restore_from_archive"}
            )
        ]
        
        return WorkflowPlan(
            id=str(uuid.uuid4()),
            title=f"Content Cleanup - {project}",
            description=f"Clean up and organize content in {project}",
            steps=steps,
            estimated_duration=15,
            risk_level="medium",
            requires_confirmation=True,
            rollback_supported=True
        )
    
    async def _create_migration_workflow(self, template_match: Dict, request: str) -> WorkflowPlan:
        """Create user migration workflow."""
        user = template_match.get("user", "unknown_user")
        target_user = template_match.get("target_user")
        
        steps = [
            WorkflowStep(
                id="inventory_content",
                description=f"Inventory all content owned by {user}",
                tool_name="get_user_content",
                arguments={"username": user},
                operation_type=OperationType.READ
            ),
            WorkflowStep(
                id="analyze_importance",
                description="Analyze content importance and usage patterns",
                tool_name="analyze_content_importance",
                arguments={"user": user},
                operation_type=OperationType.READ,
                dependencies=["inventory_content"]
            ),
            WorkflowStep(
                id="plan_migration",
                description="Plan content ownership transfer",
                tool_name="create_migration_plan",
                arguments={"from_user": user, "to_user": target_user},
                operation_type=OperationType.READ,
                dependencies=["analyze_importance"]
            ),
            WorkflowStep(
                id="transfer_ownership",
                description=f"Transfer content ownership from {user}",
                tool_name="bulk_transfer_ownership",
                arguments={"from_user": user, "migration_plan": "{{migration_plan}}"},
                operation_type=OperationType.UPDATE,
                dependencies=["plan_migration"],
                rollback_info={"action": "restore_ownership", "original_user": user}
            ),
            WorkflowStep(
                id="update_permissions",
                description="Update permissions and access controls",
                tool_name="update_user_permissions",
                arguments={"user": user, "action": "revoke_all"},
                operation_type=OperationType.UPDATE,
                dependencies=["transfer_ownership"],
                rollback_info={"action": "restore_permissions"}
            )
        ]
        
        return WorkflowPlan(
            id=str(uuid.uuid4()),
            title=f"User Migration - {user}",
            description=f"Migrate content and permissions for departing user {user}",
            steps=steps,
            estimated_duration=25,
            risk_level="high",
            requires_confirmation=True,
            rollback_supported=True
        )
    
    def _extract_project_name(self, request: str) -> Optional[str]:
        """Extract project name from request."""
        import re
        
        # Look for patterns like "in Finance project", "the Marketing project"
        patterns = [
            r'(?:in|from)\s+(?:the\s+)?(\w+)\s+project',
            r'(\w+)\s+project',
            r'project\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_cleanup_criteria(self, request: str) -> Dict[str, Any]:
        """Extract cleanup criteria from request."""
        criteria = {}
        
        if "old" in request.lower():
            criteria["age_threshold"] = 90
        if "unused" in request.lower():
            criteria["usage_threshold"] = 180
        if "archive" in request.lower():
            criteria["action"] = "archive"
        
        return criteria
    
    def _extract_target_user(self, request: str) -> Optional[str]:
        """Extract target user for migration."""
        import re
        
        patterns = [
            r'to\s+(\w+\.?\w*)',
            r'assign\s+to\s+(\w+\.?\w*)',
            r'transfer\s+to\s+(\w+\.?\w*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "team_lead"  # Default
    
    def _extract_audit_scope(self, request: str) -> Dict[str, Any]:
        """Extract audit scope from request."""
        scope = {"target": "all"}
        
        if "sensitive" in request.lower():
            scope["target"] = "sensitive"
        if "permissions" in request.lower():
            scope["type"] = "permissions"
        if "compliance" in request.lower():
            scope["compliance"] = True
        
        return scope
    
    def _extract_username(self, request: str) -> Optional[str]:
        """Extract username from request."""
        import re
        
        # Look for patterns like "John's content", "user john.doe", "migrate john"
        patterns = [
            r'(\w+\.?\w*)\'s\s+content',
            r'user\s+(\w+\.?\w*)',
            r'migrate\s+(\w+\.?\w*)',
            r'(\w+\.?\w*)\s+leaves?',
            r'(\w+\.?\w*)\s+leaving'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _load_workflow_templates(self) -> Dict[str, Any]:
        """Load predefined workflow templates."""
        return {
            "content_cleanup": {
                "description": "Clean up and organize content",
                "typical_duration": 15,
                "risk_level": "medium"
            },
            "user_migration": {
                "description": "Migrate user content and permissions", 
                "typical_duration": 25,
                "risk_level": "high"
            },
            "permission_audit": {
                "description": "Audit and optimize permissions",
                "typical_duration": 20,
                "risk_level": "low"
            }
        }


class WorkflowValidator:
    """Validates workflows for safety and feasibility."""
    
    def __init__(self, tableau_client: ExtendedTableauCloudClient):
        self.tableau_client = tableau_client
    
    async def validate_workflow(self, workflow: WorkflowPlan) -> Dict[str, Any]:
        """Validate workflow before execution."""
        
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "risk_assessment": await self._assess_risk(workflow),
            "dependency_check": await self._check_dependencies(workflow),
            "resource_check": await self._check_resources(workflow)
        }
        
        # Check for destructive operations
        if workflow.has_destructive_operations:
            validation_result["warnings"].append(
                "Workflow contains potentially destructive operations"
            )
        
        # Validate individual steps
        for step in workflow.steps:
            step_validation = await self._validate_step(step)
            if step_validation["errors"]:
                validation_result["errors"].extend(step_validation["errors"])
                validation_result["valid"] = False
            if step_validation["warnings"]:
                validation_result["warnings"].extend(step_validation["warnings"])
        
        return validation_result
    
    async def _assess_risk(self, workflow: WorkflowPlan) -> Dict[str, Any]:
        """Assess risk level of workflow."""
        risk_factors = []
        risk_score = 0
        
        # Check operation types
        for step in workflow.steps:
            if step.operation_type == OperationType.DELETE:
                risk_factors.append(f"Delete operation: {step.description}")
                risk_score += 3
            elif step.operation_type == OperationType.MOVE:
                risk_factors.append(f"Move operation: {step.description}")
                risk_score += 2
            elif step.operation_type == OperationType.UPDATE:
                risk_score += 1
        
        # Assess impact scope
        if workflow.total_steps > 10:
            risk_factors.append("Large number of operations")
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 8:
            risk_level = "high"
        elif risk_score >= 4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "score": risk_score,
            "level": risk_level,
            "factors": risk_factors,
            "requires_confirmation": risk_score >= 3
        }
    
    async def _validate_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Validate individual workflow step."""
        errors = []
        warnings = []
        
        # Check if tool exists
        if not await self._tool_exists(step.tool_name):
            errors.append(f"Unknown tool: {step.tool_name}")
        
        # Validate arguments
        if step.tool_name in ["move_workbook", "move_datasource"]:
            if "target_project_id" not in step.arguments and "target_project_name" not in step.arguments:
                errors.append(f"Move operation missing target project")
        
        return {"errors": errors, "warnings": warnings}
    
    async def _check_dependencies(self, workflow: WorkflowPlan) -> Dict[str, Any]:
        """Check workflow step dependencies."""
        return {"valid": True, "issues": []}
    
    async def _check_resources(self, workflow: WorkflowPlan) -> Dict[str, Any]:
        """Check resource availability for workflow."""
        return {"available": True, "concerns": []}
    
    async def _tool_exists(self, tool_name: str) -> bool:
        """Check if specified tool exists."""
        # This would check against available tools in the server
        # For now, assume all tools exist
        return True


class WorkflowExecutor:
    """Executes workflows with progress tracking and error handling."""
    
    def __init__(self, tableau_client: ExtendedTableauCloudClient):
        self.tableau_client = tableau_client
        self.active_workflows: Dict[str, WorkflowPlan] = {}
        self.rollback_stack: List[Dict[str, Any]] = []
    
    async def execute_workflow(self, workflow: WorkflowPlan, 
                             progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a workflow with progress tracking."""
        
        workflow.status = WorkflowStatus.IN_PROGRESS
        self.active_workflows[workflow.id] = workflow
        
        try:
            # Execute steps in dependency order
            execution_order = self._resolve_execution_order(workflow.steps)
            
            for step_id in execution_order:
                step = next(s for s in workflow.steps if s.id == step_id)
                
                # Update progress
                if progress_callback:
                    await progress_callback(workflow, step)
                
                # Execute step
                step_result = await self._execute_step(step, workflow)
                
                if step_result["success"]:
                    step.status = WorkflowStatus.COMPLETED
                    step.result = step_result["result"]
                    
                    # Add to rollback stack if supported
                    if step.rollback_info:
                        self.rollback_stack.append({
                            "step": step,
                            "rollback_info": step.rollback_info,
                            "workflow_id": workflow.id
                        })
                else:
                    step.status = WorkflowStatus.FAILED
                    step.error = step_result["error"]
                    
                    # Decide whether to continue or abort
                    if step_result.get("abort_workflow", True):
                        await self._handle_workflow_failure(workflow, step)
                        return {
                            "success": False,
                            "error": f"Workflow failed at step: {step.description}",
                            "failed_step": step.id,
                            "rollback_performed": True
                        }
            
            # Workflow completed successfully
            workflow.status = WorkflowStatus.COMPLETED
            
            return {
                "success": True,
                "workflow_id": workflow.id,
                "completed_steps": workflow.completed_steps,
                "total_steps": workflow.total_steps,
                "execution_summary": self._create_execution_summary(workflow)
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            await self._handle_workflow_failure(workflow, None, str(e))
            return {
                "success": False,
                "error": str(e),
                "rollback_performed": True
            }
        
        finally:
            # Clean up
            if workflow.id in self.active_workflows:
                del self.active_workflows[workflow.id]
    
    async def _execute_step(self, step: WorkflowStep, workflow: WorkflowPlan) -> Dict[str, Any]:
        """Execute individual workflow step."""
        
        try:
            start_time = datetime.now()
            
            # Resolve template variables in arguments
            resolved_args = await self._resolve_template_variables(
                step.arguments, workflow
            )
            
            # Execute the actual tool
            if hasattr(self.tableau_client, step.tool_name):
                tool_method = getattr(self.tableau_client, step.tool_name)
                result = await tool_method(**resolved_args)
            else:
                # Handle special workflow tools
                result = await self._execute_workflow_tool(step.tool_name, resolved_args)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            step.execution_time = execution_time
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Step execution failed: {step.id} - {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "abort_workflow": True
            }
    
    async def _execute_workflow_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute special workflow-specific tools."""
        
        if tool_name == "analyze_usage_patterns":
            return await self._analyze_usage_patterns(arguments)
        elif tool_name == "request_user_confirmation":
            return await self._request_user_confirmation(arguments)
        elif tool_name == "bulk_move_content":
            return await self._bulk_move_content(arguments)
        elif tool_name == "get_user_content":
            return await self._get_user_content(arguments)
        elif tool_name == "analyze_content_importance":
            return await self._analyze_content_importance(arguments)
        elif tool_name == "create_migration_plan":
            return await self._create_migration_plan(arguments)
        elif tool_name == "bulk_transfer_ownership":
            return await self._bulk_transfer_ownership(arguments)
        elif tool_name == "update_user_permissions":
            return await self._update_user_permissions(arguments)
        else:
            raise ValueError(f"Unknown workflow tool: {tool_name}")
    
    async def _analyze_usage_patterns(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content usage patterns to identify cleanup candidates."""
        days_threshold = arguments.get("days_threshold", 90)
        project_name = arguments.get("project_name")
        
        # In a real implementation, this would analyze actual usage data
        # For now, return mock data
        return {
            "analysis_completed": True,
            "days_threshold": days_threshold,
            "candidates": [
                {
                    "id": "wb_123",
                    "name": "Old Sales Report",
                    "type": "workbook",
                    "last_accessed": "2023-06-15",
                    "days_since_access": 120,
                    "owner": "john.doe",
                    "project": project_name or "Sales"
                },
                {
                    "id": "wb_456", 
                    "name": "Quarterly Analysis Backup",
                    "type": "workbook",
                    "last_accessed": "2023-07-20",
                    "days_since_access": 95,
                    "owner": "jane.smith",
                    "project": project_name or "Finance"
                }
            ],
            "total_candidates": 2,
            "estimated_storage_savings": "1.2GB"
        }
    
    async def _request_user_confirmation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Request user confirmation for workflow actions."""
        action = arguments.get("action", "unknown")
        items = arguments.get("items", [])
        
        # In a real implementation, this would present options to the user
        # For demo purposes, auto-confirm non-destructive actions
        auto_confirm = action in ["archive", "move"]
        
        return {
            "confirmation_requested": True,
            "action": action,
            "items_count": len(items) if isinstance(items, list) else 0,
            "auto_confirmed": auto_confirm,
            "confirmed_items": items if auto_confirm else [],
            "message": f"Auto-confirmed {action} action for demo purposes"
        }
    
    async def _bulk_move_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bulk content move operations."""
        target_project = arguments.get("target_project", "Archive")
        items = arguments.get("items", [])
        
        moved_items = []
        failed_items = []
        
        # Simulate moving each item
        for item in items:
            try:
                # In real implementation, would use actual move_workbook/move_datasource
                if item.get("type") == "workbook":
                    # await self.tableau_client.move_workbook_enhanced(...)
                    moved_items.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "type": "workbook",
                        "moved_to": target_project,
                        "status": "success"
                    })
                else:
                    moved_items.append({
                        "id": item.get("id"),
                        "name": item.get("name"), 
                        "type": item.get("type", "unknown"),
                        "moved_to": target_project,
                        "status": "success"
                    })
            except Exception as e:
                failed_items.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "error": str(e)
                })
        
        return {
            "operation": "bulk_move",
            "target_project": target_project,
            "moved_items": moved_items,
            "failed_items": failed_items,
            "success_count": len(moved_items),
            "failure_count": len(failed_items),
            "total_processed": len(items)
        }
    
    async def _get_user_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get all content owned by a specific user."""
        username = arguments.get("username")
        
        # In real implementation, would search across all content types
        # For demo, return mock data
        return {
            "user": username,
            "content_inventory": {
                "workbooks": [
                    {"id": "wb_789", "name": f"{username}'s Dashboard", "project": "Personal"},
                    {"id": "wb_790", "name": f"{username}'s Analysis", "project": "Team Projects"}
                ],
                "datasources": [
                    {"id": "ds_123", "name": f"{username}'s Data Extract", "project": "Personal"}
                ],
                "flows": [],
                "subscriptions": [
                    {"id": "sub_456", "content": "Weekly Sales Report"}
                ]
            },
            "total_items": 4,
            "projects_involved": ["Personal", "Team Projects"],
            "critical_content": 1  # Content with high usage/importance
        }
    
    async def _analyze_content_importance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze importance and usage of user's content."""
        user = arguments.get("user")
        
        return {
            "user": user,
            "importance_analysis": {
                "critical": [
                    {"id": "wb_789", "name": f"{user}'s Dashboard", "reason": "High daily usage by team"}
                ],
                "important": [
                    {"id": "wb_790", "name": f"{user}'s Analysis", "reason": "Referenced by other workbooks"}
                ],
                "low_priority": [
                    {"id": "ds_123", "name": f"{user}'s Data Extract", "reason": "Personal use only"}
                ],
                "obsolete": []
            },
            "recommendations": {
                "transfer_to_team": ["wb_789"],
                "archive": ["ds_123"],
                "requires_documentation": ["wb_790"]
            }
        }
    
    async def _create_migration_plan(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed migration plan for user content."""
        from_user = arguments.get("from_user")
        to_user = arguments.get("to_user", "team_lead")
        
        return {
            "migration_plan": {
                "from_user": from_user,
                "to_user": to_user,
                "transfer_actions": [
                    {
                        "content_id": "wb_789",
                        "content_name": f"{from_user}'s Dashboard",
                        "action": "transfer_ownership",
                        "new_owner": to_user,
                        "notify_stakeholders": True
                    },
                    {
                        "content_id": "wb_790", 
                        "content_name": f"{from_user}'s Analysis",
                        "action": "transfer_ownership",
                        "new_owner": to_user,
                        "add_documentation": True
                    }
                ],
                "archive_actions": [
                    {
                        "content_id": "ds_123",
                        "content_name": f"{from_user}'s Data Extract",
                        "action": "archive",
                        "reason": "Personal use only"
                    }
                ],
                "permission_updates": [
                    {
                        "action": "revoke_all_access",
                        "user": from_user,
                        "exceptions": []  # Content they should retain access to
                    }
                ]
            },
            "estimated_duration": "15 minutes",
            "stakeholder_notifications": 3,
            "reversible": True
        }
    
    async def _bulk_transfer_ownership(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bulk ownership transfer operations."""
        from_user = arguments.get("from_user")
        migration_plan = arguments.get("migration_plan", {})
        
        transferred = []
        failed = []
        
        # Process transfer actions
        for action in migration_plan.get("transfer_actions", []):
            try:
                # In real implementation, would update actual content ownership
                transferred.append({
                    "content_id": action["content_id"],
                    "content_name": action["content_name"],
                    "from_owner": from_user,
                    "to_owner": action["new_owner"],
                    "status": "success"
                })
            except Exception as e:
                failed.append({
                    "content_id": action["content_id"],
                    "error": str(e)
                })
        
        return {
            "operation": "bulk_transfer_ownership",
            "from_user": from_user,
            "transferred": transferred,
            "failed": failed,
            "success_count": len(transferred),
            "failure_count": len(failed),
            "notifications_sent": len([a for a in migration_plan.get("transfer_actions", []) if a.get("notify_stakeholders")])
        }
    
    async def _update_user_permissions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update user permissions across the site."""
        user = arguments.get("user")
        action = arguments.get("action", "revoke_all")
        
        if action == "revoke_all":
            # Simulate revoking all permissions
            revoked_permissions = [
                {"content": "Sales Dashboard", "permission": "View", "project": "Sales"},
                {"content": "Finance Reports", "permission": "Edit", "project": "Finance"},
                {"content": "Team Workspace", "permission": "Owner", "project": "Team Projects"}
            ]
            
            return {
                "operation": "revoke_all_permissions",
                "user": user,
                "revoked_permissions": revoked_permissions,
                "total_revoked": len(revoked_permissions),
                "user_deactivated": True,
                "cleanup_completed": True
            }
        
        return {"operation": action, "user": user, "status": "completed"}
    
    async def _resolve_template_variables(self, arguments: Dict[str, Any], 
                                        workflow: WorkflowPlan) -> Dict[str, Any]:
        """Resolve template variables in step arguments."""
        resolved = {}
        
        for key, value in arguments.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Extract variable name
                var_name = value[2:-2].strip()
                
                # Look for the variable in previous step results
                for step in workflow.steps:
                    if step.status == WorkflowStatus.COMPLETED and step.result:
                        if isinstance(step.result, dict):
                            if var_name in step.result:
                                resolved[key] = step.result[var_name]
                                break
                            # Handle nested lookups like "analysis.candidates"
                            if "." in var_name:
                                parts = var_name.split(".")
                                current = step.result
                                try:
                                    for part in parts:
                                        current = current[part]
                                    resolved[key] = current
                                    break
                                except (KeyError, TypeError):
                                    continue
                
                # If not found, keep original value
                if key not in resolved:
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
    async def _execute_rollback(self, rollback_item: Dict[str, Any]):
        """Execute rollback for a specific operation."""
        step = rollback_item["step"]
        rollback_info = rollback_item["rollback_info"]
        
        rollback_action = rollback_info.get("action")
        
        if rollback_action == "restore_from_archive":
            # Restore content from archive
            logger.info(f"Rolling back: Restoring content for step {step.id}")
            # In real implementation, would move content back to original location
            
        elif rollback_action == "restore_ownership":
            # Restore original ownership
            original_user = rollback_info.get("original_user")
            logger.info(f"Rolling back: Restoring ownership to {original_user}")
            # In real implementation, would transfer ownership back
            
        elif rollback_action == "restore_permissions":
            # Restore original permissions
            logger.info(f"Rolling back: Restoring permissions for step {step.id}")
            # In real implementation, would restore previous permission state
        
        # For demo purposes, just log the rollback
        logger.info(f"Rollback completed for step {step.id}")
    
    def _create_execution_summary(self, workflow: WorkflowPlan) -> Dict[str, Any]:
        """Create summary of workflow execution."""
        return {
            "workflow_title": workflow.title,
            "total_steps": workflow.total_steps,
            "completed_steps": workflow.completed_steps,
            "failed_steps": len([s for s in workflow.steps if s.status == WorkflowStatus.FAILED]),
            "total_execution_time": sum(s.execution_time or 0 for s in workflow.steps),
            "operations_performed": [
                {
                    "step": step.description,
                    "status": step.status.value,
                    "execution_time": step.execution_time
                }
                for step in workflow.steps
            ]
        }
    
    async def _handle_workflow_failure(self, workflow: WorkflowPlan, 
                                     failed_step: Optional[WorkflowStep],
                                     error: Optional[str] = None):
        """Handle workflow failure with rollback."""
        
        workflow.status = WorkflowStatus.FAILED
        
        # Attempt rollback if supported
        if workflow.rollback_supported and self.rollback_stack:
            try:
                await self._rollback_workflow(workflow.id)
                workflow.status = WorkflowStatus.ROLLED_BACK
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {str(rollback_error)}")
    
    async def _rollback_workflow(self, workflow_id: str):
        """Rollback workflow operations."""
        
        # Find rollback operations for this workflow
        workflow_rollbacks = [
            rb for rb in self.rollback_stack 
            if rb["workflow_id"] == workflow_id
        ]
        
        # Execute rollbacks in reverse order
        for rollback_item in reversed(workflow_rollbacks):
            try:
                await self._execute_rollback(rollback_item)
            except Exception as e:
                logger.error(f"Individual rollback failed: {str(e)}")
                # Continue with other rollbacks
        
        # Clear rollback stack for this workflow
        self.rollback_stack = [
            rb for rb in self.rollback_stack 
            if rb["workflow_id"] != workflow_id
        ]
    
    def _resolve_execution_order(self, steps: List[WorkflowStep]) -> List[str]:
        """Resolve step execution order based on dependencies."""
        
        # Simple topological sort
        executed = set()
        execution_order = []
        
        def can_execute(step):
            return all(dep in executed for dep in step.dependencies)
        
        while len(execution_order) < len(steps):
            for step in steps:
                if step.id not in executed and can_execute(step):
                    execution_order.append(step.id)
                    executed.add(step.id)
                    break
            else:
                # Circular dependency or missing dependency
                remaining = [s.id for s in steps if s.id not in executed]
                raise ValueError(f"Cannot resolve execution order for steps: {remaining}")
        
        return execution_order


class WorkflowOrchestrator:
    """Main orchestrator that coordinates all workflow components."""
    
    def __init__(self, tableau_client: ExtendedTableauCloudClient, 
                 openai_api_key: Optional[str] = None):
        self.tableau_client = tableau_client
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4",
            openai_api_key=openai_api_key
        ) if openai_api_key else None
        
        self.intent_parser = WorkflowIntentParser(self.llm)
        self.validator = WorkflowValidator(tableau_client)
        self.executor = WorkflowExecutor(tableau_client)
        
        self.active_workflows: Dict[str, WorkflowPlan] = {}
    
    async def process_workflow_request(self, user_request: str) -> str:
        """Process a complex workflow request from start to finish."""
        
        try:
            # Parse the user's intent into a structured workflow
            workflow = await self.intent_parser.parse_workflow_intent(user_request)
            
            # Validate the workflow for safety and feasibility
            validation = await self.validator.validate_workflow(workflow)
            
            if not validation["valid"]:
                return json.dumps({
                    "success": False,
                    "error": "Workflow validation failed",
                    "errors": validation["errors"],
                    "warnings": validation["warnings"]
                }, indent=2)
            
            # Check if user confirmation is required
            if workflow.requires_confirmation or validation["risk_assessment"]["requires_confirmation"]:
                # Store workflow for later execution
                self.active_workflows[workflow.id] = workflow
                
                return json.dumps({
                    "success": True,
                    "status": "confirmation_required",
                    "workflow_id": workflow.id,
                    "workflow": {
                        "title": workflow.title,
                        "description": workflow.description,
                        "steps": [
                            {
                                "description": step.description,
                                "operation_type": step.operation_type.value,
                                "risk_level": validation["risk_assessment"]["level"]
                            }
                            for step in workflow.steps
                        ],
                        "estimated_duration": workflow.estimated_duration,
                        "risk_assessment": validation["risk_assessment"]
                    },
                    "message": "This workflow requires confirmation. Review the steps and confirm to proceed."
                }, indent=2)
            
            # Execute workflow immediately
            result = await self.executor.execute_workflow(
                workflow, 
                progress_callback=self._progress_callback
            )
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Workflow processing failed: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    async def confirm_workflow(self, workflow_id: str, confirmed: bool) -> str:
        """Handle workflow confirmation response."""
        
        if workflow_id not in self.active_workflows:
            return json.dumps({
                "success": False,
                "error": "Workflow not found or expired"
            }, indent=2)
        
        workflow = self.active_workflows[workflow_id]
        
        if not confirmed:
            workflow.status = WorkflowStatus.CANCELLED
            del self.active_workflows[workflow_id]
            
            return json.dumps({
                "success": True,
                "status": "cancelled",
                "message": "Workflow cancelled by user"
            }, indent=2)
        
        # Execute the confirmed workflow
        result = await self.executor.execute_workflow(
            workflow,
            progress_callback=self._progress_callback
        )
        
        # Remove from active workflows
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
        
        return json.dumps(result, indent=2)
    
    async def get_workflow_status(self, workflow_id: str) -> str:
        """Get status of an active or completed workflow."""
        
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            
            return json.dumps({
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "progress": {
                    "completed_steps": workflow.completed_steps,
                    "total_steps": workflow.total_steps,
                    "percentage": round((workflow.completed_steps / workflow.total_steps) * 100, 1)
                },
                "current_step": self._get_current_step(workflow),
                "estimated_remaining": self._estimate_remaining_time(workflow)
            }, indent=2)
        
        return json.dumps({
            "success": False,
            "error": "Workflow not found"
        }, indent=2)
    
    async def _progress_callback(self, workflow: WorkflowPlan, current_step: WorkflowStep):
        """Callback for workflow progress updates."""
        logger.info(f"Workflow {workflow.id}: Executing step {current_step.id} - {current_step.description}")
    
    def _get_current_step(self, workflow: WorkflowPlan) -> Optional[Dict[str, Any]]:
        """Get currently executing step."""
        for step in workflow.steps:
            if step.status == WorkflowStatus.IN_PROGRESS:
                return {
                    "id": step.id,
                    "description": step.description,
                    "operation_type": step.operation_type.value
                }
        return None
    
    def _estimate_remaining_time(self, workflow: WorkflowPlan) -> Optional[int]:
        """Estimate remaining execution time in minutes."""
        if workflow.estimated_duration:
            progress_ratio = workflow.completed_steps / workflow.total_steps
            return int(workflow.estimated_duration * (1 - progress_ratio))
        return None