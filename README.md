# Weather, Crypto & Currency MCP Server 🌤️ ₿ 💱

A Model Context Protocol (MCP) server that provides weather data from OpenWeatherMap API, cryptocurrency prices from CoinGecko API, and currency exchange rates from ExchangeRate-API. This project demonstrates how to build an MCP server that enables AI assistants like Claude to answer weather, crypto, and currency-related questions.

## 🎯 What This Does

This project creates a bridge between Claude and real-world data:
- You ask: "What's the weather in Paris?"
- Or: "What's the Bitcoin price?"
- Or: "Convert 100 USD to EUR"
- Or: "What's the exchange rate between GBP and JPY?"
- Or even: "Show me weather in London and Tokyo, plus Ethereum price"
- Claude uses the MCP server to fetch real-time data
- You get a natural language answer with current information
- Supports 20+ cryptocurrencies, any city worldwide, and 160+ currencies

## 📁 Project Structure

```
weather-crypto-mcp/
├── src/
│   ├── __init__.py        # Package initialization
│   ├── server.py          # MCP server (provides weather, crypto & currency tools)
│   └── client.py          # Terminal client (asks questions)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🚀 Setup Instructions

### Step 1: Get OpenWeatherMap API Key

1. Visit https://openweathermap.org/api
2. Sign up for a free account
3. Go to API Keys section and copy your key
4. Wait a few minutes for the key to activate

### Step 2: Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API key
# OPENWEATHER_API_KEY=your_actual_api_key_here
```

### Step 4: Set Anthropic API Key

The client needs Claude to interpret your questions:

```bash
# On macOS/Linux:
export ANTHROPIC_API_KEY=your_anthropic_api_key

# On Windows:
set ANTHROPIC_API_KEY=your_anthropic_api_key
```

Get your Anthropic API key from: https://console.anthropic.com/

## 💻 Usage

### Interactive Mode

Run the client without arguments for an interactive session:

```bash
python src/client.py
```

Then ask questions like:
- "What's the weather in London?"
- "What's the Bitcoin price today?"
- "Convert 100 USD to EUR"
- "What's the exchange rate from GBP to JPY?"
- "Show me Solana and Dogecoin prices"
- "How's the weather in London and Paris?"
- "What's the weather in Tokyo and Bitcoin price?"
- "Will it rain in Tokyo?"
- "Give me the forecast for Paris"

### Single Query Mode

Pass your question as a command line argument:

```bash
python src/client.py "What's the weather in Berlin?"
```

## 🔧 How It Works

### Architecture

```
User Question → Client → MCP Server → OpenWeatherMap / CoinGecko / ExchangeRate-API
                  ↓           ↓              ↓
              Claude    4 Tools         Weather, Crypto & Currency Data
                  ↓           ↓              ↓
            Natural Language Answer ← Formatted Data
```

### Components Explained

**1. MCP Server (server.py)**
- Exposes four tools to Claude:
  - `get_current_weather`: Current conditions for a city
  - `get_weather_forecast`: 5-day forecast for a city
  - `get_crypto_price`: Dynamic crypto price tool supporting 20+ cryptocurrencies
  - `get_exchange_rate`: Currency exchange rates for 160+ currencies
- Fetches data from OpenWeatherMap, CoinGecko, and ExchangeRate-API
- Returns structured weather, crypto, and currency information
- Supports multiple simultaneous tool calls (e.g., "weather in London and Paris")

**2. Terminal Client (client.py)**
- Takes your natural language question
- Connects to the MCP server
- Uses Claude to interpret your question
- Claude decides which tool(s) to call
- Formats and displays the answer

**3. MCP Protocol**
- Standardized way for AI to access external data
- Server exposes "tools" (functions)
- Client requests available tools
- AI decides when and how to use them

## 📊 Available Tools

### Weather Tools

**get_current_weather**
Returns current weather conditions including:
- Temperature (actual and feels-like)
- Weather conditions (clear, cloudy, rainy, etc.)
- Humidity and pressure
- Wind speed
- Cloudiness percentage

**get_weather_forecast**
Returns 5-day forecast with:
- Predictions every 3 hours
- Temperature forecasts
- Expected weather conditions
- Timestamps for each forecast

### Cryptocurrency Tools

**get_crypto_price**
Dynamic tool that supports 20+ cryptocurrencies:
- Accepts symbol (btc, eth, sol) or CoinGecko ID (bitcoin, ethereum)
- Returns current price in USD
- 24-hour price change percentage
- Market cap

**Supported Cryptocurrencies:**
- **Top Coins**: BTC, ETH, USDT, BNB, SOL
- **Major Altcoins**: XRP, USDC, ADA, DOGE, TRX, AVAX, LINK, DOT, MATIC
- **Meme Coins**: SHIB, PEPE, WIF
- **DeFi**: UNI, AAVE, CRV
- **Any CoinGecko coin**: Pass the CoinGecko ID directly for unlisted coins

**Examples:**
- "What's Solana price?" (uses symbol: sol → solana)
- "Show me Bitcoin and Ethereum" (multiple coins at once)
- "arbitrum price" (passes through to CoinGecko)

### Currency Exchange Tools

**get_exchange_rate**
Get real-time currency exchange rates between any two currencies:
- Supports 160+ world currencies (USD, EUR, GBP, JPY, CAD, AUD, etc.)
- Returns current exchange rate
- Optional amount parameter for conversions
- Data from ExchangeRate-API (free, no API key required)

**Supported Currencies:**
All major world currencies including:
- **Americas**: USD, CAD, MXN, BRL, ARS
- **Europe**: EUR, GBP, CHF, SEK, NOK, DKK, PLN
- **Asia**: JPY, CNY, KRW, INR, SGD, HKD, THB
- **Oceania**: AUD, NZD
- **Middle East**: AED, SAR, ILS
- **Africa**: ZAR, EGP, NGN
- And 140+ more!

**Examples:**
- "Convert 100 USD to EUR"
- "What's the GBP to JPY exchange rate?"
- "How much is 50 CAD in AUD?"

## 🛠️ Troubleshooting

### "OPENWEATHER_API_KEY not found"
- Make sure you created the `.env` file
- Check that your API key is correct
- Ensure there are no quotes around the key in `.env`

### "City not found"
- Check the spelling of the city name
- Try using the country code: "London,UK" or "Paris,FR"

### "API request failed"
- New API keys take a few minutes to activate
- Check your internet connection
- Verify your API key is valid

### "ANTHROPIC_API_KEY not found"
- Make sure you've set the environment variable
- Use `export` (macOS/Linux) or `set` (Windows)
- Restart your terminal after setting it

## 📚 Learning Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **OpenWeatherMap API**: https://openweathermap.org/api
- **CoinGecko API**: https://www.coingecko.com/en/api
- **ExchangeRate-API**: https://www.exchangerate-api.com/
- **Anthropic API**: https://docs.anthropic.com/

## 🎓 Key Concepts

**Model Context Protocol (MCP)**
- Connects AI assistants to external data sources
- Standardized protocol created by Anthropic
- Servers expose "tools" that AI can use

**Tools in MCP**
- Functions that the AI can call
- Each tool has a name, description, and input schema
- AI decides when to use tools based on user queries

**Stdio Communication**
- Server and client communicate via standard input/output
- Allows processes to talk to each other
- Simple and efficient for local MCP servers

## 🔐 Security Notes

- Never commit `.env` files to version control
- Keep your API keys secret
- The `.env.example` file shows the format without real keys
- Add `.env` to your `.gitignore` file

## 📝 License

This is a learning project - feel free to use and modify as needed!

## 🤝 Contributing

This is an educational project. Feel free to:
- Add more weather features (UV index, air quality, etc.)
- Add more cryptocurrency symbols to CRYPTO_IDS dictionary
- Support different APIs (stocks, news, etc.)
- Add historical exchange rate data
- Improve error handling
- Add tests
- Add caching for API responses

## 📋 Changelog

**v3.0.0** (Current)
- Added currency exchange rate tool `get_exchange_rate`
- Support for 160+ world currencies (USD, EUR, GBP, JPY, etc.)
- No API key required for exchange rates (uses ExchangeRate-API)
- Examples: "Convert 100 USD to EUR", "GBP to JPY rate"

**v2.0.0**
- Replaced individual crypto tools with dynamic `get_crypto_price(symbol)` tool
- Added support for 20+ cryptocurrencies with symbol shortcuts
- Fixed bug: now handles multiple simultaneous tool calls
- Examples: "weather in London and Paris", "BTC and ETH prices"

**v1.0.0**
- Initial release with weather and basic crypto support
- 4 tools: weather, forecast, BTC price, ETH price

Happy coding! 🚀