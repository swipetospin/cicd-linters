#!/bin/bash

set -e -o pipefail  # if a command or a command in a pipe fails, exit
set -u  # treat unset variables as error
set -x  # print all debug information

if [[ -z "$GITHUB_TOKEN" ]]; then  # This is populated by our secret from the Workflow file.
	echo "Set the GITHUB_TOKEN envvar."
	exit 1
fi
if [[ -z "$INPUT_LINTER" ]]; then  # This is a required input.
	echo "Set the INPUT_LINTER envvar with the name of the linter you're trying to run."
	exit 1
fi

echo "Linter $INPUT_LINTER has been selected"

ACTION=$(jq --raw-output .action "$GITHUB_EVENT_PATH")
# First 2 actions are for pull requests, last 2 are for check suites.
ENABLED_ACTIONS="synchronize opened requested rerequested"

if [[ $ENABLED_ACTIONS != *"$ACTION"* ]]; then
  echo -e "Not interested in this event: $ACTION.\nExiting..."
  exit
fi

BASE_COMMIT=$(jq --raw-output .pull_request.base.sha "$GITHUB_EVENT_PATH")
if [[ "$BASE_COMMIT" == null ]]; then  # If this is not a pull request action it can be a check suite re-requested.
  BASE_COMMIT=$(jq --raw-output .check_suite.pull_requests[0].base.sha "$GITHUB_EVENT_PATH")
fi

if [[ "$INPUT_LINTER" == "flake8" ]]; then
	# Get files added or modified wrt base commit, filter for Python files, and replace new lines with space.
	pyfiles=$(git diff --name-only --diff-filter=AM "$BASE_COMMIT" | grep '\.py$' | tr '\n' ' ')
	if [[ ! -z $pyfiles ]]; then
		echo "Running flake8 against Python files: $pyfiles"

		# Document ignore codes here:
		# 	E402 - Some scripts (deploy scripts in particular) lazy-load modules.
		flake8 \
			--format=json \
			--max-line-length 120 \
			--ignore=E402 \
			$pyfiles \
			| jq '.' > flake8_output.json || true
		python /src/flake8_annotator.py
	fi
elif [[ "$INPUT_LINTER" == "cfn-lint" ]]; then
	# Get files added or modified wrt base commit, filter for CloudFormation files, and replace new lines with space.
	cfnfiles=$(git diff --name-only --diff-filter=AM "$BASE_COMMIT" | grep 'template.yaml$' | tr '\n' ' ')
	if [[ ! -z $cfnfiles ]]; then
		echo "Running cfn-lint against CloudFormation templates: $cfnfiles"
		cfn-lint \
			-f json \
			--output-file cfnlint_output.json \
			$cfnfiles || true
		python /src/cfn_lint_annotator.py
	fi
fi
