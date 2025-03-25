# Guerilla Model Makefile

.PHONY: install run

# Install required dependencies
install:
	git clone https://github.com/projectmesa/mesa.git ../mesa
	pip install mesa solara networkx altair

# Run the Guerilla model
run:
	python app.py