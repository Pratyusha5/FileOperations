# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import os.path , time
from flask import Flask, request, render_template
from cloudant.client import Cloudant
import hashlib
from cloudant.result import Result, ResultByKey


app = Flask(__name__)


USERNAME = "3f2b68b8-522e-46a3-86ce-43540e6e01cb-bluemix"
PASSWORD = "6b5352b22793a61ed7849015b2355b7ecade2544d4de08275b81263af3477f56"
service_url = "https://3f2b68b8-522e-46a3-86ce-43540e6e01cb-bluemix:6b5352b22793a61ed7849015b2355b7ecade2544d4de08275b81263af3477f56@3f2b68b8-522e-46a3-86ce-43540e6e01cb-bluemix.cloudant.com"

# setting up the connection

client = Cloudant(USERNAME, PASSWORD, url=service_url)

client.connect()
print "Connection is established."
session = client.session()

#creating database
databasename = 'flask_database'
my_database =client[databasename]
if my_database.exists():
  print "'{0}' Database created sucessfully.\n".format(databasename)


@app.route('/')
def index():
    return app.send_static_file('index.html')

#uploading the file
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file_name = file.filename
    #last_modified_date = time.ctime(os.path.getctime(str(file_name)))
    original_content = file.read()
    hasher = hashlib.md5()
    hasher.update(original_content)
    hashid = hasher.hexdigest()

    for doc in my_database:
        if doc['file_name'] == file_name and doc['HashID'] == hashid:
            status = ("File already exists!!")
            return status
    for doc in my_database:
        if doc['file_name'] == file_name and doc['HashID'] != hashid:
            data = {'file_name': file_name, 'HashID': hashid, 'Contents': original_content,
                        'Version': doc['Version'] + 1}
            my_database.create_document(data)
            status = 'Different version of file has been uploaded!!'
            return status
    for doc in my_database:
        if doc['file_name'] != file_name:
            data = {'file_name': file_name, 'HashID': hashid, 'Contents': original_content,
                            'Version': 1}
            my_database.create_document(data)
            status = "File uploaded sucessfully!!"
            return status
    return "done!!"


@app.route('/download', methods=['POST'])
def download():
    file_name = request.form['filename']
    print(file_name)
    file_version = request.form['version']
    print(file_version)
    for doc in my_database:
        if doc['file_name'] == file_name and doc['Version'] == int(file_version):
            contents = doc['Contents']
            with open('C:\Users\manya\Desktop\ContentFile.txt', 'w+') as my_example:
                my_example.write(contents)
                status = "File downloaded sucessfully!!"
                break
        else:
                status = "File could not be found in the Cloudant DB!!"
    return status

@app.route('/delete', methods=['POST'])
def delete():
    file_name = request.form['filename']
    file_version = request.form['version']
    for doc in my_database:
        if doc['file_name'] == file_name and doc['Version'] == int(file_version):
            doc.delete()
            status = "File found and deleted!"
            break
        else:
            status = "File not found!!"
    return status

@app.route('/list_files', methods=['POST'])
def list_files():
    docs = []
    for doc in my_database:
        filename =doc['file_name']
        vers =doc['Version']
        doclist = ['FileName:  '+str(filename) ,'Version:  '+str(vers)]
        docs.append(doclist)
        print(docs)
    return '<h3>The files currently on cloud are: </h3><br><br><ol>' + str(docs) + '<br><form action="../"></form>'

if __name__ == "__main__":
    app.run(port=455,debug=True)



