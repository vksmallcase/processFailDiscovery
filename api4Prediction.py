from flask import Flask,jsonify
from flask_restful import reqparse, abort,Api,Resource,marshal_with,fields
import joblib
import  os
import pandas as pd
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

api = Api(app)
auth = HTTPBasicAuth()
users = {
    "vk": generate_password_hash("hi"),
    "sk": generate_password_hash("hi")
}

path = os.getcwd()
model_file = path + "/savedmodel/DTree.pkl"
output_path = path + "/output"

dfSummary = pd.read_csv(output_path + "/summary.csv")
DTree = joblib.load(model_file)


parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('zprocessstate',type=int,required=True, help="alertSnap_nw cannot be blank!")
parser.add_argument('zhnotifystate',type=int,required=True, help="alertSnap_nw cannot be blank!")
parser.add_argument('zgenericactionstate',type=int, required=True, help="alertSnap_nw cannot be blank!")
parser.add_argument('zticketstate',type=int,required=True, help="alertSnap_nw cannot be blank!")

class predict_dt(Resource):
   @auth.verify_password
   def verify_password(username, password):
       if username in users and check_password_hash(users.get(username), password):
           return username

   @app.route('/predict')
   @auth.login_required
   def get(self,zprocessstate,zhnotifystate,zgenericactionstate,zticketstate):

    inputData = [zprocessstate, zhnotifystate, zgenericactionstate, zticketstate]
    Yhat = DTree.predict([inputData])
    predicted = Yhat[0]
    trans = dfSummary.loc[dfSummary['Cluster'] == predicted]
    if len(trans.index) == 1:
     if trans['alias'].isnull().any() :
      state = trans['ProblematicArea'].item()
     else:
      state = trans['alias'].item()
    else:
     state = 'Anomaly'

    return jsonify({'predicted':'Ok',
                    'Cluster': int(predicted),
                     'ProblemType' : str(state) })
                            #'FutureStatus':ZProcessState[predicted]})






api.add_resource(predict_dt, '/predict/<zprocessstate>,<zhnotifystate>,<zgenericactionstate>,<zticketstate>')


if __name__ == '__main__':
    app.run(debug=True,ssl_context='adhoc', port=5001)