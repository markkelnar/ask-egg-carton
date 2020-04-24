#!/bin/bash
# Run from top level project directory
# https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-venv

# Load directory automatically
touch lambda/__init__.py

# Set up the environment
python3 -m venv v-env
source v-env/bin/activate
pip install -r lambda/requirements.txt
deactivate

# Build bundle of files for the lambda job
rm function.zip
cd v-env/lib/python3.7/site-packages/ ; zip -r ${OLDPWD}/function.zip . ; cd -
zip -rg function.zip lambda/

# Push the bundle to the lambda job
aws lambda update-function-code --function-name egg-carton-basket --zip-file  fileb://function.zip --profile alexa_default
