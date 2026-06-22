.PHONY: all clean train evaluate figures reproduce

all: train evaluate figures

train:
	python scripts/train.py

evaluate:
	python scripts/evaluate.py

figures:
	python scripts/make_figures.py

reproduce: train evaluate figures

clean:
	rm -rf results/*.json figures/*.png
