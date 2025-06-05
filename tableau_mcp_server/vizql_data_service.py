"""
Tableau Cloud MCP Server - VizQL Data Service Client
Provides programmatic access to data behind Tableau visualizations
"""

import asyncio
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import aiohttp
from enum import Enum
import pandas as pd

logger = logging.getLogger(__name__)

class DataType(Enum):
    """VizQL Data Service supported data types"""
    INTEGER = "INTEGER"
    REAL = "REAL"
    STRING = "STRING"
    DATETIME = "DATETIME"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    SPATIAL = "SPATIAL"

class FilterType(Enum):
    """VizQL filter types"""
    CATEGORICAL = "categorical"
    QUANTITATIVE = "quantitative"
    DATE = "date"
    SET = "set"

class AggregationType(Enum):
    """VizQL aggregation types"""
    SUM = "SUM"
    AVG = "AVG"
    MEDIAN = "MEDIAN"
    COUNT = "COUNT"
    COUNTD = "COUNTD"
    MIN = "MIN"
    MAX = "MAX"
    STDEV = "STDEV"
    STDEVP = "STDEVP"
    VAR = "VAR"
    VARP = "VARP"

@dataclass
class DataSourceField:
    """Represents a field in a data source"""
    name: str
    data_type: DataType
    description: Optional[str] = None
    is_dimension: bool = True
    is_measure: bool = False
    role: Optional[str] = None
    semantic_role: Optional[str] = None

@dataclass
class QueryField:
    """Represents a field in a query"""
    name: str
    aggregation: Optional[AggregationType] = None
    alias: Optional[str] = None

@dataclass
class Filter:
    """Represents a filter in a query"""
    field: str
    filter_type: FilterType
    values: List[Any]
    operation: str = "in"  # in, not_in, between, greater_than, less_than, etc.

@dataclass
class QueryRequest:
    """Represents a complete query request"""
    datasource_luid: str
    fields: List[QueryField]
    filters: Optional[List[Filter]] = None
    limit: Optional[int] = None
    offset: Optional[int] = 0
    debug: bool = False

@dataclass
class QueryResult:
    """Represents the result of a query"""
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    row_count: int
    total_rows: Optional[int] = None
    execution_time: Optional[float] = None
    query_id: Optional[str] = None

class VizQLDataServiceClient:
    """Client for Tableau VizQL Data Service API"""
    
    def __init__(self, server_url: str, site_id: str, auth_token: str):
        self.server_url = server_url.rstrip('/')
        self.site_id = site_id
        self.auth_token = auth_token
        self.base_url = f"{self.server_url}/vizql-data-service/v1"
        self.session = None
        
        # Headers for all requests
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Tableau-Auth': self.auth_token
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on VizQL Data Service"""
        url = f"{self.base_url}/simple-request"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                result = await response.json()
                logger.info("VizQL Data Service health check passed")
                return result
            else:
                error_text = await response.text()
                logger.error(f"Health check failed: {response.status} - {error_text}")
                raise Exception(f"Health check failed: {response.status}")
    
    async def get_datasource_metadata(self, datasource_luid: str) -> Dict[str, DataSourceField]:
        """Get metadata for a data source"""
        url = f"{self.base_url}/read-metadata"
        
        payload = {
            "datasource": {
                "datasourceLuid": datasource_luid
            }
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                
                # Parse fields from metadata
                fields = {}
                if 'metadata' in result and 'fields' in result['metadata']:
                    for field_data in result['metadata']['fields']:
                        field = DataSourceField(
                            name=field_data.get('name', ''),
                            data_type=DataType(field_data.get('dataType', 'STRING')),
                            description=field_data.get('description'),
                            is_dimension=field_data.get('isDimension', True),
                            is_measure=field_data.get('isMeasure', False),
                            role=field_data.get('role'),
                            semantic_role=field_data.get('semanticRole')
                        )
                        fields[field.name] = field
                
                logger.info(f"Retrieved metadata for {len(fields)} fields")
                return fields
            else:
                error_text = await response.text()
                logger.error(f"Failed to get metadata: {response.status} - {error_text}")
                raise Exception(f"Failed to get metadata: {response.status}")
    
    async def query_datasource(self, query: QueryRequest) -> QueryResult:
        """Execute a query against a data source"""
        url = f"{self.base_url}/query-datasource"
        
        # Build query payload
        fields_payload = []
        for field in query.fields:
            field_dict = {"name": field.name}
            if field.aggregation:
                field_dict["aggregation"] = field.aggregation.value
            if field.alias:
                field_dict["alias"] = field.alias
            fields_payload.append(field_dict)
        
        # Build filters payload
        filters_payload = []
        if query.filters:
            for filter_obj in query.filters:
                filter_dict = {
                    "field": filter_obj.field,
                    "filterType": filter_obj.filter_type.value,
                    "operation": filter_obj.operation,
                    "values": filter_obj.values
                }
                filters_payload.append(filter_dict)
        
        payload = {
            "datasource": {
                "datasourceLuid": query.datasource_luid
            },
            "query": {
                "fields": fields_payload
            }
        }
        
        if filters_payload:
            payload["query"]["filters"] = filters_payload
        
        if query.limit:
            payload["query"]["limit"] = query.limit
        
        if query.offset:
            payload["query"]["offset"] = query.offset
        
        if query.debug:
            payload["debug"] = True
        
        start_time = datetime.now()
        
        async with self.session.post(url, json=payload) as response:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if response.status == 200:
                result = await response.json()
                
                # Parse result data
                data = result.get('data', [])
                metadata = result.get('metadata', {})
                row_count = len(data)
                total_rows = result.get('totalRows')
                query_id = result.get('queryId')
                
                query_result = QueryResult(
                    data=data,
                    metadata=metadata,
                    row_count=row_count,
                    total_rows=total_rows,
                    execution_time=execution_time,
                    query_id=query_id
                )
                
                logger.info(f"Query executed successfully: {row_count} rows returned in {execution_time:.2f}s")
                return query_result
            else:
                error_text = await response.text()
                logger.error(f"Query failed: {response.status} - {error_text}")
                raise Exception(f"Query failed: {response.status}")
    
    async def get_all_data(self, datasource_luid: str, 
                          fields: Optional[List[str]] = None,
                          filters: Optional[List[Filter]] = None,
                          batch_size: int = 10000) -> QueryResult:
        """Get all data from a data source with automatic pagination"""
        
        # If no fields specified, get all fields from metadata
        if not fields:
            metadata = await self.get_datasource_metadata(datasource_luid)
            fields = list(metadata.keys())
        
        # Convert field names to QueryField objects
        query_fields = [QueryField(name=field) for field in fields]
        
        all_data = []
        offset = 0
        total_rows = None
        
        while True:
            query = QueryRequest(
                datasource_luid=datasource_luid,
                fields=query_fields,
                filters=filters,
                limit=batch_size,
                offset=offset
            )
            
            result = await self.query_datasource(query)
            
            if not result.data:
                break
            
            all_data.extend(result.data)
            
            if total_rows is None:
                total_rows = result.total_rows
            
            # Check if we've retrieved all data
            if total_rows and len(all_data) >= total_rows:
                break
            
            # If we got less than batch_size, we're done
            if len(result.data) < batch_size:
                break
            
            offset += batch_size
            logger.info(f"Retrieved {len(all_data)} of {total_rows or 'unknown'} rows")
        
        return QueryResult(
            data=all_data,
            metadata=result.metadata,
            row_count=len(all_data),
            total_rows=total_rows,
            execution_time=result.execution_time
        )
    
    async def export_to_csv(self, datasource_luid: str, 
                           file_path: str,
                           fields: Optional[List[str]] = None,
                           filters: Optional[List[Filter]] = None) -> str:
        """Export data source data to CSV file"""
        
        result = await self.get_all_data(datasource_luid, fields, filters)
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(result.data)
        
        # Save to CSV
        df.to_csv(file_path, index=False)
        
        logger.info(f"Exported {result.row_count} rows to {file_path}")
        return f"Successfully exported {result.row_count} rows to {file_path}"
    
    async def export_to_json(self, datasource_luid: str, 
                            file_path: str,
                            fields: Optional[List[str]] = None,
                            filters: Optional[List[Filter]] = None) -> str:
        """Export data source data to JSON file"""
        
        result = await self.get_all_data(datasource_luid, fields, filters)
        
        # Save to JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result.data, f, indent=2, default=str)
        
        logger.info(f"Exported {result.row_count} rows to {file_path}")
        return f"Successfully exported {result.row_count} rows to {file_path}"
    
    async def analyze_data_distribution(self, datasource_luid: str, 
                                      field_name: str) -> Dict[str, Any]:
        """Analyze data distribution for a specific field"""
        
        # Get field metadata
        metadata = await self.get_datasource_metadata(datasource_luid)
        field_info = metadata.get(field_name)
        
        if not field_info:
            raise ValueError(f"Field '{field_name}' not found in data source")
        
        # Build appropriate query based on data type
        if field_info.data_type in [DataType.INTEGER, DataType.REAL]:
            # For numeric fields, get statistical measures
            query_fields = [
                QueryField(name=field_name, aggregation=AggregationType.COUNT),
                QueryField(name=field_name, aggregation=AggregationType.MIN),
                QueryField(name=field_name, aggregation=AggregationType.MAX),
                QueryField(name=field_name, aggregation=AggregationType.AVG),
                QueryField(name=field_name, aggregation=AggregationType.MEDIAN),
                QueryField(name=field_name, aggregation=AggregationType.STDEV)
            ]
        else:
            # For categorical fields, get distinct count
            query_fields = [
                QueryField(name=field_name, aggregation=AggregationType.COUNT),
                QueryField(name=field_name, aggregation=AggregationType.COUNTD)
            ]
        
        query = QueryRequest(
            datasource_luid=datasource_luid,
            fields=query_fields
        )
        
        result = await self.query_datasource(query)
        
        analysis = {
            'field_name': field_name,
            'data_type': field_info.data_type.value,
            'statistics': result.data[0] if result.data else {},
            'metadata': field_info.__dict__
        }
        
        logger.info(f"Analyzed distribution for field '{field_name}'")
        return analysis
    
    async def get_field_summary(self, datasource_luid: str) -> Dict[str, Any]:
        """Get a comprehensive summary of all fields in a data source"""
        
        metadata = await self.get_datasource_metadata(datasource_luid)
        
        summary = {
            'total_fields': len(metadata),
            'dimensions': [name for name, field in metadata.items() if field.is_dimension],
            'measures': [name for name, field in metadata.items() if field.is_measure],
            'data_types': {},
            'fields': {}
        }
        
        # Count by data type
        for field in metadata.values():
            data_type = field.data_type.value
            summary['data_types'][data_type] = summary['data_types'].get(data_type, 0) + 1
            summary['fields'][field.name] = asdict(field)
        
        logger.info(f"Generated summary for {summary['total_fields']} fields")
        return summary

class VizQLDataServiceManager:
    """Manager class for VizQL Data Service operations"""
    
    def __init__(self, tableau_client):
        self.tableau_client = tableau_client
        self.vizql_client = None
    
    async def get_vizql_client(self) -> VizQLDataServiceClient:
        """Get or create VizQL Data Service client"""
        if not self.vizql_client:
            # Use the same authentication as the main Tableau client
            auth_token = getattr(self.tableau_client, 'auth_token', None)
            if not auth_token:
                raise Exception("No authentication token available for VizQL Data Service")
            
            self.vizql_client = VizQLDataServiceClient(
                server_url=self.tableau_client.server_url,
                site_id=self.tableau_client.site_id,
                auth_token=auth_token
            )
        
        return self.vizql_client
    
    async def extract_datasource_data(self, datasource_luid: str, 
                                    output_format: str = 'json',
                                    file_path: Optional[str] = None,
                                    fields: Optional[List[str]] = None,
                                    filters: Optional[List[Filter]] = None) -> Union[str, Dict[str, Any]]:
        """Extract data from a data source in various formats"""
        
        async with await self.get_vizql_client() as client:
            if output_format.lower() == 'csv':
                if not file_path:
                    file_path = f"datasource_{datasource_luid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                return await client.export_to_csv(datasource_luid, file_path, fields, filters)
            
            elif output_format.lower() == 'json':
                if file_path:
                    return await client.export_to_json(datasource_luid, file_path, fields, filters)
                else:
                    result = await client.get_all_data(datasource_luid, fields, filters)
                    return {
                        'data': result.data,
                        'metadata': result.metadata,
                        'row_count': result.row_count,
                        'total_rows': result.total_rows
                    }
            
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
    
    async def analyze_datasource_fields(self, datasource_luid: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of data source fields"""
        
        async with await self.get_vizql_client() as client:
            # Get field summary
            summary = await client.get_field_summary(datasource_luid)
            
            # Analyze distribution for numeric fields (sample of up to 5)
            numeric_fields = [name for name, field in summary['fields'].items() 
                            if field['data_type'] in ['INTEGER', 'REAL']][:5]
            
            field_analyses = {}
            for field_name in numeric_fields:
                try:
                    analysis = await client.analyze_data_distribution(datasource_luid, field_name)
                    field_analyses[field_name] = analysis
                except Exception as e:
                    logger.warning(f"Could not analyze field {field_name}: {e}")
            
            return {
                'summary': summary,
                'field_analyses': field_analyses,
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    async def create_custom_query(self, datasource_luid: str,
                                query_fields: List[Dict[str, Any]],
                                query_filters: Optional[List[Dict[str, Any]]] = None,
                                limit: Optional[int] = None) -> Dict[str, Any]:
        """Execute a custom query with advanced options"""
        
        async with await self.get_vizql_client() as client:
            # Convert field specifications to QueryField objects
            fields = []
            for field_spec in query_fields:
                field = QueryField(
                    name=field_spec['name'],
                    aggregation=AggregationType(field_spec.get('aggregation')) if field_spec.get('aggregation') else None,
                    alias=field_spec.get('alias')
                )
                fields.append(field)
            
            # Convert filter specifications to Filter objects
            filters = []
            if query_filters:
                for filter_spec in query_filters:
                    filter_obj = Filter(
                        field=filter_spec['field'],
                        filter_type=FilterType(filter_spec['filter_type']),
                        values=filter_spec['values'],
                        operation=filter_spec.get('operation', 'in')
                    )
                    filters.append(filter_obj)
            
            query = QueryRequest(
                datasource_luid=datasource_luid,
                fields=fields,
                filters=filters if filters else None,
                limit=limit
            )
            
            result = await client.query_datasource(query)
            
            return {
                'data': result.data,
                'metadata': result.metadata,
                'row_count': result.row_count,
                'total_rows': result.total_rows,
                'execution_time': result.execution_time,
                'query_id': result.query_id
            }