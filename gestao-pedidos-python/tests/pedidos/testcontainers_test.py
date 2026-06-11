import os

import pytest


pytestmark = pytest.mark.integration


@pytest.mark.skipif(os.getenv("RUN_TESTCONTAINERS") != "1", reason="Defina RUN_TESTCONTAINERS=1 para executar.")
def test_redis_com_testcontainers():
    from redis import Redis
    from testcontainers.redis import RedisContainer

    with RedisContainer("redis:7-alpine") as redis_container:
        client = Redis.from_url(redis_container.get_connection_url(), decode_responses=True)
        client.set("pedido:1", "criado", ex=30)

        assert client.get("pedido:1") == "criado"

