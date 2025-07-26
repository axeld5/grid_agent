# Grid Agent - Datacenter Weighting API

A FastAPI-based service that provides datacenter location analysis for French locations, including grid/water/elevation scoring and installation information.

## Project Structure

```
grid_agent/
├── agent_utils/           # Core agent utilities
│   ├── prompts.py        # Prompt generation functions
│   ├── schemas.py        # Pydantic data models
│   └── tools.py          # Custom agent tools
├── app.py                # FastAPI application entry point
├── endpoints.py          # API endpoint implementations
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── README.md           # This file
```

## API Endpoints

- **POST /score** - Get grid/water/elevation weights for a French location
- **POST /information** - Get datacenter installation information for a French location

## Setup & Installation

### Prerequisites

- Python 3.11+
- Required API keys (set as environment variables):
  - `ANTHROPIC_API_KEY` - For Claude AI model access

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/axeld5/grid_agent
   cd grid_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   # .env file
   ANTHROPIC_API_KEY=your-anthropic-api-key
   MODEL_ID=anthropic/claude-sonnet-4-20250514
   PORT=8000
   ```
   
   Alternatively, export them directly:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   export MODEL_ID="anthropic/claude-sonnet-4-20250514"  # optional, defaults to this
   export PORT="8000"  # optional, defaults to 8000
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

2. **Access the API**
   - API: `http://localhost:8000`
   - Documentation: `http://localhost:8000/docs`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Required for Claude AI access | - |
| `MODEL_ID` | Claude model to use | `anthropic/claude-sonnet-4-20250514` |
| `PORT` | Port to run the server on | `8000` |
| `STREAM_OUTPUTS` | Enable streaming outputs | `false` |

## Usage

The API provides two main endpoints for analyzing French locations:

### Score Endpoint
Returns weighted scores for grid access, water availability, and elevation factors.

### Information Endpoint  
Provides detailed information about legislation, construction challenges, and environmental factors for datacenter installation.

Both endpoints accept a French location as input and return structured JSON responses.
