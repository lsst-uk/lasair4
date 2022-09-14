$(function() {
    const myDefaultAllowList = bootstrap.Popover.Default.allowList;

    myDefaultAllowList.table = [];
    myDefaultAllowList.tr = [];
    myDefaultAllowList.td = ['data-bs-option'];
    myDefaultAllowList.th = [];
    myDefaultAllowList.div = [];
    myDefaultAllowList.tbody = [];
    myDefaultAllowList.thead = [];

    $('[data-bs-toggle="popover"]').popover();
    $('[data-bs-toggle="tooltip"]').tooltip();

    // $('[data-bs-toggle="popover"]').Popover({
    //     html: true,

    //     content: function() {
    //         console.log("Shot");
    //         var content = $(this).attr("data-bs-content");
    //         return $(content).children(".popover-body").html();
    //     },
    //     title: function() {
    //         console.log("Shot");
    //         var title = $(this).attr("data-bs-content");
    //         return $(title).children(".popover-heading").html();
    //     }
    // });

    // var table = $('#datatable').dataTable({
    //     fnDrawCallback: function() {
    //         console.log("adasda")
    //         $('[data-bs-toggle="popover"]').Popover();
    //     }
    // })

});
