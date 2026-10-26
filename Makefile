PYTHON := .venv/bin/python
.PHONY: setup build smoke test demo experiment analyze dashboard netanim report
setup:
	bash scripts/setup.sh
build:
	bash scripts/build.sh
smoke:
	$(PYTHON) scripts/run_simulation.py --config config/diamond.yaml
test:
	$(PYTHON) -m pytest -q
demo:
	$(PYTHON) scripts/run_demos.py
experiment:
	$(PYTHON) scripts/run_experiments.py --config config/experiment-matrix.yaml
analyze:
	$(PYTHON) scripts/run_experiments.py --analyze results/raw
report:
	$(PYTHON) scripts/generate_report.py
dashboard:
	bash scripts/launch_dashboard.sh
netanim:
	bash scripts/launch_netanim.sh
