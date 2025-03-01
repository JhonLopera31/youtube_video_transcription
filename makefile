clean:
	make clean-build
	make clean-pyc

clean-build:
	rm -fr dist/
	rm -fr htmlcov/
	rm -fr temp/
	rm -fr .mypy_cache/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '.DS_Store' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

deploy-dag-prod:
	gsutil cp -R airflow_dags/* gs://us-central1-data-ml-orchest-18d165b7-bucket/dags/dtc_audiences/

deploy-dag-dev:
	gsutil cp -R airflow_dags/* gs://us-central1-data-ml-orchest-0e7f213e-bucket/dags/dtc_audiences/

install-local:
	pipenv install --dev
	pipenv shell pre-commit install

