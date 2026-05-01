/**
 * ============================================================
 *  PHI Integration Design — Shared Navbar Component
 *  แก้ไฟล์นี้ที่เดียว อัปเดตทุกหน้าอัตโนมัติ
 * ============================================================
 *
 *  วิธีใช้ในแต่ละหน้า:
 *  1) วางแท็กนี้ใน <body>:   <div id="phi-navbar"></div>
 *  2) โหลด script ก่อน </body>:
 *       root     → <script src="navbar.js" data-depth="0"></script>
 *       subfolder → <script src="../navbar.js" data-depth="1"></script>
 *  3) ปุ่มล้างการค้นหา: onclick="phiClearSearch()"
 * ============================================================
 */
(function () {
  var scriptEl = document.currentScript || document.querySelector('script[src*="navbar.js"]');
  var depth = parseInt((scriptEl && scriptEl.dataset.depth) || '1', 10);
  var root  = depth === 0 ? './' : '../'.repeat(depth);

  /* ══ CSS ══ */
  var style = document.createElement('style');
  style.textContent = [
    ':root{--phi-or:#f5620a;--phi-ord:#c44600;--phi-orl:#ff8c42;--phi-oglow:rgba(245,98,10,0.18);',
    '--phi-bk:#0d0d0d;--phi-bk2:#161616;--phi-bk3:#1e1e1e;--phi-bk4:#2a2a2a;',
    '--phi-ch:#333;--phi-g3:#888;--phi-tx:#e8e8e8;--phi-mu:#aaa;--phi-wh:#ffffff;}',

    /* header */
    '#phi-navbar header{background:var(--phi-bk2);border-bottom:2px solid var(--phi-or);box-shadow:0 4px 20px rgba(0,0,0,.6);}',
    '#phi-navbar .pni{max-width:1280px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:20px;}',
    '#phi-navbar .plo{display:flex;align-items:center;gap:12px;flex-shrink:0;}',
    '#phi-navbar .plo img{width:52px;height:52px;object-fit:contain;}',
    '#phi-navbar .plt .line1{font-family:"Bebas Neue",sans-serif;font-size:22px;letter-spacing:2px;color:var(--phi-wh);line-height:1;}',
    '#phi-navbar .plt .line1 span{color:var(--phi-or);}',

    /* search bar — overflow:visible ทำให้ dropdown โผล่ได้ */
    '#phi-navbar .psb{flex:1;display:flex;border:1.5px solid var(--phi-ch);border-radius:4px;background:var(--phi-bk3);transition:border-color .2s;position:relative;overflow:visible;}',
    '#phi-navbar .psb:focus-within{border-color:var(--phi-or);box-shadow:0 0 0 3px var(--phi-oglow);}',
    '#phi-navbar .psb input{flex:1;padding:10px 16px;border:none;outline:none;font-size:14px;font-family:inherit;background:transparent;color:var(--phi-tx);border-radius:4px 0 0 4px;}',
    '#phi-navbar .psb input::placeholder{color:var(--phi-g3);}',
    '#phi-navbar .psb button{background:var(--phi-or);border:none;padding:0 20px;cursor:pointer;color:#fff;font-size:18px;transition:background .2s;border-radius:0 4px 4px 0;flex-shrink:0;}',
    '#phi-navbar .psb button:hover{background:var(--phi-ord);}',

    /* search dropdown */
    '#phi-navbar .pdd{display:none;position:absolute;top:calc(100% + 4px);left:0;right:0;background:var(--phi-bk2);border:1px solid var(--phi-bk4);border-top:2px solid var(--phi-or);border-radius:0 0 6px 6px;z-index:9999;box-shadow:0 12px 40px rgba(0,0,0,.9);max-height:380px;overflow-y:auto;}',
    '#phi-navbar .pdd.show{display:block;}',
    '#phi-navbar .pdc{padding:6px 16px;font-size:11px;color:var(--phi-g3);background:var(--phi-bk3);border-bottom:1px solid var(--phi-bk4);}',
    '#phi-navbar .pdc span{color:var(--phi-orl);font-weight:700;}',
    '#phi-navbar .pdi{display:flex;align-items:center;gap:12px;padding:10px 16px;cursor:pointer;border-bottom:1px solid var(--phi-bk4);transition:background .15s;}',
    '#phi-navbar .pdi:last-child{border-bottom:none;}',
    '#phi-navbar .pdi:hover{background:var(--phi-bk4);}',
    '#phi-navbar .pdt{width:36px;height:36px;background:var(--phi-bk3);border:1px solid var(--phi-bk4);border-radius:4px;display:flex;align-items:center;justify-content:center;flex-shrink:0;overflow:hidden;font-size:18px;}',
    '#phi-navbar .pdt img{width:100%;height:100%;object-fit:contain;}',
    '#phi-navbar .pdin{flex:1;min-width:0;}',
    '#phi-navbar .pdn{font-size:13px;font-weight:600;color:var(--phi-tx);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}',
    '#phi-navbar .pdn mark{background:transparent;color:var(--phi-orl);font-weight:700;}',
    '#phi-navbar .pdcat{font-size:11px;color:var(--phi-g3);margin-top:2px;}',
    '#phi-navbar .pdarr{color:var(--phi-g3);font-size:14px;flex-shrink:0;}',
    '#phi-navbar .pdnone{padding:20px;text-align:center;color:var(--phi-g3);font-size:13px;}',

    /* nav */
    '#phi-navbar nav{background:var(--phi-bk3);border-bottom:1px solid var(--phi-bk4);}',
    '#phi-navbar .pnav{max-width:1280px;margin:0 auto;padding:0 20px;display:flex;}',
    '#phi-navbar .pmenu{position:relative;}',
    '#phi-navbar .pmbtn{display:flex;align-items:center;gap:8px;padding:12px 20px;background:var(--phi-or);color:#fff;font-size:13px;font-weight:700;cursor:pointer;border:none;font-family:inherit;letter-spacing:.5px;transition:background .2s;white-space:nowrap;}',
    '#phi-navbar .pmbtn:hover{background:var(--phi-ord);}',
    '#phi-navbar .pmarr{font-size:10px;transition:transform .2s;}',
    '#phi-navbar .pmenu:hover .pmarr{transform:rotate(180deg);}',
    '#phi-navbar .pmdd{display:none;position:absolute;top:100%;left:0;background:var(--phi-bk2);border:1px solid var(--phi-bk4);border-top:2px solid var(--phi-or);border-radius:0 0 6px 6px;width:290px;z-index:300;box-shadow:0 12px 40px rgba(0,0,0,.7);overflow:hidden;}',
    '#phi-navbar .pmenu:hover .pmdd{display:block;}',
    '#phi-navbar .pmitem{display:flex;align-items:center;gap:12px;padding:13px 18px;color:var(--phi-tx);text-decoration:none;border-bottom:1px solid var(--phi-bk4);transition:all .15s;font-size:13px;font-weight:500;}',
    '#phi-navbar .pmitem:last-child{border-bottom:none;}',
    '#phi-navbar .pmitem:hover{background:var(--phi-bk4);color:var(--phi-orl);padding-left:24px;}',
    '#phi-navbar .pnum{width:22px;height:22px;background:var(--phi-oglow);border:1px solid var(--phi-or);border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:var(--phi-orl);flex-shrink:0;}',
    '#phi-navbar .pmitem:hover .pnum{background:var(--phi-or);color:#fff;}',
    '#phi-navbar .pico{font-size:18px;flex-shrink:0;}',
    '#phi-navbar .pmitem span:nth-child(3){flex:1;}',
    '#phi-navbar .pmarrow{margin-left:auto;color:var(--phi-g3);font-size:12px;}'
  ].join('');
  document.head.appendChild(style);

  /* ══ NAV DATA — แก้ที่นี่ที่เดียว ══ */
  var menus = [
    { label:'☰ &nbsp;PHI-Catalog', items:[
      {n:'1',i:'⚙️',t:'Automation Components',  h:'automation-components/automation-components.html'},
      {n:'2',i:'💨',t:'Pneumatic System',         h:'pneumatic-system/pneumatic-system.html'},
      {n:'3',i:'📦',t:'Module STD',               h:'module-std/module-std.html'},
      {n:'4',i:'🔩',t:'AL Profile & Accessories', h:'al-profile-accessories/al-profile-accessories.html'},
      {n:'5',i:'⚡',t:'Electrical Components',    h:'electrical-components/electrical-components.html'},
    ]},
    { label:'🧮 &nbsp;Calculator Design', items:[
      {n:'1',i:'➕',t:'Calculator Motor',  h:'calculator-design/item1.html'},
      {n:'2',i:'➖',t:'Calculator IAI',    h:'calculator-design/item2.html'},
    ]},
    { label:'🏢 &nbsp;Design Tools', items:[
      {n:'1',i:'📋',t:'BOM List', h:'BOM List.html'},
      {n:'2',i:'📊',t:'Solenoid Valve & Manifold Selector', h:'Solenoid Valve & Manifold Selector.html'},
      {n:'3',i:'📈',t:'Product-Page-Generator', h:'Product_Page_Generator.html'},
      {n:'3',i:'📈',t:'PHI_Selector', h:'PHI_Selector.html'},
    ]},
    { label:'📂 &nbsp;PHI INTEGRATION', items:[
      {n:'1',i:'🔵',t:'PHI Stock Inventory Store', h:'https://docs.google.com/spreadsheets/d/1BzKfYmTSlQxDh1qpAPqkQGsLG8rQy3dNygvmt0vWO-Y/edit?gid=984590829#gid=984590829'},
      {n:'2',i:'🟢',t:'PHI Stock Inventory Store', h:'https://docs.google.com/spreadsheets/d/1BzKfYmTSlQxDh1qpAPqkQGsLG8rQy3dNygvmt0vWO-Y/edit?gid=984590829#gid=984590829'},
      {n:'3',i:'🟡',t:'STD Material size', h:'https://docs.google.com/spreadsheets/d/1NUpXNs3CQuuDLo_AAkIt8p1CNHXkNP8ydmDJpe5ikPo/edit?gid=181278085#gid=181278085'},
    ]},
    { label:'📁 &nbsp;Data2', items:[
      {n:'1',i:'🔷',t:'Data2 Item 1', h:'data2/item1.html'},
      {n:'2',i:'🔶',t:'Data2 Item 2', h:'data2/item2.html'},
      {n:'3',i:'🔸',t:'Data2 Item 3', h:'data2/item3.html'},
      {n:'4',i:'🔹',t:'Data2 Item 4', h:'data2/item4.html'},
      {n:'5',i:'💠',t:'Data2 Item 5', h:'data2/item5.html'},
      {n:'6',i:'🔘',t:'Data2 Item 6', h:'data2/item6.html'},
    ]},
  ];

  /* ══ BUILD HTML ══ */
  var navHtml = menus.map(function(m){
    return '<div class="pmenu"><button class="pmbtn">' + m.label +
      ' <span class="pmarr">▼</span></button><div class="pmdd">' +
      m.items.map(function(it){
        var href = (it.h.startsWith('http://') || it.h.startsWith('https://') || it.h.startsWith('//')) ? it.h : root + it.h;
        return '<a class="pmitem" href="' + href + '"' + (it.h.startsWith('http') ? ' target="_blank"' : '') + '>' +
          '<span class="pnum">' + it.n + '</span>' +
          '<span class="pico">' + it.i + '</span>' +
          '<span>' + it.t + '</span>' +
          '<span class="pmarrow">›</span></a>';
      }).join('') + '</div></div>';
  }).join('');

  var container = document.getElementById('phi-navbar');
  if (!container) { console.warn('[navbar.js] ไม่พบ #phi-navbar'); return; }

  container.innerHTML =
    '<header><div class="pni">' +
      '<div class="plo"><img src="' + root + 'img/PHI.png" alt="PHI Logo">' +
        '<div class="plt"><div class="line1"><span>PHI</span> INTEGRATION DESIGN</div></div>' +
      '</div>' +
      '<div class="psb" id="phiSB">' +
        '<input type="text" id="phiInp" placeholder="ค้นหาสินค้า, รหัสสินค้า..." autocomplete="off">' +
        '<button id="phiBtn">🔍</button>' +
        '<div class="pdd" id="phiDd"></div>' +
      '</div>' +
    '</div></header>' +
    '<nav><div class="pnav">' + navHtml + '</div></nav>';

  /* ══ SEARCH ══ */
  var inp = document.getElementById('phiInp');
  var dd  = document.getElementById('phiDd');
  var btn = document.getElementById('phiBtn');
  var _hits = [];

  function getCards() {
    return Array.from(document.querySelectorAll('.product-card')).map(function(card){
      var nameEl = card.querySelector('.product-name');
      var name   = card.dataset.name || (nameEl ? nameEl.textContent.trim() : '');
      var cat    = card.dataset.cat  ||
        (card.closest('.section') && card.closest('.section').querySelector('.section-label')
          ? card.closest('.section').querySelector('.section-label').textContent.trim() : '');
      var anchor = card.tagName === 'A' ? card : card.closest('a');
      var href   = anchor ? anchor.getAttribute('href') : null;
      var imgEl  = card.querySelector('img');
      var emoji  = !imgEl ? ((card.querySelector('.product-img') ? card.querySelector('.product-img').textContent.trim() : '') || '📦') : null;
      return {el:card, name:name, cat:cat, href:href, imgEl:imgEl, emoji:emoji};
    });
  }

  function hl(text, q) {
    return text.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi'),'<mark>$1</mark>');
  }

  function renderDd(q) {
    var cards = getCards();
    _hits = cards.filter(function(c){
      return c.name.toLowerCase().indexOf(q.toLowerCase()) >= 0 ||
             c.cat.toLowerCase().indexOf(q.toLowerCase()) >= 0;
    });
    if (_hits.length === 0) {
      dd.innerHTML = '<div class="pdnone">🔍 ไม่พบสินค้าที่ตรงกับ "<strong>'+q+'</strong>"</div>';
    } else {
      dd.innerHTML = '<div class="pdc">พบ <span>'+_hits.length+'</span> รายการ</div>' +
        _hits.map(function(item, idx){
          var thumb = item.imgEl ? '<img src="'+item.imgEl.src+'">' : '<span>'+item.emoji+'</span>';
          return '<div class="pdi" data-idx="'+idx+'">' +
            '<div class="pdt">'+thumb+'</div>' +
            '<div class="pdin"><div class="pdn">'+hl(item.name,q)+'</div>' +
            '<div class="pdcat">'+item.cat+'</div></div>' +
            '<div class="pdarr">›</div></div>';
        }).join('');
      dd.querySelectorAll('.pdi').forEach(function(el){
        el.addEventListener('click', function(){
          var item = _hits[parseInt(this.dataset.idx,10)];
          dd.classList.remove('show');
          inp.value = item.name;
          if (item.href && item.href !== '' && item.href !== 'null') {
            window.location.href = item.href;
          } else {
            phiApplyFilter(item.name);
          }
        });
      });
    }
    dd.classList.add('show');
  }

  inp.addEventListener('input', function(){
    var q = this.value.trim();
    if (!q) { dd.classList.remove('show'); phiClearSearch(); return; }
    renderDd(q);
  });
  inp.addEventListener('keydown', function(e){
    if (e.key==='Enter')  { dd.classList.remove('show'); phiApplyFilter(this.value.trim()); }
    if (e.key==='Escape') { dd.classList.remove('show'); phiClearSearch(); }
  });
  btn.addEventListener('click', function(){
    var q = inp.value.trim();
    dd.classList.remove('show');
    if (!q) { phiClearSearch(); return; }
    phiApplyFilter(q);
  });
  document.addEventListener('click', function(e){
    if (!document.getElementById('phiSB').contains(e.target)) dd.classList.remove('show');
  });

  /* ══ GLOBAL — ใช้ได้จาก onclick ในทุกหน้า ══ */
  window.phiApplyFilter = function(q) {
    if (!q) return;
    var cards    = getCards();
    var sections = document.querySelectorAll('.section');
    var total    = 0;
    cards.forEach(function(item){
      var match = item.name.toLowerCase().indexOf(q.toLowerCase()) >= 0 ||
                  item.cat.toLowerCase().indexOf(q.toLowerCase()) >= 0;
      item.el.classList.toggle('search-highlight', match);
      item.el.classList.toggle('search-dim', !match);
      if (match) total++;
    });
    sections.forEach(function(sec){
      var has = Array.from(sec.querySelectorAll('.product-card'))
        .some(function(c){ return c.classList.contains('search-highlight'); });
      sec.classList.toggle('search-hidden', !has);
    });
    var bar = document.getElementById('searchActiveBar');
    if (bar) {
      bar.classList.add('show');
      var kw = document.getElementById('searchKeyword');
      var ct = document.getElementById('searchCount');
      if (kw) kw.textContent = '"'+q+'"';
      if (ct) ct.textContent = total;
    }
    var first = document.querySelector('.product-card.search-highlight');
    if (first) first.scrollIntoView({behavior:'smooth',block:'center'});
  };

  /* รองรับทั้งสองชื่อ */
  window.phiClearSearch = window.clearSearch = function() {
    document.querySelectorAll('.product-card').forEach(function(c){
      c.classList.remove('search-highlight','search-dim');
    });
    document.querySelectorAll('.section').forEach(function(s){ s.classList.remove('search-hidden'); });
    var bar = document.getElementById('searchActiveBar');
    if (bar) bar.classList.remove('show');
    inp.value = '';
    dd.classList.remove('show');
  };

})();
