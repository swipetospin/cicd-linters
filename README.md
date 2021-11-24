# GitHub Actions (ghactions)

A collection of GitHub Actions used for CI/CD.

# Available Actions

## linters

A collection of linters.

### Available linters

The following linters are available:
  * cfn-lint
  * flake8

To use a linter, specify a job step with the `linter` input, like this

```yaml
uses: swipetospin/ghactions/linters@master
with:
  linter: cfn-lint
```

### Usage

In your project, create the file `.github/workflows/main.yml`. Here's an example,
```yaml
name: linters

on:
  workflow_dispatch:
  pull_request:
    paths:
      - '**.py'
      - '**/template.yaml'

jobs:
  flake8:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0  # Check out the entire branch history so that diffs diff against all branch-modified files.
      - name: lint-and-annotate
        uses: swipetospin/ghactions/linters@master
        with:
          linter: flake8
        env:
          GITHUB_TOKEN: ${{ github.token }}
  cfn-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0  # Check out the entire branch history so that diffs diff against all branch-modified files.
      - name: lint-and-annotate
        uses: swipetospin/ghactions/linters@master
        with:
          linter: cfn-lint
        env:
          GITHUB_TOKEN: ${{ github.token }}
```

With this example, the action will:
  * Trigger on a Pull Request where Python and/or CloudFormation template files have changed.
  * Run two jobs, one running the `flake8` linter and another running `cfn-lint`

**An important note on Action security**

In the example above we specify the action's `master` branch, as in `uses: swipetospin/ghactions/linters@master`.
This is safe only because the repository is known and trusted. In cases where an action uses an untrusted repository
(which is in itself discouraged) it is always safest to reference a *specific commit*,
for example `uses: swipetospin/ghactions/linters@<commit sha>`.
