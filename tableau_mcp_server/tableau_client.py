"""
Tableau Cloud Client

Handles authentication and API operations with Tableau Cloud using the Tableau Server Client library.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import tableauserverclient as TSC

logger = logging.getLogger(__name__)


class TableauCloudClient:
    """Client for interacting with Tableau Cloud via REST API."""
    
    def __init__(self, server_url: str, site_id: str, token_name: str, token_value: str):
        """Initialize the Tableau Cloud client.
        
        Args:
            server_url: Base URL of the Tableau Cloud server
            site_id: Site ID (content URL) for the Tableau Cloud site
            token_name: Personal Access Token name
            token_value: Personal Access Token value
        """
        self.server_url = server_url
        self.site_id = site_id
        self.token_name = token_name
        self.token_value = token_value
        self.server = None
        self.auth = None
        
    async def connect(self) -> None:
        """Establish connection to Tableau Cloud."""
        try:
            self.server = TSC.Server(self.server_url, use_server_version=True)
            self.auth = TSC.PersonalAccessTokenAuth(
                token_name=self.token_name,
                personal_access_token=self.token_value,
                site_id=self.site_id
            )
            
            # Sign in to establish the session
            self.server.auth.sign_in(self.auth)
            logger.info(f"Successfully connected to Tableau Cloud site: {self.site_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Tableau Cloud: {str(e)}")
            raise
            
    def _ensure_connected(self) -> None:
        """Ensure we have an active connection to Tableau Cloud."""
        if not self.server or not self.auth:
            raise RuntimeError("Not connected to Tableau Cloud. Call connect() first.")
    
    async def get_site_info(self) -> str:
        """Get information about the current Tableau Cloud site."""
        self._ensure_connected()
        
        try:
            site_item = self.server.sites.get_by_id(self.server.site_id)
            
            site_info = {
                "id": site_item.id,
                "name": site_item.name,
                "content_url": site_item.content_url,
                "admin_mode": site_item.admin_mode,
                "user_quota": site_item.user_quota,
                "storage_quota": site_item.storage_quota,
                "disable_subscriptions": site_item.disable_subscriptions,
                "subscribe_others_enabled": site_item.subscribe_others_enabled,
                "revision_history_enabled": site_item.revision_history_enabled,
                "revision_limit": site_item.revision_limit
            }
            
            return json.dumps(site_info, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to get site info: {str(e)}")
            raise
    
    async def list_users(self) -> str:
        """List all users in the Tableau Cloud site."""
        self._ensure_connected()
        
        try:
            all_users, pagination_item = self.server.users.get()
            
            users = []
            for user in all_users:
                users.append({
                    "id": user.id,
                    "name": user.name,
                    "site_role": user.site_role,
                    "auth_setting": user.auth_setting,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "email": user.email,
                    "domain_name": user.domain_name
                })
            
            return json.dumps({"users": users, "total_count": len(users)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to list users: {str(e)}")
            raise
    
    async def list_projects(self) -> str:
        """List all projects in the Tableau Cloud site."""
        self._ensure_connected()
        
        try:
            all_projects, pagination_item = self.server.projects.get()
            
            projects = []
            for project in all_projects:
                projects.append({
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": getattr(project, 'created_at', None),
                    "updated_at": getattr(project, 'updated_at', None),
                    "content_permissions": project.content_permissions,
                    "parent_id": project.parent_id
                })
            
            return json.dumps({"projects": projects, "total_count": len(projects)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}")
            raise
    
    async def list_workbooks(self) -> str:
        """List all workbooks in the Tableau Cloud site."""
        self._ensure_connected()
        
        try:
            all_workbooks, pagination_item = self.server.workbooks.get()
            
            workbooks = []
            for workbook in all_workbooks:
                workbooks.append({
                    "id": workbook.id,
                    "name": workbook.name,
                    "content_url": workbook.content_url,
                    "show_tabs": workbook.show_tabs,
                    "size": workbook.size,
                    "created_at": workbook.created_at.isoformat() if workbook.created_at else None,
                    "updated_at": workbook.updated_at.isoformat() if workbook.updated_at else None,
                    "project_id": workbook.project_id,
                    "project_name": workbook.project_name,
                    "owner_id": workbook.owner_id,
                    "tags": list(workbook.tags) if workbook.tags else []
                })
            
            return json.dumps({"workbooks": workbooks, "total_count": len(workbooks)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to list workbooks: {str(e)}")
            raise
    
    async def list_datasources(self) -> str:
        """List all data sources in the Tableau Cloud site."""
        self._ensure_connected()
        
        try:
            all_datasources, pagination_item = self.server.datasources.get()
            
            datasources = []
            for datasource in all_datasources:
                datasources.append({
                    "id": datasource.id,
                    "name": datasource.name,
                    "content_url": datasource.content_url,
                    "type": datasource.datasource_type,
                    "created_at": datasource.created_at.isoformat() if datasource.created_at else None,
                    "updated_at": datasource.updated_at.isoformat() if datasource.updated_at else None,
                    "project_id": datasource.project_id,
                    "project_name": datasource.project_name,
                    "owner_id": datasource.owner_id,
                    "tags": list(datasource.tags) if datasource.tags else [],
                    "use_remote_query_agent": datasource.use_remote_query_agent,
                    "is_certified": datasource.certified
                })
            
            return json.dumps({"datasources": datasources, "total_count": len(datasources)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to list datasources: {str(e)}")
            raise
    
    async def create_user(self, username: str, site_role: str, auth_setting: str = "ServerDefault") -> str:
        """Create a new user in Tableau Cloud."""
        self._ensure_connected()
        
        try:
            new_user = TSC.UserItem(name=username, site_role=site_role, auth_setting=auth_setting)
            created_user = self.server.users.add(new_user)
            
            result = {
                "success": True,
                "user": {
                    "id": created_user.id,
                    "name": created_user.name,
                    "site_role": created_user.site_role,
                    "auth_setting": created_user.auth_setting
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def update_user(self, user_id: str, site_role: Optional[str] = None, auth_setting: Optional[str] = None) -> str:
        """Update an existing user's properties."""
        self._ensure_connected()
        
        try:
            user_item = self.server.users.get_by_id(user_id)
            
            if site_role:
                user_item.site_role = site_role
            if auth_setting:
                user_item.auth_setting = auth_setting
            
            updated_user = self.server.users.update(user_item)
            
            result = {
                "success": True,
                "user": {
                    "id": updated_user.id,
                    "name": updated_user.name,
                    "site_role": updated_user.site_role,
                    "auth_setting": updated_user.auth_setting
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def delete_user(self, user_id: str) -> str:
        """Delete a user from Tableau Cloud."""
        self._ensure_connected()
        
        try:
            self.server.users.remove(user_id)
            
            result = {
                "success": True,
                "message": f"User {user_id} deleted successfully"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def move_workbook(self, workbook_id: str, target_project_id: str) -> str:
        """Move a workbook to a different project."""
        self._ensure_connected()
        
        try:
            workbook = self.server.workbooks.get_by_id(workbook_id)
            workbook.project_id = target_project_id
            
            updated_workbook = self.server.workbooks.update(workbook)
            
            result = {
                "success": True,
                "workbook": {
                    "id": updated_workbook.id,
                    "name": updated_workbook.name,
                    "project_id": updated_workbook.project_id,
                    "project_name": updated_workbook.project_name
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to move workbook: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def move_datasource(self, datasource_id: str, target_project_id: str) -> str:
        """Move a data source to a different project."""
        self._ensure_connected()
        
        try:
            datasource = self.server.datasources.get_by_id(datasource_id)
            datasource.project_id = target_project_id
            
            updated_datasource = self.server.datasources.update(datasource)
            
            result = {
                "success": True,
                "datasource": {
                    "id": updated_datasource.id,
                    "name": updated_datasource.name,
                    "project_id": updated_datasource.project_id,
                    "project_name": updated_datasource.project_name
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to move datasource: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def create_project(self, name: str, description: Optional[str] = None, parent_project_id: Optional[str] = None) -> str:
        """Create a new project in Tableau Cloud."""
        self._ensure_connected()
        
        try:
            new_project = TSC.ProjectItem(
                name=name,
                description=description,
                parent_id=parent_project_id
            )
            
            created_project = self.server.projects.create(new_project)
            
            result = {
                "success": True,
                "project": {
                    "id": created_project.id,
                    "name": created_project.name,
                    "description": created_project.description,
                    "parent_id": created_project.parent_id
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def grant_permissions(self, content_type: str, content_id: str, grantee_type: str, grantee_id: str, permissions: List[str]) -> str:
        """Grant permissions to a user or group for a content item."""
        self._ensure_connected()
        
        try:
            # Create permission rules
            permission_rules = []
            for permission in permissions:
                if grantee_type == "user":
                    grantee = TSC.UserItem()
                    grantee.id = grantee_id
                else:  # group
                    grantee = TSC.GroupItem()
                    grantee.id = grantee_id
                
                rule = TSC.PermissionsRule(grantee=grantee, capabilities={permission: TSC.Permission.Mode.Allow})
                permission_rules.append(rule)
            
            # Apply permissions based on content type
            if content_type == "workbook":
                self.server.workbooks.update_permissions(content_id, permission_rules)
            elif content_type == "datasource":
                self.server.datasources.update_permissions(content_id, permission_rules)
            elif content_type == "project":
                self.server.projects.update_permissions(content_id, permission_rules)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
            
            result = {
                "success": True,
                "message": f"Granted {permissions} permissions to {grantee_type} {grantee_id} on {content_type} {content_id}"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to grant permissions: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def revoke_permissions(self, content_type: str, content_id: str, grantee_type: str, grantee_id: str, permissions: List[str]) -> str:
        """Revoke permissions from a user or group for a content item."""
        self._ensure_connected()
        
        try:
            # Create permission rules for revocation
            permission_rules = []
            for permission in permissions:
                if grantee_type == "user":
                    grantee = TSC.UserItem()
                    grantee.id = grantee_id
                else:  # group
                    grantee = TSC.GroupItem()
                    grantee.id = grantee_id
                
                rule = TSC.PermissionsRule(grantee=grantee, capabilities={permission: TSC.Permission.Mode.Deny})
                permission_rules.append(rule)
            
            # Apply permission revocations based on content type
            if content_type == "workbook":
                self.server.workbooks.update_permissions(content_id, permission_rules)
            elif content_type == "datasource":
                self.server.datasources.update_permissions(content_id, permission_rules)
            elif content_type == "project":
                self.server.projects.update_permissions(content_id, permission_rules)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
            
            result = {
                "success": True,
                "message": f"Revoked {permissions} permissions from {grantee_type} {grantee_id} on {content_type} {content_id}"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to revoke permissions: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def list_content_permissions(self, content_type: str, content_id: str) -> str:
        """List all permissions for a content item."""
        self._ensure_connected()
        
        try:
            if content_type == "workbook":
                permissions = self.server.workbooks.populate_permissions(content_id)
            elif content_type == "datasource":
                permissions = self.server.datasources.populate_permissions(content_id)
            elif content_type == "project":
                permissions = self.server.projects.populate_permissions(content_id)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
            
            permission_list = []
            for rule in permissions:
                grantee_info = {
                    "type": "user" if hasattr(rule.grantee, 'name') else "group",
                    "id": rule.grantee.id,
                    "name": getattr(rule.grantee, 'name', 'Unknown')
                }
                
                capabilities = {}
                for capability, permission in rule.capabilities.items():
                    capabilities[capability] = permission.mode.name
                
                permission_list.append({
                    "grantee": grantee_info,
                    "capabilities": capabilities
                })
            
            result = {
                "content_type": content_type,
                "content_id": content_id,
                "permissions": permission_list
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to list content permissions: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def create_group(self, name: str, domain_name: Optional[str] = None) -> str:
        """Create a new group in Tableau Cloud."""
        self._ensure_connected()
        
        try:
            new_group = TSC.GroupItem(name=name, domain_name=domain_name)
            created_group = self.server.groups.create(new_group)
            
            result = {
                "success": True,
                "group": {
                    "id": created_group.id,
                    "name": created_group.name,
                    "domain_name": created_group.domain_name
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to create group: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def add_user_to_group(self, group_id: str, user_id: str) -> str:
        """Add a user to a group."""
        self._ensure_connected()
        
        try:
            self.server.groups.add_user(group_id, user_id)
            
            result = {
                "success": True,
                "message": f"Added user {user_id} to group {group_id}"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to add user to group: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def remove_user_from_group(self, group_id: str, user_id: str) -> str:
        """Remove a user from a group."""
        self._ensure_connected()
        
        try:
            self.server.groups.remove_user(group_id, user_id)
            
            result = {
                "success": True,
                "message": f"Removed user {user_id} from group {group_id}"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to remove user from group: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)