import json
import ipywidgets as widgets
from IPython.display import display

from ipyquizjb.types import QuestionWidgetPackage, Question
from ipyquizjb.question_widgets import multiple_choice, multiple_answers, no_input_question, numeric_input


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

            # Will always be considered a right solution (does not influence score computation)
            always_correct = (lambda: True)
            return no_input_question(question=question["body"], solution=solution_notes), always_correct, (lambda: None)

        case _:
            raise NameError(f"{question['type']} is not a valid question type")


def singleton_group(question: Question):
    # Unpack to not be part of a group?

    widget, _, callback = make_question(question)

    if question["type"] == "TEXT":
        return widget

    def _inner_check(button):
        callback()

    button = widgets.Button(description="Check answer", icon="check",
                            style=dict(
                                button_color="lightgreen"
                            ))
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


def question_group(questions: list[Question]) -> widgets.Box:
    """
    Makes a VBox of all the questions.
    Has a separate field for output feedback for the whole group, 
    evaluated based on a cumulation of the evaluation functions of each question.

    VBox
    Button (submit)
    Output
    """

    question_boxes, eval_functions, feedback_callbacks = zip(
        *(make_question(question) for question in questions))

    # for question in questions:
    #     widget_box, eval_func, feedback = make_question(question)
    #     question_boxes.append(widget_box)
    #     eval_functions.append(eval_func)
    #     feedback_callbacks.append(feedback)

    def group_evaluation():
        group_sum = 0
        for func in eval_functions:
            group_sum += func() if func() else 0
        return group_sum

    def feedback(evaluation: float):
        max_score = len(questions)
        if evaluation == max_score:
            return "All questions are correct!!"

        return "Wrong!!"

    output = widgets.Output()

    def _inner_check(button):
        with output:
            output.outputs = [
                {'name': 'stdout', 'text': feedback(group_evaluation()), 'output_type': 'stream'}]

        for callback in feedback_callbacks:
            callback()

    button = widgets.Button(description="Check answer", icon="check",
                            style=dict(
                                button_color="lightgreen"
                            ))
    button.on_click(_inner_check)

    questions_box = widgets.VBox(question_boxes, layout=dict(
        border="solid"
    ))

    return widgets.VBox([questions_box, button, output])


def display_json(questions: str, as_group=True):
    """
    Helper function for displaying based on the json-string from the FaceIT-format. 
    """

    questions_dict = json.loads(questions)

    display_questions(questions_dict["questions"], as_group=as_group)
