from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title=' Counting API',
    description='A simple Counting API',
)

ns = api.namespace('api', description='Counting operations')

count = api.model('Counting', {
    'OPERATIONS': fields.String(readonly=True, description='The task unique operation'),
    'KEY': fields.Integer(required=True, description='The task unique key'),
	'VALUE': fields.Integer(required=True, description='The task unique value')
})

class Counter(object):
    def __init__(self):
        self.counter = 0
        self.counts = []

    def get(self, operation):
        for count in self.counts:
            if count['OPERATIONS'] == operation:
                return count
        api.abort(404, "Todo {} doesn't exist".format(operation))

    def create(self, data):
        count = data
        count['id'] = self.counter = self.counter + 1
        self.counts.append(count)
        return count

    def update(self, id, data):
        count = self.get(id)
        count.update(data)
        return count

    def delete(self, id):
        count = self.get(id)
        self.counts.remove(count)


DAO = Counter()
DAO.create({'task': 'Build an API'})
DAO.create({'task': '?????'})
DAO.create({'task': 'profit!'})


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all counts, and lets you POST to add new tasks'''
    @ns.doc('list_count')
    @ns.marshal_list_with(count)
    def get(self):
        '''List all tasks'''
        return DAO.counts

    @ns.doc('create_count')
    @ns.expect(count)
    @ns.marshal_with(count, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:operation>')
@ns.response(404, 'Count not found')
@ns.param('operation', 'The task identifier')
class Count(Resource):
    '''Show a single count item and lets you delete them'''
    @ns.doc('get_count')
    @ns.marshal_with(count)
    def get(self, operation):
        '''Fetch a given resource'''
        return DAO.get(operation)

    @ns.doc('delete_todo')
    @ns.response(204, 'Count deleted')
    def delete(self, operation):
        '''Delete a task given its identifier'''
        DAO.delete(operation)
        return '', 204

    @ns.expect(count)
    @ns.marshal_with(count)
    def put(self, operation):
        '''Update a task given its identifier'''
        return DAO.update(operation, api.payload)


if __name__ == '__main__':
    app.run(debug=True)