"""
Query log model for tracking database queries and analytics
"""

import clickhouse_connect
from datetime import datetime
from typing import Optional
import os

CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "aidatalabs")


class ClickHouseClient:
    """ClickHouse client singleton"""

    _instance: Optional[clickhouse_connect.get_client] = None

    @classmethod
    def get_client(cls) -> clickhouse_connect.get_client:
        """Get or create ClickHouse client"""
        if cls._instance is None:
            cls._instance = clickhouse_connect.get_client(
                host=CLICKHOUSE_URL,
                port=CLICKHOUSE_PORT,
                username=CLICKHOUSE_USER,
                password=CLICKHOUSE_PASSWORD,
                database=CLICKHOUSE_DATABASE,
            )
        return cls._instance


class QueryLog:
    """
    Query log model for tracking SQL queries and their performance
    Stored in ClickHouse for analytics
    """

    TABLE_NAME = "query_logs"

    @staticmethod
    def create_table():
        """Create query_logs table in ClickHouse"""
        client = ClickHouseClient.get_client()
        client.command(f"""
            CREATE TABLE IF NOT EXISTS {QueryLog.TABLE_NAME} (
                query_id String,
                user_id UUID,
                query_text String,
                query_type String,
                execution_time_ms UInt32,
                rows_read UInt64,
                bytes_read UInt64,
                memory_used UInt64,
                status String,
                error_message String,
                timestamp DateTime64(3),
                client_ip String,
                user_agent String
            )
            ENGINE = MergeTree()
            ORDER BY (user_id, timestamp)
            PARTITION BY toYYYYMM(timestamp)
            TTL timestamp + INTERVAL 90 DAY
        """)

    @staticmethod
    def insert(
        query_id: str,
        user_id: str,
        query_text: str,
        query_type: str,
        execution_time_ms: int,
        rows_read: int,
        bytes_read: int,
        memory_used: int,
        status: str,
        error_message: str = "",
        client_ip: str = "",
        user_agent: str = "",
    ):
        """Insert query log entry"""
        client = ClickHouseClient.get_client()
        data = [{
            'query_id': query_id,
            'user_id': user_id,
            'query_text': query_text,
            'query_type': query_type,
            'execution_time_ms': execution_time_ms,
            'rows_read': rows_read,
            'bytes_read': bytes_read,
            'memory_used': memory_used,
            'status': status,
            'error_message': error_message,
            'timestamp': datetime.utcnow(),
            'client_ip': client_ip,
            'user_agent': user_agent,
        }]
        client.insert(QueryLog.TABLE_NAME, data)

    @staticmethod
    def get_query_stats(user_id: str, hours: int = 24):
        """Get query statistics for a user"""
        client = ClickHouseClient.get_client()
        result = client.query(f"""
            SELECT
                count() as query_count,
                avg(execution_time_ms) as avg_time_ms,
                max(execution_time_ms) as max_time_ms,
                sum(rows_read) as total_rows,
                sum(bytes_read) as total_bytes,
                countIf(status = 'success') as success_count,
                countIf(status = 'error') as error_count
            FROM {QueryLog.TABLE_NAME}
            WHERE user_id = %(user_id)s
              AND timestamp >= now() - INTERVAL {hours} HOUR
        """, parameters={'user_id': user_id})
        return result.result_rows[0] if result.result_rows else None
