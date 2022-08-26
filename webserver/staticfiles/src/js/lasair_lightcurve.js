function plotlc(data, div_id, bluelines) {
    var gmag = [];
    var gfmag = [];
    var ngmag = [];
    var gt = [];
    var gft = [];
    var ngt = [];
    var gerror = [];
    var gferror = [];

    var gra = [];
    var gdec = [];

    var rmag = [];
    var rfmag = [];
    var nrmag = [];
    var rt = [];
    var rft = [];
    var nrt = [];
    var rerror = [];
    var rferror = [];

    var rra = [];
    var rdec = [];
    var g = 'rgb(104,139,46)';
    var r = 'rgb(244,2,52)';
    var ng = 'rgb(216,237,207)';
    var nr = 'rgb(255,209,209)';
    var candidates = data.candidates;
    //first_item = data[0];
    //first_ra = Number(first_item.ra)*3600;
    //first_dec = Number(first_item.dec)*3600;
    var first_ra = Number(data.objectData.ramean) * 3600;
    var first_dec = Number(data.objectData.decmean) * 3600;
    var now_mjd = data.objectData.now_mjd;
    var mjdmin_ago = data.objectData.mjdmin_ago;
    var mjdmax_ago = data.objectData.mjdmax_ago;
    var minmag = 100;
    var maxmag = 0;

    candidates.forEach(function(item) {
        var y = Number(item.magpsf);
        if (y > maxmag) {
            maxmag = y;
        }
        if (y < minmag) {
            minmag = y;
        }
        var x = Number(item.since_now);
        var e = Number(item.sigmapsf);
        var x2 = first_ra - Number(item.ra) * 3600;
        var y2 = first_dec - Number(item.dec) * 3600;
        var fid = Number(item.fid);
        var det = (item.candid)
        if (det) {
            var pos = (item.isdiffpos == 't' || item.isdiffpos == '1');
            if (fid == 1 && pos) {
                gmag.push(y);
                gt.push(x);
                gerror.push(e);
                gra.push(x2);
                gdec.push(y2);
            } else if (fid == 2 && pos) {
                rmag.push(y);
                rt.push(x);
                rerror.push(e);
                rra.push(x2);
                rdec.push(y2);
            }
            if (fid == 1 && !pos) {
                gfmag.push(y);
                gft.push(x);
                gferror.push(e);
                gra.push(x2);
                gdec.push(y2);
            } else if (fid == 2 && !pos) {
                rfmag.push(y);
                rft.push(x);
                rferror.push(e);
                rra.push(x2);
                rdec.push(y2);
            }
        } else {
            if (fid == 1) {
                ngmag.push(y);
                ngt.push(x);
            } else if (fid == 2) {
                nrmag.push(y);
                nrt.push(x);
            }
        }
    });

    var lc_div = document.getElementById(div_id);
    var lcg = {
        x: gt,
        y: gmag,
        error_y: {
            type: 'data',
            color: g,
            opacity: 0.7,
            array: gerror,
            visible: true
        },
        mode: 'markers',
        marker: {
            color: g,
            size: 12
        },
        type: 'scatter'
    }
    var lcr = {
        x: rt,
        y: rmag,
        error_y: {
            type: 'data',
            color: r,
            array: rerror,
            opacity: 0.7,
            visible: true
        },
        mode: 'markers',
        marker: {
            color: r,
            size: 12
        },
        type: 'scatter'
    }
    var lcfg = {
        x: gft,
        y: gfmag,
        error_y: {
            type: 'data',
            color: g,
            opacity: 0.7,
            array: gferror,
            visible: true
        },
        mode: 'markers',
        marker: {
            color: g,
            size: 12,
            symbol: "circle-open"
        },
        type: 'scatter'
    }
    var lcfr = {
        x: rft,
        y: rfmag,
        error_y: {
            type: 'data',
            color: r,
            array: rferror,
            opacity: 0.7,
            visible: true
        },
        mode: 'markers',
        marker: {
            color: r,
            size: 12,
            symbol: "circle-open"
        },
        type: 'scatter'
    }
    var nlcg = {
        x: ngt,
        y: ngmag,
        mode: 'markers',
        marker: {
            color: ng,
            symbol: "diamond"
        },
        type: 'scatter'
    }
    var nlcr = {
        x: nrt,
        y: nrmag,
        mode: 'markers',
        marker: {
            color: nr,
            symbol: "diamond"
        },
        type: 'scatter'
    }

    if (bluelines) {
        var shapes = [{
            type: 'line',
            x0: -mjdmin_ago,
            x1: -mjdmin_ago,
            y0: minmag,
            y1: maxmag,
            line: {
                color: 'blue',
                dash: 'dot'
            }
        }, {
            type: 'line',
            x0: -mjdmax_ago,
            x1: -mjdmax_ago,
            y0: minmag,
            y1: maxmag,
            line: {
                color: 'blue',
                dash: 'dot'
            }
        }, ];
    } else {
        var shapes = []
    }

    Plotly.newPlot(lc_div, [lcg, lcr, lcfg, lcfr, nlcg, nlcr], {
        margin: {
            t: 0
        },
        displayModeBar: false,
        showlegend: false,
        xaxis: {
            title: 'MJD - ' + now_mjd,
            rangemode: 'tozero',
            tickformat: ".f"
        },
        yaxis: {
            title: 'Difference Magnitude',
            autorange: 'reversed'
        },
        shapes: shapes,
    }, {
        displayModeBar: false
    });

    var radec_div = document.getElementById('radec');

    var radecg = {
        x: gra,
        y: gdec,
        mode: 'markers',
        marker: {
            color: 'rgb(104,139,46)'
        },
        type: 'scatter'
    }

    var radecr = {
            x: rra,
            y: rdec,
            mode: 'markers',
            marker: {
                color: 'rgb(244,2,52)'
            },
            type: 'scatter'
        }
        /*
        Plotly.plot(radec_div, [radecg, radecr], {
            margin: { t: 0 },
            showlegend: false,
                width: 370,
                height: 285,
            shapes: [
                {
                    type: 'circle',
                    xref: '0',
                    yref: '0',
                    x0: -1.5,
                    y0: -1.5,
                    x1: 1.5,
                    y1: 1.5,
                    opacity: 0.3,
                    fillcolor: '#bbded6',
                    line: {
                        color: 'black'
                    }
                }]
        }, {displayModeBar: false}
        );
        */
}
