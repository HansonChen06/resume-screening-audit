PYTHON ?= python3
SEED ?= 42

.PHONY: all test figures report clean

all: data/processed/scores.csv data/processed/results.csv figures report/report.pdf

data/raw/jds.csv: data/raw/combined_applypilot.json scripts/export_jds.py
	$(PYTHON) scripts/export_jds.py --input data/raw/combined_applypilot.json

data/processed/scores.csv: data/raw/jds.csv data/base_resume.txt data/nursing_control.txt src/experiment.py src/embed.py src/score.py src/variants.py
	HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 $(PYTHON) src/experiment.py --seed $(SEED)

data/processed/results.csv: data/processed/scores.csv src/analysis.py src/score.py
	$(PYTHON) src/analysis.py --seed $(SEED)

figures: data/processed/results.csv src/figures.py
	MPLBACKEND=Agg $(PYTHON) src/figures.py

report/report.pdf: figures report/build_report.py data/processed/controls.json data/raw/quality_report.json
	$(PYTHON) report/build_report.py

test:
	$(PYTHON) -m unittest discover -s tests -v

clean:
	rm -rf data/processed figures/*.png report/report.pdf
