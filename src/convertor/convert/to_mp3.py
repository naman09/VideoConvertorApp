import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor


def start(message, fs_videos, fs_mp3, channel):
    message = json.loads(message)

    # empty temp file
    tf = tempfile.NamedTemporaryFile()

    out = fs_videos.get(ObjectId(message["video_fid"]))

    tf.write(out.read())

    audio = moviepy.editor.VideoFileClip(tf.name).audio

    tf.close()

    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"

    audio.write_audiofile(tf_path)

    f = open(tf_path, "rb")
    data = f.read()
    audio_fid = fs_mp3.put(data)

    os.remove(tf_path)

    message['mp3_fid'] = str(audio_fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
    except Exception as err:
        fs_mp3.delete(audio_fid)
        return "failed to publish message"


