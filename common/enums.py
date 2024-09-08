from enum import Enum
class RequestStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    IN_PROCESS = "in process"
    FAILED = "failed"