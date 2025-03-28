from collections.abc import Callable
from typing import Literal, NotRequired, TypedDict, TypeAlias

import ipywidgets as widgets

EvaluationFunction: TypeAlias = Callable[[], float | None]
FeedbackCallback: TypeAlias = Callable[[], None]
QuestionWidgetPackage: TypeAlias  = tuple[widgets.Box,
                                   EvaluationFunction, FeedbackCallback]
FeedbackFunction: TypeAlias = Callable[[float | None], str]
DisplayFunction: TypeAlias = Callable[..., None]


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
