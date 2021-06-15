# README

## 概要

IoT Managerは、Raspberry Piに接続されたI2Cデバイスを制御するAPIサーバーです。

## 環境

* 言語 : Python 3.10.1
* WEB フレームワーク : Flask 1.1.4, Flask-RESTX 0.4.0
* ライブラリ : smbus2 0.4.1
* OS : Raspbian Buster

## 使用方法

以下のようなJSON形式のデータをPOSTリクエストで送信してください。

| キー    | 型     | 説明                                                                                                                  |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| command | String | 温度("temperature"), 湿度("humidity"), 気圧("pressure"), 照度("illuminance")のうち、取得したい値を送信してください。 |

POSTリクエストが成功すると、以下のJSONデータが返ってきます。

| キー   | 型    | 説明                                |
| ------ | ----- | ----------------------------------- |
| result | float | 指定したcommandの値が返ってきます。 |

POSTリクエストが失敗すると、HTTPステータスコード400で以下のJSONデータが返ってきます。

| キー   | 型     | 値                | 説明                      |
| ------ | ------ | ----------------- | ------------------------- |
| result | string | Command Not Found | commandが間違っています。 |

## 実行方法

### 環境構築

`sudo ./setup.sh`

### ビルド

`docker build -t iot_manager .`

### 起動

`docker run -d --rm --net host --device=/dev/i2c-1 --name iot_manager iot_manager`

## ライセンス

MIT
