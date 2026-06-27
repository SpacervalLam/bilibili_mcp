"""Bilibili MCP Server.

基于 bilibili-api-python 17.x 的全异步实现，提供搜索、视频、用户、评论、热门等
B 站功能的 Model Context Protocol 工具集。

凭证通过 .env 文件配置（参考 .env.example）。不配置凭证也能使用公开接口。
"""

from __future__ import annotations

import logging
import os
from functools import wraps
from typing import Any, Callable, Optional

from bilibili_api import (
    Credential,
    comment,
    hot,
    rank,
    search,
    user,
    video,
)
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("bilibili_mcp")

# ---------------------------------------------------------------------------
# 凭证加载
# ---------------------------------------------------------------------------
load_dotenv()


def _load_credential() -> Optional[Credential]:
    """从环境变量加载 B 站凭证。任一关键字段缺失则返回 None。"""
    sessdata = os.getenv("BILI_SESSDATA", "").strip()
    bili_jct = os.getenv("BILI_BILI_JCT", "").strip()
    if not sessdata and not bili_jct:
        logger.info("未配置 BILI_SESSDATA / BILI_BILI_JCT，仅使用匿名访问")
        return None

    return Credential(
        sessdata=sessdata or None,
        bili_jct=bili_jct or None,
        buvid3=os.getenv("BILI_BUVID3", "").strip() or None,
        buvid4=os.getenv("BILI_BUVID4", "").strip() or None,
        dedeuserid=os.getenv("BILI_DEDEUSERID", "").strip() or None,
        ac_time_value=os.getenv("BILI_AC_TIME_VALUE", "").strip() or None,
    )


CREDENTIAL = _load_credential()

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP("bilibili_mcp")


def _safe(tool: Callable[..., Any]) -> Callable[..., Any]:
    """统一异常捕获装饰器：记录日志并将异常转为 {"error": ...} 返回。"""

    @wraps(tool)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await tool(*args, **kwargs)
        except Exception as e:  # noqa: BLE001 - MCP 工具向外暴露错误
            logger.error("%s 调用失败: %s", tool.__name__, e, exc_info=True)
            return {"error": str(e)}

    return wrapper


# ---------------------------------------------------------------------------
# 工具实现
# ---------------------------------------------------------------------------
@mcp.tool()
@_safe
async def search_general(keyword: str, page: int = 1) -> dict:
    """在 B 站进行通用关键词搜索（综合结果，包含视频/番剧/用户等）。

    Args:
        keyword: 搜索关键词，长度 1-100
        page: 页码，从 1 开始
    """
    if not keyword or len(keyword) > 100:
        return {"error": "keyword 长度需在 1-100 之间"}
    if page < 1:
        return {"error": "page 必须 >= 1"}
    logger.info("通用搜索: keyword=%s page=%d", keyword, page)
    return await search.search(keyword, page=page)


@mcp.tool()
@_safe
async def search_videos(
    keyword: str,
    page: int = 1,
    page_size: int = 20,
    order: str = "totalrank",
) -> dict:
    """在 B 站按关键词搜索视频。

    Args:
        keyword: 搜索关键词，长度 1-100
        page: 页码，从 1 开始
        page_size: 每页数量，1-50
        order: 排序方式，可选: totalrank(综合) / click(最多播放) / pubdate(最新) /
            dm(最多弹幕) / stow(最多收藏) / scores(最多评论)
    """
    if not keyword or len(keyword) > 100:
        return {"error": "keyword 长度需在 1-100 之间"}
    if page < 1 or page_size < 1 or page_size > 50:
        return {"error": "page >= 1 且 1 <= page_size <= 50"}

    order_map = {
        "totalrank": search.OrderVideo.TOTALRANK,
        "click": search.OrderVideo.CLICK,
        "pubdate": search.OrderVideo.PUBDATE,
        "dm": search.OrderVideo.DM,
        "stow": search.OrderVideo.STOW,
        "scores": search.OrderVideo.SCORES,
    }
    if order not in order_map:
        return {"error": f"order 非法，可选: {list(order_map.keys())}"}

    logger.info("视频搜索: keyword=%s page=%d size=%d order=%s", keyword, page, page_size, order)
    return await search.search_by_type(
        keyword=keyword,
        search_type=search.SearchObjectType.VIDEO,
        order_type=order_map[order],
        page=page,
        page_size=page_size,
    )


@mcp.tool()
@_safe
async def get_hot_search_keywords() -> dict:
    """获取 B 站实时热搜词列表。"""
    logger.info("获取热搜词")
    return await search.get_hot_search_keywords()


@mcp.tool()
@_safe
async def get_video_info(bvid: Optional[str] = None, aid: Optional[int] = None) -> dict:
    """获取视频详细信息（标题、UP 主、播放量、点赞、投币等）。

    Args:
        bvid: 视频 BV 号，如 BV1uv411q7Mv
        aid: 视频 AV 号（与 bvid 至少传一个，bvid 优先）
    """
    if not bvid and not aid:
        return {"error": "bvid 和 aid 至少提供一个"}
    v = video.Video(bvid=bvid, aid=aid, credential=CREDENTIAL)
    logger.info("获取视频信息: bvid=%s aid=%s", bvid, aid)
    return await v.get_info()


@mcp.tool()
@_safe
async def get_video_pages(bvid: Optional[str] = None, aid: Optional[int] = None) -> dict:
    """获取视频分 P 列表（多 P 视频的章节信息）。

    Args:
        bvid: 视频 BV 号
        aid: 视频 AV 号（与 bvid 至少传一个，bvid 优先）
    """
    if not bvid and not aid:
        return {"error": "bvid 和 aid 至少提供一个"}
    v = video.Video(bvid=bvid, aid=aid, credential=CREDENTIAL)
    logger.info("获取视频分 P: bvid=%s aid=%s", bvid, aid)
    return await v.get_pages()


@mcp.tool()
@_safe
async def get_video_stream_url(
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    page_index: int = 0,
) -> dict:
    """获取视频可下载流地址（DASH/FLV/MP4）。

    Args:
        bvid: 视频 BV 号
        aid: 视频 AV 号（与 bvid 至少传一个，bvid 优先）
        page_index: 分 P 序号，从 0 开始
    """
    if not bvid and not aid:
        return {"error": "bvid 和 aid 至少提供一个"}
    if page_index < 0:
        return {"error": "page_index >= 0"}
    v = video.Video(bvid=bvid, aid=aid, credential=CREDENTIAL)
    logger.info("获取视频流地址: bvid=%s aid=%s page_index=%d", bvid, aid, page_index)
    return await v.get_download_url(page_index=page_index)


@mcp.tool()
@_safe
async def get_hot_videos(pn: int = 1, ps: int = 20) -> dict:
    """获取 B 站热门视频列表。

    Args:
        pn: 页码，从 1 开始
        ps: 每页数量，1-50
    """
    if pn < 1 or ps < 1 or ps > 50:
        return {"error": "pn >= 1 且 1 <= ps <= 50"}
    logger.info("获取热门视频: pn=%d ps=%d", pn, ps)
    return await hot.get_hot_videos(pn=pn, ps=ps)


@mcp.tool()
@_safe
async def get_weekly_hot_videos(week: int = 1) -> dict:
    """获取 B 站「每周必看」视频列表。

    Args:
        week: 第几期，从 1 开始；不传默认最新一期
    """
    if week < 1:
        return {"error": "week >= 1"}
    logger.info("获取每周必看: week=%d", week)
    return await hot.get_weekly_hot_videos(week=week)


@mcp.tool()
@_safe
async def get_rank(rank_type: str = "all", days: str = "3") -> dict:
    """获取 B 站排行榜视频。

    Args:
        rank_type: 排行榜类型，可选: all(全站) / origin(原创) / rookie(新人)
        days: 时间范围，可选: 1(日榜) / 3(三日榜) / 7(周榜)
    """
    type_map = {
        "all": rank.RankType.All,
        "origin": rank.RankType.Origin,
        "rookie": rank.RankType.Rookie,
    }
    day_map = {
        "1": rank.RankDayType.ONE_DAY,
        "3": rank.RankDayType.THREE_DAY,
        "7": rank.RankDayType.SEVEN_DAY,
    }
    if rank_type not in type_map:
        return {"error": f"rank_type 非法，可选: {list(type_map.keys())}"}
    if days not in day_map:
        return {"error": f"days 非法，可选: {list(day_map.keys())}"}
    logger.info("获取排行榜: type=%s days=%s", rank_type, days)
    return await rank.get_rank(type_=type_map[rank_type], day=day_map[days])


@mcp.tool()
@_safe
async def get_user_info(uid: int) -> dict:
    """获取 B 站用户信息（昵称、性别、签名、头像、等级等）。

    Args:
        uid: 用户 UID，正整数
    """
    if not isinstance(uid, int) or uid <= 0:
        return {"error": "uid 必须为正整数"}
    u = user.User(uid=uid, credential=CREDENTIAL)
    logger.info("获取用户信息: uid=%d", uid)
    return await u.get_user_info()


@mcp.tool()
@_safe
async def get_user_videos(uid: int, pn: int = 1, ps: int = 30) -> dict:
    """获取用户投稿视频列表。

    Args:
        uid: 用户 UID
        pn: 页码，从 1 开始
        ps: 每页数量，1-50
    """
    if not isinstance(uid, int) or uid <= 0:
        return {"error": "uid 必须为正整数"}
    if pn < 1 or ps < 1 or ps > 50:
        return {"error": "pn >= 1 且 1 <= ps <= 50"}
    u = user.User(uid=uid, credential=CREDENTIAL)
    logger.info("获取用户投稿: uid=%d pn=%d ps=%d", uid, pn, ps)
    return await u.get_videos(pn=pn, ps=ps)


@mcp.tool()
@_safe
async def get_video_comments(
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    page_index: int = 1,
    order: str = "time",
) -> dict:
    """获取视频评论列表。

    注意：第 2 页及以后需要配置凭证。

    Args:
        bvid: 视频 BV 号
        aid: 视频 AV 号（与 bvid 至少传一个，bvid 优先）
        page_index: 评论页码，从 1 开始
        order: 排序方式，可选: time(按时间) / like(按点赞)
    """
    if not bvid and not aid:
        return {"error": "bvid 和 aid 至少提供一个"}
    if page_index < 1:
        return {"error": "page_index >= 1"}

    order_map = {
        "time": comment.OrderType.TIME,
        "like": comment.OrderType.LIKE,
    }
    if order not in order_map:
        return {"error": f"order 非法，可选: {list(order_map.keys())}"}

    v = video.Video(bvid=bvid, aid=aid, credential=CREDENTIAL)
    oid = v.get_aid()
    logger.info("获取视频评论: bvid=%s aid=%s page=%d order=%s", bvid, aid, page_index, order)
    return await comment.get_comments(
        oid=oid,
        type_=comment.CommentResourceType.VIDEO,
        page_index=page_index,
        order=order_map[order],
        credential=CREDENTIAL,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
