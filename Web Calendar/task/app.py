from flask import Flask, abort
from flask_restful import Api, Resource, reqparse, inputs
from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import datetime

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
parser = reqparse.RequestParser()
date_parser = reqparse.RequestParser()
parser.add_argument('event', type=str, help="The event name is required!", required=True)
parser.add_argument('date', type=inputs.date, help="The event date with the correct format is required! The correct format is YYYY-MM-DD!", required=True)
date_parser.add_argument('start_time', type=inputs.date, required=False)
date_parser.add_argument('end_time', type=inputs.date, required=False)


class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()


class CalendarResource(Resource):
    def get(self):
        args = date_parser.parse_args()
        if args['start_time'] and args['end_time']:
            start_time = str(datetime.date(args["start_time"]))
            end_time = str(datetime.date(args["end_time"]))
            rows = Event.query.filter(Event.date.between(start_time, end_time)).all()
        else:
            rows = Event.query.all()
        data = []
        for i in range(len(rows)):
            data.append({"id": rows[i].id, "event": rows[i].event, "date": str(rows[i].date)})
        return data

    def post(self):
        args = parser.parse_args()
        new_event = {"message": "The event has been added!", "event": args["event"], "date": str(datetime.date(args["date"]))}
        event = Event(event=new_event["event"], date=args["date"])
        db.session.add(event)
        db.session.commit()
        return new_event


class TodayEventsResource(Resource):
    def get(self):
        rows = Event.query.filter(Event.date == datetime.today().date()).all()
        data = []
        for i in range(len(rows)):
            data.append({"id": rows[i].id, "event": rows[i].event, "date": str(rows[i].date)})
        return data


class DeleteEvent(Resource):
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return {"id": event.id, "event": event.event, "date": str(event.date)}

    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        print(event)
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            db.session.delete(event)
            db.session.commit()
        return {"message": "The event has been deleted!"}


api.add_resource(CalendarResource, '/event')
api.add_resource(TodayEventsResource, '/event/today')
api.add_resource(DeleteEvent, '/event/<int:event_id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
