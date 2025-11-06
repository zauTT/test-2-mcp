#!/usr/bin/env python3
"""
Weather MCP Server
==================
This MCP server provides weather data tools using OpenWeatherMap API.
It exposes tools that Claude can use to answer weather-related questions.
"""

import os
import asyncio
import httpx
from typing import Any
from dotenv import load_dotenv

# MCP SDK imports
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in environment variables")

# OpenWeatherMap API base URL
BASE_URL = "https://api.openweathermap.org/data/2.5"

# Create MCP server instance
app = Server("weather-server")


async def fetch_weather(city: str) -> dict[str, Any]:
    """
    Fetch current weather data from OpenWeatherMap API.
    
    Args:
        city: Name of the city to get weather for
        
    Returns:
        Dictionary containing weather data
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/weather",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"  # Use Celsius
            },
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()


async def fetch_forecast(city: str) -> dict[str, Any]:
    """
    Fetch 5-day weather forecast from OpenWeatherMap API.
    
    Args:
        city: Name of the city to get forecast for
        
    Returns:
        Dictionary containing forecast data
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/forecast",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available tools that Claude can use.
    This tells Claude what weather functions are available.
    """
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather conditions for a specific city. Returns temperature, humidity, conditions, and more.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'London', 'New York', 'Tokyo')"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="get_weather_forecast",
            description="Get 5-day weather forecast for a specific city. Returns forecasted conditions every 3 hours.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'London', 'New York', 'Tokyo')"
                    }
                },
                "required": ["city"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool calls from Claude.
    When Claude wants weather data, this function is called.
    
    Args:
        name: Name of the tool being called
        arguments: Arguments passed to the tool
        
    Returns:
        List of TextContent with the tool results
    """
    try:
        if name == "get_current_weather":
            city = arguments.get("city")
            if not city:
                return [TextContent(type="text", text="Error: City name is required")]
            
            # Fetch weather data
            data = await fetch_weather(city)
            
            # Format the response
            weather = data["weather"][0]
            main = data["main"]
            wind = data["wind"]
            
            result = f"""Current Weather in {data['name']}, {data['sys']['country']}:
            
Temperature: {main['temp']}°C (feels like {main['feels_like']}°C)
Conditions: {weather['main']} - {weather['description']}
Humidity: {main['humidity']}%
Pressure: {main['pressure']} hPa
Wind Speed: {wind['speed']} m/s
Cloudiness: {data['clouds']['all']}%
"""
            return [TextContent(type="text", text=result)]
        
        elif name == "get_weather_forecast":
            city = arguments.get("city")
            if not city:
                return [TextContent(type="text", text="Error: City name is required")]
            
            # Fetch forecast data
            data = await fetch_forecast(city)
            
            # Format the response - show next 8 forecasts (24 hours)
            forecasts = data["list"][:8]
            result = f"5-Day Weather Forecast for {data['city']['name']}, {data['city']['country']}:\n\n"
            
            for forecast in forecasts:
                dt = forecast["dt_txt"]
                temp = forecast["main"]["temp"]
                conditions = forecast["weather"][0]["description"]
                result += f"{dt}: {temp}°C, {conditions}\n"
            
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return [TextContent(type="text", text=f"Error: City '{city}' not found")]
        return [TextContent(type="text", text=f"Error: API request failed - {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """
    Main entry point - starts the MCP server.
    The server communicates via stdio (standard input/output).
    """
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())