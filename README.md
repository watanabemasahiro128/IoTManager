# IoT Manager

## What is this?

IoT Manager is an API server that controls I2C devices and Serial Port devices connected to the Raspberry Pi.

## Environment

- Language : Python 3.10.4
- WEB Framework : Flask==2.1.2, Flask-RESTX==0.5.1
- Libraries : smbus2==0.4.1, mh_z19==3.1.3, python-dotenv==0.20.0, sentry-sdk[flask]==1.5.12
- OS : Raspbian Pi OS

## Usage

Send the following data in JSON format with a POST request.

| Key     | Value                |
| ------- | -------------------- |
| command | "temperature" or "humidity" or "pressure" or "illuminance" or "co2" |

If the POST request is successful, the following JSON data is returned.

| Key    | Value        |
| ------ | ------------ |
| result | (e.g.: 28.5) |

If the POST request fails, the following JSON data is returned with HTTP status code 400.

| Key    | Value               |
| ------ | ------------------- |
| result | "Command Not Found" |

## Setup

### Install Docker

```sh
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh
```

### Install pigpio

```sh
apt install -y pigpio
pip3 install pigpio
```

### Enable I2C

```sh
sudo raspi-config
```

Interface Options > I2C > Yes

### Enable Serial Port

```sh
sudo raspi-config
```

Interface Options > Serial Port > No > Yes

### Grant read permission

#### Check the link source of /dev/serial0

```sh
ls -la /dev/serial0
# lrwxrwxrwx 1 root root 5  1月 1 00:00 /dev/serial0 -> ttyS0
```

#### Grant read group permission

```sh
sudo chmod g+r /dev/ttyS0
```

### Reboot

```sh
reboot
```

### Build

```
docker build -t iot_manager .
```

## Run

```sh
docker run -d --rm --net host --device=/dev/i2c-1 --device=/dev/ttyS0 --name iot_manager iot_manager
```

## License

MIT
