FROM python:3.8.10

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY ./requirements.txt /dequeuer/requirements.txt

WORKDIR /dequeuer/

RUN pip install --upgrade -r requirements.txt

COPY ./app /dequeuer/app

WORKDIR /dequeuer/app/

ENV PYTHONPATH "${PYTHONPATH}:/dequeuer"

ENTRYPOINT ["python", "/dequeuer/app/main.py"]
