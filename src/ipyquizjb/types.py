from collections.abc import Callable
from typing import Literal, NotRequired, TypeAlias, TypedDict

import ipywidgets as widgets

EvaluationFunction: TypeAlias = Callable[[], float | None]
FeedbackCallback: TypeAlias = Callable[[], None]
QuestionWidgetPackage: TypeAlias  = tuple[widgets.Box,
                                   EvaluationFunction, FeedbackCallback]
FeedbackFunction: TypeAlias = Callable[[float | None], str]
DisplayFunction: TypeAlias = Callable[..., None]

class AdditionalMaterial(TypedDict):
    type: NotRequired[Literal["TEXT", "VIDEO", "CODE"]]
    body: str

class Question(TypedDict):
    """
    The typing of a dictionary representing a single question.
    
    when: When the question should be shown.
        - "initial": when a question group is first displayed
        - "retry": in the pool of questions to use after retrying
    """
    type: Literal["MULTIPLE_CHOICE", "NUMERIC", "TEXT"]
    body: str
    answers: NotRequired[list[str]]  # Options
    answer: NotRequired[list[str] | str]  # Correct answer
    notes: NotRequired[list[str]]
    when: NotRequired[Literal["initial", "retry"]]

class QuestionPackage(TypedDict):
    """
    The typing of a dictionary representing a question package,
    which includes a list of questions and potentially some more info.
    """
    questions: list[Question]
    additional_material: NotRequired[AdditionalMaterial]
    status: NotRequired[str]
    passing_threshold: NotRequired[float]  # number between 0-1, threshold for passing group
