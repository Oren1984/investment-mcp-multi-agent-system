from dataclasses import dataclass


@dataclass
class HealthCheckSchema:
    status: str
    timestamp: str