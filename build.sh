poetry build
pip install --upgrade -t package dist/*.whl
cd package
zip -r ../artifact.zip . -x '*.pyc'
cd ..