from invoke.tasks import task


@task
def check_format(context):
    check_black(context)
    check_flake8(context)
    check_isort(context)


@task
def check_black(context):
    print("### Black ###")
    context.run("black . --check", pty=True)


@task
def check_isort(context):
    print("### isort ###")
    context.run("isort --profile black --check .", pty=True)


@task
def check_flake8(context):
    print("### Flake8 ###")
    context.run("flake8 --version", pty=True)
    context.run("flake8 . --count --statistics", pty=True)


@task
def format_code(context):
    context.run("black . ", pty=True)
    context.run("isort --profile black .", pty=True)


@task
def test(context, args="", path=""):
    """execute pytest with coverage

    args: additional pytest args to pass. ex: -x -v
    path: sub-folder or test file to test to limit scope"""
    with context.cd("src"):
        context.run(
            "pytest --cov=backend "
            f"--cov-report term-missing {args} "
            f"../tests{'/' + path if path else ''}",
            pty=True,
        )


@task
def generate_xml_report(context):
    with context.cd("src"):
        context.run("coverage xml", pty=True)
