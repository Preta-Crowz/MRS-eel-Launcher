function loadToken(){
    try {
        return [$.cookie("name"), $.cookie("uuid"), $.cookie("access"), $.cookie("client")]
    } catch(e) {
        return [undefined, undefined, undefined, undefined]
    }
}
window.onload = function() {
    data = loadToken();
    $("#username").text(data[0]);
    $("#avatar").attr("src","https://crafatar.com/avatars/"+data[1]+"?default=MHF_Steve&overlay");
}