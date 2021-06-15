FROM python:3.10.1-buster

RUN mkdir /IoTManager
ENV APP_ROOT /IoTManager
WORKDIR $APP_ROOT

COPY requirements.txt $APP_ROOT/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . $APP_ROOT

CMD ["python3", "iot_manager.py"]
