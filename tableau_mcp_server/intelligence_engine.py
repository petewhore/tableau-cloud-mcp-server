"""
Tableau Cloud MCP Server - Intelligence Engine
Provides AI-powered semantic analysis, predictive analytics, and intelligent insights
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re
import statistics
from abc import ABC, abstractmethod

try:
    from .vizql_data_service import VizQLDataServiceManager, Filter, FilterType
except ImportError:
    # Handle case where VizQL service is not available
    VizQLDataServiceManager = None
    Filter = None
    FilterType = None

logger = logging.getLogger(__name__)

@dataclass
class ContentMetrics:
    """Metrics for content analysis"""
    view_count: int = 0
    user_engagement: float = 0.0
    last_accessed: Optional[datetime] = None
    complexity_score: float = 0.0
    performance_score: float = 0.0
    quality_score: float = 0.0

@dataclass
class SemanticAnalysis:
    """Results of semantic content analysis"""
    content_id: str
    content_type: str
    title: str
    description: Optional[str]
    tags: List[str]
    topics: List[str]
    sentiment_score: float
    readability_score: float
    business_value_score: float
    recommendations: List[str]
    similar_content: List[str]

@dataclass
class PredictiveInsight:
    """Predictive analytics insight"""
    insight_type: str
    confidence: float
    prediction: str
    impact_score: float
    timeframe: str
    recommended_actions: List[str]
    data_points: Dict[str, Any]

@dataclass
class PerformanceAnomaly:
    """Detected performance anomaly"""
    content_id: str
    anomaly_type: str
    severity: str
    detected_at: datetime
    metric_name: str
    expected_value: float
    actual_value: float
    deviation_score: float
    suggested_fixes: List[str]

class SemanticAnalyzer:
    """Semantic content analysis engine"""
    
    def __init__(self):
        self.topic_keywords = {
            'sales': ['revenue', 'profit', 'sales', 'customer', 'deal', 'conversion'],
            'marketing': ['campaign', 'lead', 'brand', 'promotion', 'engagement'],
            'finance': ['budget', 'cost', 'expense', 'investment', 'roi', 'financial'],
            'operations': ['process', 'efficiency', 'productivity', 'workflow', 'operations'],
            'hr': ['employee', 'talent', 'recruitment', 'performance', 'training'],
            'product': ['feature', 'development', 'roadmap', 'user', 'product']
        }
        
        self.quality_indicators = {
            'high': ['kpi', 'metric', 'benchmark', 'target', 'goal'],
            'medium': ['data', 'analysis', 'report', 'dashboard'],
            'low': ['test', 'draft', 'sample', 'temp']
        }
    
    async def analyze_content(self, content_data: Dict[str, Any]) -> SemanticAnalysis:
        """Perform comprehensive semantic analysis of content"""
        
        content_id = content_data.get('id', '')
        content_type = content_data.get('type', 'unknown')
        title = content_data.get('name', '')
        description = content_data.get('description', '')
        
        # Extract and analyze text content
        text_content = f"{title} {description}".lower()
        
        # Identify topics
        topics = self._identify_topics(text_content)
        
        # Generate tags
        tags = self._extract_tags(text_content)
        
        # Calculate sentiment
        sentiment_score = self._calculate_sentiment(text_content)
        
        # Calculate readability
        readability_score = self._calculate_readability(text_content)
        
        # Calculate business value
        business_value_score = self._calculate_business_value(text_content, topics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            content_type, topics, sentiment_score, business_value_score
        )
        
        # Find similar content (placeholder)
        similar_content = []
        
        return SemanticAnalysis(
            content_id=content_id,
            content_type=content_type,
            title=title,
            description=description,
            tags=tags,
            topics=topics,
            sentiment_score=sentiment_score,
            readability_score=readability_score,
            business_value_score=business_value_score,
            recommendations=recommendations,
            similar_content=similar_content
        )
    
    def _identify_topics(self, text: str) -> List[str]:
        """Identify topics in text content"""
        topics = []
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        return topics
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = []
        
        # Extract potential tags from text
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = defaultdict(int)
        
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] += 1
        
        # Get most frequent meaningful words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        tags = [word for word, freq in sorted_words[:10] if freq > 1]
        
        return tags
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score (-1 to 1)"""
        positive_words = ['good', 'great', 'excellent', 'success', 'improve', 'growth']
        negative_words = ['bad', 'poor', 'fail', 'decline', 'problem', 'issue']
        
        words = text.split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (0 to 1)"""
        if not text:
            return 0.0
        
        words = text.split()
        sentences = text.split('.')
        
        if len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Simple readability metric (inverse of complexity)
        readability = max(0, 1 - (avg_words_per_sentence - 15) / 20)
        return min(1.0, max(0.0, readability))
    
    def _calculate_business_value(self, text: str, topics: List[str]) -> float:
        """Calculate business value score"""
        value_score = 0.0
        
        # Topic-based value
        high_value_topics = ['sales', 'finance', 'operations']
        value_score += len([t for t in topics if t in high_value_topics]) * 0.3
        
        # Quality indicators
        for quality, indicators in self.quality_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text)
            if quality == 'high':
                value_score += matches * 0.2
            elif quality == 'medium':
                value_score += matches * 0.1
            else:
                value_score -= matches * 0.1
        
        return min(1.0, max(0.0, value_score))
    
    def _generate_recommendations(self, content_type: str, topics: List[str], 
                                sentiment: float, business_value: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if business_value < 0.3:
            recommendations.append("Consider adding business KPIs and metrics")
        
        if sentiment < -0.2:
            recommendations.append("Review content for negative language")
        
        if not topics:
            recommendations.append("Add descriptive tags and categorization")
        
        if content_type == 'workbook':
            recommendations.append("Ensure charts have clear titles and descriptions")
        elif content_type == 'datasource':
            recommendations.append("Document data lineage and refresh schedules")
        
        return recommendations

class PredictiveAnalytics:
    """Predictive analytics engine"""
    
    def __init__(self):
        self.historical_data = defaultdict(list)
        self.trend_window = 30  # days
    
    async def analyze_trends(self, content_metrics: Dict[str, ContentMetrics]) -> List[PredictiveInsight]:
        """Analyze trends and generate predictions"""
        insights = []
        
        for content_id, metrics in content_metrics.items():
            # Usage trend prediction
            usage_insight = await self._predict_usage_trend(content_id, metrics)
            if usage_insight:
                insights.append(usage_insight)
            
            # Performance prediction
            performance_insight = await self._predict_performance(content_id, metrics)
            if performance_insight:
                insights.append(performance_insight)
        
        return insights
    
    async def _predict_usage_trend(self, content_id: str, metrics: ContentMetrics) -> Optional[PredictiveInsight]:
        """Predict usage trends"""
        if metrics.view_count < 10:
            return None
        
        # Simple trend analysis
        recent_usage = metrics.view_count
        historical_avg = self._get_historical_average(content_id, 'usage')
        
        if recent_usage > historical_avg * 1.5:
            return PredictiveInsight(
                insight_type="usage_surge",
                confidence=0.8,
                prediction="Content usage is trending upward significantly",
                impact_score=0.7,
                timeframe="next_7_days",
                recommended_actions=[
                    "Monitor for capacity needs",
                    "Consider promoting similar content",
                    "Review for optimization opportunities"
                ],
                data_points={"current_usage": recent_usage, "historical_avg": historical_avg}
            )
        elif recent_usage < historical_avg * 0.5:
            return PredictiveInsight(
                insight_type="usage_decline",
                confidence=0.7,
                prediction="Content usage is declining",
                impact_score=0.5,
                timeframe="next_14_days",
                recommended_actions=[
                    "Review content relevance",
                    "Update or refresh content",
                    "Consider archiving if obsolete"
                ],
                data_points={"current_usage": recent_usage, "historical_avg": historical_avg}
            )
        
        return None
    
    async def _predict_performance(self, content_id: str, metrics: ContentMetrics) -> Optional[PredictiveInsight]:
        """Predict performance issues"""
        if metrics.performance_score < 0.3:
            return PredictiveInsight(
                insight_type="performance_risk",
                confidence=0.9,
                prediction="Performance degradation likely within 7 days",
                impact_score=0.8,
                timeframe="next_7_days",
                recommended_actions=[
                    "Optimize data sources",
                    "Review extract refresh schedules",
                    "Consider data source federation"
                ],
                data_points={"performance_score": metrics.performance_score}
            )
        
        return None
    
    def _get_historical_average(self, content_id: str, metric_type: str) -> float:
        """Get historical average for a metric"""
        # Placeholder - would use actual historical data
        return 100.0  # Default average

class AnomalyDetector:
    """Anomaly detection engine"""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.anomaly_threshold = 2.0  # standard deviations
    
    async def detect_anomalies(self, current_metrics: Dict[str, ContentMetrics]) -> List[PerformanceAnomaly]:
        """Detect performance anomalies"""
        anomalies = []
        
        for content_id, metrics in current_metrics.items():
            # Check for performance anomalies
            perf_anomaly = self._check_performance_anomaly(content_id, metrics)
            if perf_anomaly:
                anomalies.append(perf_anomaly)
            
            # Check for usage anomalies
            usage_anomaly = self._check_usage_anomaly(content_id, metrics)
            if usage_anomaly:
                anomalies.append(usage_anomaly)
        
        return anomalies
    
    def _check_performance_anomaly(self, content_id: str, metrics: ContentMetrics) -> Optional[PerformanceAnomaly]:
        """Check for performance anomalies"""
        baseline = self.baseline_metrics.get(content_id, {})
        expected_performance = baseline.get('performance_score', 0.8)
        
        deviation = abs(metrics.performance_score - expected_performance)
        
        if deviation > 0.3:  # Significant deviation
            return PerformanceAnomaly(
                content_id=content_id,
                anomaly_type="performance",
                severity="high" if deviation > 0.5 else "medium",
                detected_at=datetime.now(),
                metric_name="performance_score",
                expected_value=expected_performance,
                actual_value=metrics.performance_score,
                deviation_score=deviation,
                suggested_fixes=[
                    "Check data source connectivity",
                    "Review extract refresh status",
                    "Optimize workbook calculations"
                ]
            )
        
        return None
    
    def _check_usage_anomaly(self, content_id: str, metrics: ContentMetrics) -> Optional[PerformanceAnomaly]:
        """Check for usage anomalies"""
        baseline = self.baseline_metrics.get(content_id, {})
        expected_views = baseline.get('view_count', metrics.view_count)
        
        if expected_views > 0:
            deviation_ratio = abs(metrics.view_count - expected_views) / expected_views
            
            if deviation_ratio > 2.0:  # 200% deviation
                return PerformanceAnomaly(
                    content_id=content_id,
                    anomaly_type="usage",
                    severity="medium",
                    detected_at=datetime.now(),
                    metric_name="view_count",
                    expected_value=expected_views,
                    actual_value=metrics.view_count,
                    deviation_score=deviation_ratio,
                    suggested_fixes=[
                        "Investigate access permissions",
                        "Check content availability",
                        "Review user notifications"
                    ]
                )
        
        return None

class IntelligenceEngine:
    """Main intelligence engine coordinating all AI capabilities"""
    
    def __init__(self, tableau_client=None):
        self.tableau_client = tableau_client
        self.semantic_analyzer = SemanticAnalyzer()
        self.predictive_analytics = PredictiveAnalytics()
        self.anomaly_detector = AnomalyDetector()
        
        # Initialize VizQL Data Service if available
        self.vizql_manager = None
        if VizQLDataServiceManager and tableau_client:
            self.vizql_manager = VizQLDataServiceManager(tableau_client)
        
        self.content_cache = {}
        self.metrics_cache = {}
        self.insights_cache = {}
        self.data_cache = {}
    
    async def perform_comprehensive_analysis(self, content_items: List[Dict]) -> Dict[str, Any]:
        """Perform comprehensive AI analysis on content"""
        results = {
            'semantic_analysis': [],
            'predictive_insights': [],
            'anomalies': [],
            'recommendations': [],
            'summary': {}
        }
        
        # Semantic analysis
        for item in content_items:
            analysis = await self.semantic_analyzer.analyze_content(item)
            results['semantic_analysis'].append(asdict(analysis))
        
        # Generate metrics for predictive analysis
        metrics = self._generate_content_metrics(content_items)
        
        # Predictive analytics
        insights = await self.predictive_analytics.analyze_trends(metrics)
        results['predictive_insights'] = [asdict(insight) for insight in insights]
        
        # Anomaly detection
        anomalies = await self.anomaly_detector.detect_anomalies(metrics)
        results['anomalies'] = [asdict(anomaly) for anomaly in anomalies]
        
        # Generate overall recommendations
        results['recommendations'] = self._generate_overall_recommendations(results)
        
        # Create summary
        results['summary'] = self._create_analysis_summary(results)
        
        return results
    
    async def get_intelligent_recommendations(self, content_id: str = None) -> List[Dict[str, Any]]:
        """Get AI-powered recommendations"""
        recommendations = []
        
        if content_id:
            # Content-specific recommendations
            if content_id in self.content_cache:
                analysis = self.content_cache[content_id]
                recommendations.extend(analysis.get('recommendations', []))
        else:
            # Global recommendations
            recommendations.extend([
                {
                    'type': 'optimization',
                    'priority': 'high',
                    'title': 'Optimize Underperforming Content',
                    'description': 'Several workbooks show declining usage patterns',
                    'actions': ['Review content relevance', 'Update data sources', 'Improve visualizations']
                },
                {
                    'type': 'governance',
                    'priority': 'medium',
                    'title': 'Improve Content Documentation',
                    'description': 'Many items lack proper descriptions and tags',
                    'actions': ['Add metadata', 'Create documentation standards', 'Implement tagging strategy']
                }
            ])
        
        return recommendations
    
    async def discover_content_insights(self, query: str) -> List[Dict[str, Any]]:
        """Discover content using natural language"""
        insights = []
        
        # Parse query for intent
        query_lower = query.lower()
        
        if 'popular' in query_lower or 'trending' in query_lower:
            insights.append({
                'type': 'trending_content',
                'title': 'Most Popular Content This Week',
                'items': ['Sales Dashboard Q4', 'Customer Analytics', 'Revenue Trends']
            })
        
        if 'unused' in query_lower or 'inactive' in query_lower:
            insights.append({
                'type': 'inactive_content',
                'title': 'Potentially Unused Content',
                'items': ['Old Test Workbook', 'Draft Analysis', 'Archived Reports']
            })
        
        if 'similar' in query_lower:
            insights.append({
                'type': 'similar_content',
                'title': 'Related Content',
                'items': ['Financial Reports', 'Budget Analysis', 'Cost Center Dashboard']
            })
        
        return insights
    
    def _generate_content_metrics(self, content_items: List[Dict]) -> Dict[str, ContentMetrics]:
        """Generate metrics for content items"""
        metrics = {}
        
        for item in content_items:
            content_id = item.get('id', '')
            
            # Generate sample metrics (would be real data in production)
            metrics[content_id] = ContentMetrics(
                view_count=hash(content_id) % 1000,
                user_engagement=0.5 + (hash(content_id) % 50) / 100,
                last_accessed=datetime.now() - timedelta(days=hash(content_id) % 30),
                complexity_score=0.3 + (hash(content_id) % 70) / 100,
                performance_score=0.4 + (hash(content_id) % 60) / 100,
                quality_score=0.5 + (hash(content_id) % 50) / 100
            )
        
        return metrics
    
    def _generate_overall_recommendations(self, analysis_results: Dict) -> List[Dict[str, Any]]:
        """Generate overall recommendations based on analysis"""
        recommendations = []
        
        # Check semantic analysis
        semantic_analyses = analysis_results.get('semantic_analysis', [])
        low_value_count = sum(1 for analysis in semantic_analyses 
                             if analysis.get('business_value_score', 0) < 0.3)
        
        if low_value_count > 0:
            recommendations.append({
                'type': 'content_quality',
                'priority': 'medium',
                'title': f'Improve {low_value_count} Low-Value Content Items',
                'description': 'Several content items have low business value scores',
                'actions': ['Add business context', 'Include KPIs', 'Improve descriptions']
            })
        
        # Check anomalies
        anomalies = analysis_results.get('anomalies', [])
        high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'high']
        
        if high_severity_anomalies:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'title': f'Address {len(high_severity_anomalies)} Critical Performance Issues',
                'description': 'High-severity anomalies detected',
                'actions': ['Investigate immediately', 'Check system resources', 'Review configurations']
            })
        
        return recommendations
    
    def _create_analysis_summary(self, results: Dict) -> Dict[str, Any]:
        """Create analysis summary"""
        return {
            'total_items_analyzed': len(results.get('semantic_analysis', [])),
            'insights_generated': len(results.get('predictive_insights', [])),
            'anomalies_detected': len(results.get('anomalies', [])),
            'recommendations_count': len(results.get('recommendations', [])),
            'analysis_timestamp': datetime.now().isoformat(),
            'health_score': self._calculate_overall_health_score(results)
        }
    
    def _calculate_overall_health_score(self, results: Dict) -> float:
        """Calculate overall content health score"""
        base_score = 0.8
        
        # Reduce score for anomalies
        anomalies = results.get('anomalies', [])
        high_severity = len([a for a in anomalies if a.get('severity') == 'high'])
        medium_severity = len([a for a in anomalies if a.get('severity') == 'medium'])
        
        score_reduction = (high_severity * 0.2) + (medium_severity * 0.1)
        
        return max(0.0, min(1.0, base_score - score_reduction))
    
    async def analyze_datasource_data_quality(self, datasource_id: str) -> Dict[str, Any]:
        """Analyze data quality for a data source using VizQL Data Service"""
        if not self.vizql_manager:
            return {"error": "VizQL Data Service not available"}
        
        try:
            # Get comprehensive field analysis
            analysis = await self.vizql_manager.analyze_datasource_fields(datasource_id)
            
            # Enhance with AI insights
            data_quality_score = self._calculate_data_quality_score(analysis)
            recommendations = self._generate_data_quality_recommendations(analysis)
            
            return {
                'datasource_id': datasource_id,
                'field_analysis': analysis,
                'data_quality_score': data_quality_score,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to analyze data source {datasource_id}: {e}")
            return {"error": str(e)}
    
    async def extract_and_analyze_data(self, datasource_id: str, 
                                     analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """Extract data and perform AI-powered analysis"""
        if not self.vizql_manager:
            return {"error": "VizQL Data Service not available"}
        
        try:
            # Extract data from datasource
            data_result = await self.vizql_manager.extract_datasource_data(
                datasource_id, 
                output_format='json'
            )
            
            # Perform different types of analysis
            if analysis_type == 'comprehensive':
                insights = await self._perform_comprehensive_data_analysis(data_result)
            elif analysis_type == 'statistical':
                insights = await self._perform_statistical_analysis(data_result)
            elif analysis_type == 'patterns':
                insights = await self._perform_pattern_analysis(data_result)
            else:
                insights = {"error": f"Unknown analysis type: {analysis_type}"}
            
            return {
                'datasource_id': datasource_id,
                'analysis_type': analysis_type,
                'data_summary': {
                    'row_count': data_result.get('row_count', 0),
                    'column_count': len(data_result.get('data', [{}])[0].keys()) if data_result.get('data') else 0
                },
                'insights': insights,
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to extract and analyze data for {datasource_id}: {e}")
            return {"error": str(e)}
    
    async def create_intelligent_data_query(self, datasource_id: str, 
                                          natural_language_query: str) -> Dict[str, Any]:
        """Create and execute data queries from natural language descriptions"""
        if not self.vizql_manager:
            return {"error": "VizQL Data Service not available"}
        
        try:
            # Parse natural language query to determine intent
            query_intent = self._parse_query_intent(natural_language_query)
            
            # Generate appropriate query fields and filters
            query_fields, query_filters = await self._generate_query_from_intent(
                datasource_id, query_intent
            )
            
            # Execute the query
            result = await self.vizql_manager.create_custom_query(
                datasource_id=datasource_id,
                query_fields=query_fields,
                query_filters=query_filters,
                limit=query_intent.get('limit', 1000)
            )
            
            # Add AI insights to the result
            insights = self._generate_query_insights(result, query_intent)
            
            return {
                'natural_language_query': natural_language_query,
                'parsed_intent': query_intent,
                'executed_query': {
                    'fields': query_fields,
                    'filters': query_filters
                },
                'result': result,
                'insights': insights,
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to process natural language query: {e}")
            return {"error": str(e)}
    
    def _calculate_data_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall data quality score based on field analysis"""
        summary = analysis.get('summary', {})
        field_analyses = analysis.get('field_analyses', {})
        
        score = 0.8  # Base score
        
        # Penalize for missing field descriptions
        total_fields = summary.get('total_fields', 1)
        fields_with_descriptions = sum(1 for field in summary.get('fields', {}).values() 
                                     if field.get('description'))
        description_ratio = fields_with_descriptions / total_fields
        score += (description_ratio - 0.5) * 0.2
        
        # Reward balanced data types
        data_types = summary.get('data_types', {})
        type_diversity = len(data_types) / 7  # 7 possible data types
        score += type_diversity * 0.1
        
        # Analyze statistical quality for numeric fields
        for field_name, field_analysis in field_analyses.items():
            stats = field_analysis.get('statistics', {})
            # Check for reasonable distributions (no excessive nulls, outliers, etc.)
            # This is a simplified check - in production you'd want more sophisticated analysis
            
        return max(0.0, min(1.0, score))
    
    def _generate_data_quality_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving data quality"""
        recommendations = []
        summary = analysis.get('summary', {})
        
        # Check for missing descriptions
        fields_without_descriptions = [
            name for name, field in summary.get('fields', {}).items()
            if not field.get('description')
        ]
        
        if fields_without_descriptions:
            recommendations.append(
                f"Add descriptions to {len(fields_without_descriptions)} fields without documentation"
            )
        
        # Check data type distribution
        data_types = summary.get('data_types', {})
        total_fields = summary.get('total_fields', 1)
        if data_types.get('STRING', 0) > total_fields * 0.8:
            recommendations.append(
                "Consider converting string fields to more specific data types where appropriate"
            )
        
        # Check for dimension/measure balance
        dimensions = len(summary.get('dimensions', []))
        measures = len(summary.get('measures', []))
        
        if dimensions == 0:
            recommendations.append("Add dimensional fields for better analysis capabilities")
        elif measures == 0:
            recommendations.append("Add measure fields for quantitative analysis")
        
        return recommendations
    
    async def _perform_comprehensive_data_analysis(self, data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive AI analysis on extracted data"""
        data = data_result.get('data', [])
        
        if not data:
            return {"error": "No data available for analysis"}
        
        # Basic statistics
        row_count = len(data)
        columns = list(data[0].keys()) if data else []
        
        # Data type analysis
        column_types = {}
        for col in columns:
            sample_values = [row.get(col) for row in data[:100] if row.get(col) is not None]
            column_types[col] = self._infer_column_type(sample_values)
        
        # Missing value analysis
        missing_analysis = {}
        for col in columns:
            null_count = sum(1 for row in data if row.get(col) is None or row.get(col) == '')
            missing_analysis[col] = {
                'null_count': null_count,
                'null_percentage': (null_count / row_count) * 100 if row_count > 0 else 0
            }
        
        # Identify potential issues
        issues = []
        for col, analysis in missing_analysis.items():
            if analysis['null_percentage'] > 50:
                issues.append(f"Column '{col}' has high missing values ({analysis['null_percentage']:.1f}%)")
        
        return {
            'basic_stats': {
                'row_count': row_count,
                'column_count': len(columns),
                'columns': columns
            },
            'data_types': column_types,
            'missing_values': missing_analysis,
            'issues_detected': issues,
            'data_quality_score': self._calculate_simple_quality_score(missing_analysis, column_types)
        }
    
    async def _perform_statistical_analysis(self, data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis on numeric columns"""
        data = data_result.get('data', [])
        
        if not data:
            return {"error": "No data available for analysis"}
        
        numeric_columns = []
        statistics_results = {}
        
        # Identify numeric columns
        for col in data[0].keys():
            sample_values = [row.get(col) for row in data[:100] if row.get(col) is not None]
            if self._is_numeric_column(sample_values):
                numeric_columns.append(col)
        
        # Calculate statistics for numeric columns
        for col in numeric_columns:
            values = [float(row.get(col, 0)) for row in data 
                     if row.get(col) is not None and str(row.get(col)).replace('.', '').replace('-', '').isdigit()]
            
            if values:
                statistics_results[col] = {
                    'count': len(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                    'outliers_detected': self._detect_outliers(values)
                }
        
        return {
            'numeric_columns': numeric_columns,
            'statistics': statistics_results,
            'insights': self._generate_statistical_insights(statistics_results)
        }
    
    async def _perform_pattern_analysis(self, data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns and trends in the data"""
        data = data_result.get('data', [])
        
        if not data:
            return {"error": "No data available for analysis"}
        
        patterns = {}
        
        # Look for date columns and analyze trends
        date_columns = []
        for col in data[0].keys():
            sample_values = [row.get(col) for row in data[:10] if row.get(col) is not None]
            if self._is_date_column(sample_values):
                date_columns.append(col)
        
        # Categorical pattern analysis
        categorical_patterns = {}
        for col in data[0].keys():
            unique_values = set(str(row.get(col, '')) for row in data)
            if len(unique_values) < len(data) * 0.5:  # Likely categorical
                value_counts = defaultdict(int)
                for row in data:
                    value_counts[str(row.get(col, ''))] += 1
                
                categorical_patterns[col] = {
                    'unique_count': len(unique_values),
                    'most_common': sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                }
        
        return {
            'date_columns': date_columns,
            'categorical_patterns': categorical_patterns,
            'pattern_insights': self._generate_pattern_insights(categorical_patterns)
        }
    
    def _parse_query_intent(self, natural_language_query: str) -> Dict[str, Any]:
        """Parse natural language query to extract intent"""
        query_lower = natural_language_query.lower()
        
        intent = {
            'operation': 'select',
            'fields': [],
            'filters': [],
            'aggregations': [],
            'limit': None
        }
        
        # Simple intent parsing (in production, you'd use more sophisticated NLP)
        if 'sum' in query_lower or 'total' in query_lower:
            intent['aggregations'].append('SUM')
        
        if 'average' in query_lower or 'avg' in query_lower:
            intent['aggregations'].append('AVG')
        
        if 'count' in query_lower:
            intent['aggregations'].append('COUNT')
        
        if 'top' in query_lower:
            # Extract number if present
            import re
            numbers = re.findall(r'\d+', query_lower)
            if numbers:
                intent['limit'] = int(numbers[0])
        
        return intent
    
    async def _generate_query_from_intent(self, datasource_id: str, 
                                        intent: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """Generate query fields and filters from parsed intent"""
        # Get datasource metadata first
        if not self.vizql_manager:
            return [], []
        
        # This is a simplified implementation
        # In production, you'd have more sophisticated field mapping
        query_fields = [
            {'name': 'measure_field', 'aggregation': 'SUM'} if intent['aggregations'] else {'name': 'dimension_field'}
        ]
        
        query_filters = []
        
        return query_fields, query_filters
    
    def _generate_query_insights(self, result: Dict[str, Any], intent: Dict[str, Any]) -> List[str]:
        """Generate insights from query results"""
        insights = []
        
        row_count = result.get('row_count', 0)
        if row_count == 0:
            insights.append("No data returned - consider adjusting filters")
        elif row_count < 10:
            insights.append("Small result set - data may be heavily filtered")
        elif row_count > 10000:
            insights.append("Large result set - consider adding filters for better performance")
        
        return insights
    
    def _infer_column_type(self, sample_values: List[Any]) -> str:
        """Infer the data type of a column from sample values"""
        if not sample_values:
            return 'unknown'
        
        # Check if all values are numeric
        if all(isinstance(v, (int, float)) or str(v).replace('.', '').replace('-', '').isdigit() 
               for v in sample_values):
            return 'numeric'
        
        # Check if values look like dates
        if self._is_date_column(sample_values):
            return 'date'
        
        # Check if boolean
        bool_values = {'true', 'false', '1', '0', 'yes', 'no'}
        if all(str(v).lower() in bool_values for v in sample_values):
            return 'boolean'
        
        return 'string'
    
    def _is_numeric_column(self, sample_values: List[Any]) -> bool:
        """Check if a column contains numeric values"""
        if not sample_values:
            return False
        
        try:
            for value in sample_values[:10]:
                float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_date_column(self, sample_values: List[Any]) -> bool:
        """Check if a column contains date values"""
        if not sample_values:
            return False
        
        date_indicators = ['date', 'time', 'timestamp', '-', '/', ':']
        return any(any(indicator in str(v).lower() for indicator in date_indicators) 
                  for v in sample_values[:5])
    
    def _calculate_simple_quality_score(self, missing_analysis: Dict, column_types: Dict) -> float:
        """Calculate a simple data quality score"""
        if not missing_analysis:
            return 0.5
        
        # Base score
        score = 0.8
        
        # Penalize for high missing values
        avg_missing = sum(analysis['null_percentage'] for analysis in missing_analysis.values()) / len(missing_analysis)
        score -= (avg_missing / 100) * 0.3
        
        # Reward type diversity
        unique_types = len(set(column_types.values()))
        score += (unique_types / 4) * 0.1  # Max 4 basic types
        
        return max(0.0, min(1.0, score))
    
    def _detect_outliers(self, values: List[float]) -> int:
        """Simple outlier detection using IQR method"""
        if len(values) < 4:
            return 0
        
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [v for v in values if v < lower_bound or v > upper_bound]
        return len(outliers)
    
    def _generate_statistical_insights(self, statistics_results: Dict) -> List[str]:
        """Generate insights from statistical analysis"""
        insights = []
        
        for col, stats in statistics_results.items():
            if stats['outliers_detected'] > 0:
                insights.append(f"Column '{col}' has {stats['outliers_detected']} outliers")
            
            if stats['std_dev'] / stats['mean'] > 1 if stats['mean'] != 0 else False:
                insights.append(f"Column '{col}' shows high variability")
        
        return insights
    
    def _generate_pattern_insights(self, categorical_patterns: Dict) -> List[str]:
        """Generate insights from pattern analysis"""
        insights = []
        
        for col, pattern in categorical_patterns.items():
            if pattern['unique_count'] == 1:
                insights.append(f"Column '{col}' has only one unique value - consider removing")
            elif pattern['unique_count'] > 1000:
                insights.append(f"Column '{col}' has high cardinality ({pattern['unique_count']} unique values)")
        
        return insights