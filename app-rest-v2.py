# RestFull using flask_restful
from flask import Flask, abort, url_for, make_response, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()


# make public helper for user get full URI to task
def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]

    return new_task


task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}

# create a data static
tasks = [
    {
        'id': 1,
        'title': u'Buy Groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@auth.get_password
def get_password(username):
    if username == "junanda":
        return 'python'
    return None


# when error response in flask an HTML message instead JSON, because
# that is how flask generate the 404 response by default. so we need to improve
# our 404 error handler using JSON format
@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


# create class for User
class UserAPI(Resource):
    def get(self, id):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass


# create class Tasks List
# Flask-restful provides a much better way to handle validation of the request data with RequestParser
class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(TaskListAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True, help='No task title provided', location='json')
        self.reqparse.add_argument('description', type=str, default="", location='json')

    @staticmethod
    def get():
        return {'task': [marshal(task, task_fields) for task in tasks]}

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'id': tasks[-1]['id'] + 1 if len(tasks) > 0 else 1,
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        tasks.append(task)
        return {'task': marshal(task, task_fields)}, 201


class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(TaskAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')

    @staticmethod
    def get( id):
        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort(404)
        return {'task': marshal(task, task_fields)}

    def put(self, id):
        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for i, v in args.iteritems():
            if v != None:
                task[i] = v
        # Flask-RESTful automatically handles the conversion to JSON and supports passing a custom status code back
        # return {'task': make_public_task(task)}, 201
        return {'task': marshal(task, task_fields)}

    @staticmethod
    def delete(id):
        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return {'result': True}


# register routers and define endpoint
api.add_resource(UserAPI, '/user/<int:id>', endpoint='user')
api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/todo/api/v1.0/task/<int:id>', endpoint='task')
