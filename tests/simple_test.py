import ipywidgets as widgets
import playwright.sync_api
from IPython.display import display
from ipyquizjb import display_questions


def test_multiple_choice(solara_test, page_session: playwright.sync_api.Page):
    # The test code runs in the same process as solara-server (which runs in a separate thread)
    questions = [
        {
            "type": "MULTIPLE_CHOICE",
            "body": "What is the derivative of \\( \\sin(x) \\)?",
            "answers": [
                "\\( -\\cos(x) \\).",
                "\\( \\tan(x) \\).",
                "\\( \\cos(x) \\)."
            ],
            "answer": ["\\( \\cos(x) \\)."],
            "notes": ["The derivative of \\( \\sin(x) \\) is \\( \\cos(x) \\)."]
        }
    ]

    display_questions(questions)

    button_sel = page_session.locator("text=\\( -\\cos(x) \\).")
    button_sel.wait_for()
    button_sel.click()
    # page_session.locator("text=Tested event").wait_for()
