import enum

class reviewStateEnum(str, enum.Enum):
    open = "open"
    reviewed = "reviewed"
    closed = "closed"
