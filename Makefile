.PHONY: test demo
test:
	PYTHONPATH=src python -m unittest discover -s tests -v
demo:
	PYTHONPATH=src python -m transit_audit demo --output results/local_demo
