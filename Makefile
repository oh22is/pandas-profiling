.PHONY: docs examples

docs:
	rm -rf docs/
	mkdir docs/
	# pdoc3
	cp -a ./docsrc/assets/ ./docs/assets/
	pdoc3 --html --force --output-dir docs pandas_profiling
	mv docs/pandas_profiling/* docs
	rmdir docs/pandas_profiling
	# sphinx
	cd docsrc/ && make github

test:
	pytest tests/unit/
	pytest tests/issues/
	pytest --nbval tests/notebooks/
	pandas_profiling -h

test_spark:
	pytest --spark_home=${SPARK_HOME} tests/backends/spark_backend/
	pandas_profiling -h

test_cov:
	pytest --cov=. tests/unit/
	pytest --cov=. --cov-append tests/issues/
	pytest --cov=. --cov-append --nbval tests/notebooks/
	pandas_profiling -h

examples:
	find ./examples -maxdepth 2 -type f -name "*.py" -execdir python {} \;

install:
	pip install -e .[notebook]

install-spark-ci:
	sudo apt-get update
	sudo apt-get -y install openjdk-8-jdk
	curl https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
	--output ${SPARK_DIRECTORY}/spark.tgz
	cd ${SPARK_DIRECTORY} && tar -xvzf spark.tgz && mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark

lint:
	pre-commit run --all-files

clean:
	git rm --cached `git ls-files -i --exclude-from=.gitignore`

all:
	make lint
	make install
	make examples
	make docs
	make test
