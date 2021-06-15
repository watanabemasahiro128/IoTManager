FROM balenalib/rpi-raspbian:buster

# Python
WORKDIR /root
RUN sudo apt-get update -q && \
    sudo apt-get upgrade -y && \
    sudo apt install build-essential tar libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev wget zlib1g-dev && \
    wget https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz && \
    tar xzvf Python-3.9.5.tgz
WORKDIR /root/Python-3.9.5
RUN ./configure --enable-optimizations && \
    make && \
    sudo make altinstall

# pip
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.9 get-pip.py

RUN mkdir /IoTManager
ENV APP_ROOT /IoTManager
WORKDIR $APP_ROOT

COPY requirements.txt $APP_ROOT/requirements.txt
RUN pip3 install -U pip && pip3 install --no-cache-dir -r requirements.txt

COPY . $APP_ROOT

CMD ["python3.9", "iot_manager.py"]
