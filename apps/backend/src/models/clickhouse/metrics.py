"""
Metrics model for tracking system and business metrics
"""

from datetime import datetime
from typing import Optional

from .query_log import ClickHouseClient


class Metrics:
    """
    Metrics model for tracking system and business metrics
    Stored in ClickHouse for analytics and monitoring
    """

    TABLE_NAME = "metrics"

    @staticmethod
    def create_table():
        """Create metrics table in ClickHouse"""
        client = ClickHouseClient.get_client()
        client.command(f"""
            CREATE TABLE IF NOT EXISTS {Metrics.TABLE_NAME} (
                metric_id String,
                metric_name String,
                metric_value Float64,
                metric_type String,
                tags Map(String, String),
                timestamp DateTime64(3)
            )
            ENGINE = MergeTree()
            ORDER BY (metric_name, timestamp)
            PARTITION BY toYYYYMM(timestamp)
            TTL timestamp + INTERVAL 365 DAY
        """)

    @staticmethod
    def insert(
        metric_name: str,
        metric_value: float,
        metric_type: str,
        tags: dict,
        metric_id: Optional[str] = None,
    ):
        """Insert metric entry"""
        if metric_id is None:
            metric_id = f"{metric_name}_{datetime.utcnow().timestamp()}"

        client = ClickHouseClient.get_client()
        data = [{
            'metric_id': metric_id,
            'metric_name': metric_name,
            'metric_value': metric_value,
            'metric_type': metric_type,
            'tags': tags,
            'timestamp': datetime.utcnow(),
        }]
        client.insert(Metrics.TABLE_NAME, data)

    @staticmethod
    def get_metric_avg(metric_name: str, hours: int = 24, tags: Optional[dict] = None):
        """Get average metric value over time period"""
        client = ClickHouseClient.get_client()

        where_clause = f"metric_name = '{metric_name}'"
        if tags:
            for key, value in tags.items():
                where_clause += f" AND tags['{key}'] = '{value}'"

        result = client.query(f"""
            SELECT avg(metric_value) as avg_value
            FROM {Metrics.TABLE_NAME}
            WHERE {where_clause}
              AND timestamp >= now() - INTERVAL {hours} HOUR
        """)
        return result.result_rows[0][0] if result.result_rows else None

    @staticmethod
    def get_metric_sum(metric_name: str, hours: int = 24, tags: Optional[dict] = None):
        """Get sum of metric values over time period"""
        client = ClickHouseClient.get_client()

        where_clause = f"metric_name = '{metric_name}'"
        if tags:
            for key, value in tags.items():
                where_clause += f" AND tags['{key}'] = '{value}'"

        result = client.query(f"""
            SELECT sum(metric_value) as total_value
            FROM {Metrics.TABLE_NAME}
            WHERE {where_clause}
              AND timestamp >= now() - INTERVAL {hours} HOUR
        """)
        return result.result_rows[0][0] if result.result_rows else None
