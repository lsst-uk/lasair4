import pandas as pd
import plotly.graph_objects as go


def object_difference_lightcurve(
    objectData
):
    """*Generate the Plotly HTML lightcurve for the object*

    **Key Arguments:**

    - ``objectData`` -- a json object containing lightcurve data (and more)

    **Usage:**

    ```python
    from lasair.apps.objects.utils import object_difference_lightcurve
    htmlLightcurve = object_difference_lightcurve(data)
    ```
    """
    # CREATE DATA FRAME FOR LC
    df = pd.DataFrame(objectData["candidates"])
    from astropy.time import Time
    mjds = Time(df['mjd'], format='mjd')
    df['utc'] = mjds.iso
    df['utc'] = pd.to_datetime(df['utc']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # FILTER DATA FRAME
    df["marker_color"] = "#268bd2"
    df["marker_symbol"] = "arrow-bar-down-open"
    df["marker_size"] = 8
    df["marker_opacity"] = 0.6
    df["name"] = "anon"
    symbol_sequence = ["arrow-bar-down-open", "circle"]
    df.loc[(df['fid'] == 1), "marker_color"] = "#859900"
    df.loc[(df['fid'] == 1), "bcolor"] = "#606e03"
    df.loc[(df['fid'] == 2), "marker_color"] = "#dc322f"
    df.loc[(df['fid'] == 2), "bcolor"] = "#b01f1c"
    df.loc[(df['candid'] > 0), "marker_symbol"] = "circle-open"
    df.loc[((df['candid'] > 0) & (df['isdiffpos'].isin([1, 't']))), "marker_symbol"] = "circle"
    df.loc[(df['candid'] > 0), "marker_size"] = 10

    # GENERATE THE DATASETS
    gBandData = df.loc[(df['fid'] == 1)]
    rBandData = df.loc[(df['fid'] == 2)]
    rBandDetections = rBandData.loc[(rBandData['candid'] > 0)]
    rBandNonDetections = rBandData.loc[~(rBandData['candid'] > 0)]
    rBandNonDetections["name"] = "r-band limiting mag"
    gBandDetections = gBandData.loc[(gBandData['candid'] > 0)]
    gBandNonDetections = gBandData.loc[~(gBandData['candid'] > 0)]
    gBandNonDetections["name"] = "g-band limiting mag"
    rBandDetectionsPos = rBandDetections.loc[(rBandDetections['isdiffpos'].isin([1, 't']))]
    rBandDetectionsNeg = rBandDetections.loc[~(rBandDetections['isdiffpos'].isin([1, 't']))]
    gBandDetectionsPos = gBandDetections.loc[(gBandDetections['isdiffpos'].isin([1, 't']))]
    gBandDetectionsNeg = gBandDetections.loc[~(gBandDetections['isdiffpos'].isin([1, 't']))]
    rBandDetectionsPos["name"] = "r-band detection"
    rBandDetectionsNeg["name"] = "r-band neg. flux detection"
    gBandDetectionsPos["name"] = "g-band detection"
    gBandDetectionsNeg["name"] = "g-band neg. flux detection"
    allDataSets = [rBandNonDetections, rBandDetectionsPos, rBandDetectionsNeg, gBandNonDetections, gBandDetectionsPos, gBandDetectionsNeg]

    # START TO PLOT
    fig = go.Figure()

    for data in allDataSets:
        if len(data.index):
            if data['candid'].values[0] > 0:
                dataType = "Diff Mag"
                error_y = {'type': 'data', 'array': data["sigmapsf"]}
            else:
                error_y = None
                dataType = "Limiting Mag"
            fig.add_trace(
                go.Scatter(
                    x=data["mjd"],
                    y=data["magpsf"],
                    customdata=data['utc'],
                    error_y=error_y,
                    error_y_thickness=0.7,
                    error_y_color=data["bcolor"].values[0],
                    mode='markers',
                    marker_size=data["marker_size"].values[0],
                    marker_color=data["marker_color"].values[0],
                    marker_symbol=data["marker_symbol"].values[0],
                    marker_line_color=data["bcolor"].values[0],
                    marker_line_width=1.5,
                    marker_opacity=data["marker_opacity"].values[0],
                    name=data["name"].values[0],
                    hovertemplate="<b>" + data["name"] + "</b><br>" +
                    "MJD: %{x:.2f}<br>" +
                    "UTC: %{customdata}<br>" +
                    "Magnitude: %{y}" +
                    "<extra></extra>"
                )
            )
            fig.add_traces(
                go.Scatter(x=data["utc"],
                           y=data["magpsf"],
                           showlegend=False,
                           opacity=0,
                           hoverinfo='skip',
                           xaxis="x2"))

    # DETERMINE SENSIBLE X-AXIS LIMITS
    mjdMin = df.loc[(df['candid'] > 0), "mjd"].min()
    mjdMax = df.loc[(df['candid'] > 0), "mjd"].max()
    mjdRange = mjdMax - mjdMin
    if mjdRange < 5:
        mjdRange = 5
    mjdMin -= 2 + mjdRange * 0.05
    mjdMax += 2 + mjdRange * 0.05

    utcMin = Time(mjdMin, format='mjd').iso
    utcMax = Time(mjdMax, format='mjd').iso

    fig.update_xaxes(range=[mjdMin, mjdMax], tickformat='d', tickangle=-55, tickfont_size=14, showline=True, linewidth=1.5, linecolor='#1F2937',
                     gridcolor='#F0F0F0', gridwidth=1,
                     zeroline=True, zerolinewidth=1.5, zerolinecolor='#1F2937', ticks='inside', title="MJD", title_font_size=16)
    fig.update_layout(xaxis2={'range': [utcMin, utcMax],
                              'showgrid': False,
                              'anchor': 'y',
                              'overlaying': 'x',
                              'side': 'top',
                              'tickangle': -55,
                              'tickfont_size': 14,
                              'showline': True,
                              'linewidth': 1.5,
                              'linecolor': '#1F2937'})

    # DETERMINE SENSIBLE Y-AXIS LIMITS
    ymin = df.loc[(df['candid'] > 0), "magpsf"].min()
    ymax = df.loc[(df['candid'] > 0), "magpsf"].max()
    ymax += 1.0
    ymin -= 0.5

    fig.update_yaxes(
        range=[ymax, ymin],
        tickformat='.1f',
        tickfont_size=14,
        ticksuffix=" ",
        showline=True,
        linewidth=1.5,
        linecolor='#1F2937',
        gridcolor='#F0F0F0',
        gridwidth=1,
        zeroline=True,
        zerolinewidth=1.5,
        zerolinecolor='#1F2937',
        mirror=True,
        ticks='inside',
        title="Difference Magnitude",
        title_font_size=16
    )

    # UPDATE PLOT LAYOUT
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=650,
        margin_t=100,
        margin_r=1,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="left",
            x=0
        ),
        hoverlabel=dict(
            font_color="white",
            bgcolor="#1F2937",
            font_size=14,
        )
    )

    htmlLightcurve = fig.to_html(
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {'filename': objectData["objectId"] + "_lasair_lc"},
            'responsive': True
        })

    return htmlLightcurve

# use the tab-trigger below for new function
# xt-def-function
