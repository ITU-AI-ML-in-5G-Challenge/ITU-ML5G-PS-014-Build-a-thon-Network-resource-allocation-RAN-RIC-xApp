Usage of all the programs and files have been mentioned below for the reference.

main.py:
* Initiates A1 policy query towards A1-mediator
* Based on the policy details received from A1-mediator, initiates download of model from model store
* Receives PRB_PRED_REQ from alloc xApp, performs predictions and sends PRB_PRED_RESP to alloc xApp
Note: Currently A1 mediator doesn't send CREATE/UPDATE request when the policy instance is created. 
Code flow to be modified when this is supported to directly send prediction input to alloc xApp or get rid of alloc xApp and send PRB allocation to E2


How to build prbpred xApp
docker build -t prbpredxapp:3.0 -f  Dockerfile .
docker run -d --net=host -e USE_FAKE_SDL=1 prbpredxapp:3.0
docker tag alloc:3.0 nexus3.o-ran-sc.org:10002/o-ran-sc/ric-app-prbpredxapp:0.0.2

How to onboard xApp in RIC platform
cd xapp-descriptor
dms_cli onboard --config_file_path=config.json --shcema_file_path=/root/appmgr/xapp_orchestrater/dev/docs/xapp_onboarder/guide/embedded-schema.json
dms_cli install --xapp_chart_name=prbpred --version=0.0.2 --namespace=ricxapp

Uninstall xApp
dms_cli uninstall prbpred ricxapp
