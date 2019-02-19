function winPop(url, opts) {
    var popupName = opts.name || 'popup';
    var options = '';
    options += 'width=' + (opts.width ? opts.width : 200) + ', height=' + (opts.height ? opts.height : 200);
    options += opts.left && opts.width ? ', left=' + opts.left : ', left=' + ((screen.availWidth - opts.width) / 2);
    options += opts.top && opts.height ? ', top=' + opts.top : ', top=' + ((screen.availHeight - opts.height) / 2);
    options += opts.scrollbars ? ', scrollbars=' + opts.scrollbars : ', scrollbars=no';
    options += opts.resizable ? ', resizable=' + opts.resizable : ', resizable=no';
    console.log(popupName);
    window.open(url, popupName, options);
}

function JSON_parse_convertor(string) {
    string = string.replace(/'/gi, '"');
    string = string.replace(/ObjectId\(/gi, '');
    string = string.replace(/\)/gi, '');
    string = JSON.parse(string);

    return string;
}

function make_main_stock_table(list) {
    console.log("Get List : \n" + list);
    console.log("len : " + list.length);
    if (list == undefined) {
        console.log('Main Table length is empty');
    } else if (list == 0) {
        alert("필터를 적용할 대상이 없습니다.");
        return false;
    } else {
        if (typeof (list) == "string")
            list = JSON_parse_convertor(list);
        $('#main_table > tbody:last').empty();
        for (var i = 0; i < list.length; i++) {
            $('#main_table').append(
                $('<tr>').append(
                    //$('<td><input type="checkbox" name="main_checkbox"/>').append(model_row[i]['model']),
                    $('<td><input type="checkbox" name="main_checkbox"/>').append(list[i]['model']),
                    $('<td>').append(list[i]['sn']),
                    $('<td>').append(list[i]['week']),
                    $('<td>').append(list[i]['location']),
                    $('<td>').append(list[i]['state']),
                    $('<td><button type="button" id="detail_btn" name="detail_btn" value="" class="detail_btn_class btn btn-warning" data-toggle="modal" data-target="#detail_modal">자세히</button>')
                )
            );
            document.getElementsByName("detail_btn")[i].value = list[i]['product_info_id'];
        }
    }
}

function main_table() {
    var specific_date_row = $('#specific_date_list').val();
    console.log("Date serch? : " + specific_date_row);
    var table_rows = $('#main_table_list').val();
    console.log("Table rows : \n" + table_rows);
    if (specific_date_row != undefined && specific_date_row != 'None') {
        console.log("Specific date search");
        make_main_stock_table(specific_date_row);
    } else if (table_rows == undefined) {
        console.log('Main Table length is empty');
    } else {
        make_main_stock_table(table_rows);
    }
}

function state_change_table() {
    var table_rows = $('#main_table_list').val();
    console.log("State change Table rows : \n" + table_rows);
    if (table_rows == undefined) {
        console.log("main_table_list is Empty");
    } else {
        table_rows = JSON_parse_convertor(table_rows);
        for (var i = 0; i < table_rows.length; i++) {
            $('#state_table').append(
                $('<tr>').append(
                    $('<td><input class="checkbox" type="checkbox" name="check_box" value=""/>').append(table_rows[i]['model']),
                    $('<input type="hidden" name="id" value="">'),
                    $('<td>').append(table_rows[i]['sn']),
                    $('<td><input type="text" class="form-control" name="location" value="" >'),
                    $('<td><select class="form-control" name="reason" id="reason" value="">' +
                        '<option>신규생산</option>' +
                        '<option>판매</option>' +
                        '<option>기증</option>' +
                        '<option>내수용</option>' +
                        '<option>A/S</option>' +
                        '<option>불량</option>' +
                        '<option>반납</option>' +
                        '<option>이동</option>' +
                        '</select>')
                )
            );
            //$("#state option:eq(i)").attr("selected", "selected");
            document.getElementsByName("check_box")[i].value = table_rows[i]['product_info_id'];
            document.getElementsByName("id")[i].value = table_rows[i]['product_info_id'];
            document.getElementsByName("location")[i].value = table_rows[i]['location'];
            document.getElementsByName("reason")[i].value = table_rows[i]['reason'];
        }
    }
}

// 나중에 행 추가, 삭제 기능
function insert_table() {
    $('#insert_table').append(
        $('<tr>').append(
            $('<td><select class="form-control" id="insert_model" name="model">' +
                '<option>Indy3</option>\n' +
                '<option>Indy5</option>\n' +
                '<option>Indy7</option>\n' +
                '<option>Opti</option>\n' +
                '<option>Step-pc2</option>\n' +
                '<option>Core</option>\n' +
                '<option>Conty</option>\n' +
                '</select>'),
            $('<td><input type="text" class="form-control" id="insert_sn" name="sn">'),
            $('<td><input type="text" class="form-control" id="insert_header" name="header">')
        )
    );
}

function detail_tabler() {
    $(".detail_btn_class").click(function () {
        // Table initialization
        $('#detail_table > tbody:last').empty();
        $('#detail_info > tbody:last').empty();

        var product_row = $('#model_list').val();
        var product_info_row = $('#info_list').val();
        var history_row = $('#history_list').val();
        var received_id = $(this).val();
        var _date = new Array();
        var _location = new Array();
        var _state = new Array();
        var _week = new Array();
        var _reason = new Array();
        product_row = JSON_parse_convertor(product_row);
        product_info_row = JSON_parse_convertor(product_info_row);
        history_row = JSON_parse_convertor(history_row);
        var _model, _sn, _header, _model_id;
        for (var j = 0; j < history_row.length; j++) {
            if (received_id == history_row[j]['product_id']) {
                _date.push(history_row[j]['date']);
                _location.push(history_row[j]['location']);
                _state.push(history_row[j]['state']);
                _reason.push(history_row[j]['reason']);
            }
        }
        for (var k = 0; k < product_info_row.length; k++) {
            if (received_id == product_info_row[k]['_id']) {
                _model_id = product_info_row[k]['model_id'];
                _sn = product_info_row[k]['sn'];
                _week = product_info_row[k]['week'];
                _header = product_info_row[k]['header'];
                for (var p = 0; p < product_row.length; p++) {
                    if (_model_id == product_row[p]['_id']) {
                        _model = product_row[p]['model'];
                    }
                }
            }
        }
        //console.log(_date);
        //console.log(_location);
        //console.log(_state);
        if (product_info_row.length != product_info_row.length) {
            alert("DB Length is wrong !");
        }
        $('#detail_info').append(
            $('<tr>').append(
                $('<th class="text-right">').append("Model:  " + _model),
                $('<th class="text-right">').append("SN:  " + _sn),
                $('<th class="text-right">').append("생산 Week:  " + _week),
                $('<th class="text-right">').append("Header:  " + _header)
            )
        );
        for (var i = 0; i < _date.length; i++) {
            $('#detail_table').append(
                $('<tr>').append(
                    $('<td>').append(_date[i]),
                    $('<td>').append(_location[i]),
                    $('<td>').append(_state[i]),
                    $('<td>').append(_reason[i]))
            );
        }
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

// Not use
function btn_click_event() {
    $("#Button_example").click(function () {
        alert('hi');
        var rowData = new Array();
        var tdArr = new Array();
        var checkbox = $("input[name=main_checkbox]:checked");

        // 체크된 체크박스 값을 가져온다
        checkbox.each(function (i) {
            // checkbox.parent() : checkbox의 부모는 <td>이다.
            // checkbox.parent().parent() : <td>의 부모이므로 <tr>이다.
            var tr = checkbox.parent().parent().eq(i);
            var td = tr.children();

            // 체크된 row의 모든 값을 배열에 담는다.
            rowData.push(tr.text());

            // td.eq(0)은 체크박스 이므로  td.eq(1)의 값부터 가져온다.
            var no = td.eq(0).text() + ", "
            var userid = td.eq(1).text() + ", ";
            var name = td.eq(2).text() + ", ";
            var email = td.eq(3).text() + ", ";

            // 가져온 값을 배열에 담는다.
            tdArr.push(no);
            tdArr.push(userid);
            tdArr.push(name);
            tdArr.push(email);
        });

        $("#ex3_Result1").html(" * 체크된 Row의 모든 데이터 = " + rowData);
        $("#ex3_Result2").html(tdArr);
    });
}

function model_filter() {
    var table_rows = $('#main_table_list').val();
    if (table_rows == undefined) {
        console.log('Table length is empty');
    } else {
        table_rows = JSON_parse_convertor(table_rows);
        //var model_list = ['Indy3', 'Indy5', 'Indy7', 'Opti', 'Step-pc2', 'Core', 'Conty'];
        var model_list = new Array();
        for (var i = 0; i < table_rows.length; i++) {
            model_list[i] = table_rows[i]['model'];
        }
        // 중복제거
        var model_list_filtering = model_list.filter(function (item, idx, array) {
            return array.indexOf(item) === idx;
        });
        console.log(model_list_filtering);
        /*
        var uniq = model_list.slice().sort(function (a, b) {   // 복사본 만듬
            return a - b;
        })
            .reduce(function (a, b) {
                if (a.slice(-1)[0] != b) a.push(b);  // slice(-1)[0]을 통해 마지막 아이템 가져온다
                return a;
            }, []); // a가 시작될 때를 위한 비어있는 배열
        */
        for (var count = 0; count < model_list_filtering.length; count++) {
            //var option = $("<option>"+model_list[count]+"</option>");
            var option = $("<option>").append(model_list_filtering[count]);
            $('#model_filter').append(option);
        }
    }
}

function model_filter_application() {
    // select value가 model option에 일치했을 경우, 테이블 변경 출력 함수
}

function location_filter() {
    var table_rows = $('#main_table_list').val();
    if (table_rows == undefined) {
        console.log('Table length is empty');
    } else {
        table_rows = JSON_parse_convertor(table_rows);
        var location_list = new Array();
        for (var i = 0; i < table_rows.length; i++) {
            location_list[i] = table_rows[i]['location'];
        }
        var location_list_filtering = location_list.filter(function (item, idx, array) {
            return array.indexOf(item) === idx;
        });
        console.log(location_list_filtering);
        for (var count = 0; count < location_list_filtering.length; count++) {
            //var option = $("<option>"+model_list[count]+"</option>");
            var option = $("<option>").append(location_list_filtering[count]);
            $('#location_filter').append(option);
        }
    }
}

function state_filter() {
    var table_rows = $('#main_table_list').val();
    if (table_rows == undefined) {
        console.log('Table length is empty');
    } else {
        table_rows = JSON_parse_convertor(table_rows);
        var state_list = new Array();
        for (var i = 0; i < table_rows.length; i++) {
            state_list[i] = table_rows[i]['state'];
        }
        var state_list_filtering = state_list.filter(function (item, idx, array) {
            return array.indexOf(item) === idx;
        });
        console.log(state_list_filtering);
        for (var count = 0; count < state_list_filtering.length; count++) {
            //var option = $("<option>"+model_list[count]+"</option>");
            var option = $("<option>").append(state_list_filtering[count]);
            $('#state_filter').append(option);
        }
    }
}

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
                console.log("DONE");
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
                console.log("DONE");
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
                console.log("DONE");
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