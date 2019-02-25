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

function getNoneTable(tableId, colspan) {
    console.log("None Table Id : " + tableId);
    $('#' + tableId).append(
        $('<tr>').append(
            $('<td class="text-center" colspan=' + colspan + '><h1>Table Is Empty</h1></td>')
        )
    );
}

function make_main_stock_table(list, startRow, endRow) {
    console.log("Make Stock Table");
    if (list == undefined) {
        console.log('Main Table length is empty');
    } else if (list == 0) {
        alert("필터를 적용할 대상이 없습니다.");
        return false;
    } else {
        if (typeof (list) == "string")
            list = JSON_parse_convertor(list);
        list.sort(function(a, b){
            //return a.week > b.week ? -1 : a.week < b.week ? 1 : 0;
            return b.week - a.week;
        });
        console.log("Stock Row Size : " + list.length);
        $('#main_table > tbody:last').empty();
        for (var i = startRow; i < endRow; i++) {
            $('#main_table').append(
                $('<tr>').append(
                    //$('<td><input type="checkbox" name="main_checkbox"/>').append(model_row[i]['model']),
                    $('<td class="align-middle"><input type="checkbox" name="main_checkbox"/>').append(list[i]['model']),
                    $('<td class="align-middle">').append(list[i]['sn']),
                    $('<td class="align-middle">').append(list[i]['week']),
                    $('<td class="align-middle">').append(list[i]['location']),
                    $('<td class="align-middle">').append(list[i]['state']),
                    $('<td><button type="button" name="detail_btn" class="detail_btn_class btn btn-warning" data-toggle="modal" data-target="#detail_modal" value=' + list[i]['product_info_id'] + '>자세히</button>')
                )
            );
            //document.getElementsByName("detail_btn")[i].value = list[i]['product_info_id'];
        }
    }
}

function main_table(table_rows, specific_row, startRow, endRow) {
    console.log("Filtering search : " + specific_row);
    var table_rows = $('#main_rows').val();
    console.log("Table rows : \n" + table_rows);
    if (specific_row != undefined && specific_row != 'None' && specific_row != 0) {
        console.log("Specific date search");
        make_main_stock_table(specific_row, startRow, endRow);
    } else if (table_rows == undefined || table_rows == 'None' || specific_row == 0 || table_rows == '[]') {
        console.log('Main Table length is empty');
        getNoneTable('main_table', 6);
    } else {
        make_main_stock_table(table_rows, startRow, endRow);
    }
}

function state_change_table(table_rows) {
    //var table_rows = $('#main_rows').val();
    $('#state_table > tbody:last').empty();
    console.log("State change Table rows : \n" + table_rows);
    if (table_rows == undefined) {
        console.log("main_rows is Empty");
    } else {
        if (typeof (table_rows) == "string") {
            table_rows = JSON_parse_convertor(table_rows);
        }
        for (var i = 0; i < table_rows.length; i++) {
            $('#state_table').append(
                $('<tr>').append(
                    //$('<td><input class="checkbox" type="checkbox" name="check_box" value=""/>').append(table_rows[i]['model']),
                    $('<td>').append(table_rows[i]['model']),
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
            //document.getElementsByName("check_box")[i].value = table_rows[i]['product_info_id'];
            document.getElementsByName("id")[i].value = table_rows[i]['product_id'];
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

function detail_table() {
    $(".detail_btn_class").click(function () {
        // Table initialization
        $('#detail_table > tbody:last').empty();
        $('#detail_info > tbody:last').empty();

        var received_id = $(this).val();
        console.log("Received ID : " + received_id);

        $.ajax({
            url: "/getDetailTable",
            data: {
                'product_info_id': received_id
            },
            type: "GET",
            dataType: "json"
        })
            .done(function (json) {
                console.log("Detail Table Ajax is DONE");
                console.log(json);

                $('#detail_info').append(
                    $('<tr>').append(
                        $('<th class="text-right">').append("Model:  " + json[0]['model']),
                        $('<th class="text-right">').append("SN:  " + json[0]['sn']),
                        $('<th class="text-right">').append("생산 Week:  " + json[0]['week']),
                        $('<th class="text-right">').append("Header:  " + json[0]['header'])
                    )
                );
                for (var i = 1; i < json.length; i++) {
                    $('#detail_table').append(
                        $('<tr>').append(
                            $('<td class="text-center">').append(json[i]['date']),
                            $('<td class="text-center">').append(json[i]['location']),
                            $('<td class="text-center">').append(json[i]['state']),
                            $('<td class="text-center">').append(json[i]['reason']))
                    );
                }
            })
            .fail(function (xhr, status, errorThrown) {
                $("#test").html("오류발생<br>")
                    .append("오류명 : " + errorThrown + "<br>")
                    .append("상태 : " + status);
            })
            .always(function (xhr, status) {
                $("#text").html("요청 완료");
            });


        /*
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
        }*/
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
    $("#state_change_btn").click(function () {
        var rowData = new Array();
        var tdArr = new Array();
        var checkbox = $("input[name=main_checkbox]:checked");
        var checked_product_info_id = new Array();

        // 체크된 체크박스 값을 가져온다
        checkbox.each(function (i) {
            // checkbox.parent() : checkbox의 부모는 <td>이다.
            // checkbox.parent().parent() : <td>의 부모이므로 <tr>이다.
            var tr = checkbox.parent().parent().eq(i);
            var td = tr.children();
            var btn = td.eq(5).children();


            // 체크된 row의 모든 값을 배열에 담는다.
            rowData.push(tr.text());

            // td.eq(0)은 체크박스 이므로  td.eq(1)의 값부터 가져온다.
            var model = td.eq(0).text();
            var sn = td.eq(1).text();
            var week = td.eq(2).text();
            var location = td.eq(3).text();
            var state = td.eq(4).text();
            var product_id = btn.val();

            // 가져온 값을 배열에 담는다.
            tdArr.push(model);
            tdArr.push(sn);
            tdArr.push(week);
            tdArr.push(location);
            tdArr.push(state);
            tdArr.push(product_id);

            checked_product_info_id.push(product_id);
        });

        $.ajax({
            url: "/getStateChangeTable",
            data: {
                'product_info_id': JSON.stringify(checked_product_info_id)
            },
            type: "GET",
            dataType: "json"
        })
            .done(function (json) {
                console.log("State Change Table Ajax is DONE");
                console.log(json);
                if(json.length == 0){
                    getNoneTable('state_table', 4);
                }
                else if (json){
                    state_change_table(json);
                }
            })
            .fail(function (xhr, status, errorThrown) {
                $("#test").html("오류발생<br>")
                    .append("오류명 : " + errorThrown + "<br>")
                    .append("상태 : " + status);
            })
            .always(function (xhr, status) {
                $("#text").html("요청 완료");
            });

        /*
        var result_list = new Array();
        var dic = {};
        var count = 0;
        for(var j=0; j<tdArr.length; j++){
           if(count <= 5){
               if(count == 0)
               {
                   dic['model'] = tdArr[j];
               }
               else if(count==1){
                   dic['sn'] = tdArr[j];
               }
               else if(count==2){
                   dic['week'] = tdArr[j];
               }
               else if(count==3){
                   dic['location'] = tdArr[j];
               }
               else if(count==4){
                   dic['state'] = tdArr[j];
               }
               else if(count==5){
                   dic['product_info_id'] = tdArr[j];
               }
               count++;
           }
           else{
               count=0;
           }
        }
        console.log("dic :");
        console.log(dic);
        */
        console.log("tdArr : " + tdArr);
        for(var i=0; i<tdArr.length; i++){
            console.log("tdArr["+i+"] : " + tdArr[i]);
        }


        $("#ex3_Result1").html(" * 체크된 Row의 모든 데이터 = " + rowData);
        $("#ex3_Result2").html(tdArr);
    });
}

function model_filter() {
    var table_rows = $('#main_rows').val();
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
    var table_rows = $('#main_rows').val();
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
    var table_rows = $('#main_rows').val();
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

function add_and_delete_row_btn(html) {
    $('#btn-add-row').click(function () {
        var time = new Date().toLocaleTimeString();
        //$('#insert_table > tbody:last').append('<tr><td>{{ a }}</td><td>' + time + '</td></tr>');
        if (html == 'production_main')
            insert_table();
        else if (html == 'manufacture')
            insert_manufacture_table();
    });
    $('#btn-delete-row').click(function () {
        var trCount = $('#insert_table > tbody > tr').size();     // 행삭제 body row count
        if (trCount == 1) {
            alert('더이상 삭제할 수 없습니다.');
            return;
        } else
            $('#insert_table > tbody:last > tr:last').remove();
    });
}

function make_main_specific_table(list) {
    console.log("Specific Row Size : " + list.length);
    console.log("Specific Row Type : " + typeof (list));

    if (list == undefined) {
        console.log('Main Table length is empty');
        // } else if (list == 0) {
        //     alert("필터를 적용할 대상이 없습니다.");
        //     return false;
    } else {
        if (typeof (list) == "string")
            list = JSON_parse_convertor(list);
        $('#test_table > tbody:last').empty();
        for (var i = 0; i < list.length; i++) {
            $('#test_table').append(
                $('<tr>').append(
                    //$('<td><input type="checkbox" name="main_checkbox"/>').append(model_row[i]['model']),
                    $('<td><input type="checkbox" name="main_checkbox" placeholder="끼욧"/>').append(list[i]['_id']),
                    $('<td>').append(list[i]['week']),
                    $('<td>').append(list[i]['model']),
                    $('<td>').append(list[i]['number']),
                    $('<td>').append(list[i]['date'])
                )
            );
        }
    }
}

function make_main_manufacture_table(json_table_rows, startRow, endRow) {
    var model_list = Array();
    var week_list = Array();
    for (var i = 0; i < json_table_rows.length; i++) {
        model_list.push(json_table_rows[i]['model']);
        week_list.push(json_table_rows[i]['week']);
    }
    console.log("Model List : " + model_list);
    console.log("Model List Type : " + typeof (model_list));
    console.log("Week List : " + week_list);

    $.ajax({
        url: "/getProductData",
        data: {
            'model_list': JSON.stringify(model_list),
            'week_list': JSON.stringify(week_list),
            'table_list': JSON.stringify(json_table_rows)
        },
        type: "GET",
        dataType: "json"
    })
        .done(function (json) {
            console.log("getProductData Ajax is DONE");
            console.log(json);
            // Just only Dic Type
            /*
            for (key in json) {
                console.log(key + ' ' + json.value);
            }
            $.each(json, function (key, value) {
                console.log(key + ' ' + value);
                //return_dic[key] = value;
            });*/

            if (json == undefined) {
                console.log('Main Table length is empty');
                // } else if (json == 0) {
                //     alert("필터를 적용할 대상이 없습니다.");
                //     return false;
            } else {
                if (typeof (json) == "string")
                    json = JSON_parse_convertor(json);
                $('#main_table > tbody:last').empty();
                for (var i = startRow; i < endRow; i++) { // 출력 row
                    var aging = json[i]['number'] - json[i][json[i]['model']];
                    if(aging < 0)
                        aging = 0;
                    $('#main_table').append(
                        $('<tr>').append(
                            //$('<td><input type="checkbox" name="main_checkbox" placeholder="Test"/>').append(i),
                            $('<td class="align-middle">').append(i),
                            $('<td class="align-middle">').append(json[i]['week']),
                            $('<td class="align-middle">').append(json[i]['model']),
                            $('<td class="align-middle">').append(json[i]['number']),
                            $('<td class="align-middle">').append(aging),
                            $('<td class="align-middle">').append(json[i][json[i]['model']]),
                            $('<td class="align-middle"><button type="button" name="detail_btn" value="" class="detail_btn_class btn btn-warning" data-toggle="modal" data-target="#detail_modal">자세히</button>')
                        )
                    );
                    //document.getElementsByName("detail_btn")[i].value = json[i]['_id'];
                }
            }
        })
        .fail(function (xhr, status, errorThrown) {
            $("#test").html("오류발생<br>")
                .append("오류명 : " + errorThrown + "<br>")
        })
        .always(function (xhr, status) {
            $("#text").html("요청 완료");
        });
}

function main_manufacture_table(rows, specific_rows, startRow, endRow) {
    if (specific_rows != undefined && specific_rows != 'None') {
        console.log(" 바꿔야행 ");
        make_main_specific_table(rows);
    } else if (rows == undefined) {
        console.log('Main Table length is empty');
    } else {
        make_main_manufacture_table(rows, startRow, endRow);
        make_main_specific_table(rows); // Test
    }
}

function insert_manufacture_table() {
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
            $('<td><input type="text" class="form-control" id="insert_number" name="number">')
        )
    );
}

function pagination_test(html, number) {

    var specific_row = $('#specific_list').val();
    var rows;

    if(specific_row != undefined && specific_row != 'None' && specific_row != 0){
        rows = $('#specific_list').val();
    }
    else{
        rows = $('#main_rows').val();
    }

    if (typeof (rows) == 'string')
        rows = JSON_parse_convertor(rows);
    var rows_length = rows.length;
    console.log("Main Rows List : " + rows);
    console.log("Total Rows Size : " + rows_length);
    var number_of_visual_row = number;
    var totalPages;
    if (rows_length == 0) {
        totalPages = 1;
    } else {
        totalPages = rows_length / number_of_visual_row;
    }
    if (rows_length % number_of_visual_row > 0) {
        totalPages++;
    }
    $('#pagination').twbsPagination({
        totalPages: totalPages, // 전체 page블럭 수
        visiblePages: number_of_visual_row,  // 출력될 page 블럭수 상수로 지정해 줘도 되고, 변수로 지정해줘도 된다.
        prev: "이전",
        next: "다음",
        first: '<span aria-hidden="true">«</span>',
        last: '<span aria-hidden="true">»</span>',
        onPageClick: function (event, page) {
            //$('#page_content').text('페이지 ' + page);
            console.log("Pagination");
            paging(html, page, rows, specific_row, rows_length, number_of_visual_row);
        }
    });
    // Class를 이용한 여러개 콘텐츠에 동기화하기
    // $('.sync-pagination')
}

function paging(html, page, rows, specific_row, number_of_total_row, number_of_visual_row) {
    $('#main_table > tbody').empty();
    var startRow = (page - 1) * number_of_visual_row;  // 1 page = 0 * 5 = 0,  2 page = 1 * 5 = 5, 3 page = 2 * 5 = 10 -> start row
    var endRow = page * number_of_visual_row;  // 1 page = 5, 2 page = 10, 3 page = 15 -> end row
    if (endRow > number_of_total_row) {  // 5, 10, 15 > total (ex 12) -> 마지막 row 맞추기
        endRow = number_of_total_row;
    }
    // 페이지 바뀔 때 마다 적용해야할 함수
    // html 변수에 맞는 테이블 만들기
    if (html == 'production_main') {
        main_table(rows, specific_row, startRow, endRow);
    } else if (html == 'manufacture') {
        main_manufacture_table(rows, specific_row, startRow, endRow);
    } else if (html == 'sales_main') {
        main_sales_table(rows, specific_row, startRow, endRow);
    }
    // 페이지 생성 후 적용해야 할 함수
    detail_table();
    $('#main_table').tablesorter({ sortList: [[2,1], [0,0], [1,0]]}).trigger('update');
}

