from enum import Enum

class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ReminderFrequency(str, Enum):
    ONCE = "once"
    DAILY = "daily"

class MonitorFrequency(str, Enum):
    ONCE = "once"
    DAILY = "daily"
    PER_WEEK = "per_week"
    PER_MONTH = "per_month"
    PER_YEAR = "per_year"

class InputType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
