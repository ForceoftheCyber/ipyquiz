"""
This files includes some functions for adding HTML to workaround
issues with rendering latex and ipywidgets together.
"""

from IPython.display import display, HTML
import ipywidgets as widgets


def latexize(widget: widgets.DOMWidget):
    """
    Adds an HTML class to the widget that is used to tell
    MathJax to render it as math. 
    """
    widget.add_class("ipyquizjb-render-math")
    return widget


def setup_latex():
    """
    Sets up functions for Math/Latex rendering 
    and does an initial typesetting.

    NOTE:
    The version of MathJax seems to change when using IPython.display.HTML,
    but exactly when it happens varies, we are therefore checking the version
    before calling the corresponding typesetting function.
    """
    display(HTML("""<script>
function versionAgnosticTypeset(element) {
    if (MathJax.version.startsWith("3")) {
        if (element) {
            MathJax.typeset([element]) 
        } else {
            MathJax.typeset()
        }   
    } else {
        if (element) {
            MathJax.Hub.Queue(['Typeset', MathJax.Hub, element]);
        } else {
            MathJax.Hub.Queue(['Typeset', MathJax.Hub]);
        }   
    }
}

// Makes buttons with rendered math clickable by
// listening for click on the math and then resending a math
function make_latex_buttons_clickable() {
    // Get elements where either CHTML or PreviewHTML is the renderer
    const math_elements = [...document.getElementsByClassName("MathJax_CHTML"), ...document.getElementsByClassName("MathJax_PHTML")]
    for (el of document.getElementsByClassName("mjx-chtml MathJax_CHTML")) {
        if (element.hasAttribute('clickable-math-listener')) {
            // Skip if listener is already attached
                 return;
        }
        el.addEventListener("click", (e) => {
            // Find the actual button and click it
            e.stopPropagation();
            var element = e.target;
            var parent = element.parentElement
            while (!parent.classList.contains("jupyter-button")) {
                parent = parent.parentElement;
            }
            parent.click();	
        });
        el.setAttribute("clickable-math-listener", "");
    };
}
                
// Used on every rerender
function typesetAll() {
    console.log("Rerender typeset");
    for (element of document.getElementsByClassName("ipyquizjb-render-math")) {
        versionAgnosticTypeset(element);
    }
}


// Will repeatedly check for MathJax version 2 and change renderer
// if its available. Will stop after a minute, if it is not found.
function changeRendererOnReady(retries) {
    // If we have not yet overridden version 3, we should
    // use another renderer that does not have a visual bug on some devices (e. g. Mac).
    // PreviewHTML is not available for MathJax version 3, though.
    if (!MathJax.version.startsWith("3")) {
        MathJax.Hub.setRenderer("PreviewHTML");
        versionAgnosticTypeset();
    } else if (retries < 600) {
        setTimeout(() => {changeRendererOnReady(retries+1)}, 100)
    }
}

// Initiate busy waiting
setTimeout(() => {changeRendererOnReady(0)}, 0)
</script>"""))


def render_latex():
    """
    Typesets elements with the "ipyquizjb-render-math"-class.
    """
    display(HTML("<script>typesetAll()</script>"))


def make_latex_buttons_clickable():
    """
    Schedules the function for making buttons with latex clickable
    after the Latex is typeset.
    """
    display(HTML("""<script>
MathJax.Hub.Queue(make_latex_buttons_clickable)
</script>"""))
