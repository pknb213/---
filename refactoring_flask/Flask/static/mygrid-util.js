var mydb = function (dburl) {
    return {
        loadData: function (filter) {
            console.log("GET");
            var d = $.Deferred();
            $.ajax({
                type: "GET",
                url: dburl,
                data: filter
            }).done(function (result) {
                // result = $.grep(result, function (item) {
                //     return item.SomeField === filter.SomeField;
                // });
                d.resolve($.map(result, function (item) {
                    return item;
                }));
            });
            return d.promise();
        },

        insertItem: function (item) {
            console.log("POST");
            return $.ajax({
                type: "POST",
                url: dburl,
                data: item
            });
        },

        updateItem: function (item) {
            console.log("PUT");
            return $.ajax({
                type: "PUT",
                url: dburl,
                data: item
            });
        },

        deleteItem: function (item) {
            console.log("DELETE");
            return $.ajax({
                type: "DELETE",
                url: dburl,
                data: item
            });
        }
    };
};

const modaldb = function (dburl) {
    return {
        loadData: function (filter) {
            console.log("GET modal");
            var d = $.Deferred();
            $.ajax({
                type: "GET",
                url: dburl,
                data: filter
            }).done(function (result) {
                // result = $.grep(result, function (item) {
                //     return item.SomeField === filter.SomeField;
                // });
                d.resolve($.map(result, function (item) {
                    return item;
                }));
            });
            return d.promise();
        },
        insertItem: function (item) {
            console.log("POST modal");
            return $.ajax({
                type: "POST",
                url: dburl,
                data: item
            });
        },
        updateItem: function (item) {
            console.log("PUT modal");
            return $.ajax({
                type: "PUT",
                url: dburl,
                data: item
            });
        },
        deleteItem: function (item) {
            console.log("DELETE modal");
            return $.ajax({
                type: "DELETE",
                url: dburl,
                data: item
            });
        }
    };
}

