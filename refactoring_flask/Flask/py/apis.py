from Flask.py.utils import *
from Flask.db.products import Product
from Flask.db.charts import Chart


@app.route("/product", methods=['POST', 'GET', 'PUT', 'DELETE'])
def product_table():
    if request.method == 'GET':
        filterDic = request.args.to_dict()
        print("GET API : product_table()")
        return Product.show_main_table_rows(filterDic)
    req = form2dict(request.form)
    print("\nrequest form ------------------------------")
    print(req)
    if request.method == 'POST':
        print("POST API : product_table()")
        return Product.add_table_row(req)
    elif request.method == 'PUT':   # model, sn, week, location, state
        print("PUT API : product_table()")
        return Product.update_table_row(req)
    elif request.method == 'DELETE':
        print("DELETE API : product_table()")
        return Product.delete_table_row(req)


@app.route("/product/detailModal", methods=['POST'])
def detail_table():
    req = form2dict(request.form)
    print("POST API : detail_table()")
    print("request form ------------------------------")
    print(req)
    if request.method == 'POST':
        return Product.show_detail_modal_table_rows(req)
    else:
        return Response("Invalid RESTful Route Methods", status=404)


@app.route("/product/detailModal/<product_id>", methods=['POST', 'GET', 'PUT', 'DELETE'])
def detail_modal(product_id):
    print('\nProduct ID : ' + product_id)
    if request.method == 'GET':
        print("GET API : product_table()")
        return Product.show_detail_modal_table_rows(product_id)
    req = form2dict(request.form)
    print("request form ------------------------------")
    print(req)
    if request.method == 'POST':
        print("POST API : detail_modal()")
        return Product.add_detail_table(req, product_id)
    elif request.method == 'PUT':   # model, sn, week, location, state
        print("PUT API : detail_modal()")
        return Product.update_detail_table(req, product_id)
    elif request.method == 'DELETE':
        print("DELETE API : detail_modal()")
        return Product.delete_detail_table(req, product_id)


@app.route("/chart/<postData>", methods=['POST', 'GET', 'PUT', 'DELETE'])
def chart_table(postData):
    postData = json.loads(postData)
    print("\nPost Data : -------------------------------")
    print(postData)
    req = form2dict(request.form)
    print("request form ------------------------------")
    print(req)
    if request.method == 'GET':
        print("GET API : chart_table()")
        return Chart.show_chart_table(postData)
    elif request.method == 'POST':
        print("POST API : chart_table2()")
        return Chart.show_chart_table2(postData)
    # Error
    return jsonify({'name': 'chart'})


@app.route("/chart/chart_one/<postData>")
def custom_chart(postData):
    postData = json.loads(postData)
    print("\nPost Data : ", end="")
    print(postData)
    if request.method == 'GET':
        print("GET API : chart_table_two()")
        return Chart.show_chart_table_two(postData)
    else:
        return Response("Invalid RESTful Route Methods", status=404)


@app.route("/chart/chart_two/<postData>")
def custom_chart2(postData):
    postData = json.loads(postData)
    print("\nPost Data : ", end="")
    print(postData)
    if request.method == 'GET':
        print("GET API : chart_table2()")
        return Chart.show_chart_table2(postData)
    else:
        return Response("Invalid RESTful Route Methods", status=404)


@app.route("/chart/chart_three/<postData>")
def custom_chart3(postData):
    postData = json.loads(postData)
    print("\nPost Data : ", end="")
    print(postData)
    if request.method == 'GET':
        print("GET API : chart_table3()")
        return Chart.show_chart_table3(postData)
    else:
        return Response("Invalid RESTful Route Methods", status=404)


@app.route("/chart/chart_four/<postData>")
@LoginRequired()
def custom_chart4(postData):
    if postData:
        postData = json.loads(postData)
        print("\nPost Data : ", end="")
        print(postData)
    if request.method == 'GET':
        print("GET API : chart_table4()")
        return Chart.show_chart_table4(postData)
    else:
        return Response("Invalid RESTful Route Methods", status=404)


@app.route("/chart/chart_six/<postData>")
@LoginRequired("admin")
def custom_chart6(postData):
    if postData:
        postData = json.loads(postData)
        print("\nPost Data : ", end="")
        print(postData)
    if request.method == 'GET':
        print("GET API : chart_table6()")
        return Chart.show_chart_table6(postData)
    else:
        return Response("Invalid RESTful Route Methods", status=404)
