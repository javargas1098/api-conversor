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
URL_ARCHIVOS = "ec2-3-224-135-28.compute-1.amazonaws.com"



class VistaFiles(Resource):

    def post(self):
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
            filename = secure_filename(file.filename.replace("uploaded", ""))
            filename = '{}.{}'.format(os.path.splitext(filename)[0] + str(uuid.uuid4()),
                                      os.path.splitext(filename)[1])  # Build input name
            output = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            print("******",filename)
            print(output)
            file.save(output)
            
            uuidSelected = uuid.uuid4()
            dfile = '{}.{}'.format(os.path.splitext(filename)[
                                        0] + str(uuidSelected), str(format))  # Build file name
            outputF = os.path.join(os.path.dirname(__file__).replace("vistas", "") + current_app.config['DOWNLOAD_FOLDER'], dfile)
            inputF  = URL_ARCHIVOS+'/upload/' + filename 
            json = {
                'output':output,
                'urlFile':URL_ARCHIVOS,
                'outputF':outputF,
                'inputF':inputF,
                'filename':filename,
                'dfile':dfile,
                'creation_date': str(int(time.time())),
                'taskId': request.form.get("taskId")
            }
            #args = (json,)
            file_save.delay(json)
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
        outputF = os.path.join(os.path.dirname(__file__).replace("vistas", "") + current_app.config['DOWNLOAD_FOLDER'],
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
        outputF = os.path.join(current_app.config['UPLOAD_FOLDER'], name)  # Build previous name path
        outputFormat = os.path.join(current_app.config['DOWNLOAD_FOLDER'],
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