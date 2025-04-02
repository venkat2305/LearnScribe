from enum import Enum


class SourceTypes(str, Enum):
    YOUTUBE = "youtube"
    ARTICLE = "article"
    MANUAL = "manual"
    MISTAKES = "mistakes"
    TEXT = "text"
