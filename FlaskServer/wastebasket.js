function detect_model_filter() {
    $('#model_filter').change(function () {
        var filter_value = $('#model_filter').val();
        var filter_key = 'model';
        console.log("FIlter Value : " + filter_value);

        var main_table = main_table_info();
        console.log("MT : ");
        console.log(main_table);
        $.ajax({
            url: "/filtering",
            data: {
                'table_list': JSON.stringify(main_table),
                'filter_key': filter_key,
                'filter': filter_value
            },
            type: "GET",
            dataType: "json"
        })
            .done(function (json) {
                console.log("Filtering Ajax is DONE");
                console.log(json);
                console.log(json['filter_name']);
                console.log(json.key);
                for (key in json) {
                    console.log(key + ' ' + json.key);
                }
                $.each(json, function (key, value) {
                    console.log(key + ' ' + value);
                });

                make_main_stock_table(json);

                // 바꿔야할점 -> main table 함수에 row_list 인자를 받아 해당리스트로 출력으로 변환
                // 그리고 필터가 중첩되는거 바꿔야할듯, 필터자체 파이썬 코드로 변환해야할듯
            })
            .fail(function (xhr, status, errorThrown) {
                $("#test").html("오류발생<br>")
                    .append("오류명 : " + errorThrown + "<br>")
                    .append("상태 : " + status);
            })
            .always(function (xhr, status) {
                $("#text").html("요청 완료");
            });
    });
}

function detect_location_filter() {
    $('#location_filter').change(function () {
        var filter_value = $('#location_filter').val();
        var filter_key = 'location';
        console.log("FIlter Value : " + filter_value);

        var main_table = main_table_info();
        console.log("MT : ");
        console.log(main_table);
        $.ajax({
            url: "/filtering",
            data: {
                'table_list': JSON.stringify(main_table),
                'filter_key': filter_key,
                'filter': filter_value
            },
            type: "GET",
            dataType: "json"
        })
            .done(function (json) {
                console.log("Filtering Ajax is DONE");
                console.log(json);
                console.log(json['filter_name']);
                console.log(json.key);
                for (key in json) {
                    console.log(key + ' ' + json.key);
                }
                $.each(json, function (key, value) {
                    console.log(key + ' ' + value);
                });

                make_main_stock_table(json);

                // 바꿔야할점 -> main table 함수에 row_list 인자를 받아 해당리스트로 출력으로 변환
                // 그리고 필터가 중첩되는거 바꿔야할듯, 필터자체 파이썬 코드로 변환해야할듯
            })
            .fail(function (xhr, status, errorThrown) {
                $("#test").html("오류발생<br>")
                    .append("오류명 : " + errorThrown + "<br>")
                    .append("상태 : " + status);
            })
            .always(function (xhr, status) {
                $("#text").html("요청 완료");
            });
    });
}

function detect_state_filter() {
    $('#state_filter').change(function () {
        var filter_value = $('#state_filter').val();
        var filter_key = 'state';
        console.log("FIlter Value : " + filter_value);
        var main_table = main_table_info();
        console.log("MT : ");
        console.log(main_table);
        $.ajax({
            url: "/filtering",
            data: {
                'table_list': JSON.stringify(main_table),
                'filter_key': filter_key,
                'filter': filter_value
            },
            type: "GET",
            dataType: "json"
        })
            .done(function (json) {
                console.log("Filtering Ajax is DONE");
                console.log(json);
                console.log(json['filter_name']);
                console.log(json.key);
                for (key in json) {
                    console.log(key + ' ' + json.key);
                }
                $.each(json, function (key, value) {
                    console.log(key + ' ' + value);
                });

                make_main_stock_table(json);

                // 바꿔야할점 -> main table 함수에 row_list 인자를 받아 해당리스트로 출력으로 변환
                // 그리고 필터가 중첩되는거 바꿔야할듯, 필터자체 파이썬 코드로 변환해야할듯
            })
            .fail(function (xhr, status, errorThrown) {
                $("#test").html("오류발생<br>")
                    .append("오류명 : " + errorThrown + "<br>")
                    .append("상태 : " + status);
            })
            .always(function (xhr, status) {
                $("#text").html("요청 완료");
            });
    });
}


function main_table_info() {
    var tableList = new Array();
    var table = $('#main_table > tbody > tr');
    console.log(table);
    table.each(function () {
        var rowData = new Array();
        $(this).find("td").each(function (index) {
            //console.log("text val(" + index + ") \n" + $(this).text());
            rowData.push($(this).text());
        })
        rowData.pop(); // '자세히' 마지막 text 삭제
        var dic = {};
        dic["model"] = rowData[0];
        dic["sn"] = rowData[1];
        dic["week"] = rowData[2];
        dic["location"] = rowData[3];
        dic["state"] = rowData[4];
        //console.log(dic);
        tableList.push(dic)
        console.log("rowData: ");
        console.log(rowData);
    });
    console.log("tableList: ");
    console.log(tableList);

    return tableList
}