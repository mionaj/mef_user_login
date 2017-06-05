function AjaxZahtev(options, callback) {
  var req = new XMLHttpRequest();
  req.open(options.metod, options.putanja, true);
  req.addEventListener("load", function() {
    if (req.status < 400) {
 		  callback(req.responseText);
    }
    else {
 		  callback(new Error("Request failed: " + req.statusText));
    }
  });
  req.addEventListener("error", function() {
    callback(new Error("Network error"));
  });
  req.send(options.sadrzaj || null);
}

function PosaljiAjaxZahtev(){
  var options = {}
  options.metod = document.getElementById("metod").value
  options.putanja  = document.getElementById("putanja").value
  options.sadrzaj = document.getElementById("sadrzaj").value
  AjaxZahtev(options, ProcesirajOdgovor)
}

function ProcesirajOdgovor(odgovor){
  document.getElementById("odgovor").innerHTML = "<h3>Odgovor servera</h3><pre>"+odgovor+"</pre>"
}
