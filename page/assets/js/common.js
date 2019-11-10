function addLoadEvent(func) {
    var oldonload = window.onload;
        if(typeof window.onload != 'function') {
            window.onload = func;
        } else {
            window.onload = function() {
                oldonload();
                func();
        }
    }
}
function loadToken(){
    try {
        return [$.cookie("name"), $.cookie("uuid"), $.cookie("access"), $.cookie("client")]
    } catch(e) {
        return [undefined, undefined, undefined, undefined]
    }
}