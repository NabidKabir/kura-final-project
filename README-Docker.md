# Docker Setup

This Docker Compose setup runs the recycling agent application with the following services:

## Services

- **chroma**: Vector database for storing knowledge base embeddings
- **mcp-server**: MCP server providing recycling tools and location services
- **supervisor**: Supervisor agent with Slack integration

## Quick Start

1. Copy environment variables:
```bash
cp .env.example .env
```

2. Edit `.env` with your actual API keys and tokens

3. Start all services:
```bash
docker-compose up -d
```

4. Check service health:
```bash
docker-compose ps
```

5. View logs:
```bash
docker-compose logs -f
```

6. Stop services:
```bash
docker-compose down
```

## Environment Variables

Make sure to set these in your `.env` file:
- `OPENAI_API_KEY`: Your OpenAI API key
- `TAVILY_API_KEY`: Your Tavily search API key
- `GOOGLE_API_KEY`: Your Google Places API key
- `SLACK_BOT_TOKEN`: Your Slack bot token
- `SLACK_APP_TOKEN`: Your Slack app token

## Ports

- MCP Server: http://localhost:8000
- Chroma DB: http://localhost:8001
- Supervisor: Runs in background, connects to Slack