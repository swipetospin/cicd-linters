"""Define the Flake8Annotator class."""

from annotator import Annotator


class Flake8Annotator(Annotator):
    """The Flake8Annotator class annotates GitHub PRs with the results of the flake8 linter."""

    name = 'flake8_annotator'

    def __init__(self, linter_output_file: str) -> None:
        """Construct Flake8Annotator."""
        Annotator.__init__(self, linter_output_file)

    def compile_annotations(self) -> None:
        """Create the list of annotations that will be posted to the PR."""
        for file_path, error_list in self.lint_results.items():
            if not error_list:
                continue
            for i, error in enumerate(error_list):
                self.add_annotation(
                    file=file_path,
                    severity='notice',  # Flake8 doesn't output severity levels.
                    sline=error['line_number'],
                    eline=error['line_number'],
                    scol=error['column_number'],
                    ecol=error['column_number'],
                    message=f'{error["text"]} ({error["code"]})',
                )


if __name__ == '__main__':
    Flake8Annotator('flake8_output.json').annotate_pr()
