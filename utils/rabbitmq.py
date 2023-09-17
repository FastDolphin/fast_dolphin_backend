import time
import pika


def connect_to_rabbitmq(rabbitmq_host, rabbitmq_user, rabbitmq_pass):
    max_retries = 10
    retry_delay = 5  # in seconds
    for _ in range(max_retries):
        try:
            print(f"Attempting to connect to RabbitMQ host: {rabbitmq_host}")
            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=rabbitmq_host,
                credentials=credentials,
                heartbeat=600,  # set a 10-minute heartbeat (you can adjust this value)
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue="notify_admin")
            print("Connected to RabbitMQ successfully!")
            return connection, channel
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            time.sleep(retry_delay)
    else:
        raise Exception("Failed to connect to RabbitMQ after multiple retries")


# Proactive Monitoring (optional but recommended)
async def monitor_rabbitmq_connection():
    while True:
        if not app.rabbitmq_connection.is_open:
            print("RabbitMQ connection lost. Reconnecting...")
            app.rabbitmq_connection, app.rabbitmq_channel = connect_to_rabbitmq()
        await asyncio.sleep(60)  # check every minute
