"""
Simple test that checks that the output of the display_functions are correct
"""
from ipyquizjb.questions import display_questions, question_group
import ipywidgets as widgets
from IPython.display import display

def test_text():
    questions = [
    {
      "type": "TEXT",
      "body": "Is this a numeric question?",
      "notes": ["No"]
    }
    ]
    output = question_group(questions)
    # display(output)

    assert isinstance(output, widgets.Output)
    # title  = output
    # assert False