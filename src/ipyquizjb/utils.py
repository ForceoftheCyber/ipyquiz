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
