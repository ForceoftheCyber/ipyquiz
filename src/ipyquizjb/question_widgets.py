import ipywidgets as widgets
from typing import Any
from ipyquizjb.types import QuestionWidgetPackage, EvaluationFunction, FeedbackFunction


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
                     feedback: FeedbackFunction = standard_feedback) -> QuestionWidgetPackage:
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

    output = widgets.Output()

    def feedback_callback():
        with output:
            output.outputs = [
                {'name': 'stdout', 'text': feedback(evaluation_function()), 'output_type': 'stream'}]

            if (evaluation_function() == 0):
                output.layout = {"border": "solid red 1em"}

            elif (evaluation_function() == None):
                output.layout = {"border": "Solid yellow 1em"}

            else:
                output.layout = {"border": "solid lightgreen 1em"}

    layout = widgets.VBox([title_widget,
                           widgets.HBox([input_widget],
                                        layout=widgets.Layout(padding="10px 20px 10px 20px", border="solid")),
                           widgets.VBox([output],
                                        layout=widgets.Layout(margin="10px 10px 0px 0px"))])

    return layout, evaluation_function, feedback_callback


def multiple_choice(question: str,
                    options: list[Any],
                    correct_option: Any) -> QuestionWidgetPackage:
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
                            evaluation_function=eval_func)


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
            return "Incorrect answer"
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
