import asyncio


def run_async(coroutine):
    """비동기 함수를 안전하게 실행하는 헬퍼"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 이미 루프가 돌고 있으면 그 안에서 실행
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(coroutine)
        else:
            return loop.run_until_complete(coroutine)
    except RuntimeError:
        # 루프가 없으면 새로 만들어서 실행
        return asyncio.run(coroutine)
