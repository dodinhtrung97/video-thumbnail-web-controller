from flask import Flask, request, jsonify
import os
import pika
import json
import glob
import requests
app = Flask(__name__)

@app.route("/add", methods=['POST'])
def add_job_to_queue():
    src_host = os.getenv('STORAGE_HOST','localhost')
    src_bucket_name = request.args.get('srcBucketName')
    src_object_name = request.args.get('srcObjectName')
    dest_bucket_name = request.args.get('destBucketName')
    dest_object_name = request.args.get('destObjectName')

    job_request = {
        "srcHost": src_host,
        "srcBucketName": src_bucket_name,
        "srcObjectName": src_object_name,
        "destHost": src_host,
        "destBucketName": dest_bucket_name,
        "destObjectName": dest_object_name
    }

    job = json.dumps(job_request)
    queue_job(job)
    print("Job added to queue")

@app.route("/addAll", methods=['POST'])
def add_all():
    src_host = os.getenv('STORAGE_HOST','localhost')
    src_bucket_name = request.args.get('bucket')

    get_all_object_request_url = "http://" + src_host + ":8080" + '/' + src_bucket_name + "?list"
    all_objects = requests.get(get_all_object_request_url)

    for object in all_objects.get('objects'):
        video_name = object.get('name')
        job_request = {
            "srcHost": src_host,
            "srcBucketName": src_bucket_name,
            "srcObjectName": video_name,
            "destHost": src_host,
            "destBucketName": src_bucket_name,
            "destObjectName": video_name.rsplit('.',1)[0] + ".gif"
        }
        job = json.dumps(job_request)
        queue_job(job)
        print("Job with video name " + video_name + " added to queue")

@app.route("/list", methods=['GET'])
def list():
    src_host = os.getenv('STORAGE_HOST','localhost')
    src_bucket_name = request.args.get('bucket')

    get_all_object_request_url = "http://" + src_host + ":8080" + '/' + src_bucket_name + "?list"
    all_objects = requests.get(get_all_object_request_url)

    all_gifs = []
    for object in all_objects.get('objects'):
    	file_name = object.get('name')
    	if file_name.rsplit(',',1)[1] == 'gif':
    		all_gifs.append(object)

    response = {
    	"created" : all_objects.get('created'),
    	"modified" : all_objects.get('modified'),
    	"name" : all_objects.get('name'),
    	"objects" : all_gifs
    }
    return jsonify(response)


def queue_job(message):
    RABBIT_HOST = os.getenv('RABBIT_HOST','localhost')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue')

    channel.basic_publish(exchange='',
                            routing_key='task_queue',
                            body=message)
    connection.close()

if __name__ == '__main__':
    print("Starting Flask ...")
    app.run(host="0.0.0.0", debug=True, port=5000)