"use strict";const d=document;function plotlc(e,t,i){var o=[],h=[],d=[],l=[],c=[],g=[],u=[],m=[],p=[],y=[],f=[],w=[],v=[],b=[],x=[],_=[],S=[],I=[],z=[],T=[],s="rgb(104,139,46)",r="rgb(244,2,52)",a=e.candidates,F=3600*Number(e.objectData.ramean),k=3600*Number(e.objectData.decmean),n=e.objectData.now_mjd,A=e.objectData.mjdmin_ago,e=e.objectData.mjdmax_ago,M=100,E=0,a=(a.forEach(function(e){var t=Number(e.magpsf),i=(E<t&&(E=t),t<M&&(M=t),Number(e.since_now)),s=Number(e.sigmapsf),r=F-3600*Number(e.ra),a=k-3600*Number(e.dec),n=Number(e.fid);e.candid?(e="t"==e.isdiffpos||"1"==e.isdiffpos,1==n&&e?(o.push(t),l.push(i),u.push(s),p.push(r),y.push(a)):2==n&&e&&(f.push(t),b.push(i),S.push(s),z.push(r),T.push(a)),1!=n||e?2!=n||e||(w.push(t),x.push(i),I.push(s),z.push(r),T.push(a)):(h.push(t),c.push(i),m.push(s),p.push(r),y.push(a))):1==n?(d.push(t),g.push(i)):2==n&&(v.push(t),_.push(i))}),document.getElementById(t));t=i?[{type:"line",x0:-A,x1:-A,y0:M,y1:E,line:{color:"blue",dash:"dot"}},{type:"line",x0:-e,x1:-e,y0:M,y1:E,line:{color:"blue",dash:"dot"}}]:[],Plotly.newPlot(a,[{x:l,y:o,error_y:{type:"data",color:s,opacity:.7,array:u,visible:!0},mode:"markers",marker:{color:s,size:12},type:"scatter"},{x:b,y:f,error_y:{type:"data",color:r,array:S,opacity:.7,visible:!0},mode:"markers",marker:{color:r,size:12},type:"scatter"},{x:c,y:h,error_y:{type:"data",color:s,opacity:.7,array:m,visible:!0},mode:"markers",marker:{color:s,size:12,symbol:"circle-open"},type:"scatter"},{x:x,y:w,error_y:{type:"data",color:r,array:I,opacity:.7,visible:!0},mode:"markers",marker:{color:r,size:12,symbol:"circle-open"},type:"scatter"},{x:g,y:d,mode:"markers",marker:{color:"rgb(216,237,207)",symbol:"diamond"},type:"scatter"},{x:_,y:v,mode:"markers",marker:{color:"rgb(255,209,209)",symbol:"diamond"},type:"scatter"}],{margin:{t:0},displayModeBar:!1,showlegend:!1,xaxis:{title:"MJD - "+n,rangemode:"tozero",tickformat:".f"},yaxis:{title:"Difference Magnitude",autorange:"reversed"},shapes:t},{displayModeBar:!1}),document.getElementById("radec")}function plotlc_apparent(t){gmag=[],gt=[],gerror=[],rmag=[],rt=[],rerror=[],g="rgb(104,139,46)",r="rgb(244,2,52)",(candidates=t.candidates).forEach(function(t){y=Number(t.dc_mag),x=Number(t.mjd),e=Number(t.dc_sigmag),fid=Number(t.fid),(det=t.candid)&&(1==fid?(gmag.push(y),gt.push(x),gerror.push(e)):2==fid&&(rmag.push(y),rt.push(x),rerror.push(e)))}),lc_div=document.getElementById("lc_apparent");var t={x:gt,y:gmag,error_y:{type:"data",color:g,opacity:.7,array:gerror,visible:!0},mode:"markers",marker:{color:g,size:8},type:"markers"},i={x:rt,y:rmag,error_y:{type:"data",color:r,array:rerror,opacity:.7,visible:!0},mode:"markers",marker:{color:r,size:8},type:"markers"};Plotly.plot(lc_div,[t,i],{margin:{t:0},displayModeBar:!1,showlegend:!1,xaxis:{title:"MJD",tickformat:".f"},yaxis:{title:"Apparent Magnitude",autorange:"reversed"}},{displayModeBar:!1})}function fixJS9ExtraStyles(e){let t=document.querySelectorAll(".JS9");t.forEach(function(t){var i=setInterval(function(){var e;$("#"+t.id).length&&(clearInterval(i),e=JS9.LookupDisplay(t.id),JS9.ResizeDisplay(t.id,e.width,e.width))},100)});var i=setInterval(function(){if(document.querySelectorAll(".ImExamRadialProj").length){clearInterval(i);let e=document.querySelectorAll(".ImExamRadialProj");e.forEach(function(e){e.style.height=e.offsetWidth+"px"})}},100);setTimeout(()=>{e()},2e3)}function loadFitsImages(e){let t=document.querySelectorAll(".fitsStamp");t.forEach(function(e){var t=e.getAttribute("src");const i=document.createElement("span");var s=uuidv4();i.innerHTML=`<div class="JS9" data-width="100%" id="${s}" ></div>`,e.classList.contains("fits-lite")||(e.classList.contains("fits-toggle")?i.innerHTML=`<div class="JS9Menubar d-none" id="${s}Menubar" data-width="100%"></div>`+i.innerHTML:i.innerHTML=`<div class="JS9Menubar" id="${s}Menubar" data-width="100%"></div>`+i.innerHTML),e.parentNode.replaceChild(i,e),JS9.Preload(t,{scale:"linear",zoom:"toFit",onload:setDefaultParams},{display:s})}),e()}function collapseJS9Extras(e){var t=document.getElementById("collapseJS9Extras");null!=t&&(t.classList.add("collapse"),e())}function setDefaultParams(e){JS9.SetZoom("ToFit",{display:e}),JS9.SetColormap("grey",{display:e}),JS9.SetScale("dataminmax",{display:e}),JS9.AddRegions("circle",{radius:10},{display:e})}function uuidv4(){return([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,e=>(e^crypto.getRandomValues(new Uint8Array(1))[0]&15>>e/4).toString(16))}function toggleJS9Menus(){event.preventDefault();let e=document.getElementsByClassName("JS9Menubar");for(var t=0;t<e.length;t++)e[t].classList.toggle("d-none")}d.addEventListener("DOMContentLoaded",function(e){Swal.mixin({customClass:{confirmButton:"btn btn-primary me-3",cancelButton:"btn btn-gray"},buttonsStyling:!1});var t,i=document.getElementById("theme-settings"),s=document.getElementById("theme-settings-expand");i&&(t=new bootstrap.Collapse(i,{show:!0,toggle:!1}),"true"===window.localStorage.getItem("settings_expanded")?(t.show(),s.classList.remove("show")):(t.hide(),s.classList.add("show")),i.addEventListener("hidden.bs.collapse",function(){s.classList.add("show"),window.localStorage.setItem("settings_expanded",!1)}),s.addEventListener("click",function(){s.classList.remove("show"),window.localStorage.setItem("settings_expanded",!0),setTimeout(function(){t.show()},300)}));const r={sm:540,md:720,lg:960,xl:1140};var i=document.getElementById("sidebarMenu"),a=(i&&d.body.clientWidth<r.lg&&(i.addEventListener("shown.bs.collapse",function(){document.querySelector("body").style.position="fixed"}),i.addEventListener("hidden.bs.collapse",function(){document.querySelector("body").style.position="relative"})),d.querySelector(".notification-bell"));a&&a.addEventListener("shown.bs.dropdown",function(){a.classList.remove("unread")}),[].slice.call(d.querySelectorAll("[data-background]")).map(function(e){e.style.background="url("+e.getAttribute("data-background")+")"}),[].slice.call(d.querySelectorAll("[data-background-lg]")).map(function(e){document.body.clientWidth>r.lg&&(e.style.background="url("+e.getAttribute("data-background-lg")+")")}),[].slice.call(d.querySelectorAll("[data-background-color]")).map(function(e){e.style.background="url("+e.getAttribute("data-background-color")+")"}),[].slice.call(d.querySelectorAll("[data-color]")).map(function(e){e.style.color="url("+e.getAttribute("data-color")+")"});[].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]')).map(function(e){return new bootstrap.Tooltip(e)}),[].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]')).map(function(e){return new bootstrap.Popover(e)}),[].slice.call(d.querySelectorAll("[data-datepicker]")).map(function(e){return new Datepicker(e,{buttonClass:"btn"})}),d.querySelector(".input-slider-container")&&[].slice.call(d.querySelectorAll(".input-slider-container")).map(function(e){var t=e.querySelector(":scope .input-slider"),i=t.getAttribute("id"),s=t.getAttribute("data-range-value-min"),t=t.getAttribute("data-range-value-max"),e=e.querySelector(":scope .range-slider-value"),r=e.getAttribute("id"),e=e.getAttribute("data-range-value-low"),i=d.getElementById(i);d.getElementById(r);noUiSlider.create(i,{start:[parseInt(e)],connect:[!0,!1],range:{min:[parseInt(s)],max:[parseInt(t)]}})}),d.getElementById("input-slider-range")&&(i=d.getElementById("input-slider-range"),l=d.getElementById("input-slider-range-value-low"),c=d.getElementById("input-slider-range-value-high"),n=[d,c],noUiSlider.create(i,{start:[parseInt(l.getAttribute("data-range-value-low")),parseInt(c.getAttribute("data-range-value-high"))],connect:!0,tooltips:!0,range:{min:parseInt(i.getAttribute("data-range-value-min")),max:parseInt(i.getAttribute("data-range-value-max"))}}),i.noUiSlider.on("update",function(e,t){n[t].textContent=e[t]})),d.querySelector(".ct-chart-sales-value")&&new Chartist.Line(".ct-chart-sales-value",{labels:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],series:[[0,10,30,40,80,60,100]]},{low:0,showArea:!0,fullWidth:!0,plugins:[Chartist.plugins.tooltip()],axisX:{position:"end",showGrid:!0},axisY:{showGrid:!1,showLabel:!1,labelInterpolationFnc:function(e){return"$"+ +e+"k"}}}),d.querySelector(".ct-chart-ranking")&&new Chartist.Bar(".ct-chart-ranking",{labels:["Mon","Tue","Wed","Thu","Fri","Sat"],series:[[1,5,2,5,4,3],[2,3,4,8,1,2]]},{low:0,showArea:!0,plugins:[Chartist.plugins.tooltip()],axisX:{position:"end"},axisY:{showGrid:!1,showLabel:!1,offset:0}}).on("draw",function(e){"line"!==e.type&&"area"!==e.type||e.element.animate({d:{begin:2e3*e.index,dur:2e3,from:e.path.clone().scale(1,0).translate(0,e.chartRect.height()).stringify(),to:e.path.clone().stringify(),easing:Chartist.Svg.Easing.easeOutQuint}})}),d.querySelector(".ct-chart-traffic-share")&&(o={series:[70,20,10]},h=function(e,t){return e+t},new Chartist.Pie(".ct-chart-traffic-share",o,{labelInterpolationFnc:function(e){return Math.round(e/o.series.reduce(h)*100)+"%"},low:0,high:8,donut:!0,donutWidth:20,donutSolid:!0,fullWidth:!1,showLabel:!1,plugins:[Chartist.plugins.tooltip()]})),d.getElementById("loadOnClick")&&d.getElementById("loadOnClick").addEventListener("click",function(){var e=this,t=d.getElementById("extraContent"),i=d.getElementById("allLoadedText");e.classList.add("btn-loading"),e.setAttribute("disabled","true"),setTimeout(function(){t.style.display="block",e.style.display="none",i.style.display="block"},1500)}),new SmoothScroll('a[href*="#"]',{speed:500,speedAsDuration:!0});d.querySelector(".current-year")&&(d.querySelector(".current-year").textContent=(new Date).getFullYear()),d.querySelector(".glide")&&new Glide(".glide",{type:"carousel",startAt:0,perView:3}).mount(),d.querySelector(".glide-testimonials")&&new Glide(".glide-testimonials",{type:"carousel",startAt:0,perView:1,autoplay:2e3}).mount(),d.querySelector(".glide-clients")&&new Glide(".glide-clients",{type:"carousel",startAt:0,perView:5,autoplay:2e3}).mount(),d.querySelector(".glide-news-widget")&&new Glide(".glide-news-widget",{type:"carousel",startAt:0,perView:1,autoplay:2e3}).mount(),d.querySelector(".glide-autoplay")&&new Glide(".glide-autoplay",{type:"carousel",startAt:0,perView:3,autoplay:2e3}).mount();var n,o,h,l=d.getElementById("billingSwitch");if(l){const g=new countUp.CountUp("priceStandard",99,{startVal:199}),u=new countUp.CountUp("pricePremium",199,{startVal:299});l.addEventListener("change",function(){billingSwitch.checked?(g.start(),u.start()):(g.reset(),u.reset())})}var c=d.getElementById("datatable");c&&new simpleDatatables.DataTable(c)}),document.addEventListener("DOMContentLoaded",function(){let e=d.querySelectorAll(".datatable");e.forEach(function(i){if(i){let e=null,t=(i.hasAttribute("id")&&(e=i.id),100);i.hasAttribute("data-perPage")&&(t=i.getAttribute("data-perPage"));const r=new simpleDatatables.DataTable(i,{labels:{placeholder:"Search table...",perPage:"{select} rows per page",noRows:"No objects found",info:"Showing {start} to {end} of {rows} rows"},layout:{top:"{search}",bottom:"{select}{info}{pager}"},perPage:t,perPageSelect:[5,10,50,100,500,1e4]}),s=r.columns().dt.labels;s.includes("objectId")?(i=s.indexOf("objectId"),r.columns().sort(i,"desc")):s.includes("Created")&&(i=s.indexOf("Created"),r.columns().sort(i,"desc")),null!==e&&document.querySelectorAll(`a[data-table=${CSS.escape(e)}]`).forEach(function(s){s.addEventListener("click",function(e){var t=s.dataset.type,i=s.dataset.filename,i={type:t,filename:i=null==i?"lasair-export":i};"csv"===t&&(i.columnDelimiter=","),"json"===t&&(i.replacer=null,i.space=4),r.export(i)})})}})}),document.addEventListener("DOMContentLoaded",function(){JS9.globalOpts.alerts=!1,JS9.globalOpts.updateTitlebar=!1,JS9.imageOpts={inherit:!1,contrast:1,bias:.5,invert:!1,exp:1e3,colormap:"heat",overlay:!0,scale:"linear",scaleclipping:"dataminmax",scalemin:Number.NaN,scalemax:Number.NaN,flip:"none",rot90:0,rotate:0,zscalecontrast:.25,zscalesamples:600,zscaleline:120,wcssys:"native",lcs:"physical",valpos:!1,sigma:"none",opacity:1,alpha:255,nancolor:"#FF0000",nocolor:{red:0,green:0,blue:0,alpha:0},zoom:"toFit",zooms:6,topZooms:2,wcsalign:!0,rotationMode:"relative",crosshair:!0,disable:[],ltvbug:!1,listonchange:!1,whichonchange:"selected"};let i=[loadFitsImages,fixJS9ExtraStyles,collapseJS9Extras];!function e(t){t&&t(()=>e(i.shift()))}(i.shift())});var fits,fits_url,NROIS=0;function gebi(e){return document.getElementById(e)}function start_fitsview(e,t){fits=e,fits_url=t,console.log(fits_url);e=gebi("stretch_sel");e?(console.log(e.value),fits.setStretch(e.value)):(console.log("no stretch div"),fits.setStretch("linear")),fits.addROIChangedHandler(onROIChange),window.onunload=function(){fits.header_win&&fits.header_win.close()},fits.imageFromUrl(fits_url)}function showHeader(){fits.showHeader(!0)}function newContrast(e){var t=e.target.id,e=e.target.id.substring(t.length-1,t.length),t=gebi("contrast_slider_"+e).value;gebi("contrast_value_"+e).innerHTML=t,fits.setContrast(fits.rois[e],t/100)}function onStretchSel(){fits.setStretch(gebi("stretch_sel").value)}function onROIChange(e,t,i){var s=gebi("roiinfo_"+e.z),r=0==e.z?"Image":"ROI "+e.z,s=(s&&displayStats(s,"black",r,e),gebi("roihcanvas_"+e.z));s&&fits.displayHistogram(e,s)}function onDisplayROI(e){var t=gebi("display_roi_"+e);fits.enableROI(e,t.checked)}function displayStats(e,t,i,s){var r=s.stats,a=fits.image2FITS(s),n=fits.image2FITS(s.stats.minat),o=fits.image2FITS(s.stats.maxat);e.innerHTML=i+": "+pad(s.width,4)+" x "+pad(s.height,5)+" @ ["+pad(a.x,5)+", "+pad(a.y,5)+"]<br>Min "+pad(r.min.toFixed(1),11)+pad("",4)+" @ ["+pad(n.x.toFixed(0),5)+", "+pad(n.y.toFixed(0),5)+"]<br>Max "+pad(r.max.toFixed(1),11)+pad("",4)+" @ ["+pad(o.x.toFixed(0),5)+", "+pad(o.y.toFixed(0),5)+"]<br>Mean "+pad(r.mean.toFixed(1),10)+pad("",2)+"StdDev "+pad(r.stddev.toFixed(1),12)+"<br>Median "+pad(r.median.toFixed(1),8)+pad("",1)+" Sum "+pad(r.sum.toFixed(1),15),e.style.color=t}function pad(e,t){for(var i=t-(e=e.toString()).length,s=0;s<i;s++)e="&nbsp;"+e;return e}function FITS(e,t){if(!e||"DIV"!=e.tagName)throw"FITS requires a div";isNaN(parseInt(t))&&(t=0);for(var i=this,s=(createResizeListener(),addResizeListener(e,function(){i.handleResize()}),this.rois=new Array(t+1),["#bbb","#55f","#393","orange","#1ff","#f1f","#fa1","white"]),r=0;r<=t;r++){var a={x:0,y:0};a.z=r,a.enabled=!0,a.width=1e7,a.height=1e7,a.contrast=0,a.color=s[r],a.stats={},a.black=void 0,a.white=void 0,a.cvs=FITS_newCanvas(e,"roi_canvas"+r,r+1),a.ctx=a.cvs.getContext("2d"),this.rois[r]=a}this.gcvs=FITS_newCanvas(e,"glass_canvas",t+2),this.gctx=this.gcvs.getContext("2d"),window.addEventListener("mousemove",function(e){FITS_handleMouse(e,i)},!0),window.addEventListener("mousedown",function(e){FITS_handleMouse(e,i)},!0),window.addEventListener("keydown",function(e){FITS_handleKeyboard(e,i)},!0),window.addEventListener("keyup",function(e){FITS_handleKeyboard(e,i)},!0),this.icroi=t,this.div_id=e,this.image=void 0,this.filename=void 0,this.header={},this.rawheader=[],this.drew_glass=!1,this.glass_size=.05,this.glass_mag=4,this.glass_mic=void 0,this.mic=void 0,this.width=void 0,this.height=void 0,this.resize_scale=void 0,this.header_win=void 0,this.stretch="linear",this.userMouseHandler=void 0,this.userROIChangedHandler=void 0,this.userGlassCanvas=void 0,this.drag_roi=void 0,this.drag_code=void 0,this.drag_mvos={dx:0,dy:0},this.cursors={"n-resize":"ns-resize","s-resize":"ns-resize","e-resize":"ew-resize","w-resize":"ew-resize","ne-resize":"nesw-resize","sw-resize":"nesw-resize","nw-resize":"nwse-resize","se-resize":"nwse-resize",move:"move"}}function FITS_newCanvas(e,t,i){var s=document.createElement("canvas");return s.setAttribute("id",t),s.setAttribute("style","position:absolute; z-index:"+i),s.setAttribute("width",parseInt(e.style.width)),s.setAttribute("height",parseInt(e.style.height)),e.appendChild(s),s}function FITS_handleKeyboard(e,t){e=e||event,t.showGlass=e.shiftKey}function FITS_handleMouse(e,t){t.image&&(0<=(e=t.event2image(e)).x&&e.x<t.width&&0<=e.y&&e.y<t.height?t.mic=e:t.glass_mic&&(t.mic=t.glass_mic))}function noSmoothing(e){e.imageSmoothingEnabled=!1,e.mozImageSmoothingEnabled=!1}function createResizeListener(){var t,i,s=document.attachEvent,r=navigator.userAgent.match(/Trident/),a=(t=window.requestAnimationFrame||window.mozRequestAnimationFrame||window.webkitRequestAnimationFrame||function(e){return window.setTimeout(e,20)},function(e){return t(e)}),n=(i=window.cancelAnimationFrame||window.mozCancelAnimationFrame||window.webkitCancelAnimationFrame||window.clearTimeout,function(e){return i(e)});function o(i){var e=i.target||i.srcElement;e.__resizeRAF__&&n(e.__resizeRAF__),e.__resizeRAF__=a(function(){var t=e.__resizeTrigger__;t.__resizeListeners__.forEach(function(e){e.call(t,i)})})}function h(e){this.contentDocument.defaultView.__resizeTrigger__=this.__resizeElement__,this.contentDocument.defaultView.addEventListener("resize",o)}window.addResizeListener=function(e,t){var i;e.__resizeListeners__||(e.__resizeListeners__=[],s?(e.__resizeTrigger__=e).attachEvent("onresize",o):("static"==getComputedStyle(e).position&&(e.style.position="relative"),(i=e.__resizeTrigger__=document.createElement("object")).setAttribute("style","display: block; position: absolute; top: 0; left: 0; height: 100%; width: 100%; overflow: hidden; pointer-events: none; z-index: -1;"),i.__resizeElement__=e,i.onload=h,i.type="text/html",r&&e.appendChild(i),i.data="about:blank",r||e.appendChild(i))),e.__resizeListeners__.push(t)},window.removeResizeListener=function(e,t){e.__resizeListeners__.splice(e.__resizeListeners__.indexOf(t),1),e.__resizeListeners__.length||(s?e.detachEvent("onresize",o):(e.__resizeTrigger__.contentDocument.defaultView.removeEventListener("resize",o),e.__resizeTrigger__=!e.removeChild(e.__resizeTrigger__)))}}function copy(e,t){setTimeout(function(){$(".tooltip").fadeOut("slow")},500);var i=document.createElement("input"),e=(i.setAttribute("value",e),document.body.appendChild(i),i.select(),document.execCommand("copy"));return document.body.removeChild(i),e}FITS.prototype.imageFromUrl=function(e){var i=new XMLHttpRequest;i.onload=function(e){var t=i.response;200==i.status&&(fits.setNewImage("fits_file",t),fits.showHeader(!1))},i.open("GET",e),i.responseType="arraybuffer",i.overrideMimeType("text/plain; charset=x-user-defined"),i.send(null)},FITS.prototype.setNewImage=function(e,t){this.filename=e,this.header={},this.rawheader=[];var i=0;try{for(i=0;i<t.byteLength;i+=80){var s,r,a=String.fromCharCode.apply(null,new Uint8Array(t,i,80));if(a.match(/^END */)){i+=80;break}this.rawheader.push(a),a.indexOf("=")<0||(s=(s=a.substring(0,8)).replace(/ *$/,""),r=0<=(r=(r=(r=(r=a.substring(10)).replace(/^ */,"")).replace(/\/.*$/,"")).replace(/ *$/,"")).indexOf("'")?r.substring(1,r.length-2):0<=r.indexOf("T")||!(0<=r.indexOf("F"))&&(0<=r.indexOf(".")?parseFloat:parseInt)(r),this.header[s]=r)}}catch(e){throw this.filename+": not a FITS file: "+e}if(!this.header.SIMPLE||"number"!=typeof this.header.NAXIS1||"number"!=typeof this.header.NAXIS2||"number"!=typeof this.header.BITPIX)throw this.filename+": not a valid FITS file";0<i%2880&&(i+=2880-i%2880),this.width=this.rois[0].width=this.header.NAXIS1,this.height=this.rois[0].height=this.header.NAXIS2;var e=this.width*this.height,n=e*Math.abs(this.header.BITPIX)/8;if(t.byteLength<i+n)throw this.filename+": too short: "+t.byteLength+" < "+(i+n);var o=this.header.BZERO||0,h=this.header.BSCALE||1,d=(this.image=new Array(e),new DataView(t,i,n));if(8==this.header.BITPIX)for(var l=0,c=0;c<this.height;c++)for(var g=(this.height-1-c)*this.width,u=0;u<this.width;u++)this.image[l]=o+h*d.getUint8(g),l++,g++;else if(16==this.header.BITPIX)for(l=0,c=0;c<this.height;c++)for(g=(this.height-1-c)*this.width,u=0;u<this.width;u++)this.image[l]=o+h*d.getInt16(2*g,!1),l++,g++;else if(32==this.header.BITPIX)for(l=0,c=0;c<this.height;c++)for(g=(this.height-1-c)*this.width,u=0;u<this.width;u++)this.image[l]=o+h*d.getInt32(4*g,!1),l++,g++;else{if(-32!=this.header.BITPIX)throw this.filename+": BITPIX "+this.header.BITPIX+" is not yet supported";for(l=0,c=0;c<this.height;c++)for(g=(this.height-1-c)*this.width,u=0;u<this.width;u++)this.image[l]=o+h*d.getFloat32(4*g,!1),l++,g++}this.handleResize()},FITS.prototype.showHeader=function(e){if(this.filename&&this.rawheader&&(this.header_win&&!this.header_win.closed||e)){null!=this.header_win&&!this.header_win.closed||(this.header_win=window.open("","_blank","width=500, height=500, scrollbars=yes"),this.header_win.document.write("<html></html>"));for(var t="<head><title>"+this.filename+" Header</title></head><body><pre>",i=0;i<this.rawheader.length;i++)t+=this.rawheader[i]+"<br>";this.header_win.document.documentElement.innerHTML=t+="</pre></body>"}},FITS.prototype.computeROIStats=function(e){if(this.image){if(e.x<0||e.width<0||e.x+e.width>this.width||e.y<0||e.height<0||e.y+e.height>this.height)throw this.filename+": roi is outside image ["+e.x+","+e.y+"], "+e.width+" x "+e.height;for(var t=e.width*e.height,i=e.y*this.width+e.x,s=this.image[i],r=s,a=e.x,n=e.y,o=e.x,h=e.y,d=0,l=0,c=0;c<e.height;c++){for(var g=0;g<e.width;g++)(w=this.image[i++])<s&&(s=w,o=g+e.x,h=c+e.y),r<w&&(r=w,a=g+e.x,n=c+e.y),d+=w,l+=w*w;i+=this.width-e.width}for(var u=Math.max(1,r-s),m=Math.sqrt(t*l-d*d)/t,p=new Array(128),y=0;y<p.length;y++)p[y]=0;for(var i=e.y*this.width+e.x,f=0,c=0;c<e.height;c++){for(g=0;g<e.width;g++){var w=this.image[i++],v=Math.floor((p.length-1)*(w-s)/u);++p[v]>f&&(f=p[v])}i+=this.width-e.width}for(var b=0,x=0;x<t/2;b++)x+=p[b];return{npixels:t,min:s,minat:{x:o,y:h},max:r,maxat:{x:a,y:n},range:u,sum:d,mean:d/t,median:Math.floor(s+u*b/p.length),stddev:m,histo:p,histomax:f}}},FITS.prototype.setContrast=function(e,t){if(this.image){if(t<0||1<t)throw"setContrast "+t+" must be 0 .. 1";e.contrast=Math.sqrt(t),this.renderROI(e,!1,!1)}},FITS.prototype.findBlackAndWhite=function(e,t){if(t)return t.histo,{black:Math.max(t.min,t.mean-6*t.stddev*(1-e)),white:Math.min(t.max,t.mean+6*t.stddev*(1-e))}},FITS.prototype.handleResize=function(){if(this.image){for(var e=parseInt(this.div_id.style.width),t=parseInt(this.div_id.style.height),i=0;i<this.rois.length;i++)this.rois[i].cvs.setAttribute("width",e),this.rois[i].cvs.setAttribute("height",t);this.gcvs.setAttribute("width",e),this.gcvs.setAttribute("height",t),e/t>this.width/this.height?this.resize_scale=t/this.height:this.resize_scale=e/this.width;for(i=0;i<this.rois.length;i++)this.rois[i].ctx.setTransform(1,0,0,1,0,0),this.rois[i].ctx.translate(.5,.5),this.rois[i].ctx.scale(this.resize_scale,this.resize_scale);this.gctx.setTransform(1,0,0,1,0,0),this.gctx.translate(.5,.5),this.gctx.scale(this.resize_scale,this.resize_scale),this.renderAll()}},FITS.prototype.renderAll=function(){for(var e=this.rois.length,t=!1,i=0;i<e;i++){var s=this.rois[i];(s.x+s.width>this.width||s.y+s.height>this.height||s.width*this.resize_scale<20&&s.height*this.resize_scale<20)&&(s.x=Math.floor((e-i)%e*3*this.width/20),s.y=Math.floor(this.height/20),s.width=Math.floor(this.width/10),s.height=Math.floor(this.height/10),t=!0)}for(i=0;i<this.rois.length;i++)this.renderROI(this.rois[i],!1,t)},FITS.prototype.setStretch=function(e){this.stretch=e,this.renderAll()},FITS.prototype.enableROI=function(e,t){if(e<1||e>=this.rois.length)throw"enableROI("+e+") must be 1 .. "+(this.rois.length-1);e=this.rois[e];e.enabled=t,this.renderROI(e,!1,!1)},FITS.prototype.redefineROI=function(e,t){if(e<1||e>=this.rois.length)throw"redefineROI("+e+") must be 1 .. "+(this.rois.length-1);if(t.x<0||t.x+t.width>this.width||t.y<0||t.y+t.height>this.height)throw"redefineROI ["+t.x+","+t.y+";"+t.width+"x"+t.height+"] not inside image ["+this.width+"x"+this.height+"]";e=this.rois[e];e.x=t.x,e.y=t.y,e.width=t.width,e.height=t.height,this.renderROI(e,!0,!0),1<this.rois.length&&e==this.rois[this.icroi]&&this.renderROI(this.rois[0],!1,!1)},FITS.prototype.renderROI=function(e,t,i){if(this.image){e.stats=this.computeROIStats(e);var s,r=this.findBlackAndWhite(e.contrast,e.stats),a=e.black=r.black,n=e.white=r.white,o=(e==this.rois[0]&&1<this.rois.length&&this.rois[this.icroi].enabled&&(o=this.computeROIStats(this.rois[this.icroi]),a=(r=this.findBlackAndWhite(e.contrast,o)).black,n=r.white),e.ctx),h=Math.max(1,n-a);if("linear"==this.stretch)s=function(e){return 255*(e-a)/h};else if("square"==this.stretch)s=function(e){e=(e-a)/h;return 255*e*e};else{if("sqrt"!=this.stretch)throw"Unknown stetch: "+this.stretch+", choices are linear, square and sqrt";s=function(e){return 255*Math.sqrt((e-a)/h)}}if(e.enabled){for(var r=new ImageData(e.width,e.height),d=r.data,l=0,c=e.y+e.height-1;c>=e.y;c--)for(var g=e.x;g<e.x+e.width;g++){var u=s(this.image[c*this.width+g]);d[4*l]=u,d[4*l+1]=u,d[4*l+2]=u,d[4*l+3]=255,l++}n=document.createElement("canvas");n.width=e.width,n.height=e.height,n.getContext("2d").putImageData(r,0,0),this.clearLayer(o),noSmoothing(o),o.drawImage(n,e.x,e.y),n=void 0,o.strokeStyle=e.color,o.lineWidth=2,o.beginPath(),o.moveTo(e.x,e.y),o.lineTo(e.x+e.width,e.y),o.lineTo(e.x+e.width,e.y+e.height),o.lineTo(e.x,e.y+e.height),o.lineTo(e.x,e.y),o.lineTo(e.x+e.width,e.y),o.stroke()}else this.clearLayer(o);null!=this.userROIChangedHandler&&this.userROIChangedHandler(e,t,i)}},FITS.prototype.renderGlass=function(e){var t,i,s,r,a,n,o,h;e&&this.gcvs&&this.image&&(o=(t=this.glass_size*this.width)*this.glass_mag,h=e.x,e=e.y,h<0||h>=this.width||(n=h<o/2?(i=0,(r=2*h)/this.glass_mag):h>this.width-o/2?(r=2*(this.width-h),i=this.width-r,r/this.glass_mag):(i=h-o/2,r=o,t),e<0||e>=this.height||(o=e<o/2?(s=0,(a=2*e)/this.glass_mag):e>this.height-o/2?(a=2*(this.height-e),s=this.height-a,a/this.glass_mag):(s=e-o/2,a=o,t),noSmoothing(this.gctx),this.gctx.drawImage(this.rois[0].cvs,(h-n/2)*this.resize_scale+1,(e-o/2)*this.resize_scale+1,n*this.resize_scale,o*this.resize_scale,i,s,r,a),this.gctx.strokeStyle="yellow",this.gctx.beginPath(),this.gctx.moveTo(i,s),this.gctx.lineTo(i+r,s),this.gctx.lineTo(i+r,s+a),this.gctx.lineTo(i,s+a),this.gctx.lineTo(i,s),this.gctx.stroke())))},FITS.prototype.image2FITS=function(e){var t;if(this.height&&e)return(t=JSON.parse(JSON.stringify(e))).x=e.x+1,t.y=this.height-e.y,e.height&&(t.y-=e.height-1),t},FITS.prototype.FITS2Image=function(e){var t;if(this.height&&e)return(t=JSON.parse(JSON.stringify(e))).x=e.x-1,t.y=this.height-e.y,e.height&&(t.y-=e.height-1),t},FITS.prototype.event2image=function(e){var t={},e=(e.pageX?(t.x=e.pageX,t.y=e.pageY):(t.x=e.clientX,t.y=e.clientY),this.rois[0].cvs.getBoundingClientRect());return t.x-=window.pageXOffset+e.left,t.y-=window.pageYOffset+e.top,t.x=Math.floor(t.x/this.resize_scale),t.y=Math.floor(t.y/this.resize_scale),t},FITS.prototype.addMouseHandler=function(e){this.userMouseHandler=e},FITS.prototype.addROIChangedHandler=function(e){this.userROIChangedHandler=e},FITS.prototype.addResizeHandler=function(e){addResizeListener(this.div_id,e)},FITS.prototype.addGlassCanvas=function(e){this.userGlassCanvas=e},FITS.prototype.findROI=function(e){var t=4/this.resize_scale;this.drag_roi=void 0,this.drag_code=void 0;for(var i=1;null==this.drag_code&&i<this.rois.length;i++){var s,r,a,n=this.rois[i];n.enabled&&e.x>n.x-t&&e.x<n.x+n.width+t&&e.y>n.y-t&&e.y<n.y+n.height+t&&((s=e.y<n.y+t)&&Math.abs(e.x-(n.x+n.width/2))<n.width/6?this.drag_code="move":(r=e.x<n.x+t,a=e.x>n.x+n.width-t,n=e.y>n.y+n.height-t,r?this.drag_code=s?"nw-resize":n?"sw-resize":"w-resize":a?this.drag_code=s?"ne-resize":n?"se-resize":"e-resize":s?this.drag_code=r?"nw-resize":a?"ne-resize":"n-resize":n&&(this.drag_code=r?"sw-resize":a?"se-resize":"s-resize")),null!=this.drag_code&&(this.drag_roi=i))}},FITS.prototype.moveROI=function(e){var t,i,s=this.rois[this.drag_roi],r=void 0;"move"==this.drag_code?(s.x=Math.min(Math.max(0,e.x+this.drag_mvos.dx-Math.round(s.width/2+.5)),this.width-s.width),s.y=Math.min(Math.max(0,e.y+this.drag_mvos.dy-Math.round(s.height/2+.5)),this.height-s.height)):"n-resize"==this.drag_code?(t=e.y-s.y,s.y+=t,s.height-=t,s.height<0&&(r="s-resize")):"s-resize"==this.drag_code?(s.height+=e.y-(s.y+s.height),s.height<0&&(r="n-resize")):"e-resize"==this.drag_code?(s.width+=e.x-(s.x+s.width),s.width<0&&(r="w-resize")):"w-resize"==this.drag_code?(i=e.x-s.x,s.x+=i,s.width-=i,s.width<0&&(r="e-resize")):"ne-resize"==this.drag_code?(s.width+=e.x-(s.x+s.width),t=e.y-s.y,s.y+=t,s.height-=t,s.width<0&&s.height<0?r="sw-resize":s.width<0?r="nw-resize":s.height<0&&(r="se-resize")):"se-resize"==this.drag_code?(s.width+=e.x-(s.x+s.width),s.height+=e.y-(s.y+s.height),s.width<0&&s.height<0?r="nw-resize":s.width<0?r="sw-resize":s.height<0&&(r="ne-resize")):"nw-resize"==this.drag_code?(t=e.y-s.y,s.y+=t,s.height-=t,i=e.x-s.x,s.x+=i,s.width-=i,s.width<0&&s.height<0?r="se-resize":s.width<0?r="ne-resize":s.height<0&&(r="sw-resize")):"sw-resize"==this.drag_code&&(i=e.x-s.x,s.x+=i,s.width-=i,s.height+=e.y-(s.y+s.height),s.width<0&&s.height<0?r="ne-resize":s.width<0?r="se-resize":s.height<0&&(r="nw-resize")),null!=r&&(s.width<0&&s.height<0?(s.x+=s.width,s.width=-s.width,s.y+=s.height,s.height=-s.height,this.drag_code=r):s.width<0?(s.x+=s.width,s.width=-s.width,this.drag_code=r):s.height<0&&(s.y+=s.height,s.height=-s.height,this.drag_code=r)),0==s.width&&(s.width=1),0==s.height&&(s.height=1),this.renderROI(s,!1,!0),1<this.rois.length&&s==this.rois[this.icroi]&&this.renderROI(this.rois[0],!1,!1)},FITS.prototype.clearLayer=function(e){e.clearRect(0,0,this.width,this.height)},FITS.prototype.getPixelAtFITS=function(e){return null!=e&&0<=(e=this.FITS2Image(e)).x&&e.x<this.width&&0<=e.y&&e.y<this.height?this.image[e.y*this.width+e.x]:0},FITS.prototype.displayHistogram=function(e,t){var i=t.getContext("2d"),s=t.width,r=t.height,t=e.stats,a=t.histo,n=Math.log(t.histomax);if(noSmoothing(i),i.setTransform(1,0,0,1,0,0),i.translate(.5,.5),i.fillStyle="#888",i.fillRect(0,0,s,r),s>a.length){i.fillStyle=e.color,i.beginPath(),i.moveTo(0,r-1);for(var o=0;o<a.length;o++){var h=Math.floor(s*o/a.length),d=1<a[o]?Math.floor(r*(1-Math.log(a[o])/n)):r-1;i.lineTo(h,d)}}else{i.fillStyle=e.color,i.beginPath(),i.moveTo(0,r-1);for(h=0;h<s;h++){d=1<a[o=Math.floor(h*a.length/s)]?Math.floor(r*(1-Math.log(a[o])/n)):r-1;i.lineTo(h,d)}}i.lineTo(s,r-1),i.lineTo(0,r-1),i.fill(),i.strokeStyle="black",i.beginPath(),i.moveTo(0,0),i.lineTo(0,r),i.lineTo(s,r),i.lineTo(s,0),i.lineTo(0,0),i.stroke(),i.strokeStyle="#aa44aa",i.beginPath();var l=Math.floor((s-1)*(t.median-t.min)/t.range),l=(i.moveTo(l,0),i.lineTo(l,r-1),i.stroke(),i.strokeStyle="#44aa44",i.beginPath(),Math.floor((s-1)*(t.mean-t.min)/t.range)),l=(i.moveTo(l,0),i.lineTo(l,r-1),i.stroke(),i.strokeStyle="black",i.beginPath(),Math.floor((s-1)*(e.black-t.min)/t.range)),l=(i.moveTo(l,0),i.lineTo(l,r-1),i.stroke(),i.strokeStyle="white",i.beginPath(),Math.floor((s-1)*(e.white-t.min)/t.range));i.moveTo(l,0),i.lineTo(l,r-1),i.stroke()},document.addEventListener("DOMContentLoaded",function(){const e=bootstrap.Popover.Default.allowList;e.table=[],e.tr=[],e.td=["data-bs-option"],e.th=[],e.div=[],e.tbody=[],e.thead=[],$('[data-bs-toggle="popover"]').popover();var t=bootstrap.Tooltip.Default.allowList;t.table=[],t.tr=[],t.td=["data-bs-option"],t.th=[],t.div=[],t.tbody=[],t.thead=[],$('[data-bs-toggle="tooltip"]').tooltip()});
//# sourceMappingURL=main.js.map