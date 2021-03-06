from app import app, db
from flask import make_response, request, abort, jsonify,  redirect, url_for
from app.models import User, Session, Chargingpoint, Message
from datetime import datetime

@app.route('/api/create_session/chargingpoint_<int:key>/<string:licenseplate>', methods=["POST"])
def create_session(key, licenseplate):
        user = User.query.filter_by(licenseplate = licenseplate).first_or_404()
        msg = Message(recipient=user, body="Would you like to charge here?", chargingpoint_id=key)
        db.session.add(msg)
        db.session.commit()
        return str(msg.id), 201

@app.route('/authorize_session/<int:message_id>')
def authorize_session(message_id):
        message = Message.query.filter_by(id = message_id).first_or_404()
        chargingpoint = Chargingpoint.query.filter_by(id = message.chargingpoint_id).first_or_404()
        if chargingpoint.availability is 1 :
                abort(415)
        chargingpoint.availability=1
        user = User.query.filter_by(id = message.recipient_id).first_or_404()
        session = Session(user_id=user.id, chargingpoint_id=chargingpoint.id)
        db.session.add(session)
        db.session.commit()
        Message.query.filter_by(id=message_id).delete()
        db.session.commit()
        return redirect(url_for('admin_dashboard'))


@app.route('/api/create_session_unknown_user/chargingpoint_<int:key>/<string:licenseplate>', methods=["POST"])
def create_session_unknown_user(key, licenseplate):
        chargingpoint = Chargingpoint.query.filter_by(id = key).first_or_404()
        # chargingpoint = q.first_or_404()
        if chargingpoint.availability is 1 :
                abort(415)
        chargingpoint.availability=1
        session = Session(user_id=licenseplate, chargingpoint_id=key)
        db.session.add(session)
        db.session.commit()
        return str(chargingpoint.availability), 201


@app.route('/api/setup', methods=["POST"])
def setupdb():
        db.session.query(Chargingpoint).delete()
        db.session.commit()
        for x in range(6):
                chargingpoint = Chargingpoint(price=x+1,availability=0)
                db.session.add(chargingpoint)
                db.session.commit()
        return "setup has succesfully finished", 201

@app.route('/api/create_user', methods=["POST"])
def setup_user():
        # db.session.query(Chargingpoint).delete()
        # db.session.commit()
        user = User(username="admin",name="koen cremers",email="koen@admin.nl",licenseplate="11111")
        user.set_password("admin")
        db.session.add(user)
        db.session.commit()
        return "user has been created", 201

@app.route('/api/stop_session/chargingpoint_<int:key>', methods=["POST"])
def stop_session(key):
        chargingpoint = Chargingpoint.query.filter_by(id = key).first_or_404()
        # chargingpoint = q.one()
        session = Session.query.filter_by(chargingpoint_id = key).filter_by(endtime = None).first_or_404()
        # session = q.one()
        if chargingpoint.availability is 0 and session.endtime is None:
                abort(415)
        chargingpoint.availability=0
        session.endtime = datetime.now()
        session.totalprice = session.endtime - session.endtime
        db.session.commit()
        return str(chargingpoint.availability), 201

@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(415)
def wrong_input(error):
        return make_response(jsonify({'error': 'wrong input'}), 415)
