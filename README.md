# Bilibili MCP Server

A Model Context Protocol (MCP) server that provides access to Bilibili's API functionality.

## Features

- Search Bilibili content
- Get video information
- Get user information
- Fetch video comments

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies:
```bash
pip install bilibili-api mcp-server-fastmcp
```

3. Run the server:
```bash
python bilibili_mcp_server.py
```

## API Endpoints

### General Search
```python
@mcp.tool('general_search')
def general_search(keyword: str) -> dict
```
Searches Bilibili for the given keyword.

Example:
```json
{"keyword": "python tutorial"}
```

### Video Information
```python
@mcp.tool('video_info')
def video_info(aid: int) -> dict
```
Gets information about a video by its AID.

Example:
```json
{"aid": 123456}
```

### User Information
```python
@mcp.tool('user_info')
def user_info(uid: int) -> dict
```
Gets information about a user by their UID.

Example:
```json
{"uid": 123456}
```

### Video Comments
```python
@mcp.tool('video_comments')
def video_comments(aid: int, page: int = 1) -> dict
```
Gets comments for a video by AID and page number.

Example:
```json
{"aid": 123456, "page": 1}
```

### Popular Videos
```python
@mcp.tool('popular_videos')
def popular_videos() -> dict
```
Gets currently popular videos on Bilibili.

Example:
```json
{}
```

## Error Handling

All endpoints return:
- Success: API response data
- Error: Dictionary with "error" key containing error message

Common errors:
- Invalid input parameters (ValueError)
- API request failures
- Network issues

## Logging

The server logs all operations to stdout with timestamps. Logs include:
- API calls with parameters
- Successful responses
- Error conditions

## License

没有
