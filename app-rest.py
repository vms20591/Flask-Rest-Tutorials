from flask import Flask
from flask import abort,jsonify,make_response
from flask.ext.restful import Resource,Api,reqparse
from flask.ext.restful import fields,marshal
from flask.ext.httpauth import HTTPBasicAuth

app=Flask(__name__)
api=Api(app)
auth=HTTPBasicAuth(app)

tasks=[
		{
			"todoid":1,
			"title":"Learn Python",
			"description":"Learn basics of python",
			"status":True,
		},
		{
			"todoid":2,
			"title":"Learn JQuery",
			"description":"Learn basics of JQuery",
			"status":False,
		},
		{
			"todoid":3,
			"title":"Learn GO",
			"description":"Learn basics of GO",
			"status":True,
		},
	]
	
@auth.get_password
def get_password(username):
	if username=='vms20591':
		return 'password'
	return None
	
class TodoListApi(Resource):

	decorators=[auth.login_required]

	def __init__(self):
		self.req_parse=reqparse.RequestParser()
		self.req_parse.add_argument('title',type=str,required=True,location='json',help='No title present')
		self.req_parse.add_argument('description',type=str,default='',location='json')
		self.req_parse.add_argument('status',type=bool,default=False,location='json')
		self.tasks=tasks
		self.task_fields={
			'title':fields.String,
			'description':fields.String,
			'status':fields.Boolean,
			'uri':fields.Url(endpoint='todo',absolute=True),
		}
		super(TodoListApi,self).__init__()
					
	def get(self):
		return jsonify({'tasks':[marshal(task,self.task_fields) for task in self.tasks]})
		
	def post(self):
		args=self.req_parse.parse_args()
		task={}
		
		for k,v in args.iteritems():
			if v is not None:
				task[k]=v
			
		task['todoid']=self.tasks[-1]['todoid']+1
		
		self.tasks.append(task)
		
		return {'task':marshal(task,self.task_fields)},201

class TodoApi(Resource):

	decorators=[auth.login_required]

	def __init__(self):
		self.req_parse=reqparse.RequestParser()
		self.req_parse.add_argument('title',type=str,location='json')
		self.req_parse.add_argument('description',type=str,location='json')
		self.req_parse.add_argument('status',type=bool,location='json')
		self.tasks=tasks
		self.task_fields={
			'title':fields.String,
			'description':fields.String,
			'status':fields.Boolean,
			'uri':fields.Url(endpoint='todo',absolute=True),
		}
		super(TodoApi,self).__init__()

	def get(self,todoid):
	
		task=filter(lambda t:t['todoid']==todoid,self.tasks)
		
		if len(task)==0:
			abort(404)
			
		task=task[0]
		
		return jsonify({'task':marshal(task,self.task_fields)})
		
	def put(self,todoid):
	
		task=filter(lambda t:t['todoid']==todoid,self.tasks)
		
		if len(task)==0:
			abort(404)
		
		task=task[0]
			
		args=self.req_parse.parse_args()
		
		for k,v in args.iteritems():
			if v is not None:
				task[k]=v
				
		return jsonify({'task':marshal(task,self.task_fields)})
		
@auth.error_handler
def login_errorhandler():
	return make_response(jsonify({
		'message':{
		'title':'Not Authorized',
		}
	}),403)

				
api.add_resource(TodoListApi,'/api/v1.0/todo/tasks/',endpoint='todolist')		
api.add_resource(TodoApi,'/api/v1.0/todo/tasks/<int:todoid>',endpoint='todo')

if __name__=='__main__':
	app.run(debug=True)
