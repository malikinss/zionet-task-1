# ./src/tools/weather.py

"""Real-time weather lookup tool.

This module provides `WeatherTool`, a `BaseTool` implementation that
fetches current weather data for a given city from the WeatherAPI
service.

Falls back to `MOCK_WEATHER` if `WEATHER_API_KEY` is not set.

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

MOCK_WEATHER: dict[str, str] = {
    "london": "London, UK: Cloudy, 15.0°C, humidity 80%, wind 20.0 kph",
    "tokyo": "Tokyo, Japan: Sunny, 22.0°C, humidity 60%, wind 10.0 kph",
    "new york": "New York, USA: Clear, 18.0°C, humidity 55%, wind 15.0 kph",
}
"""Fallback weather responses keyed by lowercase city name.

Used when `WEATHER_API_KEY` is not set.

Cities not present in this mapping receive a generic sunny response with
a `(mocked)` suffix.
"""


class WeatherTool(BaseTool):
    """A tool that fetches current weather data from `WeatherAPI`.

    Calls the `WeatherAPI` current weather endpoint and returns a
    human-readable summary of conditions for the requested city.
    Falls back to `MOCK_WEATHER` if `WEATHER_API_KEY` is not set.

    Attributes:
        BASE_URL: `WeatherAPI` endpoint URL for current weather queries.

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
            A `ToolSchema` requiring a single string property `city`.

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
        """Returns current weather for the given city.

        Uses the live `WeatherAPI` if `WEATHER_API_KEY` is set, otherwise
        falls back to `MOCK_WEATHER`.

        Args:
            city: Name of the city to fetch weather for.

        Returns:
            A formatted weather string or an error message if the
            API request fails.

        Example:
        ```
        tool.run("London")
        # "London, UK: Cloudy, 15.0°C, humidity 80%, wind 20.0 kph"
        ```
        """
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return self._mock(city)
        return self._fetch(city, api_key)

    def _mock(self, city: str) -> str:
        """Returns a mocked weather string for the given city.

        Looks up the city in `MOCK_WEATHER` by lowercase name. Returns
        a generic sunny response if the city is not found.

        Args:
            city: Name of the city to look up.

        Returns:
            A weather string from `MOCK_WEATHER`, or a generic fallback
            with a `(mocked)` suffix.

        Example:
        ```
        self._mock("london")
        # "London, UK: Cloudy, 15.0°C, humidity 80%, wind 20.0 kph"
        self._mock("Paris")
        # "Paris: Sunny, 20.0°C, humidity 60%, wind 10.0 kph (mocked)"
        ```
        """
        return MOCK_WEATHER.get(
            city.lower(),
            f"{city}: Sunny, 20.0°C, humidity 60%, wind 10.0 kph (mocked)"
        )

    def _fetch(self, city: str, api_key: str) -> str:
        """Fetches live weather data from `WeatherAPI` for the given city.

        Args:
            city: Name of the city to fetch weather for.
            api_key: `WeatherAPI` authentication key.

        Returns:
            A formatted weather string on success, or an error message
            if the request fails.

        Example:
        ```
        self._fetch("Berlin", "my_api_key")
        # "Berlin, Germany: Partly cloudy, 18°C, humidity 72%, wind 14.4 kph"
        ```
        """
        try:
            response = requests.get(
                self.BASE_URL,
                params={"key": api_key, "q": city},
                timeout=5,
            )
            response.raise_for_status()
            return self._format_result_string(response)
        except requests.RequestException as e:
            return f"Weather API error: {e}"

    def _format_result_string(self, response: requests.Response) -> str:
        """Parses a `WeatherAPI` response and formats it as a readable string.

        Args:
            response: A successful `requests.Response` object from
                the `WeatherAPI` current weather endpoint.

        Returns:
            A string of the form
            `"<city>, <country>: <condition>,
            <temp>°C, humidity <h>%, wind <w> kph"`.

        Example:
        ```
        self._format_result_string(response)
        # "Rome, Italy: Clear, 24°C, humidity 50%, wind 8.0 kph"
        ```
        """
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
