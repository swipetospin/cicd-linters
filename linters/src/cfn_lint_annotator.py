"""Define the CfnLintAnnotator class."""

from annotator import Annotator


class CfnLintAnnotator(Annotator):
    """The CfnLintAnnotator class annotates GitHub PRs with the results of cfn-lint."""

    name = 'cfn_lint_annotator'

    def __init__(self, linter_output_file: str) -> None:
        """Construct CfnLintAnnotator."""
        Annotator.__init__(self, linter_output_file)

    def compile_annotations(self) -> None:
        """Create the list of annotations that will be posted to the PR."""
        for i, error in enumerate(self.lint_results):
            self.add_annotation(
                file=error['Filename'],
                severity=error['Level'],
                sline=error['Location']['Start']['LineNumber'],
                eline=error['Location']['End']['LineNumber'],
                scol=error['Location']['Start']['ColumnNumber'],
                ecol=error['Location']['End']['ColumnNumber'],
                message=f'[{str(error["Rule"])}] {error["Message"]}',
            )


if __name__ == '__main__':
    CfnLintAnnotator('cfnlint_output.json').annotate_pr()
