from datetime import datetime, timezone


def parse_iso8601_timestamp(timestamp: str) -> datetime:
    """
    Parse an ISO 8601 timestamp string (with or without milliseconds) into a timezone-aware datetime object in UTC.
    Args:
        timestamp (str): The ISO 8601 timestamp string.
    Returns:
        datetime: The parsed datetime object in UTC.
    Raises:
        ValueError: If the timestamp format is invalid.
    """
    try:
        # Try parsing with milliseconds
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            # Try parsing without milliseconds
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            # Raise error if format is invalid
            raise ValueError(f"Invalid ISO 8601 timestamp format: {timestamp}")
    return dt.replace(tzinfo=timezone.utc)