document.addEventListener('DOMContentLoaded', function() {

    const myDefaultAllowList = bootstrap.Popover.Default.allowList;

    myDefaultAllowList.table = [];
    myDefaultAllowList.tr = [];
    myDefaultAllowList.td = ['data-bs-option'];
    myDefaultAllowList.th = [];
    myDefaultAllowList.div = [];
    myDefaultAllowList.tbody = [];
    myDefaultAllowList.thead = [];

    $('[data-bs-toggle="popover"]').popover();

    var ttDefaultAllowList = bootstrap.Tooltip.Default.allowList;
    ttDefaultAllowList.table = [];
    ttDefaultAllowList.tr = [];
    ttDefaultAllowList.td = ['data-bs-option'];
    ttDefaultAllowList.th = [];
    ttDefaultAllowList.div = [];
    ttDefaultAllowList.tbody = [];
    ttDefaultAllowList.thead = [];

    $('[data-bs-toggle="tooltip"]').tooltip();

});
