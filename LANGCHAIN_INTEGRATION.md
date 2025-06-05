# LangChain Integration for Tableau MCP Server

## Overview

Your Tableau MCP Server now includes **Phase 1** of LangChain integration, adding natural language query processing capabilities. This allows users to interact with Tableau Cloud using conversational queries instead of requiring specific tool parameters or LUIDs.

## What's New

### 🆕 Natural Language Query Tool
- **Tool Name**: `natural_language_query`
- **Purpose**: Process natural language queries about Tableau content
- **Fallback**: Works without OpenAI API key using pattern matching

### 🔧 Enhanced Capabilities
- **22 total tools** (up from 13 original + 8 search tools + 1 natural language tool)
- **Intelligent query parsing** with regex-based pattern matching
- **Flexible input handling** for names, projects, users, tags, etc.

## Usage Examples

### Basic Natural Language Queries

```json
{
  "tool": "natural_language_query",
  "arguments": {
    "query": "Find sales dashboards"
  }
}
```

```json
{
  "tool": "natural_language_query", 
  "arguments": {
    "query": "Show me workbooks in Finance project"
  }
}
```

```json
{
  "tool": "natural_language_query",
  "arguments": {
    "query": "Get data sources created by john"
  }
}
```

### Supported Query Patterns

#### Workbook Searches
- `"Find sales dashboards"`
- `"Show me workbooks in Finance project"`
- `"Dashboards created by john"`
- `"Workbooks tagged with quarterly"`

#### Data Source Searches  
- `"Customer data sources"`
- `"Postgres datasources in Marketing project"`
- `"Data sources created by admin"`

#### User Searches
- `"Find john doe"`
- `"Users with Creator role"`
- `"Show me john.doe@company.com"`

#### Specific Content Retrieval
- `"Get workbook 'Sales Dashboard' from Finance project"`
- `"Find user john.doe"`
- `"Show me the Analytics project"`

## Configuration

### Without OpenAI (Pattern Matching Only)
The server works out-of-the-box with intelligent pattern matching:

```bash
# No additional configuration needed
# Uses regex-based parsing to understand queries
```

### With OpenAI (Full LLM Support) 
For advanced natural language understanding:

```bash
# Set environment variable
export OPENAI_API_KEY=your_openai_api_key_here

# The server will automatically use GPT-3.5-turbo for query processing
```

## How It Works

### 1. Query Processing Pipeline
```
Natural Language Query → Pattern Matching → Tool Selection → Tableau API → Formatted Response
```

### 2. Intelligence Layers

#### Pattern Matching (Always Available)
- Extracts project names: `"in Finance project"` → `project_name="Finance"`
- Identifies owners: `"created by john"` → `owner_name="john"`
- Recognizes content types: `"workbooks"` → uses workbook search tool
- Parses quoted names: `"'Sales Dashboard'"` → exact name match

#### LLM Enhancement (With OpenAI API Key)
- Advanced natural language understanding
- Context-aware query processing
- Intelligent tool orchestration
- Better error handling and suggestions

### 3. Tool Mapping
```
"Find workbooks" → search_workbooks tool
"Show users" → search_users tool  
"Get specific content" → get_*_by_name tools
"Data sources" → search_datasources tool
```

## Available Tools Summary

### Search & Discovery Tools (8)
1. `search_workbooks` - Search workbooks by name, project, owner, tags
2. `search_datasources` - Search data sources by name, project, owner, type, tags
3. `search_users` - Search users by name, email, site role
4. `search_projects` - Search projects by name, description
5. `get_workbook_by_name` - Get specific workbook by name + project
6. `get_datasource_by_name` - Get specific data source by name + project  
7. `get_user_by_name` - Get specific user by name
8. `get_project_by_name` - Get specific project by name

### Enhanced Management Tools (4)
- `update_user` - Now accepts username OR user_id
- `delete_user` - Now accepts username OR user_id
- `move_workbook` - Now accepts names OR IDs
- `move_datasource` - Now accepts names OR IDs

### Natural Language Interface (1)
- `natural_language_query` - Process conversational queries

### Original Administration Tools (9)
- All original user, project, permission, and group management tools

## Benefits

### ✅ User Experience
- **No more LUID hunting** - Work with familiar names
- **Conversational interface** - Natural language queries
- **Flexible input** - Multiple ways to specify the same content
- **Intelligent parsing** - Understands context and intent

### ✅ Productivity  
- **Faster discovery** - Find content without knowing exact names
- **Reduced cognitive load** - No need to remember tool parameters
- **Error tolerance** - Handles variations in query phrasing
- **Progressive enhancement** - Works better with OpenAI, degrades gracefully without

### ✅ Backwards Compatibility
- **All existing tools work unchanged**
- **ID-based operations still supported**
- **No breaking changes**
- **Gradual adoption possible**

## Example Workflows

### Content Discovery Workflow
```
1. "Find sales dashboards" 
   → Returns list of sales-related workbooks
   
2. "Get workbook 'Q4 Sales Report' from Finance project"
   → Returns specific workbook with LUID
   
3. Use LUID in move_workbook tool to relocate content
```

### User Management Workflow  
```
1. "Find users with Creator role"
   → Returns list of Creator users
   
2. "Get user john.doe"
   → Returns specific user details with LUID
   
3. Use LUID in permission tools for access management
```

## Future Enhancements (Phase 2+)

- **Multi-step workflow automation** 
- **Semantic content search with embeddings**
- **Predictive suggestions and recommendations**
- **Complex conditional operations**
- **Batch operations with safety checks**

## Testing

Run the test suite to verify functionality:

```bash
python test_natural_language_simple.py
```

## Troubleshooting

### Common Issues

1. **"Query processor not initialized"**
   - Ensure TableauCloudClient is properly connected
   - Check environment variables

2. **Pattern matching limitations**
   - Use more specific language: "workbooks in Finance project" vs "Finance stuff"
   - Include quoted names for exact matches: "'Sales Dashboard'"

3. **OpenAI integration issues**
   - Verify OPENAI_API_KEY is set correctly
   - Fallback pattern matching will still work

### Debug Mode
```python
# Enable verbose logging for LangChain agent
query_processor = TableauQueryProcessor(client, openai_api_key, verbose=True)
```

## Summary

🎉 **Phase 1 Complete**: Your Tableau MCP server now supports natural language queries with intelligent pattern matching and optional LLM enhancement. Users can discover and interact with content using conversational language while maintaining full backwards compatibility with existing tools.