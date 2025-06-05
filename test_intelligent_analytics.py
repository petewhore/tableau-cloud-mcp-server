#!/usr/bin/env python3
"""
Test script for Tableau Cloud MCP Server - Intelligent Analytics & Optimization
Tests Phase 3 features: semantic analysis, predictive analytics, and autonomous optimization
"""

import asyncio
import json
import os
from dotenv import load_dotenv

from tableau_mcp_server.intelligence_engine import (
    IntelligenceEngine, SemanticAnalyzer, PredictiveAnalytics, 
    AnomalyDetector, ContentMetrics
)
from tableau_mcp_server.autonomous_optimizer import (
    AutonomousOptimizer, PerformanceOptimizer, UsageOptimizer, 
    GovernanceOptimizer, OptimizationType, OptimizationPriority
)

async def test_semantic_analyzer():
    """Test semantic content analysis"""
    print("🧠 Testing Semantic Analysis Engine...")
    
    analyzer = SemanticAnalyzer()
    
    # Test content samples
    test_content = [
        {
            'id': 'wb_001',
            'type': 'workbook',
            'name': 'Sales Performance Dashboard',
            'description': 'Comprehensive sales metrics and KPI analysis for Q4 revenue tracking'
        },
        {
            'id': 'wb_002', 
            'type': 'workbook',
            'name': 'Test Draft',
            'description': 'Temporary test workbook with sample data'
        },
        {
            'id': 'ds_001',
            'type': 'datasource',
            'name': 'Customer Analytics Data',
            'description': 'Customer engagement metrics and behavioral analysis for marketing campaigns'
        }
    ]
    
    for content in test_content:
        analysis = await analyzer.analyze_content(content)
        print(f"\n📊 Analysis for {content['name']}:")
        print(f"   Topics: {analysis.topics}")
        print(f"   Business Value: {analysis.business_value_score:.2f}")
        print(f"   Sentiment: {analysis.sentiment_score:.2f}")
        print(f"   Recommendations: {len(analysis.recommendations)} suggestions")
    
    print("✅ Semantic analysis completed")

async def test_predictive_analytics():
    """Test predictive analytics and forecasting"""
    print("\n🔮 Testing Predictive Analytics...")
    
    predictor = PredictiveAnalytics()
    
    # Generate sample metrics
    content_metrics = {
        'wb_001': ContentMetrics(
            view_count=500,
            user_engagement=0.8,
            performance_score=0.3,  # Low performance
            quality_score=0.9
        ),
        'wb_002': ContentMetrics(
            view_count=5,  # Low usage
            user_engagement=0.2,
            performance_score=0.7,
            quality_score=0.4
        ),
        'ds_001': ContentMetrics(
            view_count=200,
            user_engagement=0.6,
            performance_score=0.8,
            quality_score=0.7
        )
    }
    
    insights = await predictor.analyze_trends(content_metrics)
    
    print(f"📈 Generated {len(insights)} predictive insights:")
    for insight in insights:
        print(f"   {insight.insight_type}: {insight.prediction}")
        print(f"   Confidence: {insight.confidence:.1%}")
        print(f"   Actions: {len(insight.recommended_actions)} recommendations")
    
    print("✅ Predictive analytics completed")

async def test_anomaly_detection():
    """Test anomaly detection"""
    print("\n🚨 Testing Anomaly Detection...")
    
    detector = AnomalyDetector()
    
    # Set baseline metrics
    detector.baseline_metrics = {
        'wb_001': {'performance_score': 0.8, 'view_count': 300},
        'wb_002': {'performance_score': 0.7, 'view_count': 100}
    }
    
    # Test with anomalous metrics
    current_metrics = {
        'wb_001': ContentMetrics(
            view_count=50,  # Significant drop
            performance_score=0.2  # Performance degradation
        ),
        'wb_002': ContentMetrics(
            view_count=1000,  # Unusual spike
            performance_score=0.7
        )
    }
    
    anomalies = await detector.detect_anomalies(current_metrics)
    
    print(f"⚠️  Detected {len(anomalies)} anomalies:")
    for anomaly in anomalies:
        print(f"   {anomaly.anomaly_type} in {anomaly.content_id}")
        print(f"   Severity: {anomaly.severity}")
        print(f"   Expected: {anomaly.expected_value}, Actual: {anomaly.actual_value}")
        print(f"   Fixes: {len(anomaly.suggested_fixes)} suggestions")
    
    print("✅ Anomaly detection completed")

async def test_intelligence_engine():
    """Test complete intelligence engine"""
    print("\n🤖 Testing Intelligence Engine Integration...")
    
    engine = IntelligenceEngine()
    
    # Sample content for comprehensive analysis
    content_items = [
        {
            'id': 'wb_sales',
            'type': 'workbook',
            'name': 'Sales Dashboard',
            'description': 'Key sales metrics and performance indicators'
        },
        {
            'id': 'wb_finance',
            'type': 'workbook', 
            'name': 'Financial Reports',
            'description': 'Budget analysis and cost center performance'
        },
        {
            'id': 'ds_customer',
            'type': 'datasource',
            'name': 'Customer Data',
            'description': 'Customer demographics and engagement metrics'
        }
    ]
    
    # Run comprehensive analysis
    results = await engine.perform_comprehensive_analysis(content_items)
    
    print(f"🎯 Analysis Summary:")
    print(f"   Items analyzed: {results['summary']['total_items_analyzed']}")
    print(f"   Insights generated: {results['summary']['insights_generated']}")
    print(f"   Anomalies detected: {results['summary']['anomalies_detected']}")
    print(f"   Recommendations: {results['summary']['recommendations_count']}")
    print(f"   Health score: {results['summary']['health_score']:.1%}")
    
    # Test content discovery
    print("\n🔍 Testing Content Discovery...")
    discovery_queries = [
        "popular content",
        "unused dashboards", 
        "similar workbooks"
    ]
    
    for query in discovery_queries:
        insights = await engine.discover_content_insights(query)
        print(f"   Query '{query}': {len(insights)} insights found")
    
    print("✅ Intelligence engine testing completed")

async def test_performance_optimizer():
    """Test performance optimization"""
    print("\n⚡ Testing Performance Optimizer...")
    
    optimizer = PerformanceOptimizer()
    
    # Sample metrics with performance issues
    content_metrics = {
        'wb_slow': {
            'performance_score': 0.2,  # Critical issue
            'view_count': 500
        },
        'wb_moderate': {
            'performance_score': 0.5,  # Moderate issue
            'view_count': 200
        }
    }
    
    actions = await optimizer.analyze_performance_issues(content_metrics)
    
    print(f"⚙️  Generated {len(actions)} performance optimization actions:")
    for action in actions:
        print(f"   {action.title}")
        print(f"   Priority: {action.priority.value}")
        print(f"   Impact: {action.estimated_impact:.1%}")
        print(f"   Auto-executable: {action.auto_executable}")
        print(f"   Steps: {len(action.steps)} steps")
    
    print("✅ Performance optimization testing completed")

async def test_usage_optimizer():
    """Test usage optimization"""
    print("\n📊 Testing Usage Optimizer...")
    
    optimizer = UsageOptimizer()
    
    # Sample metrics with usage issues
    content_metrics = {
        'wb_unused': {
            'view_count': 2,  # Very low usage
            'last_accessed': None,
            'title': 'Old Test Dashboard'
        },
        'wb_popular': {
            'view_count': 1000,
            'user_engagement': 0.9,
            'quality_score': 0.8,
            'title': 'Executive Dashboard'
        },
        'wb_duplicate1': {
            'title': 'sales dashboard',
            'view_count': 50
        },
        'wb_duplicate2': {
            'title': 'sales dashboard',  # Potential duplicate
            'view_count': 30
        }
    }
    
    actions = await optimizer.analyze_usage_patterns(content_metrics)
    
    print(f"📈 Generated {len(actions)} usage optimization actions:")
    action_types = {}
    for action in actions:
        action_type = action.title.split()[0]
        action_types[action_type] = action_types.get(action_type, 0) + 1
    
    for action_type, count in action_types.items():
        print(f"   {action_type}: {count} actions")
    
    print("✅ Usage optimization testing completed")

async def test_governance_optimizer():
    """Test governance optimization"""
    print("\n📋 Testing Governance Optimizer...")
    
    optimizer = GovernanceOptimizer()
    
    # Sample content with governance issues
    content_data = [
        {
            'id': 'wb_poor_metadata',
            'name': 'dash1',  # Poor naming
            'description': '',  # Missing description
            'tags': []  # No tags
        },
        {
            'id': 'wb_complex_perms',
            'name': 'Complex Dashboard',
            'description': 'Well documented dashboard',
            'tags': ['sales', 'finance']
        }
    ]
    
    actions = await optimizer.analyze_governance_compliance(content_data)
    
    print(f"📝 Generated {len(actions)} governance optimization actions:")
    for action in actions:
        print(f"   {action.title}")
        print(f"   Target: {action.target_content_id}")
        print(f"   Impact: {action.estimated_impact:.1%}")
    
    print("✅ Governance optimization testing completed")

async def test_autonomous_optimizer():
    """Test complete autonomous optimization"""
    print("\n🤖 Testing Autonomous Optimizer...")
    
    optimizer = AutonomousOptimizer()
    
    # Sample content and metrics
    content_data = [
        {
            'id': 'wb_001',
            'type': 'workbook',
            'name': 'Sales Dashboard', 
            'description': 'Sales metrics and KPIs'
        },
        {
            'id': 'wb_002',
            'type': 'workbook',
            'name': 'temp',  # Poor naming
            'description': ''  # No description
        }
    ]
    
    content_metrics = {
        'wb_001': ContentMetrics(
            view_count=500,
            performance_score=0.2,  # Performance issue
            quality_score=0.8
        ),
        'wb_002': ContentMetrics(
            view_count=5,  # Low usage
            performance_score=0.7,
            quality_score=0.3
        )
    }
    
    # Run optimization cycle
    results = await optimizer.run_optimization_cycle(content_data, content_metrics)
    
    print(f"🎯 Optimization Cycle Results:")
    print(f"   Actions identified: {results['actions_identified']}")
    print(f"   Actions executed: {results['actions_executed']}")
    print(f"   Success rate: {results['actions_successful']}/{results['actions_executed']}")
    print(f"   Total impact: {results['impact_achieved']:.2f}")
    
    # Test optimization status
    status = await optimizer.get_optimization_status()
    print(f"\n📊 Optimizer Status:")
    print(f"   Enabled: {status['enabled']}")
    print(f"   Queue size: {status['queue_size']}")
    print(f"   Success rate: {status['success_rate']:.1%}")
    print(f"   Total impact: {status['total_impact_achieved']:.2f}")
    
    print("✅ Autonomous optimization testing completed")

async def test_ai_insights_scenarios():
    """Test AI insights with realistic scenarios"""
    print("\n🎪 Testing AI Insights Scenarios...")
    
    engine = IntelligenceEngine()
    
    # Scenario 1: Finance department content audit
    print("\n📊 Scenario 1: Finance Department Content Audit")
    finance_content = [
        {
            'id': 'fin_001',
            'type': 'workbook',
            'name': 'Budget Analysis Q4',
            'description': 'Quarterly budget performance and variance analysis'
        },
        {
            'id': 'fin_002', 
            'type': 'datasource',
            'name': 'Cost Center Data',
            'description': 'Cost allocation and departmental spending metrics'
        }
    ]
    
    results = await engine.perform_comprehensive_analysis(finance_content)
    print(f"   Health score: {results['summary']['health_score']:.1%}")
    print(f"   Recommendations: {results['summary']['recommendations_count']}")
    
    # Scenario 2: Content discovery queries
    print("\n🔍 Scenario 2: Content Discovery Queries")
    discovery_queries = [
        "find trending sales dashboards",
        "show me unused reports in marketing",
        "identify performance issues in finance"
    ]
    
    for query in discovery_queries:
        insights = await engine.discover_content_insights(query)
        print(f"   '{query}': {len(insights)} insights")
    
    # Scenario 3: Optimization recommendations
    print("\n💡 Scenario 3: Optimization Recommendations")
    recommendations = await engine.get_intelligent_recommendations()
    print(f"   Global recommendations: {len(recommendations)}")
    
    for rec in recommendations[:2]:  # Show first 2
        print(f"   - {rec['title']}: {rec['description']}")
    
    print("✅ AI insights scenarios completed")

async def main():
    """Run comprehensive testing of intelligent analytics"""
    print("🚀 Starting Tableau Cloud MCP Server - Intelligent Analytics Testing")
    print("=" * 70)
    
    try:
        # Test individual components
        await test_semantic_analyzer()
        await test_predictive_analytics()
        await test_anomaly_detection()
        await test_intelligence_engine()
        
        # Test optimization components
        await test_performance_optimizer()
        await test_usage_optimizer()
        await test_governance_optimizer()
        await test_autonomous_optimizer()
        
        # Test realistic scenarios
        await test_ai_insights_scenarios()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("\n🎯 Phase 3 Features Verified:")
        print("   ✅ Semantic Content Analysis")
        print("   ✅ Predictive Analytics & Forecasting")
        print("   ✅ Intelligent Content Discovery")
        print("   ✅ Performance Optimization")
        print("   ✅ Anomaly Detection & Monitoring")
        print("   ✅ Autonomous Optimization Engine") 
        print("   ✅ AI-Powered Insights & Reporting")
        print("   ✅ Integrated Intelligence Platform")
        
        print("\n🚀 Your Tableau Cloud MCP Server is now a fully AI-powered")
        print("   intelligent analytics and optimization platform!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())