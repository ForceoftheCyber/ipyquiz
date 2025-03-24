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

