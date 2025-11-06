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

#MCP SDK imports
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

#Load environment variables
load_dotenv()

#OpenWeatherMap API key
API_key = os.getenv("OPENWEATHER_API_KEY")
if not API_key:
    raise ValueError("OPENWEATHER_API_KEY is not set in the environment variables")

#OpenWeatherMap API base URL
BASE_URL = "https://api.openweathermap.org/data/2.5"

# Create MCP server instance
app = Server("weather-server")

async def fetch_weather(city: str) -> dict[str, Any]:
    """
    Fetch current weather data from OpenWeatherMap API.

    Args:
        city: The name of the city to fetch weather data for.

    Returns:
        A dictionary containing the weather data.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/weather",
            params={
                "q": city,
                "appid": API_key,
                "units": "metric",
            },
            timeout=10.0,
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
                    },
                },
                "required": ["city"],
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
                    },
                },
                "required": ["city"],
            }
        )
    ]


