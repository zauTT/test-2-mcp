# Weather MCP Server 🌤️

A simple Model Context Protocol (MCP) server that provides weather data from OpenWeatherMap API. This project demonstrates how to build an MCP server that enables AI assistants like Claude to answer weather-related questions.

## 🎯 What This Does

This project creates a bridge between Claude and real-world weather data:
- You ask: "What's the weather in Paris?"
- Claude uses the MCP server to fetch real-time weather data
- You get a natural language answer with current conditions

## 📁 Project Structure

```
weather-mcp/
├── src/
│   ├── __init__.py        # Package initialization
│   ├── server.py          # MCP server (provides weather tools)
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
- "Will it rain in Tokyo?"
- "Give me the forecast for Paris"
- "How's the weather in New York right now?"

### Single Query Mode

Pass your question as a command line argument:

```bash
python src/client.py "What's the weather in Berlin?"
```

## 🔧 How It Works

### Architecture

```
User Question → Client → MCP Server → OpenWeatherMap API
                  ↓           ↓              ↓
              Claude    Weather Tools    Weather Data
                  ↓           ↓              ↓
            Natural Language Answer ← Formatted Data
```

### Components Explained

**1. MCP Server (server.py)**
- Exposes two tools to Claude:
  - `get_current_weather`: Current conditions for a city
  - `get_weather_forecast`: 5-day forecast for a city
- Fetches data from OpenWeatherMap API
- Returns structured weather information

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

### get_current_weather
Returns current weather conditions including:
- Temperature (actual and feels-like)
- Weather conditions (clear, cloudy, rainy, etc.)
- Humidity and pressure
- Wind speed
- Cloudiness percentage

### get_weather_forecast
Returns 5-day forecast with:
- Predictions every 3 hours
- Temperature forecasts
- Expected weather conditions
- Timestamps for each forecast

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
- Add more weather features
- Support different APIs
- Improve error handling
- Add tests

Happy coding! 🚀