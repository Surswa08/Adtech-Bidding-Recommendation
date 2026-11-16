.PHONY: install run test train compose-up compose-down
install:
	pip install -r requirements.txt
run:
	uvicorn app.main:app --reload
test:
	pytest -q
train:
	python scripts/generate_training_data.py
	python scripts/train_models.py
compose-up:
	docker compose up --build
compose-down:
	docker compose down
