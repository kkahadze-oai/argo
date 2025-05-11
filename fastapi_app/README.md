# Mingrelian Translator API

A FastAPI wrapper for the Mingrelian-to-Georgian/English translator.

## Installation

1. Clone this repository
2. Install the requirements:

```bash
pip install -r requirements.txt
```

## Running the API

Start the API server locally:

```bash
uvicorn api:app --reload --port 8000
```

The API will be available at http://localhost:8000

## API Usage

### Translate Mingrelian Text

**Endpoint:** POST /chat

**Request body:**

```json
{
  "prompt": "Your Mingrelian text here",
  "api_key": "your-openai-api-key",
  "target_language": "english"  // or "georgian"
}
```

**Example with curl:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "skua", "api_key": "your-openai-api-key", "target_language": "english"}'
```

**Response:**

```json
{
  "mingrelian_latinized": "skua",
  "mingrelian_mkhedruli": "სქუა",
  "georgian": "შვილი",
  "english": "child",
  "full_response": "..."
}
```

## Testing the API

We've provided two ways to test the API:

### 1. Using the Python Test Script

```bash
# Make sure to set the OPENAI_API_KEY environment variable or pass it as an argument
python test_api.py "your mingrelian text" --api-key "your-openai-api-key" --target english
```

Options:
- `--api-key`: Your OpenAI API key (if not provided, will look for OPENAI_API_KEY environment variable)
- `--target`: Target language, either 'english' or 'georgian' (default: 'english')
- `--url`: API server URL (default: 'http://localhost:8000')

### 2. Using the HTML Test Page

1. Start the API server with `uvicorn api:app --reload --port 8000`
2. Open the `test.html` file in your browser 
3. Enter your OpenAI API key and Mingrelian text
4. Select the target language
5. Click "Translate" to see the results

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes

- The API uses the o4-mini model by default
- You must provide your own OpenAI API key
- The `target_language` parameter determines which translation to prioritize in the frontend 