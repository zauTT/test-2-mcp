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

# Cryptocurrency symbol to CoinGecko ID mappings
CRYPTO_IDS = {
    # Top 5 by market cap
    "btc": "bitcoin",
    "eth": "ethereum",
    "usdt": "tether",           # Stablecoin
    "bnb": "binancecoin",       # Binance Coin
    "sol": "solana",

    # Major altcoins
    "xrp": "ripple",
    "usdc": "usd-coin",         # Stablecoin
    "ada": "cardano",
    "doge": "dogecoin",
    "trx": "tron",
    "avax": "avalanche-2",      # Note: has "-2" suffix!
    "link": "chainlink",
    "dot": "polkadot",
    "matic": "matic-network",   # Polygon

    # Popular meme/trending coins
    "shib": "shiba-inu",
    "pepe": "pepe",
    "wif": "dogwifcoin",

    # DeFi favorites
    "uni": "uniswap",
    "aave": "aave",
    "crv": "curve-dao-token",
}


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
            name="get_crypto_price",
            description="Get current cryptocurrency price in USD. Supports BTC, ETH, SOL, DOGE and many more. Returns price, 24hr change, and market cap.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g., 'btc', 'eth', 'sol') or full name (e.g., 'bitcoin', 'ethereum')"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_exchange_rate",
            description="Get currency exchange rate between two currencies. Supports all major world currencies (USD, EUR, GBP, JPY, etc.). Returns the current exchange rate and conversion.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code (e.g., 'USD', 'EUR', 'GBP', 'JPY')"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code (e.g., 'USD', 'EUR', 'GBP', 'JPY')"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Optional amount to convert (defaults to 1)",
                        "default": 1
                    }
                },
                "required": ["from_currency", "to_currency"]
            }
        )
    ]

async def fetch_crypto_prices(symbol: str) -> dict[str, Any]:
    """
    Fetch cryptocurrency price from CoinGecko API

    Args:
        symbol: cryptocurrency symbol (e.g., 'btc', 'eth', 'sol') or CoinGecko ID

    Returns:
        Dictionary containing price data
    """
    # Translate symbol to CoinGecko ID (with fallback to use symbol as-is)
    crypto_id = CRYPTO_IDS.get(symbol.lower(), symbol.lower())

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

async def fetch_exchange_rate(from_currency: str, to_currency: str) -> dict[str, Any]:
    """
    Fetch currency exchange rate from exchangerate-api.com

    Args:
        from_currency: Source currency code (e.g., 'USD', 'EUR', 'GBP')
        to_currency: Target currency code (e.g., 'USD', 'EUR', 'GBP')

    Returns:
        Dictionary containing exchange rate data
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}",
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

        elif name == "get_crypto_price":
            symbol = arguments.get("symbol")
            if not symbol:
                return [TextContent(type="text", text="Error: Symbol is required")]

            # Translate symbol to CoinGecko ID
            crypto_id = CRYPTO_IDS.get(symbol.lower(), symbol.lower())

            # Fetch price data
            data = await fetch_crypto_prices(symbol)

            # Extract data using crypto_id as key
            crypto_data = data.get(crypto_id, {})
            price = crypto_data.get("usd", "N/A")
            change_24h = crypto_data.get("usd_24h_change", "N/A")
            market_cap = crypto_data.get("usd_market_cap", "N/A")

            # Format response
            result = f"""{symbol.upper()} Price:

            Price: ${price:,.2f} USD
            24h Change: {change_24h:+.2f}%
            Market Cap: ${market_cap:,.0f} USD
            """
            return [TextContent(type="text", text=result)]

        elif name == "get_exchange_rate":
            from_currency = arguments.get("from_currency")
            to_currency = arguments.get("to_currency")
            amount = arguments.get("amount", 1)

            if not from_currency or not to_currency:
                return [TextContent(type="text", text="Error: Both from_currency and to_currency are required")]

            data = await fetch_exchange_rate(from_currency, to_currency)

            rates = data.get("rates", {})
            to_currency_upper = to_currency.upper()

            if to_currency_upper not in rates:
                return [TextContent(type="text", text=f"Error: Currency '{to_currency_upper}' not found")]

            exchange_rate = rates[to_currency_upper]
            converted_amount = amount * exchange_rate

            result = f"""Exchange Rate - {from_currency.upper()} to {to_currency_upper}:

            Exchange Rate: 1 {from_currency.upper()} = {exchange_rate:.4f} {to_currency_upper}
            Conversion: {amount:,.2f} {from_currency.upper()} = {converted_amount:,.2f} {to_currency_upper}
            Last Updated: {data.get('date', 'N/A')}
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