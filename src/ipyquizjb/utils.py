import ipywidgets as widgets
from ipyquizjb.types import DisplayFunction
from IPython.display import display

def get_evaluation_color(evaluation: float | None) -> str:
    """
    Returns a string with a css color name based on a question evaluation 
    """
    if evaluation == None:
        return "lightgrey"
    elif evaluation == 0:
        return "lightcoral"
    elif evaluation == 1:
        return "lightgreen"
    elif 0 < evaluation < 1:
        return "yellow"
    else:
        # Returns not-real color on error, does not display the border.
        return "none"

def standard_feedback(evaluation: float | None) -> str:
    """
    Returns a standard feedback based on a question evaluation
    """
    if evaluation == None:
        return "No answer selected"
    elif evaluation == 0:
        return "Wrong answer!"
    if evaluation == 1:
        return "Correct!"
    elif 0 < evaluation < 1:
        return "Partially correct!"
    else:
        # Should not happen
        return "Your score could not be correctly calculated"

def disable_input(input_widget: widgets.Box | widgets.Widget):
    if isinstance(input_widget, widgets.Box):
        for child in input_widget.children:
            disable_input(child)
    elif isinstance(input_widget, widgets.Widget) and hasattr(input_widget,"disabled"):
        # Not all widgets can be disabled, only disable those that can be
        input_widget.disabled = True  # type: ignore

def question_title(question: str) -> widgets.Widget:
    """
    Returns a widget for question title with some styling
    """
    return widgets.HTMLMath(value=f"<h2 style='font-size: 1.25em;'>{question}</h2>")

def display_message_on_error(message: str = "Could not display questions."):
    """
    Can be used as a decorator for display functions.
    This will display a error message in case of an exception being thrown.

    Usage:
        put "@display_message_on_error()"
        on the line above the display function definition,
        and optionally provide a custom error message.
    """
    def decorator(display_function: DisplayFunction):
        def wrapper(*args, **kwargs):
            try:
                display_function(*args, **kwargs)
            except Exception:
                # Catches all exceptions
                display(widgets.HTML(f"<p style='font-size: 2em; font-weight: bold; font-style: italic; background-color: lightcoral; padding: 1em'>An error occurred: {message}</p>"))
        return wrapper
    return decorator
