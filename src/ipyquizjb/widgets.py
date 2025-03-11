import ipywidgets as widgets
# Uses any because the pyodide kernel is on a Python version that don't support typing generics.
from typing import Any 

def RadioButtons(options: list[Any]) -> widgets.VBox:
    """
    Custom widget that simulates radio buttons through checkboxes.

    Done this way because ipywidgets.RadioButtons don't render Latex correctly
    """
    def changeHandler(change):
        # Set all other checkboxes to unchecked
        if change.new:
            for checkbox in checkboxes:
                if checkbox == change.owner:
                    continue # Skip self
                checkbox.value = False

    checkboxes = []
    for option in options:
        checkbox = widgets.Checkbox(value=False, description=option, indent=False, 
            layout={'width': 'max-content'})
        
        checkbox.observe(changeHandler, names="value")
        checkboxes.append(checkbox)     

    return widgets.VBox(checkboxes)
