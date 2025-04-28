# ipyquizjb

ipyquizjb is a Python package for use with Jupyter Notebooks that adds support for interactive quizzes based on IPyWidgets controls.

## Installation

### Install through PyPI
```bash
pip install ipyquizjb
```

### Install in Jupyter Notebook (`.ipynb`-files) cell through cell magic
Add the following line to a cell in the notebook and run it:
```ipynb
%pip install ipyquizjb
```
This is the method you have to use when using JupyterBook/TeachBooks with Thebe and a Pyodide kernel.

### Install directly from the github repo
```bash
pip install ipyquizjb @ git+https://github.com/ForceoftheCyber/ipyquiz.git
```

## Quick start

*See the notebook [example.ipynb](examples/example.ipynb) for examples of the quizzes.*

Add a quiz to the notebook using the function `display_package(questions: QuestionPackage, as_group=True)`.
- `questions` is a dictionary of questions and ekstra data in the `QuestionPackage`-format described below under [Question format](#question-format).
- If `as_group` is true, the questions will be displayed in a group with controls for checking the answers and evaluation of the group as a whole. If it is false, each question will have their own "Check answer"-button.

Main functionality for question groups:
- Specify how many questions need to be answered correctly for the group to be considered passed through `passing_threshold`.
- If student does not pass the group, they will be prompted to try again.
    - You can provide extra questions that will only be displayed when trying again by adding `"when": "retry"` to the question dictionary (see below under [Question format](#question-format)). Default is `"initial"` which will display the question as part of the initial rendering. Retrying will pick random questions from the retry pool (questions with `"when": "retry"`), as many as the original group had.
- You can specify additional material that will be shown when the student does not pass a group through `additional_material`.
    - There are three types of additional material: text, video (a YouTube-video) and code (which will render the provided text using the HTML `<pre>`-tag.)
    - The additional_material will be present even after the question group has been answered correctly.
    
If you use ipyquizjb in a frontend environment that supports math rendering through MathJax, math will also be rendered in the quizzes. Remember to escape the backslash before commands so Python will interpret the backslash as a backslash (e.g. `"\\cos(x)"` instead of `"\cos(x)"`).

### Fetching questions from FaceIT
You can fetch questions from [FaceIT](https://faceittools.com/)'s database of questions:
- `display_simple_search(body: str, max_questions: int = 10)` will display a question group with questions fetched from FaceIT based on a search word given in `body`. Change the number of displayed questions by specifying `max_questions`. By default, up to 10 questions will be displayed (limited by number of search results).

### Other display functions
There are also other display functions, that can be utilized.
- `display_questions(questions: list[Question])` takes in just a list of questions (as in `questions["questions"]` under [Question format](#question-format)).
- `display_json(questions: str)` - As `display_package(...)`, but takes as input a json string representation of the question dictionary instead.

### Question types
There are three main question types:
- `MULTIPLE_CHOICE`: Either one or multiple correct answers
- `NUMERIC`: Answer is a float.
- `TEXT`: No input, solution will be shown on click of a button.
    - **Note**: When using TEXT-questions as part of a group, they will be treated as if they have been answered correct in the evaluation (since they have no input). The value set in `passing_threshold` should take this into consideration. 

These question types are supported in the `QuestionPackage`-format, but can also be called directly with their respective functions: `multple_choice(question: Question)`, `multiple_answers(question: Question)`, `numeric_input(question: Question)` or `no_input_question(question: Question)`. 

There is also a code question type (`code_question(question, expected_output)`) that will evaluate a function written in some code cell (defined in the global scope) and will test the provided function against some expected results on the following format: `((inputs), expected_output)` (example: `[((2, 4), 8)]`). 
The code question is standalone and can not be specified and displayed through `display_questions(...)`.

The direct question functions (such as `multiple_choice(...)` and `code_question(...)`) will return a tuple of the widget (which can be displayed through `IPython.display.display(...)`), evaluation function (function evaluating if the given answer is correct) and feedback callback (function that can be called to evaluate the answer and display feedback).

### Question format
The `QuestionPackage`-format is based on the format used by [FaceIT](https://faceittools.com/) but with some extensions to support extra functionality.

```python
questions = {
    "questions": [
        {
            "type": "MULTIPLE_CHOICE",
            "body": "What is the derivative of \\( \\sin(x) \\)?",
            "answers": [
                "\\( -\\cos(x) \\).",
                "\\( \\tan(x) \\).",
                "\\( \\cos(x) \\)."
            ],  # Alternatives
            "answer": ["\\( \\cos(x) \\)."],  # Correct answers, one or more
            "notes": ["This solution explanation will be displayed when the student has answered correctly.", "There can be multiple explanations"],
            "when": "initial", # Optional. "initial" if this should always be displayed on first load, "retry" if it should be part of the pool of questions loaded when trying again with new questions.
        },
        {
            "type": "TEXT",
            "body": "Is this a text answer?",
            "notes": ["Yes"],  # Solution to be displayed when clicking "Show solution"
            "when": "retry",  # Optional, same as above
        },
        {
            "type": "NUMERIC",
            "body": "What's the derivative of z (z'), with respect to x, of z = 4y+x?",
            "answer": "1",
            "when": "retry",
        },
    ],
    "passing_threshold": 0.75,  # Number between 0-1, threshold for passing group
    "status": "success"  # Used when the questions are fetched from FaceIT to indicate if the request was successful
    "additional_material": {
        "type": "TEXT",
        "body": "Extra text that is displayed when students answer wrong to the whole group."
    }
    # Another option for additional_material:
    # "additional_material": {
    # "type": "VIDEO",
    # "body": "dQw4w9WgXcQ"  # YouTube video ID
    # }   
}
```
