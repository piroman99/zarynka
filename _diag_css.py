# -*- coding: utf-8 -*-
"""Что реально в CSS: есть ли правило .cr-roll.run и @keyframes crUp."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

b = Browser(400, 300)
try:
    b.navigate('file://' + os.path.join(HERE, 'vn2', 'index.html'), wait=1.5)
    expr = """
(function(){
  var out={rules:[], kf:null, total:0, sheets:0};
  for (var i=0;i<document.styleSheets.length;i++){
    var sh=document.styleSheets[i]; var rs;
    try{rs=sh.cssRules}catch(e){continue}
    out.sheets++;
    for (var j=0;j<rs.length;j++){
      var r=rs[j]; out.total++;
      var t=r.cssText||'';
      if (/cr-roll|crUp/.test(t)) out.rules.push(t.slice(0,160));
      if (r.type===7 && r.name && r.name.indexOf('crUp')>=0) out.kf='crUp found';
    }
  }
  return JSON.stringify(out);
})()
"""
    print(b.js(expr))
finally:
    b.close()
