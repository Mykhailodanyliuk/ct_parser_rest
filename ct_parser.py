import datetime
import json
import os
import shutil
import time
from zipfile import ZipFile
import requests

import wget


def delete_directory(path_to_directory):
    if os.path.exists(path_to_directory):
        shutil.rmtree(path_to_directory)


def create_directory(path_to_dir, name):
    mypath = f'{path_to_dir}/{name}'
    if not os.path.isdir(mypath):
        os.makedirs(mypath)


def download_file(url, file_name):
    try:
        wget.download(url, file_name)
    except:
        download_file(url, file_name)


def upload_clinical_trials(ct_data_rest_url):
    current_directory = os.getcwd()
    directory_name = 'clinical_trials'
    path_to_directory = f'{current_directory}/{directory_name}'
    delete_directory(path_to_directory)
    create_directory(current_directory, directory_name)
    path_to_zip = f'{path_to_directory}/AllAPIJSON.zip'
    download_file('https://ClinicalTrials.gov/AllAPIJSON.zip', path_to_zip)
    with ZipFile(path_to_zip, 'r') as zip:
        zip_files = zip.namelist()
        zip_files.remove('Contents.txt')
        for index, file in enumerate(zip_files):
            try:
                response = requests.get(f'{ct_data_rest_url}?FullStudy.Study.ProtocolSection.IdentificationModule.NCTId={file[-16:-5]}')
            except:
                continue
            if response.status_code == 200:
                response_json = json.loads(response.text)
                is_in_database = False if response_json.get('total') == 0 else True
                if not is_in_database:
                    zip.extract(file, path=path_to_directory, pwd=None)
                    with open(f'{path_to_directory}/{file}', 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)
                        requests.post(ct_data_rest_url, json=data)
    delete_directory(path_to_directory)


if __name__ == '__main__':
    collection_url = 'http://62.216.33.167:21005/api/clinical_trials'
    while True:
        start_time = time.time()
        upload_clinical_trials(collection_url)
        work_time = int(time.time() - start_time)
        print(work_time)
        print(14400 - work_time)
        time.sleep(abs(work_time % 14400 - 14400))
