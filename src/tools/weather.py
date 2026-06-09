# ./src/tools/weather.py

"""Real-time weather lookup tool.

This module provides `WeatherTool`, a `BaseTool` implementation that
fetches current weather data for a given city from the WeatherAPI
service. The API key is read from the `WEATHER_API_KEY` environment
variable.

Example:
    Basic usage:
    ```
    from src.tools.weather import WeatherTool

    tool = WeatherTool()
    print(tool.run("Berlin"))
    # "Berlin, Germany: Partly cloudy, 18°C, humidity 72%, wind 14.4 kph"
    print(tool.run("__invalid__"))
    # "Weather API error: ..."
    ```
"""

import os
import requests
from src.tools.base import BaseTool
from src.tools.schema import ToolSchema, PropertySchema


class WeatherTool(BaseTool):
    """A tool that fetches current weather data from WeatherAPI.

    Calls the WeatherAPI current weather endpoint and returns a
    human-readable summary of conditions for the requested city.
    Requires the `WEATHER_API_KEY` environment variable to be set.

    Attributes:
        BASE_URL: WeatherAPI endpoint for current weather data.

    Example:
    ```
    tool = WeatherTool()
    tool.run("Tokyo")
    # "Tokyo, Japan: Sunny, 27°C, humidity 60%, wind 10.0 kph"
    ```
    """

    BASE_URL: str = "http://api.weatherapi.com/v1/current.json"
    """WeatherAPI endpoint URL for current weather queries."""

    @property
    def name(self) -> str:
        """Returns the tool identifier used in LLM function calls.

        Returns:
            The string `"get_weather"`.

        Example:
        ```
        tool.name  # "get_weather"
        ```
        """
        return "get_weather"

    @property
    def description(self) -> str:
        """Returns a short description of the tool for the LLM.

        Returns:
            A plain-text description of the tool's purpose.

        Example:
        ```
        tool.description  # "Get current real weather for a given city"
        ```
        """
        return "Get current real weather for a given city"

    @property
    def parameters(self) -> ToolSchema:
        """Returns the parameter schema expected by this tool.

        Returns:
            A ToolSchema requiring a single string property `city`.

        Example:
        ```
        tool.parameters.properties
        # {"city": PropertySchema(type="string")}
        ```
        """
        return ToolSchema(
            type="object",
            properties={"city": PropertySchema(type="string")},
            required=["city"],
        )

    def run(self, city: str) -> str:
        """Fetches and formats current weather data for the given city.

        Reads the API key from the `WEATHER_API_KEY` environment variable,
        calls the WeatherAPI current weather endpoint, and returns a
        formatted summary string. Returns an error message instead of
        raising if the request fails.

        Args:
            city: Name of the city to fetch weather for,
                e.g. `"London"` or `"New York"`.

        Returns:
            A formatted string of the form
            `"<city>, <country>: <condition>,
            <temp>°C, humidity <h>%, wind <w> kph"`
            on success, or `"Weather API error: <reason>"` on failure.

        Example:
        ```
        tool.run("Paris")
        # "Paris, France: Clear, 22°C, humidity 55%, wind 12.6 kph"
        tool.run("__invalid__")
        # "Weather API error: 400 Client Error: Bad Request"
        ```
        """
        api_key = os.getenv("WEATHER_API_KEY")
        try:
            response = requests.get(
                self.BASE_URL,
                params={"key": api_key, "q": city},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            location = data["location"]["name"]
            country = data["location"]["country"]
            temp_c = data["current"]["temp_c"]
            condition = data["current"]["condition"]["text"]
            humidity = data["current"]["humidity"]
            wind_kph = data["current"]["wind_kph"]
            return (
                f"{location}, {country}: {condition}, "
                f"{temp_c}°C, humidity {humidity}%, wind {wind_kph} kph"
            )
        except requests.RequestException as e:
            return f"Weather API error: {e}"
