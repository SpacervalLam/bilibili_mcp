# Bilibili MCP Server

基于 [Model Context Protocol](https://modelcontextprotocol.io) 的 B 站 API 接入服务器，让 AI 助手能够调用 B 站的搜索、视频、用户、评论、热门等能力。

底层依赖 [`bilibili-api-python`](https://github.com/Nemo2011/bilibili-api) 17.x，全程异步实现。

## 功能特性

- **全异步**：基于 `asyncio` + `aiohttp`，与 FastMCP 事件循环天然契合
- **凭证可选**：不配置凭证也能调用公开接口（搜索、视频信息、热门第 1 页等）
- **统一错误处理**：所有异常被捕获并返回 `{"error": ...}`，不会让 MCP 协议层崩溃
- **完整工具集**：12 个工具覆盖搜索/视频/用户/评论/热门/排行榜

## 工具列表

| 工具名 | 描述 |
| --- | --- |
| `search_general` | 通用关键词搜索（综合结果） |
| `search_videos` | 视频搜索（支持排序、分页、每页数量） |
| `get_hot_search_keywords` | 实时热搜词 |
| `get_video_info` | 视频详情（标题/播放量/点赞等） |
| `get_video_pages` | 视频分 P 列表 |
| `get_video_stream_url` | 视频流地址（DASH/FLV/MP4） |
| `get_hot_videos` | 热门视频列表 |
| `get_weekly_hot_videos` | 「每周必看」视频 |
| `get_rank` | 全站/原创/新人排行榜（日/三日/周） |
| `get_user_info` | 用户基本信息 |
| `get_user_videos` | 用户投稿视频 |
| `get_video_comments` | 视频评论列表 |

## 安装

需要 Python >= 3.12，推荐使用 [`uv`](https://github.com/astral-sh/uv)：

```bash
# 1. 克隆并进入项目
git clone <repo-url> bilibili_mcp
cd bilibili_mcp

# 2. 同步依赖（自动创建虚拟环境）
uv sync
```

或使用 `pip`：

```bash
pip install -e .
```

## 凭证配置（可选但推荐）

很多接口（用户信息、评论第 2 页+、需要风控token的接口等）需要登录态。复制示例文件并填入真实值：

```bash
cp .env.example .env
```

`.env` 内容：

```env
BILI_SESSDATA=你的 SESSDATA
BILI_BILI_JCT=你的 bili_jct
BILI_BUVID3=你的 buvid3
BILI_BUVID4=你的 buvid4
BILI_DEDEUSERID=你的 DedeUserID
BILI_AC_TIME_VALUE=你的 ac_time_value
```

**获取方法**：在浏览器登录 B 站 → F12 开发者工具 → Application → Cookies → `bilibili.com` 下复制对应 cookie 值。

## 启动

```bash
python bilibili_mcp_server.py
```

服务器通过 **stdio** 传输与 MCP 客户端通信。

## 在客户端中接入

### Claude Desktop / Cursor / 其它 MCP 客户端

在客户端的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "bilibili": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\bilibili_mcp", "run", "bilibili_mcp_server.py"]
    }
  }
}
```

或使用 Python 直接执行：

```json
{
  "mcpServers": {
    "bilibili": {
      "command": "python",
      "args": ["C:\\path\\to\\bilibili_mcp\\bilibili_mcp_server.py"]
    }
  }
}
```

## 错误处理

所有工具统一返回：

- **成功**：API 原始返回数据（dict）
- **失败**：`{"error": "<错误信息>"}`，同时写入日志

## 日志

通过 stderr 输出，包含：

- 调用参数
- 成功响应概要
- 异常堆栈（含 `exc_info`）

## License

没有
