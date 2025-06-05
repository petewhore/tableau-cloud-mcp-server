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
    
    async def list_groups(self) -> str:
        """List all groups in the Tableau Cloud site."""
        self._ensure_connected()
        
        try:
            all_groups, pagination_item = self.server.groups.get()
            
            groups = []
            for group in all_groups:
                groups.append({
                    "id": group.id,
                    "name": group.name,
                    "domain_name": group.domain_name
                })
            
            return json.dumps({"groups": groups, "total_count": len(groups)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to list groups: {str(e)}")
            raise
    
    async def search_workbooks(self, name: Optional[str] = None, project_name: Optional[str] = None, tag: Optional[str] = None, owner_name: Optional[str] = None) -> str:
        """Search for workbooks by various criteria."""
        self._ensure_connected()
        
        try:
            all_workbooks, pagination_item = self.server.workbooks.get()
            
            filtered_workbooks = []
            for workbook in all_workbooks:
                # Apply filters
                if name and name.lower() not in workbook.name.lower():
                    continue
                if project_name and project_name.lower() != workbook.project_name.lower():
                    continue
                if tag and not any(tag.lower() in t.lower() for t in workbook.tags or []):
                    continue
                if owner_name:
                    # Get owner details
                    try:
                        owner = self.server.users.get_by_id(workbook.owner_id)
                        if owner_name.lower() not in owner.name.lower():
                            continue
                    except:
                        continue
                
                filtered_workbooks.append({
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
            
            return json.dumps({"workbooks": filtered_workbooks, "total_count": len(filtered_workbooks)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to search workbooks: {str(e)}")
            raise
    
    async def search_datasources(self, name: Optional[str] = None, project_name: Optional[str] = None, tag: Optional[str] = None, owner_name: Optional[str] = None, datasource_type: Optional[str] = None) -> str:
        """Search for data sources by various criteria."""
        self._ensure_connected()
        
        try:
            all_datasources, pagination_item = self.server.datasources.get()
            
            filtered_datasources = []
            for datasource in all_datasources:
                # Apply filters
                if name and name.lower() not in datasource.name.lower():
                    continue
                if project_name and project_name.lower() != datasource.project_name.lower():
                    continue
                if tag and not any(tag.lower() in t.lower() for t in datasource.tags or []):
                    continue
                if datasource_type and datasource_type.lower() != datasource.datasource_type.lower():
                    continue
                if owner_name:
                    # Get owner details
                    try:
                        owner = self.server.users.get_by_id(datasource.owner_id)
                        if owner_name.lower() not in owner.name.lower():
                            continue
                    except:
                        continue
                
                filtered_datasources.append({
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
            
            return json.dumps({"datasources": filtered_datasources, "total_count": len(filtered_datasources)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to search datasources: {str(e)}")
            raise
    
    async def search_users(self, name: Optional[str] = None, email: Optional[str] = None, site_role: Optional[str] = None) -> str:
        """Search for users by various criteria."""
        self._ensure_connected()
        
        try:
            all_users, pagination_item = self.server.users.get()
            
            filtered_users = []
            for user in all_users:
                # Apply filters
                if name and name.lower() not in user.name.lower():
                    continue
                if email and email.lower() not in (user.email or "").lower():
                    continue
                if site_role and site_role.lower() != user.site_role.lower():
                    continue
                
                filtered_users.append({
                    "id": user.id,
                    "name": user.name,
                    "site_role": user.site_role,
                    "auth_setting": user.auth_setting,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "email": user.email,
                    "domain_name": user.domain_name
                })
            
            return json.dumps({"users": filtered_users, "total_count": len(filtered_users)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to search users: {str(e)}")
            raise
    
    async def search_projects(self, name: Optional[str] = None, description: Optional[str] = None) -> str:
        """Search for projects by various criteria."""
        self._ensure_connected()
        
        try:
            all_projects, pagination_item = self.server.projects.get()
            
            filtered_projects = []
            for project in all_projects:
                # Apply filters
                if name and name.lower() not in project.name.lower():
                    continue
                if description and description.lower() not in (project.description or "").lower():
                    continue
                
                filtered_projects.append({
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": getattr(project, 'created_at', None),
                    "updated_at": getattr(project, 'updated_at', None),
                    "content_permissions": project.content_permissions,
                    "parent_id": project.parent_id
                })
            
            return json.dumps({"projects": filtered_projects, "total_count": len(filtered_projects)}, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to search projects: {str(e)}")
            raise
    
    async def get_workbook_by_name(self, workbook_name: str, project_name: str) -> str:
        """Get a workbook by name and project."""
        self._ensure_connected()
        
        try:
            all_workbooks, pagination_item = self.server.workbooks.get()
            
            for workbook in all_workbooks:
                if (workbook.name.lower() == workbook_name.lower() and 
                    workbook.project_name.lower() == project_name.lower()):
                    
                    result = {
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
                    }
                    
                    return json.dumps(result, indent=2)
            
            return json.dumps({"error": f"Workbook '{workbook_name}' not found in project '{project_name}'"})
            
        except Exception as e:
            logger.error(f"Failed to get workbook by name: {str(e)}")
            return json.dumps({"error": str(e)}, indent=2)
    
    async def get_datasource_by_name(self, datasource_name: str, project_name: str) -> str:
        """Get a data source by name and project."""
        self._ensure_connected()
        
        try:
            all_datasources, pagination_item = self.server.datasources.get()
            
            for datasource in all_datasources:
                if (datasource.name.lower() == datasource_name.lower() and 
                    datasource.project_name.lower() == project_name.lower()):
                    
                    result = {
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
                    }
                    
                    return json.dumps(result, indent=2)
            
            return json.dumps({"error": f"Data source '{datasource_name}' not found in project '{project_name}'"})
            
        except Exception as e:
            logger.error(f"Failed to get datasource by name: {str(e)}")
            return json.dumps({"error": str(e)}, indent=2)
    
    async def get_user_by_name(self, username: str) -> str:
        """Get a user by name."""
        self._ensure_connected()
        
        try:
            all_users, pagination_item = self.server.users.get()
            
            for user in all_users:
                if user.name.lower() == username.lower():
                    result = {
                        "id": user.id,
                        "name": user.name,
                        "site_role": user.site_role,
                        "auth_setting": user.auth_setting,
                        "last_login": user.last_login.isoformat() if user.last_login else None,
                        "email": user.email,
                        "domain_name": user.domain_name
                    }
                    
                    return json.dumps(result, indent=2)
            
            return json.dumps({"error": f"User '{username}' not found"})
            
        except Exception as e:
            logger.error(f"Failed to get user by name: {str(e)}")
            return json.dumps({"error": str(e)}, indent=2)
    
    async def get_project_by_name(self, project_name: str) -> str:
        """Get a project by name."""
        self._ensure_connected()
        
        try:
            all_projects, pagination_item = self.server.projects.get()
            
            for project in all_projects:
                if project.name.lower() == project_name.lower():
                    result = {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "created_at": getattr(project, 'created_at', None),
                        "updated_at": getattr(project, 'updated_at', None),
                        "content_permissions": project.content_permissions,
                        "parent_id": project.parent_id
                    }
                    
                    return json.dumps(result, indent=2)
            
            return json.dumps({"error": f"Project '{project_name}' not found"})
            
        except Exception as e:
            logger.error(f"Failed to get project by name: {str(e)}")
            return json.dumps({"error": str(e)}, indent=2)
    
    async def update_user_enhanced(self, user_id: Optional[str] = None, username: Optional[str] = None, site_role: Optional[str] = None, auth_setting: Optional[str] = None) -> str:
        """Update an existing user's properties with enhanced name support."""
        self._ensure_connected()
        
        if not user_id and not username:
            return json.dumps({"success": False, "error": "Either user_id or username must be provided"})
        
        try:
            # Get user by name if needed
            if not user_id and username:
                all_users, _ = self.server.users.get()
                for user in all_users:
                    if user.name.lower() == username.lower():
                        user_id = user.id
                        break
                
                if not user_id:
                    return json.dumps({"success": False, "error": f"User '{username}' not found"})
            
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
    
    async def delete_user_enhanced(self, user_id: Optional[str] = None, username: Optional[str] = None) -> str:
        """Delete a user from Tableau Cloud with enhanced name support."""
        self._ensure_connected()
        
        if not user_id and not username:
            return json.dumps({"success": False, "error": "Either user_id or username must be provided"})
        
        try:
            # Get user by name if needed
            if not user_id and username:
                all_users, _ = self.server.users.get()
                for user in all_users:
                    if user.name.lower() == username.lower():
                        user_id = user.id
                        break
                
                if not user_id:
                    return json.dumps({"success": False, "error": f"User '{username}' not found"})
            
            self.server.users.remove(user_id)
            
            result = {
                "success": True,
                "message": f"User deleted successfully"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
    
    async def move_workbook_enhanced(self, workbook_id: Optional[str] = None, workbook_name: Optional[str] = None, current_project_name: Optional[str] = None, target_project_id: Optional[str] = None, target_project_name: Optional[str] = None) -> str:
        """Move a workbook to a different project with enhanced name support."""
        self._ensure_connected()
        
        try:
            # Resolve workbook ID if needed
            if not workbook_id:
                if not workbook_name or not current_project_name:
                    return json.dumps({"success": False, "error": "Either workbook_id or both workbook_name and current_project_name must be provided"})
                
                all_workbooks, _ = self.server.workbooks.get()
                for workbook in all_workbooks:
                    if (workbook.name.lower() == workbook_name.lower() and 
                        workbook.project_name.lower() == current_project_name.lower()):
                        workbook_id = workbook.id
                        break
                
                if not workbook_id:
                    return json.dumps({"success": False, "error": f"Workbook '{workbook_name}' not found in project '{current_project_name}'"})
            
            # Resolve target project ID if needed
            if not target_project_id:
                if not target_project_name:
                    return json.dumps({"success": False, "error": "Either target_project_id or target_project_name must be provided"})
                
                all_projects, _ = self.server.projects.get()
                for project in all_projects:
                    if project.name.lower() == target_project_name.lower():
                        target_project_id = project.id
                        break
                
                if not target_project_id:
                    return json.dumps({"success": False, "error": f"Target project '{target_project_name}' not found"})
            
            # Move the workbook
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
    
    async def move_datasource_enhanced(self, datasource_id: Optional[str] = None, datasource_name: Optional[str] = None, current_project_name: Optional[str] = None, target_project_id: Optional[str] = None, target_project_name: Optional[str] = None) -> str:
        """Move a data source to a different project with enhanced name support."""
        self._ensure_connected()
        
        try:
            # Resolve datasource ID if needed
            if not datasource_id:
                if not datasource_name or not current_project_name:
                    return json.dumps({"success": False, "error": "Either datasource_id or both datasource_name and current_project_name must be provided"})
                
                all_datasources, _ = self.server.datasources.get()
                for datasource in all_datasources:
                    if (datasource.name.lower() == datasource_name.lower() and 
                        datasource.project_name.lower() == current_project_name.lower()):
                        datasource_id = datasource.id
                        break
                
                if not datasource_id:
                    return json.dumps({"success": False, "error": f"Data source '{datasource_name}' not found in project '{current_project_name}'"})
            
            # Resolve target project ID if needed
            if not target_project_id:
                if not target_project_name:
                    return json.dumps({"success": False, "error": "Either target_project_id or target_project_name must be provided"})
                
                all_projects, _ = self.server.projects.get()
                for project in all_projects:
                    if project.name.lower() == target_project_name.lower():
                        target_project_id = project.id
                        break
                
                if not target_project_id:
                    return json.dumps({"success": False, "error": f"Target project '{target_project_name}' not found"})
            
            # Move the datasource
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