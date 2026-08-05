from flask import Flask, render_template, request
# Import everything from your logic library
from logic_modules import senior_engagement, youth_amanah, tax_calculator, halal_economy, hazard_lookup

app = Flask(__name__)

# The 'Pretty' Registry: Adding a new module is now just one line here.
MODULES = {
    'senior': senior_engagement,
    'youth': youth_amanah,
    'tax': tax_calculator,
    'halal': halal_economy,
    'hazard': hazard_lookup
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<module_name>')
def show_module(module_name):
    # This single route handles EVERYTHING. No more messy, duplicate routes.
    if module_name in MODULES:
        # Pass all query parameters (like ?val=48005) directly to the module
        args = request.args.to_dict()
        content = MODULES[module_name].run(**args)
        return render_template('module.html', title=module_name, content=content)
    
    return "Module not found", 404

if __name__ == '__main__':
    app.run(port=9003, debug=True)