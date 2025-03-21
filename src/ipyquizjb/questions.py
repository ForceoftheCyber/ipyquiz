import json
import ipywidgets as widgets
from IPython.display import display, clear_output
from collections.abc import Callable
from typing import Any
import random

from ipyquizjb.types import QuestionWidgetPackage, Question
from ipyquizjb.question_widgets import (
    multiple_choice,
    multiple_answers,
    no_input_question,
    numeric_input,
)

type EvaluationFunction = Callable[[], float | None]
type FeedbackCallback = Callable[[], None]
type QuestionWidgetPackage = tuple[widgets.Box, EvaluationFunction, FeedbackCallback]


def make_question(question: Question) -> QuestionWidgetPackage:
    """
    Delegates to the other questions functions based on question type and returns a widget.
    """
    match question["type"]:
        case "MULTIPLE_CHOICE" if len(question["answer"]) == 1:
            # Multiple choice, single answer
            # TODO: Add validation of format?
            if "answers" not in question or not question["answers"]:
                raise AttributeError(
                    "Multiple choice should have list of possible answers (options)"
                )
            return multiple_choice(
                question=question["body"],
                options=question["answers"],
                correct_option=question["answer"][0],
            )

        case "MULTIPLE_CHOICE":
            # Multiple choice, multiple answer
            if isinstance(question["answer"], str):
                raise TypeError(
                    "question['answer'] should be a list when question type is multiple choice"
                )
            if "answers" not in question or not question["answers"]:
                raise AttributeError(
                    "Multiple choice should have list of possible answers (options)"
                )
            return multiple_answers(
                question=question["body"],
                options=question["answers"],
                correct_answers=question["answer"],
            )

        case "NUMERIC":
            if isinstance(question["answer"], list):
                raise TypeError(
                    "question['answer'] should not be a list when question type is multiple choice"
                )
            return numeric_input(
                question=question["body"], correct_answer=float(question["answer"])
            )

        case "TEXT":
            solution_notes = question["notes"] if "notes" in question else []

            # Will always be considered a right solution (does not influence score computation)
            always_correct = lambda: True
            return (
                no_input_question(question=question["body"], solution=solution_notes),
                always_correct,
                (lambda: None),
            )

        case _:
            raise NameError(f"{question['type']} is not a valid question type")


def singleton_group(question: Question):
    # Unpack to not be part of a group?

    widget, _, callback = make_question(question)

    if question["type"] == "TEXT":
        return widget

    def _inner_check(button):
        callback()

    button = widgets.Button(
        description="Check answer", icon="check", style=dict(button_color="lightgreen")
    )
    button.on_click(_inner_check)

    return widgets.VBox([widget, button])


def display_questions(questions: list[Question], as_group=True):
    """
    Displays a list of questions.

    TODO: Document as_group
    """
    if as_group:
        display(question_group(questions))
    else:
        for question in questions:
            # We are currently only interesting in displaying the question widget
            # and do not care about the eval
            display(singleton_group(question))

    # TODO


def question_group(
    questions: list[Question], num_displayed: int = None
) -> widgets.Output:
    """

    Makes a widget of all the questions, along with a submit button.

    Args:
        questions (list[Question]):
        num_displayed (int): The number of questions to be displayed at once.

    Upon submission, a separate field for output feedback for the whole group will be displayed.
    The feedback is determined by the aggregate evaluation functions of each question.
    Depending on whether the submission was approved or not, a "try again" button will appear, which rerenders the group with new questions.

    Returns:
        An Output widget containing the elements:

        - VBox (questions)
        - Button (submit)
        - Output (text feedback)
        - Button (try again)

    """

    num_displayed = num_displayed or len(questions)

    # A group of questions is referred to as a 'quiz'. Could rename back to group if confusing.

    output = widgets.Output()  # This the output for *this* group (or quiz).

    def render_quiz():
        with output:
            clear_output(wait=True)

            # Suggestion:
            random.shuffle(questions)
            questions_displayed = questions[0:num_displayed]

            display(build_quiz(questions_displayed))

    def build_quiz(questions) -> widgets.Box:
        # Unpack
        question_boxes, eval_functions, feedback_callbacks = zip(
            *(make_question(question) for question in questions)
        )

        def _inner_check(button):
            # Rename this function to e.g. 'check_answers'?

            def group_evaluation() -> float:
                return sum(func() if func() else 0 for func in eval_functions)

            def approved(evaluation: float):
                return len(questions) == evaluation

            def feedback(approved: bool):
                # Maybe have evaluation here as argument to have more fine-grained feedback messages.
                return "All questions are correct!" if approved else "Wrong!"

            is_approved = approved(group_evaluation())

            with feedback_output:
                print(feedback(is_approved))

            for callback in feedback_callbacks:
                callback()

            if not is_approved:
                retry_btn.layout.display = "block"

        # The text output.
        feedback_output = widgets.Output()

        retry_btn = widgets.Button(
            description="Try again",
            icon="refresh",
            style=dict(button_color="lightgreen"),
        )
        retry_btn.layout.display = "none"
        retry_btn.on_click(lambda btn: render_quiz())

        check_btn = widgets.Button(
            description="Check answer",
            icon="check",
            style=dict(button_color="lightgreen"),
        )
        check_btn.on_click(_inner_check)

        questions_box = widgets.VBox(question_boxes, layout=dict(border="solid"))

        return widgets.VBox([questions_box, check_btn, feedback_output, retry_btn])

    render_quiz()
    return output


def display_json(questions: str, as_group=True):
    """
    Helper function for displaying based on the json-string from the FaceIT-format.
    """

    questions_dict = json.loads(questions)

    display_questions(questions_dict["questions"], as_group=as_group)
