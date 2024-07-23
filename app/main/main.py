from flask import Blueprint, render_template, current_app

main = Blueprint(
    "main",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/main",
)


@main.route("/")
def index():
    """ 
    Главная страцица.

    Parameters:
        GET:/

    Returns:
        Рендеринг шаблона main/index.html.

    """
    current_app.logger.debug('main')
    return render_template("main/index.html")
