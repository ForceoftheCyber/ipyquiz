from typing import TypedDict, Literal, NotRequired
import json
import ipywidgets as widgets
from IPython.display import display
from collections.abc import Callable
from typing import Any


def multiple_choice(question: str,
                    options: list[Any],
                    correct_option: Any,
                    description: str = "") -> widgets.Widget:
    """
    Multiple-choice-single-answer type question.

    Delegates to generic_question.
    """
    options_widget = widgets.ToggleButtons(
        options=options,
        value=None,
        disabled=False
    )

    def eval_func(widget):
        if widget.value is None:
            return None
        return widget.value == correct_option

    return generic_question(question=question,
                            input_widget=options_widget,
                            evaluation_function=eval_func,
                            description=description)


def multiple_answers(question: str,
                     options: list[Any],
                     correct_answers: list[Any]) -> widgets.Widget:
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

    def eval_func(widget: widgets.HBox):
        answers = set(
            button.description for button in widget.children if button.value)
        if len(answers) == 0:
            return None
        # Evaluates number of correct choices minus number of incorrect choices.
        return len(answers.intersection(correct_answers)) - len(answers.difference(correct_answers))

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
                     evaluation_function: Callable[[widgets.Widget], Any],
                     description: str = "",
                     feedback: Callable[[Any], str] = standard_feedback) -> widgets.Widget:
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

    def _inner_check(button):
        with output:
            output.outputs = [
                {'name': 'stdout', 'text': feedback(evaluation_function(input_widget)), 'output_type': 'stream'}]

    button = widgets.Button(description="Check answer", icon="check",
                            style=dict(
                                button_color="lightgreen"
                            ))
    button.on_click(_inner_check)

    layout = widgets.VBox([title_widget,
                           description_widget,
                           widgets.HBox([input_widget],
                                        layout=widgets.Layout(padding="10px 20px 10px 20px", border="solid")),
                           widgets.VBox([button, output],
                                        layout=widgets.Layout(margin="10px 10px 0px 0px"))])

    return layout


def numeric_input(question: str, correct_answer: float) -> widgets.Widget:
    """
    Question with box for numeric input.

    Delegates to generic_question.
    """

    input_widget = widgets.FloatText(
        value=None,
    )

    def eval_func(widget):
        if widget.value is None:
            return None
        return widget.value == correct_answer

    return generic_question(question=question,
                            input_widget=input_widget,
                            evaluation_function=eval_func)


def code_question(question: str, expected_outputs: list[tuple[tuple, Any]]) -> widgets.Widget:
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

    def eval_func(widget):
        function_name = widget.value
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

def no_input_question(question: str, solution: str) -> widgets.Widget:
    """
    Questions with no input. Reveals solution on button click.
    
    Corresponds to the FaceIT question type: TEXT.
    """
    title_widget = widgets.HTMLMath(value=f"<h3>{question}</h3>")

    solution_box = widgets.HTMLMath(value=f"<p>{solution}</p>")
    solution_box.layout.display = "none"  # Initially hidden

    def reveal_solution(button):
        solution_box.layout.display = "block"

    button = widgets.Button(description="Show solution", icon="check",
                            style=dict(
                                button_color="lightgreen"
                            ))
    
    button.on_click(reveal_solution)

    return widgets.VBox([title_widget, button, solution_box])


class Question(TypedDict):
    type: Literal["MULTIPLE_CHOICE", "NUMERIC", "TEXT"]
    body: str
    answers: NotRequired[list[str]] # Options
    answer: list[str] | str  # Correct answer
    notes: NotRequired[list[str]]


def make_question(question: Question) -> widgets.Widget:
    """
    Delegates to the other questions functions based on question type and returns a widget.
    """
    match question["type"]:
        case "MULTIPLE_CHOICE" if len(question["answer"]) == 1:
            # Multiple choice, single answer
            # TODO: Add validation of format?
            if "answers" not in question or not question["answers"]:
                raise AttributeError("Multiple choice should have list of possible answers (options)")
            return multiple_choice(question=question["body"], options=question["answers"], correct_option=question["answer"][0])

        case "MULTIPLE_CHOICE":
            # Multiple choice, multiple answer
            if isinstance(question["answer"], str):
                raise TypeError(
                    "question['answer'] should be a list when question type is multiple choice")
            if "answers" not in question or not question["answers"]:
                raise AttributeError("Multiple choice should have list of possible answers (options)")
            return multiple_answers(question=question["body"], options=question["answers"], correct_answers=question["answer"])

        case "NUMERIC":
            if isinstance(question["answer"], list):
                raise TypeError(
                    "question['answer'] should not be a list when question type is multiple choice")
            return numeric_input(question=question["body"], correct_answer=float(question["answer"]))

        case "TEXT":
            return no_input_question(question=question["body"], solution=question["answer"])

        case _:
            raise NameError(f"{question['type']} is not a valid question type")


def display_questions(questions: list[Question]):
    """
    Displays a list of questions.
    """
    for question in questions:
        display(make_question(question))


def display_json(questions: str):
    """
    Helper function for displaying based on the json-string from the FaceIT-format. 
    """

    questions_dict = json.loads(questions)

    display_questions(questions_dict["questions"])
