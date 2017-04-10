FROM python:2.7-slim

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY cs-chaosmonkey.py ./
CMD [ "python", "./cs-chaosmonkey.py" ]
