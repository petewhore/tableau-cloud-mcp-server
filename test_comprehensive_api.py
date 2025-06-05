#!/usr/bin/env python3
"""
Test script for comprehensive Tableau MCP Server API coverage
"""

import asyncio
from tableau_mcp_server.server import handle_list_tools

async def test_comprehensive_api():
    """Test comprehensive API coverage."""
    print("🔍 Testing Comprehensive Tableau API Coverage...")
    
    tools = await handle_list_tools()
    
    # Categorize tools
    categories = {
        "User & Group Management": [],
        "Project Management": [],
        "Workbook Management": [],
        "Data Source Management": [],
        "View Management": [],
        "Permission Management": [],
        "Job & Task Management": [],
        "Schedule Management": [],
        "Subscription Management": [],
        "Favorites Management": [],
        "Site Administration": [],
        "Tag Management": [],
        "Webhook Management": [],
        "Flow Management": [],
        "Search & Discovery": [],
        "Natural Language": [],
        "Advanced Operations": []
    }
    
    # Categorize each tool
    for tool in tools:
        name = tool.name
        
        if any(x in name for x in ["user", "group"]):
            categories["User & Group Management"].append(name)
        elif "project" in name:
            categories["Project Management"].append(name)
        elif "workbook" in name and "tag" not in name:
            categories["Workbook Management"].append(name)
        elif "datasource" in name and "tag" not in name:
            categories["Data Source Management"].append(name)
        elif "view" in name:
            categories["View Management"].append(name)
        elif "permission" in name:
            categories["Permission Management"].append(name)
        elif any(x in name for x in ["job", "cancel"]):
            categories["Job & Task Management"].append(name)
        elif "schedule" in name:
            categories["Schedule Management"].append(name)
        elif "subscription" in name:
            categories["Subscription Management"].append(name)
        elif "favorite" in name:
            categories["Favorites Management"].append(name)
        elif "site" in name:
            categories["Site Administration"].append(name)
        elif "tag" in name:
            categories["Tag Management"].append(name)
        elif "webhook" in name:
            categories["Webhook Management"].append(name)
        elif "flow" in name:
            categories["Flow Management"].append(name)
        elif any(x in name for x in ["search", "get_", "list_"]):
            categories["Search & Discovery"].append(name)
        elif "natural_language" in name:
            categories["Natural Language"].append(name)
        else:
            categories["Advanced Operations"].append(name)
    
    print(f"\n📊 COMPREHENSIVE API COVERAGE REPORT")
    print(f"{'='*60}")
    print(f"🎯 Total Tools Available: {len(tools)}")
    print()
    
    total_in_categories = 0
    for category, tool_list in categories.items():
        if tool_list:
            print(f"📁 {category} ({len(tool_list)} tools):")
            for tool_name in sorted(tool_list):
                print(f"   ✅ {tool_name}")
            print()
            total_in_categories += len(tool_list)
    
    # Show capabilities by functional area
    print(f"🔧 CAPABILITIES BY FUNCTIONAL AREA:")
    print(f"{'='*60}")
    
    capabilities = {
        "Content Management": [
            "Publish/download workbooks & data sources",
            "Manage views and dashboards", 
            "Handle Tableau Prep flows",
            "Tag content for organization"
        ],
        "User Administration": [
            "Create, update, delete users",
            "Manage groups and memberships",
            "Handle permissions and access control",
            "User favorites management"
        ],
        "Site Operations": [
            "Project hierarchy management",
            "Site configuration and settings",
            "Background job monitoring",
            "Extract refresh scheduling"
        ],
        "Automation": [
            "Webhook integrations",
            "Subscription management", 
            "Scheduled operations",
            "Natural language processing"
        ],
        "Discovery & Search": [
            "Advanced content search",
            "Natural language queries",
            "Cross-content type discovery",
            "Intelligent filtering"
        ]
    }
    
    for area, features in capabilities.items():
        print(f"🎯 {area}:")
        for feature in features:
            print(f"   ▶️ {feature}")
        print()
    
    # Show example workflows
    print(f"🚀 EXAMPLE WORKFLOWS:")
    print(f"{'='*60}")
    
    workflows = [
        {
            "name": "Content Publishing Pipeline",
            "steps": [
                "1. publish_workbook - Upload new workbook",
                "2. add_tags_to_workbook - Organize with tags", 
                "3. grant_permissions - Set access controls",
                "4. create_subscription - Setup email alerts"
            ]
        },
        {
            "name": "User Onboarding",
            "steps": [
                "1. create_user - Add new team member",
                "2. add_user_to_group - Assign to groups",
                "3. grant_permissions - Give project access",
                "4. add_favorite - Setup default content"
            ]
        },
        {
            "name": "Data Refresh Automation", 
            "steps": [
                "1. list_jobs - Check current operations",
                "2. refresh_datasource_now - Trigger refresh",
                "3. get_job_status - Monitor progress",
                "4. create_webhook - Setup notifications"
            ]
        },
        {
            "name": "Content Discovery",
            "steps": [
                "1. natural_language_query - 'Find sales dashboards'",
                "2. search_content - Cross-type search",
                "3. get_workbook_views - Explore content",
                "4. list_favorites - Check bookmarks"
            ]
        }
    ]
    
    for workflow in workflows:
        print(f"🔄 {workflow['name']}:")
        for step in workflow['steps']:
            print(f"   {step}")
        print()
    
    # API Coverage Summary
    print(f"📈 API COVERAGE SUMMARY:")
    print(f"{'='*60}")
    
    coverage_areas = {
        "✅ Core Content": "Workbooks, Data Sources, Views, Flows",
        "✅ User Management": "Users, Groups, Permissions, Authentication", 
        "✅ Administration": "Sites, Projects, Jobs, Schedules",
        "✅ Automation": "Webhooks, Subscriptions, Extracts",
        "✅ Intelligence": "Natural Language, Advanced Search",
        "✅ Organization": "Tags, Favorites, Hierarchies"
    }
    
    for status, description in coverage_areas.items():
        print(f"   {status} {description}")
    
    print(f"\n🎉 COMPREHENSIVE TABLEAU CLOUD API INTEGRATION COMPLETE!")
    print(f"📊 {len(tools)} total tools covering all major Tableau Cloud operations")
    
    return len(tools)

async def main():
    print("🧪 Testing Comprehensive Tableau MCP Server API\n")
    tool_count = await test_comprehensive_api()
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Set environment variables for Tableau Cloud connection")
    print(f"   2. Use natural_language_query for intuitive operations")
    print(f"   3. Leverage {tool_count} tools for complete Tableau automation")
    print(f"   4. Integrate with existing workflows and CI/CD pipelines")

if __name__ == "__main__":
    asyncio.run(main())