function loadPackList(callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET" , "https://api.mysticrs.tk/list" , true);
    xhr.onreadystatechange = function() {
        if(xhr.readyState == 4 && xhr.status == 200) {
            callback(JSON.parse(xhr.responseText));
        }
    }
    xhr.send();
}

isload = false;
function refreshPackItems() {
    if (isload) {
        return;
    }
    else {
        isload = true;
    }
    
    console.log("start loading packs");
    
    loadPackList(function(j) {
        var par = document.getElementById("modpack-list-wrapper");
        while (par.firstChild) {
            par.removeChild(par.firstChild);
        }
        var lop = document.getElementById("loading-p");
        lop.style.visibility = "visible";
        
        for (i=0; i<j.length;i++) {
            pack = j[i];
        
            var dv = document.createElement("div");
            dv.classList.add("modpack-list");
        
            var im = document.createElement("img");
            im.classList.add("pack-item-img");
            im.src = pack["icon"];
            dv.appendChild(im);
        
            var pp = document.createElement("p");
            pp.classList.add("pack-item-p");
            pp.innerHTML = pack["name"];
            dv.appendChild(pp);
        
            dv.setAttribute('pack', pack["name"]);
            dv.onclick = movePackPage;
            par.appendChild(dv);
        }
        lop.style.visibility = "hidden";
        
        console.log("end loading packs");
        isload = false;
    });
}

function movePackPage(e) {
    pname = e.target.getAttribute('pack');
    if (!pname) {
        pname = e.target.parentElement.getAttribute('pack');
    }
    
    uri = 'modpackpage.html?name=' + encodeURI(pname);
    window.location.href = uri;
}

refreshPackItems();
