from flask import Flask
from flask import jsonify
from flask import request,make_response
from flask import abort
from flask import url_for
from flask.views import MethodView
from flask.ext.httpauth import HTTPBasicAuth

app=Flask(__name__)

auth=HTTPBasicAuth(app)

tasks=[
		{
			"id":1,
			"title":"Learn Python",
			"description":"Learn basics of python",
			"status":True,
		},
		{
			"id":2,
			"title":"Learn JQuery",
			"description":"Learn basics of JQuery",
			"status":False,
		},
		{
			"id":3,
			"title":"Learn GO",
			"description":"Learn basics of GO",
			"status":True,
		},
	]
	
def make_uri(task,endpoint):
	if "id" in task and not "uri" in task:
		task.setdefault("uri",url_for(endpoint,taskid=task["id"],_external=True))

	return task
	
@auth.get_password
def get_password(username):
	if username=='vms20591':
		return 'password'	
	
@app.route('/api/v1.0/todo/tasks',methods=['GET','POST','OPTIONS'])
@auth.login_required
def task_list_API():

	if request.method=='OPTIONS':
		resp=make_response()
		resp.headers.setdefault('Access-Control-Allow-Origin','*')
		resp.headers.setdefault('Access-Control-Allow-Methods','GET,POST')
		resp.headers.setdefault('Access-Control-Allow-Headers','authorization,content-type')		
		resp.headers.setdefault('Access-Control-Allow-Credentials','true')
		return resp
		
	if request.method=='GET':
		return make_response(jsonify({"tasks":[make_uri(task,'tasksAPI') for task in tasks]}),200)
		
	if request.method=='POST':
		if not request.json or not 'title' in request.json:
			abort(400)
		
		req=request.json	
		
		task={}
		
		task['id']=tasks[-1]['id']+1
		task['title']=req.get('title')
		task['description']=req.get('description','')
		task['done']=req.get('done',False)
		
		tasks.append(task)
	
		if len(task):
			return make_response(jsonify({'task':make_uri(task,'tasksAPI')}),201)	
	
	abort(405)

@app.route('/api/v1.0/todo/tasks/<int:taskid>',methods=['GET','PUT','DELETE'])
@auth.login_required
def tasksAPI(taskid):
	
	task=filter(lambda task:task['id']==taskid,tasks)
	if len(task)==0:
		abort(404)	
	
	if request.method=='GET':
		return make_response(jsonify({'task':make_uri(task[0],'tasksAPI')}),200)
			
	if request.method=='PUT':
		if not request.json or not 'title' in request.json:
			abort(400)
			
		req=request.json	
			
		t=task[0]
		
		t['title']=req.get('title',t['title'])
		t['description']=req.get('description',t['description'])
		t['done']=req.get('done',t['done'])
		
		return make_response(jsonify({'task':make_uri(t,'tasksAPI')}),200)
		
	if request.method=='DELETE':
		
		t=None
			
		for task in tasks:
			if task['id']==taskid:
				t=task
				tasks.remove(task)	
			
		return make_response(jsonify({'task':make_uri(t,'tasksAPI'),'status':'removed'}),200)
		
	abort(405)
	
@app.errorhandler(400)	
def errorhandler_400(error):
	return make_response(jsonify({
		'errorcode':400,
		'errorreason':'Incorrect request format',
	}),400)
	
@app.errorhandler(404)	
def errorhandler_404(error):
	return make_response(jsonify({
		'errorcode':404,
		'errorreason':'Resource Not Found',
	}),404)

@app.errorhandler(405)	
def errorhandler_405(error):
	return make_response(jsonify({
		'errorcode':405,
		'errorreason':'Method Not Allowed',
	}),405)
	
@auth.error_handler
def login_errorhandler():
	return make_response(jsonify({
		'errorcode':403,
		'errorreason':'Not Authorized',
	}),403)

if __name__=='__main__':
	app.run(debug=True)
