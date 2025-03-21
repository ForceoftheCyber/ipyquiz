import json
import ipywidgets as widgets
from IPython.display import display
from collections.abc import Callable
from typing import Any

from ipyquizjb.types import QuestionWidgetPackage, Question, EvaluationFunction


def multiple_choice(question: str,
                    options: list[Any],
                    correct_option: Any,
                    description: str = "") -> QuestionWidgetPackage:
    """
    Multiple-choice-single-answer type question.

    Delegates to generic_question.
    """
    options_widget = widgets.ToggleButtons(
        options=options,
        value=None,
        disabled=False,
        style={"button_width": "auto"},
    )

    def eval_func():
        if options_widget.value is None:
            return None
        return float(options_widget.value == correct_option)

    return generic_question(question=question,
                            input_widget=options_widget,
                            evaluation_function=eval_func,
                            description=description)


def multiple_answers(question: str,
                     options: list[Any],
                     correct_answers: list[Any]) -> QuestionWidgetPackage:
    """
    Multiple-choice-multiple-answers type question.

    Delegates to generic_question.

    """
    buttons = [widgets.ToggleButton(
        value=False, description=option) for option in options]

    def feedback(evaluation_result):
        if evaluation_result == None:
            return "Please pick an answer"
        elif evaluation_result == 0:
            return "Correct answer"
        else:
            return f"Correct answers: {evaluation_result}/{len(correct_answers)}"

    def eval_func():
        # Returns the proportion of correct answers.

        answers = set(
            button.description for button in buttons if button.value)
        if len(answers) == 0:
            return None

        num_correct_answers = len(answers.intersection(correct_answers))

        return num_correct_answers / len(correct_answers)

    return generic_question(question=question,
                            input_widget=widgets.HBox(buttons),
                            evaluation_function=eval_func,
                            feedback=feedback)


def standard_feedback(evaluation_result: Any):
    if evaluation_result == None:
        return "No answer selected"
    elif evaluation_result == 0:
        return "Wrong answer!"
    else:
        return "Correct!"


def generic_question(question: str,
                     input_widget: widgets.Widget,
                     evaluation_function: EvaluationFunction,
                     description: str = "",
                     feedback: Callable[[Any], str] = standard_feedback) -> QuestionWidgetPackage:
    """
    Abstract question function used by the other question types to display questions.

    Delegates to generic_question.

    params:
    - question: Title of question
    - input_widget: Widget used for getting user input
    - evaluation_function: a function returning an evaluation of the answer provided based on the input widget
    - description: Additional text to be provided with the question
    - feedback: A function giving textual feedback based on the result of the evaluation_function

    """

    title_widget = widgets.HTMLMath(value=f"<h3>{question}</h3>")
    description_widget = widgets.HTMLMath(value=f"<p>{description}</p>")

    output = widgets.Output()

    def feedback_callback():
        with output:
            output.outputs = [
                {'name': 'stdout', 'text': feedback(evaluation_function()), 'output_type': 'stream'}]

    layout = widgets.VBox([title_widget,
                           description_widget,
                           widgets.HBox([input_widget],
                                        layout=widgets.Layout(padding="10px 20px 10px 20px", border="solid")),
                           widgets.VBox([output],
                                        layout=widgets.Layout(margin="10px 10px 0px 0px"))])

    return layout, evaluation_function, feedback_callback


def numeric_input(question: str, correct_answer: float) -> QuestionWidgetPackage:
    """
    Question with box for numeric input.

    Delegates to generic_question.
    """

    input_widget = widgets.FloatText(
        value=None,
    )

    def eval_func():
        if input_widget.value is None:
            return None
        return float(input_widget.value == correct_answer)

    return generic_question(question=question,
                            input_widget=input_widget,
                            evaluation_function=eval_func)


def code_question(question: str, expected_outputs: list[tuple[tuple, Any]]) -> QuestionWidgetPackage:
    """
    Code question that uses a textbox for the user to write.
    The provided function is tested against the expected_outputs.

    Delegates to generic_question.

    params:
    - expected_output - a list of pairs in the format:
        - ((inputs), expected_output)
        - Example: [
            ((2, 4), 8)
        ]
    """

    input_widget = widgets.Text(
        description="What is the name of your function?", placeholder="myFunction",
        style=dict(description_width="initial"))

    def eval_func():
        function_name = input_widget.value
        if function_name not in globals():
            # Error handling
            return None

        function = globals()[function_name]
        return all([function(*test_input) == test_output
                    for test_input, test_output in expected_outputs])

    def feedback(evaluation_result):
        if evaluation_result is None:
            return "No function defined with that name. Remember to run the cell to define the function."
        if evaluation_result:
            return "Correct!"
        else:
            return "Incorrect answer!"

    return generic_question(question=question, input_widget=input_widget, evaluation_function=eval_func, feedback=feedback)


def no_input_question(question: str, solution: list[str]) -> widgets.Box:
    """
    Questions with no input. 
    Reveals solution on button click if solution exists.

    Corresponds to the FaceIT question type: TEXT.
    """
    title_widget = widgets.HTMLMath(value=f"<h3>{question}</h3>")

    if len(solution) == 0:
        # If no solution provided
        no_solution_widget = widgets.HTML(
            value="<p><i>This question has no suggested solution.</i></p>")
        return widgets.VBox([title_widget, no_solution_widget])

    # Solution has been provided

    solution_box = widgets.VBox(
        [widgets.HTMLMath(value=f"<p>{sol}</p>") for sol in solution])
    solution_box.layout.display = "none"  # Initially hidden

    def reveal_solution(button):
        if solution_box.layout.display == "none":
            solution_box.layout.display = "block"
            button.description = "Hide solution"
        else:
            solution_box.layout.display = "none"
            button.description = "Show solution"

    button = widgets.Button(description="Show solution", icon="check",
                            style=dict(
                                button_color="lightgreen"
                            ))

    button.on_click(reveal_solution)

    return widgets.VBox([title_widget, button, solution_box])


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
