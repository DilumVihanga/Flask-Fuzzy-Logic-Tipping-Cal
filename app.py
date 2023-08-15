from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes

# Define the input variables
quality = ctrl.Antecedent(np.arange(0, 11, 1), 'quality')
service = ctrl.Antecedent(np.arange(0, 11, 1), 'service')
tip = ctrl.Consequent(np.arange(0, 26, 1), 'tip')

# Define the membership functions for the input variables
quality['very_poor'] = fuzz.trimf(quality.universe, [0, 0, 3])
quality['poor'] = fuzz.trimf(quality.universe, [0, 1, 5])
quality['average'] = fuzz.trimf(quality.universe, [1, 5, 10])
quality['good'] = fuzz.trimf(quality.universe, [5, 10, 10])
service['very_poor'] = fuzz.trimf(service.universe, [0, 0, 1])
service['poor'] = fuzz.trimf(service.universe, [0, 1, 5])
service['average'] = fuzz.trimf(service.universe, [1, 5, 10])
service['good'] = fuzz.trimf(service.universe, [5, 10, 10])
tip['very_low'] = fuzz.trimf(tip.universe, [0, 0, 5])
tip['low'] = fuzz.trimf(tip.universe, [0, 5, 13])
tip['medium'] = fuzz.trimf(tip.universe, [5, 13, 25])
tip['high'] = fuzz.trimf(tip.universe, [13, 25, 25])

# Define the fuzzy rules
rule0 = ctrl.Rule(quality['very_poor'] & service['very_poor'], tip['very_low'])
rule1 = ctrl.Rule(quality['poor'] | service['poor'], tip['low'])
rule2 = ctrl.Rule(quality['average'], tip['medium'])
rule3 = ctrl.Rule(quality['good'] | service['good'], tip['high'])

# Create the fuzzy control system
tipping_ctrl = ctrl.ControlSystem([rule0, rule1, rule2, rule3])
tipping = ctrl.ControlSystemSimulation(tipping_ctrl)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
@cross_origin() # This will enable CORS for this specific route
def calculate():
    quality_input = float(request.form['quality'])
    service_input = float(request.form['service'])
    tipping.input['quality'] = quality_input
    tipping.input['service'] = service_input
    tipping.compute()
    tip_percentage = tipping.output['tip']
    return jsonify(tip_percentage=f"{tip_percentage:.2f}%")

if __name__ == '__main__':
    app.run(debug=True)
