import httpx
from dataclasses import dataclass
from contextlib import asynccontextmanager

from mcp.server import FastMCP
from mcp.server.fastmcp import Context


@dataclass
# 初始化一个生命周期上下文对象
class AppContext:
    # 里面有一个字段用于存储请求历史
    histories: dict


@asynccontextmanager
async def app_lifespan(server):
    # 在 MCP 初始化时执行
    histories = {}
    try:
        # 每次通信会把这个上下文通过参数传入工具
        yield AppContext(histories=histories)
    finally:
        # 当 MCP 服务关闭时执行
        print(histories)


app = FastMCP(
    'web-search', 
    # 设置生命周期监听函数
    lifespan=app_lifespan
)


@app.tool()
# 第一个参数会被传入上下文对象
async def web_search(ctx: Context, query: str) -> str:
    """
    搜索互联网内容

    Args:
        query: 要搜索内容

    Returns:
        搜索结果的总结
    """
    # 如果之前问过同样的问题，就直接返回缓存
    histories = ctx.request_context.lifespan_context.histories
    if query in histories:
    	return histories[query]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://open.bigmodel.cn/api/paas/v4/tools',
            headers={'Authorization': 'YOUR API KEY'},
            json={
                'tool': 'web-search-pro',
                'messages': [
                    {'role': 'user', 'content': query}
                ],
                'stream': False
            }
        )

        res_data = []
        for choice in response.json()['choices']:
            for message in choice['message']['tool_calls']:
                search_results = message.get('search_result')
                if not search_results:
                    continue
                for result in search_results:
                    res_data.append(result['content'])

        return_data = '\n\n\n'.join(res_data)

        # 将查询值和返回值存入到 histories 中
        ctx.request_context.lifespan_context.histories[query] = return_data
        return return_data


if __name__ == "__main__":
    app.run()
