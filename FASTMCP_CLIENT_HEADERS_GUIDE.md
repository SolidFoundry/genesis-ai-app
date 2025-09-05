# FastMCP Client HTTP Headers Configuration Guide

## Problem

The original code was getting this error:
```
Client.__init__() got an unexpected keyword argument 'headers'
```

This error occurs because FastMCP Client does not accept a `headers` parameter directly in its constructor.

## Solution

To configure custom HTTP headers with FastMCP Client, you need to use the `StreamableHttpTransport` class, which supports the `headers` parameter.

### Correct Approach

```python
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Create transport with custom headers
transport = StreamableHttpTransport(
    url="http://127.0.0.1:8888/mcp",
    headers={
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "User-Agent": "Your-App/1.0.0",
        "Authorization": "Bearer your-token-here"
    }
)

# Create client with transport
client = Client(transport)
```

### Complete Example

```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    # Configure headers
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "User-Agent": "Genesis-AI-App/1.0.0"
    }
    
    # Create transport with headers
    transport = StreamableHttpTransport(
        url="http://127.0.0.1:8888/mcp",
        headers=headers
    )
    
    # Create client
    client = Client(transport)
    
    # Use client
    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        result = await client.call_tool("greet", {"name": "World"})
        print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Common Header Types

### 1. Content Type Headers
```python
headers = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json"
}
```

### 2. Authentication Headers
```python
headers = {
    "Authorization": "Bearer your-token-here",
    "X-API-Key": "your-api-key-here"
}
```

### 3. Custom Headers
```python
headers = {
    "X-Client-ID": "your-client-id",
    "X-Request-ID": "unique-request-id",
    "X-Custom-Header": "custom-value"
}
```

## What NOT to Do

### ❌ Wrong: Direct headers parameter
```python
# This will cause an error
client = Client(
    "http://127.0.0.1:8888/mcp",
    headers={"Accept": "application/json"}  # ❌ Not supported
)
```

### ❌ Wrong: Using wrong transport class
```python
# Other transport classes may not support headers
from fastmcp.client.transports import StdioTransport
transport = StdioTransport(...)  # ❌ No headers parameter
```

### ❌ Wrong: Incorrect header format
```python
# Headers must be a dictionary, not a list
headers = ["Accept: application/json"]  # ❌ Wrong format
```

## Transport Classes Comparison

| Transport Class | Headers Support | Use Case |
|------------------|----------------|----------|
| `StreamableHttpTransport` | ✅ Yes | HTTP/HTTPS connections |
| `StdioTransport` | ❌ No | Standard input/output |
| `SSETransport` | ❌ No | Server-sent events |
| `NodeStdioTransport` | ❌ No | Node.js processes |

## Reusable Client Class Example

```python
from typing import Dict, Any, Optional
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

class ConfigurableMCPClient:
    """MCP Client with configurable headers"""
    
    def __init__(self, server_url: str, headers: Optional[Dict[str, str]] = None):
        self.server_url = server_url
        self.mcp_url = f"{server_url}/mcp"
        self.headers = headers or {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        self.client = None
    
    async def get_client(self):
        """Get configured FastMCP client"""
        if self.client is None:
            transport = StreamableHttpTransport(
                url=self.mcp_url,
                headers=self.headers
            )
            self.client = Client(transport)
        return self.client
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None):
        """Call MCP tool"""
        try:
            client = await self.get_client()
            async with client:
                result = await client.call_tool(tool_name, arguments or {})
                return result
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            raise

# Usage
mcp_client = ConfigurableMCPClient(
    server_url="http://127.0.0.1:8888",
    headers={
        "X-Client-ID": "my-app",
        "Authorization": "Bearer token"
    }
)

result = await mcp_client.call_tool("greet", {"name": "User"})
```

## API Reference

### StreamableHttpTransport Constructor

```python
StreamableHttpTransport(
    url: str | AnyUrl,
    headers: dict[str, str] | None = None,
    auth: Union[str, Literal['oauth'], httpx.Auth, NoneType] = None,
    sse_read_timeout: timedelta | float | int | None = None,
    httpx_client_factory: McpHttpClientFactory | None = None
)
```

**Parameters:**
- `url`: The MCP server URL
- `headers`: Dictionary of HTTP headers (optional)
- `auth`: Authentication configuration (optional)
- `sse_read_timeout`: Timeout for SSE connections (optional)
- `httpx_client_factory`: Custom HTTP client factory (optional)

### Client Constructor

```python
Client(
    transport: ClientTransportT | FastMCP | AnyUrl | Path | dict[str, Any] | str,
    name: str | None = None,
    roots: RootsList | RootsHandler | None = None,
    sampling_handler: ClientSamplingHandler | None = None,
    elicitation_handler: ElicitationHandler | None = None,
    log_handler: LogHandler | None = None,
    message_handler: MessageHandlerT | MessageHandler | None = None,
    progress_handler: ProgressHandler | None = None,
    timeout: timedelta | float | int | None = None,
    init_timeout: timedelta | float | int | None = None,
    client_info: mcp.types.Implementation | None = None,
    auth: httpx.Auth | Literal['oauth'] | str | None = None
)
```

**Parameters:**
- `transport`: The transport layer (can be a StreamableHttpTransport instance)
- Other parameters are optional and handle various client configurations

## Testing

To test your FastMCP Client configuration:

1. Start your MCP server
2. Run the example script:
```bash
python fastmcp_client_headers_example.py
```

3. Verify the output shows successful connections and tool calls

## Troubleshooting

### Connection Issues
- Ensure MCP server is running on the correct port
- Check firewall settings
- Verify the URL format (include `/mcp` path)

### Header Issues
- Headers must be a dictionary, not a list
- Header names should be strings
- Header values should be strings

### Authentication Issues
- Verify token format
- Check token expiration
- Ensure authentication headers are correctly formatted

## Files Modified

1. **D:\GitHub_Projects\genesis-ai-app\apps\rest_api\v1\routers\mcp_router.py**
   - Fixed the `_get_client()` method to use `StreamableHttpTransport`
   - Added proper headers configuration

2. **D:\GitHub_Projects\genesis-ai-app\fastmcp_client_headers_example.py**
   - Created comprehensive examples of FastMCP Client configuration
   - Demonstrates different header types and use cases
   - Shows common errors and solutions

## Conclusion

The key insight is that FastMCP Client doesn't accept headers directly, but you can configure them using the `StreamableHttpTransport` class. This approach provides full control over HTTP headers while maintaining the clean FastMCP API.