from flask import Flask, request
from flask_restx import Api, Resource, fields
import sht35dis
import lps25hb
import tsl25721
import os
from os.path import join, dirname
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(verbose=True, dotenv_path=dotenv_path)
SENTRY_DSN = os.environ.get("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="IoT Manager API Document",
    description="IoT Managerは、Raspberry Piに接続されたI2Cデバイスを制御するAPIサーバーです。",
    doc="/doc/",
    default="Default Endpoint",
    default_label="default"
)
expect_model = api.model("IoTManagerExpect", {
    "command": fields.String(description="温度(\"temperature\"), 湿度(\"humidity\"), 気圧(\"pressure\"), 照度(\"illuminance\")のうち、取得したい値を送信してください。")
})
response_model = api.model("IoTManagerResponse", {
    "result": fields.String(description="指定したcommandの値が返ってきます。")
})


@api.route("/")
@api.expect(expect_model)
class Switch(Resource):
    @api.marshal_with(response_model)
    def post(self):
        print("Params :", request.json)
        if request.json["command"] == "temperature":
            temperature = sht35dis.measure_temperature()
            print("Temperature :", temperature)
            return {"result": format(temperature, ".1f")}
        elif request.json["command"] == "humidity":
            humidity = sht35dis.measure_humidity()
            print("Humidity :", humidity)
            return {"result": format(humidity, ".1f")}
        elif request.json["command"] == "pressure":
            pressure = lps25hb.measure_pressure_millibars()
            print("Pressure :", pressure)
            return {"result": format(pressure, ".1f")}
        elif request.json["command"] == "illuminance":
            illuminance = tsl25721.measure_illuminance()
            print("Illuminance :", illuminance)
            return {"result": format(illuminance, ".1f")}
        else:
            print("Error")
            return {"result": "Command Not Found"}, 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
