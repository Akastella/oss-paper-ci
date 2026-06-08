.PHONY: all data train evaluate figures clean

all: figures

data:
	python scripts/download_data.py

train: data
	python scripts/train.py --config configs/default.yml

evaluate: train
	python scripts/evaluate.py

figures: evaluate
	python scripts/make_figures.py

clean:
	rm -rf results/* figures/*

smoke:
	python scripts/train.py --config configs/smoke.yml