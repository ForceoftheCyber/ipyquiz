import json
from ipyquizjb.utils import get_evaluation_color
import ipywidgets as widgets
from IPython.display import display

from ipyquizjb.types import QuestionWidgetPackage, Question
from ipyquizjb.question_widgets import multiple_choice, multiple_answers, no_input_question, numeric_input


def make_question(question: Question) -> QuestionWidgetPackage:
    """
    Makes a question.
    Delegates to the other questions functions based on question type.
    """
    match question["type"]:
        case "MULTIPLE_CHOICE" if len(question["answer"]) == 1:
            # Multiple choice, single answer
            # TODO: Add validation of format?
            if "answers" not in question or not question["answers"]:
                raise AttributeError(
                    "Multiple choice should have list of possible answers (options)")
            return multiple_choice(question=question["body"], options=question["answers"], correct_option=question["answer"][0])

        case "MULTIPLE_CHOICE":
            # Multiple choice, multiple answer
            if isinstance(question["answer"], str):
                raise TypeError(
                    "question['answer'] should be a list when question type is multiple choice")
            if "answers" not in question or not question["answers"]:
                raise AttributeError(
                    "Multiple choice should have list of possible answers (options)")
            return multiple_answers(question=question["body"], options=question["answers"], correct_answers=question["answer"])

        case "NUMERIC":
            if isinstance(question["answer"], list):
                raise TypeError(
                    "question['answer'] should not be a list when question type is multiple choice")
            return numeric_input(question=question["body"], correct_answer=float(question["answer"]))

        case "TEXT":
            solution_notes = question["notes"] if "notes" in question else []
            
            return no_input_question(question=question["body"], solution=solution_notes)

        case _:
            raise NameError(f"{question['type']} is not a valid question type")


def question_group(questions: list[Question]) -> widgets.Box:
    """
    Combines a list of questions in a group, returns a ipywidgets.Box
    consisting of the individual questions boxes.
    Has a separate output for output feedback for the whole group, 
    evaluated based on a cumulation of the evaluation functions of each question.
    """

    question_boxes, eval_functions, feedback_callbacks = zip(
        *(make_question(question) for question in questions))

    def group_evaluation():
        max_score = len(questions)
        group_sum = sum(func() if func() else 0 for func in eval_functions)

        return group_sum / max_score  # Normalized to 0-1

    def feedback(evaluation: float):
        if evaluation == 1:
            return "All questions are correctly answered!"
        elif evaluation == 0:
            return "Wrong! No questions are correctly answered."
        return "Partially correct! Some questions are correctly answered."

    output = widgets.Output()
    output.layout = {"padding": "0.25em", "margin": "0.2em"}

    def feedback_callback(button):
        evaluation = group_evaluation()

        with output:
            # Clear output in case of successive calls
            output.clear_output()

            # Print feedback to output
            print(feedback(evaluation))

            # Sets border color based on evaluation
            output.layout.border_left = f"solid {get_evaluation_color(evaluation)} 1em"

        for callback in feedback_callbacks:
            callback()

    button = widgets.Button(description="Check answer", icon="check",
                            style=dict(
                                button_color="lightgreen"
                            ))
    button.on_click(feedback_callback)

    questions_box = widgets.VBox(question_boxes, layout=dict(
        border="solid"
    ))

    return widgets.VBox([questions_box, button, output])


def singleton_group(question: Question) -> widgets.Box:
    """
    Makes a question group with a single question,
    including a button for evaluation the question. 
    """

    widget, _, feedback_callback = make_question(question)

    if question["type"] == "TEXT":
        # Nothing to check if the question has no input
        return widget

    button = widgets.Button(description="Check answer", icon="check",
                            style=dict(
                                button_color="lightgreen"
                            ))
    button.on_click(lambda button: feedback_callback())

    return widgets.VBox([widget, button])


def display_questions(questions: list[Question], as_group=True):
    """
    Displays a list of questions.

    If as_group is true, it is displayed as a group with one "Check answer"-button,
    otherwise, each question gets a button.
    """
    if as_group:
        display(question_group(questions))
    else:
        for question in questions:
            display(singleton_group(question))


def display_json(questions: str, as_group=True):
    """
    Displays question based on the json-string from the FaceIT-format.

    Delegates to display_questions. 
    """

    questions_dict = json.loads(questions)

    display_questions(questions_dict["questions"], as_group=as_group)
