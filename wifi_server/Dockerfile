FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

#RUN wget -c https://sqlite.org/2021/sqlite-autoconf-3350400.tar.gz
#RUN mkdir sqlite3
#RUN tar xvfz sqlite-autoconf-3350400.tar.gz -C ./sqlite3/
#RUN cd sqlite3/sqlite-autoconf-3350400/ \
#    && ./configure \
#    && make \
#    && make install

#WORKDIR /

COPY ./requirements.txt /wifi_server/requirements.txt

WORKDIR /wifi_server/

RUN pip install -r requirements.txt

COPY ./app /wifi_server/app

WORKDIR /wifi_server/app/

ENV PYTHONPATH "${PYTHONPATH}:/wifi_server"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]