"""
LangChain integration for Tableau MCP Server

Provides natural language query processing and intelligent tool routing.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .tableau_client import TableauCloudClient


class TableauTool(BaseTool):
    """Base LangChain tool wrapper for Tableau operations."""
    
    tableau_client: Any = Field(description="Tableau client instance")
    
    class Config:
        arbitrary_types_allowed = True


class SearchWorkbooksTool(TableauTool):
    """Search workbooks with natural language support."""
    
    name: str = "search_workbooks"
    description: str = """
    Search for workbooks in Tableau Cloud. Can handle:
    - Workbook names (exact or partial matches)
    - Project names to filter by
    - Owner names to filter by
    - Tags to filter by
    
    Example inputs:
    - "sales dashboards"
    - "workbooks in finance project"
    - "dashboards created by john"
    """
    
    def _run(self, query: str) -> str:
        """Execute workbook search based on parsed query."""
        parsed = self._parse_search_query(query)
        return self.tableau_client.search_workbooks(
            name=parsed.get('name'),
            project_name=parsed.get('project'),
            owner_name=parsed.get('owner'),
            tag=parsed.get('tag')
        )
    
    def _parse_search_query(self, query: str) -> Dict[str, Optional[str]]:
        """Parse natural language search query."""
        query_lower = query.lower()
        parsed = {}
        
        # Extract project references
        project_patterns = [
            r'(?:in|from) (?:the )?(\w+) project',
            r'project (?:named )?["\']?([^"\']+)["\']?',
        ]
        for pattern in project_patterns:
            match = re.search(pattern, query_lower)
            if match:
                parsed['project'] = match.group(1)
                break
        
        # Extract owner references
        owner_patterns = [
            r'(?:by|from|created by|owned by) (\w+)',
            r'(\w+)\'s (?:workbooks?|dashboards?)',
        ]
        for pattern in owner_patterns:
            match = re.search(pattern, query_lower)
            if match:
                parsed['owner'] = match.group(1)
                break
        
        # Extract tag references
        tag_patterns = [
            r'tagged (?:with )?["\']?([^"\']+)["\']?',
            r'tag[:\s]+["\']?([^"\']+)["\']?',
        ]
        for pattern in tag_patterns:
            match = re.search(pattern, query_lower)
            if match:
                parsed['tag'] = match.group(1)
                break
        
        # Extract name (everything else, cleaned up)
        name = query_lower
        # Remove parsed elements
        for key, value in parsed.items():
            if value:
                name = re.sub(rf'\b{re.escape(value.lower())}\b', '', name)
        
        # Clean up common words and patterns
        name = re.sub(r'\b(?:workbooks?|dashboards?|in|from|by|created|owned|the|project|tagged|with|tag)\b', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        if name and len(name) > 1:
            parsed['name'] = name
        
        return parsed


class SearchDatasourcesTool(TableauTool):
    """Search data sources with natural language support."""
    
    name: str = "search_datasources"
    description: str = """
    Search for data sources in Tableau Cloud. Can handle:
    - Data source names (exact or partial matches)
    - Project names to filter by
    - Owner names to filter by
    - Data source types to filter by
    - Tags to filter by
    """
    
    def _run(self, query: str) -> str:
        parsed = self._parse_search_query(query)
        return self.tableau_client.search_datasources(
            name=parsed.get('name'),
            project_name=parsed.get('project'),
            owner_name=parsed.get('owner'),
            datasource_type=parsed.get('type'),
            tag=parsed.get('tag')
        )
    
    def _parse_search_query(self, query: str) -> Dict[str, Optional[str]]:
        """Parse natural language search query for data sources."""
        query_lower = query.lower()
        parsed = {}
        
        # Similar parsing logic as workbooks but for data sources
        # Extract project references
        project_match = re.search(r'(?:in|from) (?:the )?(\w+) project', query_lower)
        if project_match:
            parsed['project'] = project_match.group(1)
        
        # Extract owner references
        owner_match = re.search(r'(?:by|from|created by|owned by) (\w+)', query_lower)
        if owner_match:
            parsed['owner'] = owner_match.group(1)
        
        # Extract type references
        type_patterns = [
            r'(?:type|kind) (?:of )?(\w+)',
            r'(\w+) (?:data sources?|datasources?)',
        ]
        for pattern in type_patterns:
            type_match = re.search(pattern, query_lower)
            if type_match:
                parsed['type'] = type_match.group(1)
                break
        
        # Extract name
        name = query_lower
        for key, value in parsed.items():
            if value:
                name = re.sub(rf'\b{re.escape(value.lower())}\b', '', name)
        
        name = re.sub(r'\b(?:data\s*sources?|datasources?|in|from|by|created|owned|the|project|type|kind|of)\b', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        if name and len(name) > 1:
            parsed['name'] = name
        
        return parsed


class SearchUsersTool(TableauTool):
    """Search users with natural language support."""
    
    name: str = "search_users"
    description: str = """
    Search for users in Tableau Cloud. Can handle:
    - User names (exact or partial matches)
    - Email addresses
    - Site roles (Creator, Explorer, Viewer, etc.)
    """
    
    def _run(self, query: str) -> str:
        parsed = self._parse_search_query(query)
        return self.tableau_client.search_users(
            name=parsed.get('name'),
            email=parsed.get('email'),
            site_role=parsed.get('site_role')
        )
    
    def _parse_search_query(self, query: str) -> Dict[str, Optional[str]]:
        """Parse natural language search query for users."""
        query_lower = query.lower()
        parsed = {}
        
        # Extract email references
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', query)
        if email_match:
            parsed['email'] = email_match.group(1)
        
        # Extract role references
        role_patterns = [
            r'(?:with |role |site role )?(creator|explorer|viewer|siteadministrator)',
            r'(creator|explorer|viewer|admin)s?',
        ]
        for pattern in role_patterns:
            role_match = re.search(pattern, query_lower)
            if role_match:
                role = role_match.group(1)
                if role == 'admin':
                    role = 'SiteAdministratorCreator'
                parsed['site_role'] = role.capitalize()
                break
        
        # Extract name
        name = query_lower
        if parsed.get('email'):
            name = name.replace(parsed['email'].lower(), '')
        if parsed.get('site_role'):
            name = re.sub(rf'\b{re.escape(parsed["site_role"].lower())}\b', '', name)
        
        name = re.sub(r'\b(?:users?|with|role|site|creators?|explorers?|viewers?|admins?)\b', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        if name and len(name) > 1:
            parsed['name'] = name
        
        return parsed


class GetContentByNameTool(TableauTool):
    """Get specific content by name with natural language support."""
    
    name: str = "get_content_by_name"
    description: str = """
    Get specific workbook, data source, user, or project by name. Can handle:
    - "get workbook 'Sales Dashboard' from Finance project"
    - "find user john.doe"
    - "show me the Analytics project"
    - "get data source 'Customer DB' from Marketing project"
    """
    
    def _run(self, query: str) -> str:
        parsed = self._parse_content_query(query)
        
        if parsed['type'] == 'workbook':
            return self.tableau_client.get_workbook_by_name(
                workbook_name=parsed['name'],
                project_name=parsed['project']
            )
        elif parsed['type'] == 'datasource':
            return self.tableau_client.get_datasource_by_name(
                datasource_name=parsed['name'],
                project_name=parsed['project']
            )
        elif parsed['type'] == 'user':
            return self.tableau_client.get_user_by_name(username=parsed['name'])
        elif parsed['type'] == 'project':
            return self.tableau_client.get_project_by_name(project_name=parsed['name'])
        else:
            return json.dumps({"error": f"Could not determine content type from query: {query}"})
    
    def _parse_content_query(self, query: str) -> Dict[str, str]:
        """Parse query to extract content type, name, and project."""
        query_lower = query.lower()
        parsed = {'type': '', 'name': '', 'project': ''}
        
        # Determine content type
        if any(word in query_lower for word in ['workbook', 'dashboard']):
            parsed['type'] = 'workbook'
        elif any(word in query_lower for word in ['datasource', 'data source']):
            parsed['type'] = 'datasource'
        elif 'user' in query_lower:
            parsed['type'] = 'user'
        elif 'project' in query_lower:
            parsed['type'] = 'project'
        
        # Extract quoted names
        quoted_match = re.search(r'["\']([^"\']+)["\']', query)
        if quoted_match:
            parsed['name'] = quoted_match.group(1)
        
        # Extract project if workbook or datasource
        if parsed['type'] in ['workbook', 'datasource']:
            project_match = re.search(r'(?:from|in) (?:the )?(\w+) project', query_lower)
            if project_match:
                parsed['project'] = project_match.group(1)
        
        return parsed


class TableauQueryProcessor:
    """Main class for processing natural language queries about Tableau."""
    
    def __init__(self, tableau_client: TableauCloudClient, openai_api_key: Optional[str] = None):
        self.tableau_client = tableau_client
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            openai_api_key=openai_api_key
        ) if openai_api_key else None
        self.tools = self._create_tools()
        self.agent = self._create_agent() if self.llm else None
    
    def _create_tools(self) -> List[BaseTool]:
        """Create LangChain tools from Tableau operations."""
        return [
            SearchWorkbooksTool(tableau_client=self.tableau_client),
            SearchDatasourcesTool(tableau_client=self.tableau_client),
            SearchUsersTool(tableau_client=self.tableau_client),
            GetContentByNameTool(tableau_client=self.tableau_client),
        ]
    
    def _create_agent(self) -> Optional[AgentExecutor]:
        """Create LangChain agent for query processing."""
        if not self.llm:
            return None
        
        prompt = PromptTemplate.from_template("""
You are a Tableau Cloud assistant. You help users find and manage content in their Tableau environment.

Available tools:
{tools}

Guidelines:
- For search queries, use the appropriate search tool
- For specific content requests, use get_content_by_name
- Always provide helpful, formatted responses
- If a query is ambiguous, ask for clarification

User query: {input}

{agent_scratchpad}
        """)
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True
        )
    
    async def process_query(self, query: str) -> str:
        """Process a natural language query about Tableau content."""
        try:
            if self.agent:
                # Use LangChain agent for complex processing
                result = await self.agent.ainvoke({"input": query})
                return result.get("output", "No response generated")
            else:
                # Fallback to simple pattern matching
                return await self._simple_process_query(query)
        
        except Exception as e:
            return json.dumps({
                "error": f"Failed to process query: {str(e)}",
                "suggestion": "Try rephrasing your query or use the specific search tools directly"
            }, indent=2)
    
    async def _simple_process_query(self, query: str) -> str:
        """Simple query processing without LLM (fallback)."""
        query_lower = query.lower()
        
        # Route to appropriate tool based on keywords
        if any(word in query_lower for word in ['workbook', 'dashboard']):
            tool = SearchWorkbooksTool(tableau_client=self.tableau_client)
            return tool._run(query)
        elif any(word in query_lower for word in ['datasource', 'data source']):
            tool = SearchDatasourcesTool(tableau_client=self.tableau_client)
            return tool._run(query)
        elif 'user' in query_lower:
            tool = SearchUsersTool(tableau_client=self.tableau_client)
            return tool._run(query)
        elif any(word in query_lower for word in ['get', 'find', 'show']):
            tool = GetContentByNameTool(tableau_client=self.tableau_client)
            return tool._run(query)
        else:
            return json.dumps({
                "error": "Could not understand the query",
                "suggestion": "Try queries like 'find sales dashboards', 'search users', or 'get workbook Sales Report from Finance project'"
            }, indent=2)


# Example usage and test queries
EXAMPLE_QUERIES = [
    "Find all sales dashboards",
    "Search for workbooks in the Finance project",
    "Show me dashboards created by john",
    "Find data sources tagged with customer",
    "Get all users with Creator role", 
    "Show me the Analytics project",
    "Find workbook 'Q4 Report' in Finance project",
    "Search for unused data sources",
    "Show me john.doe's workbooks",
    "Find all Excel data sources in Marketing project"
]