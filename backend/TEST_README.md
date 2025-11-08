# Testing Claude SDK Integration

This directory contains tests to verify that the Claude Agents SDK is properly integrated and working.

## Prerequisites

1. **Create and activate virtual environment**:
   ```bash
   cd backend

   # Create virtual environment
   python -m venv venv

   # Activate it:
   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   # Make sure venv is activated first!
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

   Or create a `.env` file in the backend directory:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Quick Start - Complete Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies (latest versions)
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your API key
# Open .env in your editor and set:
# ANTHROPIC_API_KEY=sk-ant-api03-...your-key-here...

# Now run tests
python test_sdk_basic.py
```

## Available Tests

### 1. Basic SDK Test (Recommended First)

This test verifies the Claude SDK works without any of our application code:

```bash
python test_sdk_basic.py
```

**What it tests:**
- Direct Claude SDK connection
- Simple query/response
- Conversation context retention

**Expected output:**
```
Test 1: Single Query
Query: What is 2+2?
Response: 4
✅ Test 1 passed: Got correct answer

Test 2: Continuous Conversation
✅ Test 2 passed: Context retained across messages

🎉 All tests passed! Claude SDK is working correctly.
```

### 2. Full Agent System Test

This test verifies our complete agent implementation:

```bash
python test_agent_sdk.py
```

**What it tests:**
- Basic single queries
- Continuous conversations with context
- Data analysis capabilities
- Multi-turn interactions
- Streaming responses

**Expected output:**
```
TEST 1: Basic Single Query
✅ Basic query test passed

TEST 2: Continuous Conversation
✅ Continuous conversation test passed

TEST 3: Data Analysis Agent
✅ Data analysis agent test passed

TEST 4: Multi-turn Analysis
✅ Multi-turn analysis test passed

TEST 5: Streaming Responses
✅ Streaming test passed

TEST RESULTS
✅ Passed: 5/5
🎉 All tests passed!
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Make sure you've exported the environment variable or added it to `.env`
- Verify with: `echo $ANTHROPIC_API_KEY`

### "Module 'claude_agent_sdk' not found"
- Install the SDK: `pip install claude-agent-sdk`
- Or reinstall all requirements: `pip install -r requirements.txt`

### "Connection error" or timeouts
- Check your internet connection
- Verify the API key is valid
- Try a simpler test first with `test_sdk_basic.py`

### Tests pass but responses seem wrong
- Check you're using the correct model (claude-3-5-sonnet-20241022)
- Ensure your API key has proper permissions

## What Success Means

When all tests pass, it confirms:

1. **SDK Integration**: The Claude Agents SDK is properly installed and configured
2. **API Connectivity**: Your API key works and can connect to Claude
3. **Conversation Management**: The system can maintain context across multiple messages
4. **Agent Architecture**: Our multi-agent system correctly uses the SDK
5. **Data Processing**: Agents can analyze data and generate insights
6. **Streaming**: Real-time response streaming works

This proves the foundation of DealIQ is working correctly and ready for use!

## Next Steps

After tests pass:

1. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Test via API:
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```

3. Use the full application with the frontend

## Performance Notes

- Each test makes real API calls to Claude
- Tests may take 10-30 seconds to complete
- API usage will count against your Anthropic quota
- Consider using cached responses for repeated testing