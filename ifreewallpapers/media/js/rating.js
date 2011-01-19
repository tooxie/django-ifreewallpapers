function datosServidor() {
};
datosServidor.prototype.iniciar = function() {
    try {
        // Mozilla / Safari
        this._xh = new XMLHttpRequest();
    } catch (e) {
        // Explorer
        var _ieModelos = new Array(
        'MSXML2.XMLHTTP.5.0',
        'MSXML2.XMLHTTP.4.0',
        'MSXML2.XMLHTTP.3.0',
        'MSXML2.XMLHTTP',
        'Microsoft.XMLHTTP'
        );
        var success = false;
        for (var i=0;i < _ieModelos.length && !success; i++) {
            try {
                this._xh = new ActiveXObject(_ieModelos[i]);
                success = true;
            } catch (e) {
                // Implementar manejo de excepciones
            }
        }
        if ( !success ) {
            // Implementar manejo de excepciones, mientras alerta.
            return false;
        }
        return true;
    }
}

datosServidor.prototype.ocupado = function() {
    estadoActual = this._xh.readyState;
    return (estadoActual && (estadoActual < 4));
}

datosServidor.prototype.procesa = function() {
    if (this._xh.readyState == 4 && this._xh.status == 200) {
        this.procesado = true;
    }
}

datosServidor.prototype.enviar = function(urlget,datos) {
    if (!this._xh) {
        this.iniciar();
    }
    if (!this.ocupado()) {
        this._xh.open("GET",urlget,false);
        this._xh.send(datos);
        if (this._xh.readyState == 4 && this._xh.status == 200) {
            return this._xh.responseText;
        }
        
    }
    return false;
}


// Este es un acceso rapido, le paso la url y el div a cambiar
function _gr(reqseccion,divcont) {
    remotos = new datosServidor;
    nt = remotos.enviar(reqseccion,"");
    document.getElementById(divcont).innerHTML = nt;
}

function addView(productID) {
    remotos = new datosServidor;
    nt = remotos.enviar('update.php?view=1&productID='+productID);
}

function addComment(productID) {
    text = document.getElementById('commenttext').value; 
    remotos = new datosServidor;
    nt = remotos.enviar('update.php?comment='+text+'&productID='+productID);
    document.getElementById('newcomment').innerHTML = nt; 
    document.getElementById('commentform').style.display  = 'none'; 
}

function rateProduct(rating,productID)  {
    remotos = new datosServidor;
    nt = remotos.enviar('update.php?rating='+rating+'&productID='+productID);
    rating = (rating * 25) - 6;
    document.getElementById('current-rating').style.width = rating+'px';
    document.getElementById('ratelinks').style.display = 'none';
    document.getElementById('ratingtext').innerHTML = 'Thank you for your vote!';
}

var offsetfromcursorX=12 //Customize x offset of tooltip
var offsetfromcursorY=10 //Customize y offset of tooltip

var offsetdivfrompointerX=10 //Customize x offset of tooltip DIV relative to pointer image
var offsetdivfrompointerY=14 //Customize y offset of tooltip DIV relative to pointer image. Tip: Set it to (height_of_pointer_image-1).

// document.write('<div id="dhtmltooltip" ></div>') //write out tooltip DIV
// document.write('<img id="dhtmlpointer" style="visibility: hidden" src="images/arrow2.gif">') //write out pointer image

var ie=document.all
var ns6=document.getElementById && !document.all
var enabletip=false
if (ie||ns6)
var tipobj=document.all? document.all["dhtmltooltip"] : document.getElementById? document.getElementById("dhtmltooltip") : ""

var pointerobj=document.all? document.all["dhtmlpointer"] : document.getElementById? document.getElementById("dhtmlpointer") : ""

function ietruebody(){
    return (document.compatMode && document.compatMode!="BackCompat")? document.documentElement : document.body
}


function sTD(term){
    if (ns6||ie){
        if (typeof thewidth!="undefined") tipobj.style.width=thewidth+"px"
        if (typeof thecolor!="undefined" && thecolor!="") tipobj.style.backgroundColor=thecolor
        remotos = new datosServidor;
        nt = remotos.enviar('update.php?term='+term);
        tipobj.innerHTML="<strong>"+term+"</strong>: "+nt;
        enabletip=true
        return false
    }
}

function positiontip(e){
    if (enabletip){
        var nondefaultpos=false
        var curX=(ns6)?e.pageX : event.clientX+ietruebody().scrollLeft;
        var curY=(ns6)?e.pageY : event.clientY+ietruebody().scrollTop;
        //Find out how close the mouse is to the corner of the window
        var winwidth=ie&&!window.opera? ietruebody().clientWidth : window.innerWidth-20
        var winheight=ie&&!window.opera? ietruebody().clientHeight : window.innerHeight-20

        var rightedge=ie&&!window.opera? winwidth-event.clientX-offsetfromcursorX : winwidth-e.clientX-offsetfromcursorX
        var bottomedge=ie&&!window.opera? winheight-event.clientY-offsetfromcursorY : winheight-e.clientY-offsetfromcursorY

        var leftedge=(offsetfromcursorX<0)? offsetfromcursorX*(-1) : -1000

        //if the horizontal distance isn't enough to accomodate the width of the context menu
        if (rightedge<tipobj.offsetWidth){
            //move the horizontal position of the menu to the left by it's width
            tipobj.style.left=curX-tipobj.offsetWidth+"px"
            nondefaultpos=true
        }
        else if (curX<leftedge)
            tipobj.style.left="5px"
        else{
            //position the horizontal position of the menu where the mouse is positioned
            tipobj.style.left=curX+offsetfromcursorX-offsetdivfrompointerX+"px"
            pointerobj.style.left=curX+offsetfromcursorX+"px"
        }

        //same concept with the vertical position
        if (bottomedge<tipobj.offsetHeight){
            tipobj.style.top=curY-tipobj.offsetHeight-offsetfromcursorY+"px"
            nondefaultpos=true
        }
        else{
            tipobj.style.top=curY+offsetfromcursorY+offsetdivfrompointerY+"px"
            pointerobj.style.top=curY+offsetfromcursorY+"px"
        }
        tipobj.style.visibility="visible"
        if (!nondefaultpos)
            pointerobj.style.visibility="visible"
        else
            pointerobj.style.visibility="hidden"
    }
}

function hTD(){
    if (ns6||ie){
        enabletip=false
        tipobj.style.visibility="hidden"
        pointerobj.style.visibility="hidden"
        tipobj.style.left="-1000px"
        tipobj.style.backgroundColor=''
        tipobj.style.width=''
    }
}

$(document).ready(function(){
    var current = document.getElementById('current-rating');
    rating = (current.innerHTML * 25) - 6;
    current.style.width = rating + 'px';
})
