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

    Assumes MathJax version 3.
    """
    display(HTML("""<script>
// Makes buttons with rendered math clickable by
// listening for click on the math and then 
// resending a click to the actual button
function make_latex_buttons_clickable() {
    for (element of document.querySelectorAll("button mjx-container")) {
        if (element.hasAttribute('clickable-math-listener')) {
            // Skip if listener is already attached
            continue;
        }
        element.addEventListener("click", (e) => {
            // Find the actual button and click it
            e.stopPropagation();
            var parent = e.target.parentElement
            while (!parent.classList.contains("jupyter-button")) {
                parent = parent.parentElement;
            }
            parent.click();	
        });
        element.setAttribute("clickable-math-listener", "");
    };
}

function processAllTikz() {
    const scripts = document.getElementsByTagName('script');
    var tikzScripts = Array.prototype.slice.call(scripts).filter(e => e.getAttribute('type') === 'text/tikz');
    tikzScripts.reduce(async (promise, element) => {
        await promise;
        return process_tikz(element);
    }, Promise.resolve());
}
                
// Used on every rerender
function typesetAll() {
    console.log("Rerender typeset");
    MathJax.typeset([...document.getElementsByClassName("ipyquizjb-render-math")]);
    if (window.process_tikz) {
        processAllTikz()
    }
    make_latex_buttons_clickable();
}

typesetAll();
</script>"""))


def render_latex():
    """
    Typesets elements with the "ipyquizjb-render-math"-class.
    """
    display(HTML("<script>typesetAll();</script>"))
