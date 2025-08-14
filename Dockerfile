FROM python:3.12.6

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--timeout", "300", "app:server"]