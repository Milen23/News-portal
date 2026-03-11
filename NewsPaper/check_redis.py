import redis
import ssl

REDIS_URL ='redis://localhost:6379/0'

# Разбираем URL
# redis://:password@host:port
parts = REDIS_URL.replace('redis://', '').split('@')
credentials = parts[0].split(':')
host_port = parts[1].split(':')

password = credentials[1]  # password после :
host = host_port[0]
port = int(host_port[1])

print(f"Host: {host}")
print(f"Port: {port}")
print(f"Password: {'*' * len(password)}")

# Пробуем подключиться разными способами
print("\n1. Попытка подключения без SSL:")
try:
    r = redis.Redis(
        host=host,
        port=port,
        password=password,
        socket_connect_timeout=5,
        socket_timeout=5,
        decode_responses=True
    )
    r.ping()
    print("✅ Успешно подключились!")
    print(f"Информация о сервере: {r.info('server')['redis_version']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n2. Попытка подключения с SSL:")
try:
    r = redis.Redis(
        host=host,
        port=port,
        password=password,
        ssl=True,
        ssl_cert_reqs=None,  # для самоподписанных сертификатов
        socket_connect_timeout=5,
        socket_timeout=5,
        decode_responses=True
    )
    r.ping()
    print("✅ Успешно подключились с SSL!")
    print(f"Информация о сервере: {r.info('server')['redis_version']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")