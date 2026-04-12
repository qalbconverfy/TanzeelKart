from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.api.v1.weather.schemas import (
    SensorDataRequest,
    WeatherResponse,
    WeatherForecastResponse,
    SensorNodeResponse
)
from app.core.exceptions import (
    ValidationException,
    AuthException
)
from loguru import logger
from datetime import datetime


# ─────────────────────────────────────────
# ESP32 Sensor Data Receive
# ─────────────────────────────────────────

async def receive_sensor_data(
    payload: SensorDataRequest,
    db: AsyncSession,
) -> dict:
    # API key verify
    if payload.api_key != settings.SECRET_KEY:
        raise AuthException("Invalid sensor API key")

    # InfluxDB mein save karo
    try:
        from influxdb_client import InfluxDBClient, Point
        from influxdb_client.client.write_api import SYNCHRONOUS

        client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        write_api = client.write_api(
            write_options=SYNCHRONOUS
        )

        point = Point("weather_data") \
            .tag("node_id", payload.node_id) \
            .field("temperature", payload.temperature) \
            .field("humidity", payload.humidity)

        if payload.pressure:
            point = point.field(
                "pressure", payload.pressure
            )
        if payload.rainfall:
            point = point.field(
                "rainfall", payload.rainfall
            )
        if payload.soil_moisture:
            point = point.field(
                "soil_moisture", payload.soil_moisture
            )
        if payload.wind_speed:
            point = point.field(
                "wind_speed", payload.wind_speed
            )

        write_api.write(
            bucket=settings.INFLUXDB_BUCKET,
            org=settings.INFLUXDB_ORG,
            record=point
        )
        client.close()

        logger.info(
            f"Sensor data received: {payload.node_id} "
            f"— {payload.temperature}°C"
        )

    except Exception as e:
        logger.error(f"InfluxDB error: {e}")

    # Crop advice generate karo
    advice = _generate_crop_advice(
        payload.temperature,
        payload.humidity,
        payload.rainfall or 0
    )

    return {
        "success": True,
        "message": "Data received",
        "node_id": payload.node_id,
        "advice": advice
    }


# ─────────────────────────────────────────
# Get Latest Weather
# ─────────────────────────────────────────

async def get_latest_weather(
    node_id: str = "reoti_main",
) -> WeatherResponse:
    try:
        from influxdb_client import InfluxDBClient

        client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        query_api = client.query_api()

        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["node_id"] == "{node_id}")
            |> last()
        '''

        tables = query_api.query(query)
        client.close()

        data = {}
        for table in tables:
            for record in table.records:
                data[record.get_field()] = record.get_value()

        if not data:
            return _get_default_weather(node_id)

        advice = _generate_crop_advice(
            data.get("temperature", 25),
            data.get("humidity", 60),
            data.get("rainfall", 0)
        )

        return WeatherResponse(
            node_id=node_id,
            location_name="Reoti, Ballia",
            temperature=data.get("temperature", 25),
            humidity=data.get("humidity", 60),
            pressure=data.get("pressure"),
            rainfall=data.get("rainfall"),
            soil_moisture=data.get("soil_moisture"),
            wind_speed=data.get("wind_speed"),
            recorded_at=datetime.utcnow(),
            advice=advice
        )

    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        return _get_default_weather(node_id)


# ─────────────────────────────────────────
# Get Weather Forecast
# ─────────────────────────────────────────

async def get_weather_forecast(
    node_id: str = "reoti_main",
) -> WeatherForecastResponse:
    current = await get_latest_weather(node_id)

    forecast = _generate_forecast(
        current.temperature,
        current.humidity,
        current.rainfall or 0
    )

    return WeatherForecastResponse(
        location="Reoti, Ballia, UP",
        current=current,
        forecast_24h=forecast["24h"],
        forecast_48h=forecast["48h"],
        forecast_72h=forecast["72h"],
        crop_advice=forecast["crop_advice"],
        rain_probability=forecast["rain_probability"]
    )


# ─────────────────────────────────────────
# All Sensor Nodes
# ─────────────────────────────────────────

async def get_sensor_nodes() -> list:
    # Hardcoded Reoti ke nodes
    # Baad mein database se aayenge
    return [
        {
            "node_id": "reoti_main",
            "location_name": "Reoti Bazaar",
            "latitude": 26.0500,
            "longitude": 84.1800,
            "is_active": True,
            "battery_level": 85.0
        },
        {
            "node_id": "reoti_khet",
            "location_name": "Reoti Khet Area",
            "latitude": 26.0450,
            "longitude": 84.1750,
            "is_active": True,
            "battery_level": 92.0
        },
        {
            "node_id": "reoti_nadi",
            "location_name": "Nadi Ke Paas",
            "latitude": 26.0600,
            "longitude": 84.1900,
            "is_active": False,
            "battery_level": 15.0
        },
    ]


# ─────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────

def _generate_crop_advice(
    temp: float,
    humidity: float,
    rainfall: float
) -> str:
    advice = []

    if temp > 40:
        advice.append(
            "Bahut garmi hai — fasal ko zyada paani do"
        )
    elif temp < 10:
        advice.append(
            "Thand hai — fasal ko thanda se bachao"
        )
    else:
        advice.append("Mausam theek hai")

    if humidity > 80:
        advice.append(
            "Humidity zyada — fungal disease ka darr"
        )
    elif humidity < 30:
        advice.append(
            "Sukha mausam — irrigation zaroor karo"
        )

    if rainfall > 50:
        advice.append(
            "Baarish hui — aaj irrigation mat karo"
        )
    elif rainfall == 0 and humidity < 50:
        advice.append("Aaj irrigation karo")

    return ". ".join(advice)


def _generate_forecast(
    temp: float,
    humidity: float,
    rainfall: float
) -> dict:
    rain_prob = min(
        (humidity / 100) * 0.7 +
        (rainfall / 100) * 0.3,
        1.0
    ) * 100

    return {
        "24h": (
            f"Temp: {temp-1:.1f}°C - {temp+2:.1f}°C. "
            f"Humidity: {humidity:.0f}%"
        ),
        "48h": (
            f"Temp: {temp-2:.1f}°C - {temp+3:.1f}°C. "
            f"{'Baarish possible' if rain_prob > 50 else 'Saaf mausam'}"
        ),
        "72h": (
            f"Temp: {temp:.1f}°C. "
            f"{'Baarish aa sakti hai' if rain_prob > 60 else 'Theek rahega'}"
        ),
        "crop_advice": _generate_crop_advice(
            temp, humidity, rainfall
        ),
        "rain_probability": round(rain_prob, 1)
    }


def _get_default_weather(node_id: str) -> WeatherResponse:
    return WeatherResponse(
        node_id=node_id,
        location_name="Reoti, Ballia",
        temperature=32.0,
        humidity=65.0,
        pressure=1013.0,
        rainfall=0.0,
        soil_moisture=45.0,
        wind_speed=8.0,
        recorded_at=datetime.utcnow(),
        advice="Sensor se data nahi mila. Default data."
    )
