from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML 模板
html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BMI Calculator</title>
    </head>
    <body>
        <h1>BMI Calculator</h1>
        <form method="post">
            Height (in meters): <input type="text" name="height"><br>
            Weight (in kilograms): <input type="text" name="weight"><br>
            <input type="submit" value="Calculate BMI">
        </form>
        {% if bmi %}
            <h2>Your BMI is: {{ bmi }}</h2>
        {% endif %}
    </body>
    </html>
'''

@app.route('/', methods=['GET', 'POST'])
def bmi_calculator():
    bmi = ''
    if request.method == 'POST':
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        bmi = round(weight / (height ** 2), 2)
    return render_template_string(html, bmi=bmi)

if __name__ == '__main__':
    app.run(debug=True)
