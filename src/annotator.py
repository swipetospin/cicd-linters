"""Define the Annotator class."""

from datetime import datetime, timezone
from json import loads
from os import environ
from pprint import pprint

from requests import post


class Annotator:
    """The Annotator class annotates GitHub PRs with the results of a linter."""

    uri = 'https://api.github.com'
    accept_header = 'application/vnd.github+json'
    auth_header = f'token {environ["GITHUB_TOKEN"]}'

    name = 'annotator'

    def __init__(self, linter_output_file: str) -> None:
        """Construct Annotator."""
        self.files_with_errors = set()

        with open(environ['GITHUB_EVENT_PATH']) as f:
            self.event = loads(f.read())
        with open(linter_output_file) as f:
            self.lint_results = loads(f.read())

        self.annotations = []

    @property
    def branch_commit_hash(self):
        """Return the latest commit hash of the branch HEAD."""
        if self.event.get('pull_request'):
            return self.event.get('pull_request')['head']['sha']
        return self.event['check_suite']['pull_requests'][0]['base']['sha']

    @property
    def repo_full_name(self):
        """Return the name of the repository the PR was created in."""
        return self.event['repository']['full_name']

    def annotate_pr(self):
        """Create the annotations and POST them to the PR on GitHub."""
        self.compile_annotations()

        summary = f'''
        {self.name} run summary:

        Files with Errors: {len(self.files_with_errors)}
        Total Errors: {len(self.annotations)}
        '''

        # The GitHub API is only able to accept fifty annotations at a time.
        # TODO: Work around this limit.
        if len(self.annotations) > 50:
            self.annotations = self.annotations[:50]

        payload = {
            'name': self.name,
            'head_sha': self.branch_commit_hash,
            'status': 'completed',
            'conclusion': 'success' if len(self.annotations) == 0 else 'failure',
            'completed_at': datetime.now(timezone.utc).isoformat(),
            'output': {
                'title': f'{self.name} result',
                'summary': summary,
                'text': f'{self.name} results',
                'annotations': self.annotations,
            },
        }
        pprint(payload)
        response = post(
            f'{self.uri}/repos/{self.repo_full_name}/check-runs',
            headers={
                'Accept': self.accept_header,
                'Authorization': self.auth_header,
            },
            json=payload,
        )
        pprint(response.content.decode())
        response.raise_for_status()

    def compile_annotations(self) -> None:
        """Create the list of annotations that will be posted to the PR.

        This method must be overridden in an inherited class.
        """
        raise NotImplementedError

    def add_annotation(
        self, file: str, sline: str, eline: str, scol: str, ecol: str, severity: str, message: str
    ) -> None:
        """Add a single annotation."""
        def get_annotation_level(severity: str) -> str:
            """Return one of GitHub's annotation levels.

            Attempt to match up the linter's severity level with one of the three that GitHub uses;
            "warning", "failure", or "notice".
            """
            if severity.lower() in ['warning', 'warn']:
                return 'warning'
            if severity.lower() in ['error', 'fail', 'failure']:
                return 'failure'
            return 'notice'

        if file not in self.files_with_errors:
            self.files_with_errors.add(file)

        self.annotations.append(dict(
            path=file,
            start_line=sline,
            end_line=eline,
            annotation_level=get_annotation_level(severity),
            message=message,
            start_column=scol,
            end_column=ecol,
        ))
