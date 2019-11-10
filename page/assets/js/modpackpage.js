packname = "";
isWorking = false;

function init() {
    const urlParams = new URLSearchParams(window.location.search);
    packname = urlParams.get("name");
    
    document.getElementById("pack-title-p").innerHTML = packname;
    document.getElementById("patch-log-iframe").src = 
        "https://api.mysticrs.tk/update?name=" + encodeURI(packname);
}

function backClick() {
    if (isWorking) return;
    window.location.href = "modpacklist.html";
}

function startClick() {
    if (isWorking) return;
    launch(packname, false);
}

function updateClick() {
    if (isWorking) return;
    launch(packname, true);
}

function removeClick() {
    if (isWorking) return;
    removePack(packname);
}

function folderClick() {
    openPack(packname);
}

function showStatus(v) {
    cn = "";
    if (v)
        cn = "patch-status-wrapper-visible";
    else
        cn = "patch-status-wrapper-hidden";

    wrapper = document.getElementById("patch-status-wrapper");
    wrapper.className = "";
    wrapper.classList.add(cn);
}

function changeTitle(msg) {
    document.getElementById("patch-title-p").innerHTML = msg;
}

function changeFile(msg) {
    document.getElementById("patch-filename-p").innerHTML = msg;
}

function changeProgress(total, count) {
    var pcg = Math.floor(count/total*100);
    var npc = Number(pcg);
    
    var pb = document.getElementById('patch-progress-bar');
    pb.setAttribute('aria-valuenow',pcg);
    pb.setAttribute('style','width:'+npc+'%');
    pb.innerHTML = npc + '%';
}

init();
showStatus(true);
changeProgress(1000, 900);