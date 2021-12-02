import os
import time
import uuid
import io
from ..tareas import file_conversion ,file_update,file_save
from flask import request, send_from_directory, current_app , send_file
from flask.json import jsonify
from flask_restful import Resource
from werkzeug.utils import secure_filename
import requests

ALLOWED_EXTENSIONS = set(['mp3', 'wav', 'ogg', 'aac', 'wma'])
URL_ARCHIVOS = "http://ec2-3-235-152-37.compute-1.amazonaws.com"



class VistaFiles(Resource):

    def post(self):
        print("entreee")
        if 'file' not in request.files:
            resp = jsonify({'message': 'No file part in the request'}) 
            resp.status_code = 400
            return resp
        if 'fileType' not in request.form:
            resp = jsonify({'message': 'No newFormat part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['file']

        if file.filename == '':
            resp = jsonify({'message': 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename.replace("uploaded", "")):
            format = request.form.get("fileType")
            # filename = secure_filename(file.filename.replace("uploaded", ""))
            # filename = '{}.{}'.format(os.path.splitext(filename)[0] + str(uuid.uuid4()),
                                    #   os.path.splitext(filename)[1])  # Build input name
            # MYDIR = os.path.dirname(__file__).replace("vistas", "").replace("/app/","")                          
            # output = os.path.join(current_app.config['UPLOAD_FOLDER_FACES'], filename)
            print("******",file.filename)
            # print(output)
            # file.save(output)
            
            uuidSelected = uuid.uuid4()
            dfile = '{}.{}'.format(os.path.splitext(file.filename)[0] + str(uuidSelected), str(format))  # Build file name
            outputF = os.path.join( current_app.config['UPLOAD_FOLDER_FACES'], dfile)
            # cont=requests.post(URL_ARCHIVOS+'/upload',files=sendFile,verify=False) 
            # sendFile = {"file": (dfile, file.stream, file.mimetype)}
            # outputF = URL_ARCHIVOS+'/download/' + dfile
            # outputF = './tmp/' + dfile
            inputF  = URL_ARCHIVOS+'/upload/' + file.filename 
            print(inputF)
            # json = {
            #     'output':output,
            #     'urlFile':URL_ARCHIVOS,
            #     'outputF':outputF,
            #     'inputF':inputF,
            #     'filename':filename,
            #     'creation_date': str(int(time.time())),
            #     'taskId': 
            # }
            json = {
            'creation_date':str(int(time.time())),
            'filename': file.filename,
            'taskId': request.form.get("taskId"),
            'output':outputF,
            'input':inputF,
            'dfile':dfile,
            'urlFile': URL_ARCHIVOS+'/download'
        }
            #args = (json,)
            print("llegue aca")
            file_conversion.delay(json)
            return "Task converted", 201
        else:
            resp = jsonify(
                {'message': 'Allowed file types are mp3, wav, ogg ,aac ,wma'})
            resp.status_code = 400
            return resp


class VistaGetFiles(Resource):
    def get(self, filename):
        try:
            #print(os.path.join(os.path.dirname(__file__).replace("vistas", "") + current_app.config['DOWNLOAD_FOLDER']))
            content = requests.get(URL_ARCHIVOS+'/download/' + filename, stream=True,verify=False)
            return send_file(io.BytesIO(content.content), as_attachment=True, attachment_filename=filename)
        except FileNotFoundError:
            abort(404)


class VistaUpdateFiles(Resource):

    def put(self):
        # Convert file
        name = request.json['name']
        newFormat = request.json['newFormat']
        status = request.json['status']

        dfile = '{}.{}'.format(os.path.splitext(name)[0] + str(uuid.uuid4()), str(newFormat))  # Build file name

        inputF=URL_ARCHIVOS+'/upload/' +name  # Build input path
        outputF = os.path.join(current_app.config['UPLOAD_FOLDER_FACES'],
                            dfile)  # Build output path

        json = {
            'creation_date': str(int(time.time())),
            'filename': name,
            'dfile': dfile,
            'taskId': request.json["taskId"],
            'status': status,
            'nameFormat': request.json['nameFormat'],
            'output':outputF,
            'input':inputF,
            'urlFile': URL_ARCHIVOS+'/download'
        }

        #args = (json,)
        file_update.delay(json)

        return "Task updated", 201


class VistaDeleteFiles(Resource):

    def delete(self):
        name = request.json['name']
        nameFormat = request.json['nameFormat']
        MYDIR = os.path.dirname(__file__).replace("vistas", "").replace("/app/","")   
        outputF = os.path.join(current_app.config['UPLOAD_FOLDER_FACES'], name)  # Build previous name path
        outputFormat = os.path.join(current_app.config['UPLOAD_FOLDER_FACES'],
                                    nameFormat)  # Build previous format name path
        os.remove(outputF)
        os.remove(outputFormat)

        resp = jsonify(
            {'message': 'Files deleted'}
        )
        resp.status_code = 200
        return resp


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class VistaTest(Resource):
    def get(self):
        return "funcionando"