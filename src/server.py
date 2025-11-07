#!/usr/bin/env python3
"""
Weather & Crypto MCP Server
============================
This MCP server provides weather data (OpenWeatherMap API) and cryptocurrency prices (CoinGecko API).
It exposes tools that Claude can use to answer weather and crypto-related questions.
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
app = Server("weather-crypto-server")


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
    This tells Claude what weather/crypto functions are available.
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
        ),
        Tool(
            name="get_btc_price",
            description="Get current Bitcoin (BTC) price in USD. Returns price, 24hr change, and market cap.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_eth_price",
            description="Get current Ethereum (ETH) price in USD. Returns price, 24hr change, and market cap.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

async def fetch_crypto_prices(symbol: str) -> dict[str, Any]:
    """
    Fetch cryptocurrency price from CoinGecko API

    Args:
        symbol: cryptocurrency symbol (btc or eth)

    Returns:
        Dictionary containing price data
    """
    # Map symbols to CoinGecko IDs
    crypto_ids = {
        "btc": "bitcoin",
        "eth": "ethereum",
    }

    crypto_id = crypto_ids.get(symbol.lower())
    if not crypto_id:
        raise ValueError(f"Unsupported cryptocurrency: {symbol}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": crypto_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true"
            },
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool calls from Claude.
    When Claude wants weather/crypto data, this function is called.
    
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

        elif name == "get_btc_price":
            # Fetch BTC price
            data = await fetch_crypto_prices("btc")

            # Format the response
            btc_data = data.get("bitcoin", {})
            price = btc_data.get("usd", "N/A")
            change_24h = btc_data.get("usd_24h_change", "N/A")
            market_cap = btc_data.get("usd_market_cap", "N/A")

            result = f"""Bitcoin (BTC) Price:

Price: ${price:,.2f} USD
24h Change: {change_24h:+.2f}%
Market Cap: ${market_cap:,.0f} USD
"""
            return [TextContent(type="text", text=result)]

        elif name == "get_eth_price":
            # Fetch ETH price
            data = await fetch_crypto_prices("eth")

            # Format the response
            eth_data = data.get("ethereum", {})
            price = eth_data.get("usd", "N/A")
            change_24h = eth_data.get("usd_24h_change", "N/A")
            market_cap = eth_data.get("usd_market_cap", "N/A")

            result = f"""Ethereum (ETH) Price:

Price: ${price:,.2f} USD
24h Change: {change_24h:+.2f}%
Market Cap: ${market_cap:,.0f} USD
"""
            return [TextContent(type="text", text=result)]

        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return [TextContent(type="text", text=f"Error: Resource not found (404)")]
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