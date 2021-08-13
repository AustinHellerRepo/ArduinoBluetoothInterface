FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./requirements.txt /wifi_server/requirements.txt

WORKDIR /wifi_server/

RUN pip install -r requirements.txt

COPY ./app /wifi_server/app

WORKDIR /wifi_server/app/

ENV PYTHONPATH "${PYTHONPATH}:/wifi_server"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]