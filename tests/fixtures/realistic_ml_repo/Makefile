.PHONY: train evaluate figures data clean

data:
	python scripts/download_data.py

train:
	python scripts/train.py --config configs/default.yml

evaluate:
	python scripts/evaluate.py --checkpoint results/checkpoints/best.pt

figures:
	python scripts/make_figures.py

clean:
	rm -rf results/checkpoints/* results/metrics.csv
