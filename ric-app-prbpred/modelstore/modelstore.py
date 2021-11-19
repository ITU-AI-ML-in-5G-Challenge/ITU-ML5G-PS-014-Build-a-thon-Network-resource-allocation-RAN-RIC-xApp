# ==================================================================================
#  This SW is developed as part of ITU-5G-AI/ML challenge
#  ITU-ML5G-PS-014: Build-a-thon(PoC) Network resource allocation
#  for emergency management based on closed loop analysis
#  Team : RAN-RIC-xApp
#  Author : Divyani R Achari
# ==================================================================================


from flask import Flask, send_from_directory
from art import *
repo_app = Flask(__name__)

DOWNLOAD_DIRECTORY = "/root/customxapp/model_store"

@repo_app.route('/model_store/1.0.0/<path:path>',methods = ['GET','POST'])
def get_files(path):
    print('path',path)
    return send_from_directory(DOWNLOAD_DIRECTORY, path, as_attachment=True)

if __name__ == '__main__':
    Art=text2art("ACUMOS",font="rnd-xlarge",chr_ignore=True)
    print(Art)
    repo_app.run(host='0.0.0.0', port=10001, threaded=True)
