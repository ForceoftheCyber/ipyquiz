import json
from ipyquizjb.utils import get_evaluation_color, display_message_on_error
import ipywidgets as widgets
from IPython.display import display, clear_output, YouTubeVideo
import random

from ipyquizjb.types import QuestionWidgetPackage, Question, AdditionalMaterial

from ipyquizjb.question_widgets import (
    multiple_choice,
    multiple_answers,
    no_input_question,
    numeric_input,
)


def make_question(question: Question) -> QuestionWidgetPackage:
    """
    Makes a question.
    Delegates to the other questions functions based on question type.
    """
    match question["type"]:
        case "MULTIPLE_CHOICE" if "answer" in question and len(question["answer"]) == 1:
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
            assert "answer" in question
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
            assert "answer" in question
            if isinstance(question["answer"], list):
                raise TypeError(
                    "question['answer'] should not be a list when question type is multiple choice"
                )
            return numeric_input(
                question=question["body"], correct_answer=float(
                    question["answer"])
            )

        case "TEXT":
            solution_notes = question["notes"] if "notes" in question else []

            return no_input_question(question=question["body"], solution=solution_notes)

        case _:
            raise NameError(f"{question['type']} is not a valid question type")


def question_group(
    questions: list[Question], 
    additional_material: AdditionalMaterial | None = None
) -> widgets.Box:
    """
    Makes a widget of all the questions, along with a submit button.

    Upon submission, a separate field for output feedback for the whole group will be displayed.
    The feedback is determined by the aggregate evaluation functions of each question.
    Depending on whether the submission was approved or not, a "try again" button will appear, which rerenders the group with new questions.

    Args:
        questions (list[Question]):
        num_displayed (int): The number of questions to be displayed at once.

    Returns:
        An Output widget containing the elements:

        - VBox (questions)
        - Button (submit)
        - Output (text feedback)
        - Button (try again)

    """
    # Splits questions into the initials and the retry pool
    initial_questions = []
    retry_questions = []
    for question in questions:
        # Will default to initial, if not provided
        if "when" not in question or question["when"] == "initial":
            initial_questions.append(question)
        elif question["when"] == "retry":
            retry_questions.append(question)
    if len(retry_questions) == 0:
        # Use same questions for retry if there are no designated
        # retry questions.
        retry_questions = initial_questions

    # Will use the same number of questions for retry_pool
    num_displayed = len(initial_questions)

    output = widgets.Output()  # This the output containing the whole group
    material_output = widgets.Output()

    if (additional_material is not None):
        def render_additional_material():
            with material_output:
                body = additional_material["body"]
                match additional_material["type"]:
                    case "TEXT":
                        # Styled to h3, because p tag doesn't work
                        styled_text = f'<h3 style="font-size: 1em; font-weight: normal; line-height: normal">{body}</h3>'
                        display(widgets.HTML(styled_text))
                    case "VIDEO":
                        display(YouTubeVideo(body))
                    case "CODE":
                        display(widgets.HTML(body))

        render_additional_material()
        material_output.layout.display = "none"

    def render_group(first_render: bool):
        """
        first_render is True if inital_questions should be display,
        False if they should be taken from the retry pool.
        """
        with output:
            clear_output(wait=True)

            if first_render:
                questions_displayed = initial_questions
            else:
                # Randomizes questions
                random.shuffle(retry_questions)
                questions_displayed = retry_questions[0:num_displayed]

            display(build_group(questions_displayed))

    def build_group(questions) -> widgets.Box:
        question_boxes, eval_functions, feedback_callbacks = zip(
            *(make_question(question) for question in questions))

        def group_evaluation():
            if any(func() is None for func in eval_functions):
                # Returns None if any of the eval_functions return None.
                return None

            max_score = len(questions)
            group_sum = sum(func() for func in eval_functions)

            return group_sum / max_score  # Normalized to 0-1

        def feedback(evaluation: float | None):
            if evaluation == None:
                return "Some questions are not yet answered"
            elif evaluation == 1:
                return "All questions are correctly answered!"
            elif evaluation == 0:
                return "Wrong! No questions are correctly answered"
            return "Partially correct! Some questions are correctly answered"

        feedback_output = widgets.Output()
        feedback_output.layout = {"padding": "0.25em", "margin": "0.2em"}

        def feedback_callback(button):
            evaluation = group_evaluation()

            with feedback_output:
                # Clear output in case of successive calls
                feedback_output.clear_output()

                # Print feedback to output
                print(feedback(evaluation))

                # Sets border color based on evaluation
                feedback_output.layout.border_left = f"solid {get_evaluation_color(evaluation)} 1em"

            if evaluation is None:
                # If some questions are not answered, only give feedback about them
                for i, eval_function in enumerate(eval_functions):
                    if eval_function() is None:
                        feedback_callbacks[i]()
                return

            for callback in feedback_callbacks:
                callback()

            if evaluation != 1:
                # Exchange check_button for retry_button if wrong answers
                check_button.layout.display = "none"
                retry_button.layout.display = "block"
                material_output.layout.display = "block"

        check_button = widgets.Button(description="Check answer", icon="check",
                                      style=dict(
                                          button_color="lightgreen"
                                      ),
                                      layout=dict(width="auto"))
        check_button.on_click(feedback_callback)

        retry_button = widgets.Button(
            description="Try again with new questions",
            icon="refresh",
            style=dict(
                button_color="orange"
            ),
            layout=dict(width="auto")
        )
        retry_button.layout.display = "none"  # Initially hidden
        retry_button.on_click(lambda btn: render_group(False))

        questions_box = widgets.VBox(question_boxes, layout=dict(
            padding="1em"
        ))

        return widgets.VBox([questions_box, widgets.HBox([check_button, retry_button]), feedback_output])

    render_group(True)
    return widgets.VBox([output, material_output])


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


@display_message_on_error()
def display_questions(questions: list[Question], 
                      as_group=True, 
                      additional_material: AdditionalMaterial | None = None):
    """
    Displays a list of questions.

    If as_group is true, it is displayed as a group with one "Check answer"-button,
    otherwise, each question gets a button.
    """
    # If only text questions: no reason to group, and add no check-answer-button
    only_text_questions = all(
        question["type"] == "TEXT" for question in questions)

    if as_group and not only_text_questions:
        display(question_group(questions, additional_material=additional_material))
    else:
        for question in questions:
            display(singleton_group(question))


@display_message_on_error()
def display_json(questions: str, 
                 as_group=True):
    """
    Displays question based on the json-string from the FaceIT-format.

    Delegates to display_questions. 
    """

    questions_dict = json.loads(questions)

    if ("additional_material" in questions_dict):
        display_questions(questions_dict["questions"], as_group=as_group,
                          additional_material=questions_dict["additional_material"])
    else:
        display_questions(questions_dict["questions"], as_group=as_group)
