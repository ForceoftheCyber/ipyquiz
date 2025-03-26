from typing import TypedDict, Literal, NotRequired, Any
from collections.abc import Callable
import ipywidgets as widgets

type EvaluationFunction = Callable[[], float | None]
type FeedbackCallback = Callable[[], None]
type QuestionWidgetPackage = tuple[widgets.Box,
                                   EvaluationFunction, FeedbackCallback]
type FeedbackFunction = Callable[[Any], str]

class AdditionalMaterial(TypedDict):
    type: NotRequired[Literal["TEXT", "VIDEO", "CODE"]]
    body: str

class Question(TypedDict):
    type: Literal["MULTIPLE_CHOICE", "NUMERIC", "TEXT"]
    body: str
    answers: NotRequired[list[str]]  # Options
    answer: list[str] | str  # Correct answer
    notes: NotRequired[list[str]]