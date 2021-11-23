FROM python:3.7-alpine

LABEL "com.github.actions.name"="SpinCar PR Linter"
LABEL "com.github.actions.description"="GitHub Action to run linters against pull requests and annotate"
LABEL "com.github.actions.icon"="thumbs-up"
LABEL "com.github.actions.color"="green"

RUN apk add --no-cache git bash jq curl
RUN pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install --no-cache -r /requirements.txt
RUN python --version; pip --version; flake8 --version; cfn-lint --version

COPY src /src
CMD ["/src/entrypoint.sh"]
