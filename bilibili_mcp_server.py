import logging
from bilibili_api import search, sync, video, user, comment
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bilibili_mcp')

mcp = FastMCP('bilibili_mcp')

@mcp.tool('general_search')
def general_search(keyword: str) -> dict:
    """
    Perform a general search on Bilibili with the given keyword.

    Args:
        keyword (str): The keyword to search for on Bilibili.

    Returns:
        dict: A dictionary containing the search results from Bilibili API.
        On error, returns dict with 'error' key containing error message.

    Raises:
        ValueError: If keyword is empty or too long (>100 chars)
    """
    if not keyword or len(keyword) > 100:
        error_msg = "Keyword must be 1-100 characters long"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        logger.info(f"Searching Bilibili for: {keyword}")
        search_result = search.search(keyword)
        result = sync(search_result)
        logger.info(f"Search completed for: {keyword}")
        return result
    except Exception as e:
        logger.error(f"Search failed for {keyword}: {str(e)}")
        return {'error': str(e)}

@mcp.tool('video_info')
def video_info(aid: int) -> dict:
    """
    Get the information of a video on Bilibili with the given AID.

    Args:
        aid (int): The AID of the video to get information for.

    Returns:
        dict: A dictionary containing the video information from Bilibili API.
        On error, returns dict with 'error' key containing error message.

    Raises:
        ValueError: If aid is not a positive integer
    """
    if not isinstance(aid, int) or aid <= 0:
        error_msg = f"Invalid AID: {aid}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        logger.info(f"Fetching video info for AID: {aid}")
        video_result = video.get_video_info(aid)
        result = sync(video_result)
        logger.info(f"Successfully fetched video info for AID: {aid}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch video info for AID {aid}: {str(e)}")
        return {'error': str(e)}

@mcp.tool('user_info')
def user_info(uid: int) -> dict:
    """
    Get information about a Bilibili user by UID.

    Args:
        uid (int): The UID of the user to get information for.

    Returns:
        dict: A dictionary containing the user information from Bilibili API.
        On error, returns dict with 'error' key containing error message.

    Raises:
        ValueError: If uid is not a positive integer
    """
    if not isinstance(uid, int) or uid <= 0:
        error_msg = f"Invalid UID: {uid}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        logger.info(f"Fetching user info for UID: {uid}")
        user_result = user.get_user_info(uid)
        result = sync(user_result)
        logger.info(f"Successfully fetched user info for UID: {uid}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch user info for UID {uid}: {str(e)}")
        return {'error': str(e)}

@mcp.tool('video_comments')
def video_comments(aid: int, page: int = 1) -> dict:
    """
    Get comments for a video by AID.

    Args:
        aid (int): The AID of the video
        page (int): Page number of comments (default: 1)

    Returns:
        dict: A dictionary containing the video comments from Bilibili API.
        On error, returns dict with 'error' key containing error message.

    Raises:
        ValueError: If aid is not positive or page is < 1
    """
    if not isinstance(aid, int) or aid <= 0 or page < 1:
        error_msg = f"Invalid parameters: aid={aid}, page={page}"
        logger.error(error_msg)
        raise ValueError("AID must be positive and page >= 1")
    
    try:
        logger.info(f"Fetching comments for AID: {aid}, page: {page}")
        comments = comment.get_comments(aid, page)
        result = sync(comments)
        logger.info(f"Successfully fetched comments for AID: {aid}, page: {page}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch comments for AID {aid}: {str(e)}")
        return {'error': str(e)}

@mcp.tool('popular_videos')
def popular_videos() -> dict:
    """
    Get popular videos from Bilibili.

    Returns:
        dict: A dictionary containing popular videos from Bilibili API.
        On error, returns dict with 'error' key containing error message.
    """
    try:
        logger.info("Fetching popular videos")
        popular = video.get_popular()
        result = sync(popular)
        logger.info("Successfully fetched popular videos")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch popular videos: {str(e)}")
        return {'error': str(e)}

if __name__ == '__main__':
    mcp.run(transport='stdio')
