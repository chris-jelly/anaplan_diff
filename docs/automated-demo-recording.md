# Automated Demo Recording

## Overview

This document outlines the plan to implement automated demo recording for the anaplan-diff tool to create interactive examples for the README.

## TODO: Implementation Tasks

### 1. Create Demo Script
- [ ] Create `scripts/demo.sh` that runs example commands with proper timing
- [ ] Include realistic CSV files in `demo/` folder for demonstration
- [ ] Add commands showing:
  - Basic usage: `anaplan-diff baseline.csv comparison.csv`
  - Help output: `anaplan-diff --help`
  - Error handling examples

### 2. Automation Setup
- [ ] Install asciinema as development dependency
- [ ] Install agg (asciinema GIF generator) for CI
- [ ] Create Make target for `make demo` command
- [ ] Add GitHub Actions workflow to auto-generate demo on releases

### 3. Integration
- [ ] Add generated GIF to README.md
- [ ] Create CI workflow to update demo when CLI changes
- [ ] Add demo recording to release process

## Technical Approach

**Recording Method**: Script-based automation using asciinema with shell script
**Output Format**: Animated GIF for README compatibility
**Automation**: GitHub Actions + Make targets
**Storage**: Commit generated GIFs to repo for reliability

## Example Implementation

```bash
# scripts/demo.sh
#!/bin/bash
echo "$ anaplan-diff baseline.csv comparison.csv"
sleep 1
anaplan-diff demo/baseline.csv demo/comparison.csv
sleep 2
echo "$ anaplan-diff --help"
sleep 1
anaplan-diff --help
```

```makefile
# Makefile target
demo:
	asciinema rec demo.cast -c "./scripts/demo.sh"
	agg demo.cast assets/demo.gif
	rm demo.cast
```

## Benefits

- Consistent, reproducible demos
- Automated updates when CLI changes
- Professional presentation in README
- Reduced maintenance overhead