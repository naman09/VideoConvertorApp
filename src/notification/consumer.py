import pika, sys, os
from send import email


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = email.notification(body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=os.environ.get("MP3_QUEUE"), on_message_callback=callback)

    print("Waiting for messages")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        # test_data = {"mp3_fid": "dwadwad", "username": "nadnad"}
        # email.notification(json.dumps(test_data))
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)





