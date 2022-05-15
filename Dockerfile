FROM python:3.10.4-buster

RUN mkdir /IoTManager
ENV APP_ROOT /IoTManager
WORKDIR $APP_ROOT

COPY requirements.txt $APP_ROOT/requirements.lock
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.lock

COPY . $APP_ROOT

CMD ["python3", "iot_manager.py"]
