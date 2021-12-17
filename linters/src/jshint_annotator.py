"""Define the JSHintAnnotator class."""

from annotator import Annotator


class JSHintAnnotator(Annotator):
    """The JSHintAnnotator class annotates GitHub PRs with the results of jshint."""

    name = 'jshint_annotator'

    def __init__(self, linter_output_file: str) -> None:
        """Construct JSHintAnnotator."""
        Annotator.__init__(self, linter_output_file)

    def compile_annotations(self) -> None:
        """Create the list of annotations that will be posted to the PR."""
        for i, error in enumerate(self.lint_results['result']):
            self.add_annotation(
                file=error['file'],
                severity=error['error']['id'].strip('()'),  # example jshint output: "id": "(error)"
                sline=error['error']['line'],
                eline=error['error']['line'],
                scol=error['error']['character'],
                ecol=error['error']['character'],
                message=f'[{error["error"]["code"]}] {error["error"]["reason"]}',
            )


if __name__ == '__main__':
    JSHintAnnotator('jshint_output.json').annotate_pr()
