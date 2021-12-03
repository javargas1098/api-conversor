import datetime
import os
import subprocess as sp
from subprocess import Popen, PIPE
from celery import Celery
from celery.signals import task_postrun
from flask import current_app,Flask,send_from_directory
from ..modelos import Task, TaskSchema,db
import requests
import boto3


broker = os.environ['REDIS_URL']
backend = os.environ['REDIS_URL']
URL_ARCHIVOS = "http://ec2-3-236-163-109.compute-1.amazonaws.com"

celery  = Celery(__name__, broker=broker,
                backend=backend)
# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", 'redis://redis:6379/0')
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND",  'redis://redis:6379/0')
celery.conf.broker_pool_limit = 0


def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:uniandes@db-0001.cexmvypaid2k.us-east-1.rds.amazonaws.com:5432/postgres"
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['JWT_SECRET_KEY']='frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

@celery.task(name="file_save")
def file_save(request_json):
    app = create_app('default')
    db.init_app(app)
    output = request_json["output"] 
    inputF  = request_json["inputF"]  
    urlFile = request_json["urlFile"] 
    filename = request_json["filename"]
    outputF = request_json["outputF"]
    creation_date = request_json["creation_date"]
    # dfile = request_json["dfile"] 
    taskId = request_json["taskId"] 
    with app.app_context():
        # file = open(output, "rb")
        # sendFile = {"file": file}
        # requests.post(urlFile+'/upload',files=sendFile) 
        # os.remove(output) 
        # file = requests.get(URL_ARCHIVOS+'/upload/'+filename)              
        json = {
            'creation_date':creation_date,
            'filename': filename,
            'taskId': taskId,
            'output':outputF,
            'input':inputF,
            'urlFile': urlFile+'/download'
        }
        #args = (json,)
        file_conversion.delay(json)
    return True

@celery.task(name="file_conversion")
def file_conversion(request_json):
    app = create_app('default')
    db.init_app(app)
    # Build input path and add file
    # inputF = os.path.join(
    #     os.path.dirname(__file__).replace("tareas", "") + current_app.config['UPLOAD_FOLDER'],
    #     request_json["filename"])
    # Build output path and add file
   
    outputF = request_json["output"] 
    inputF  = request_json["input"] 
    urlFile = request_json["urlFile"] 
    # 
    
    # Ffmpeg is flexible enough to handle wildstar conversions
    # convertCMD = ['ffmpeg', '-y', '-i', inputF, outputF]
    print("**/****",inputF)
    print("**/****",outputF)
    
    # ffmpeg -re -i in.ts -f hls -method PUT http://example.com/live/out.m3u8
    # convertCMD = ['ffmpeg', '-re', '-i','-f' ,'hls' ,'-method PUT', inputF, out]
    
    convertCMD = ['ffmpeg', '-y', '-i', inputF, outputF]
    executeOrder66 = sp.Popen(convertCMD)
    
    try:
        # executeOrder66 = sp.run(convertCMD, stdout=sp.PIPE, stderr=sp.PIPE,timeout=10)
        outs, errs = executeOrder66.communicate(
            timeout=10)  # tell program to wait
    except TimeoutError:
        proc.kill()

    print("DONE\n")
    # send_from_directory(directory=current_app.config['UPLOAD_FOLDER_FACES'], filename=request_json["dfile"], as_attachment=True)
    #send download file to s3 and delete from local
    #upload file
    '''fileUp = open(os.path.join(
         os.path.dirname(__file__).replace("tareas", "") + current_app.config['DOWNLOAD_FOLDER'], request_json["filename"]), "rb")
    sendFileUp = {"file": fileUp}
    requests.post(os.getenv('URL_ARCHIVOS')+'/upload',
                                files=sendFileUp)
    os.remove(os.path.join(
         os.path.dirname(__file__).replace("tareas", "") + current_app.config['DOWNLOAD_FOLDER'], request_json["filename"]))
    '''
    #download file
    # print("oooooooooooooooooooooo")
    # print(os.getcwd())
    # print(os.path.dirname(__file__))
    # print(outputF)
    # file.save(outputF)
    f = open(outputF, "rb")
    # sendFile2 = {"file": (request_json["dfile"], f.stream, f.mimetype)}
    sendFile = {"file": f}
    print("file",sendFile)
    # file = open(outputF, "rb")
    # file = requests.get(URL_ARCHIVOS+'/download/'+request_json["filename"])
    # sendFile = {"file": file.content}
    
    requests.post(urlFile,files=sendFile)
    # Build previous format name path
    # os.remove(outputF)
    # Update DB
    with app.app_context():
        task = Task.query.get_or_404(request_json["taskId"])
        task.name = request_json["filename"]
        task.status = "PROCESSED"
        task.nameFormat = request_json["dfile"]
        task.dateUp = task.dateUp
        ts2 = datetime.datetime.now()
        task.datePr = ts2
        db.session.commit()
    return True

@celery.task(name="file_update")
def file_update(request_json):
    app = create_app('default')
    db.init_app(app)
    with app.app_context():
        outputF = request_json["output"] 
        inputF  = request_json["input"] 
        urlFile = request_json["urlFile"] 
        urlFile = URL_ARCHIVOS+'/download'
       
        # Ffmpeg is flexible enough to handle wildstar conversions
        # convertCMD = ['ffmpeg', '-y', '-i', inputF, outputF]
        convertCMD = ['ffmpeg', '-y', '-i', inputF, outputF]
        # convertCMD = ['ffmpeg', '-y', '-i', inputF, outputF]
        executeOrder66 = sp.Popen(convertCMD)

        try:
            outs, errs = executeOrder66.communicate(timeout=20)  # tell program to wait
        except TimeoutError:
            proc.kill()

        # Delete previous file
        if request_json["status"] == "PROCESSED":
            previousName = request_json['nameFormat']
            # outputF = os.path.join(os.path.dirname(__file__).replace("tareas", "") + current_app.config['DOWNLOAD_FOLDER'],
            #                        previousName)  # Build previous path
            # os.remove(outputF)
            
            #send download file to s3 and delete from local
        
            file = open(outputF, "rb")
            sendFile = {"file": file}
            requests.post(urlFile,files=sendFile)
            #outputFormat = os.path.join(current_app.config['DOWNLOAD_FOLDER'],request_json["dfile"])  # Build previous format name path
            os.remove(outputF)

        print("DONE\n")

        task = Task.query.get_or_404(request_json["taskId"])
        task.status = "PROCESSED"
        task.datePr = datetime.datetime.now()
        task.nameFormat = request_json["dfile"]

        db.session.commit()
    return True

'''@task_postrun.connect
def close_session(*args, **kwargs):
    db.session.remove()'''         
