from Flask.py.utils import *


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/')
#@login_required
def test():
    return render_template('product_table.html')


@app.route('/chart')
def chart():
    return render_template('statistics_table.html')


@app.route('/chart_one')
def chart_one():
    return render_template('chart_one.html')


@app.route('/chart_two')
def chart_two():
    return render_template('chart_two.html')


@app.route('/chart_three')
def chart_three():
    return render_template('chart_three.html')


@app.route('/chart_four')
def chart_four():
    return render_template('chart_four.html')


@app.route('/chart_five')
def chart_five():
    return render_template('chart_five.html')


@app.route('/chart_six')
def chart_six():
    return render_template('chart_six.html')


@app.route('/hello')
def hello():
    return "Hello World"


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', title='Route Fail :(', str='Please... rewrite the path.', url='test'), 404


@app.errorhandler(405)
def page_not_found(e):
    return render_template('error.html', title='405 method not allowed :(', str='Please... re try the login.', url='test'), 404

