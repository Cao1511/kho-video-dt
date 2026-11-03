/**
 * Apps Script gan vao Google Sheet "DS mau may" – cho GitHub/Codex/Claude ghi
 * ten may, trang thai, thoi gian dang, link web, link Facebook vao bang.
 * Cach dung: Tien ich mo rong > Apps Script > dan toan bo file nay > sua dong KEY
 * > Luu > Trien khai > Trien khai moi > Ung dung web (Thuc thi: Toi, Truy cap: Bat ky ai).
 */
const KEY = 'DAT_MAT_MA_CUA_ANH_O_DAY';   // <-- doi thanh mat ma rieng (giong secret SHEET_KEY tren GitHub)

const HEADER_ROW = 2, FIRST_ROW = 3;
const NEW_COLS = ['Trạng thái', 'Thời gian đăng', 'Link web', 'Link Facebook'];
const NORM = t => String(t).normalize('NFC').trim().toLowerCase();
const LOCKED = ['STT'];                   // khong cho ghi de cot nay

const VIDEO_TAB = 'DS video';
const VIDEO_COLS = ['STT', 'Tên máy', 'Link video', 'Trạng thái', 'Thời gian đăng', 'YouTube', 'Facebook', 'TikTok', 'Bài web', 'Ghi chú', 'Bài YouTube', 'Bài Facebook', 'Bài TikTok'];

function sheet_(tab) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!tab) return ss.getSheets()[0];
  let sh = ss.getSheetByName(tab);
  if (!sh) {                                   // tu tao tab video giong kieu bang san pham
    sh = ss.insertSheet(tab);
    const src = ss.getSheets()[0], n = VIDEO_COLS.length;
    src.getRange(1, 1, 2, n).copyTo(sh.getRange(1, 1, 2, n), { formatOnly: true });
    sh.getRange(1, 1, 1, n).merge().setValue('Danh sách video đăng mạng xã hội Đức Thành');
    sh.getRange(HEADER_ROW, 1, 1, n).setValues([VIDEO_COLS]);
    [50, 260, 140, 120, 140, 130, 130, 130, 220, 260, 320, 320, 320].forEach((w, i) => sh.setColumnWidth(i + 1, w));
    sh.setFrozenRows(2);
  }
  return sh;
}

function ensureHeaders_(sh) {
  const last = Math.max(sh.getLastColumn(), 4);
  const head = sh.getRange(HEADER_ROW, 1, 1, last).getValues()[0].map(String);
  NEW_COLS.forEach(name => {
    if (head.indexOf(name) < 0) {
      const c = head.length + 1;
      sh.getRange(HEADER_ROW, 4).copyTo(sh.getRange(HEADER_ROW, c), { formatOnly: true });
      sh.getRange(HEADER_ROW, c).setValue(name);
      sh.setColumnWidth(c, name === 'Trạng thái' ? 120 : name === 'Thời gian đăng' ? 140 : 260);
      head.push(name);
    }
  });
  return head;
}

function caiDat() {               // chay tay 1 lan (tuy chon): tao cot moi
  ensureHeaders_(sheet_());
}

function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

function doPost(e) {
  let req;
  try { req = JSON.parse(e.postData.contents); } catch (err) { return out_({ ok: false, error: 'JSON loi' }); }
  if (!req || req.key !== KEY) return out_({ ok: false, error: 'sai key' });
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const sh = sheet_(req.tab);
    const head = req.tab ? sh.getRange(HEADER_ROW, 1, 1, sh.getLastColumn()).getValues()[0].map(String) : ensureHeaders_(sh);
    if (req.action === 'read') {                 // doc bang (dung cho tab video)
      const last = sh.getLastRow();
      const rows = last >= FIRST_ROW ? sh.getRange(FIRST_ROW, 1, last - FIRST_ROW + 1, head.length).getDisplayValues() : [];
      return out_({ ok: true, head: head, rows: rows.filter(r => String(r[0]).trim()) });
    }
    const n = Math.max(sh.getLastRow() - FIRST_ROW + 1, 1);
    const stts = sh.getRange(FIRST_ROW, 1, n, 1).getValues().map(r => String(r[0]).trim());
    const results = [];
    (req.updates || []).forEach(u => {
      let i = stts.indexOf(String(u.stt).trim());
      if (String(u.stt) === 'moi') {             // them dong moi, STT = so lon nhat + 1
        const nums = stts.map(Number).filter(x => x > 0);
        const next = (nums.length ? Math.max.apply(null, nums) : 0) + 1;
        const r = Math.max(sh.getLastRow() + 1, FIRST_ROW);
        sh.getRange(r, 1).setValue(next);
        stts[r - FIRST_ROW] = String(next);
        u.stt = String(next); i = r - FIRST_ROW;
      }
      if (i < 0) { results.push({ stt: u.stt, ok: false, error: 'khong thay STT' }); return; }
      const row = FIRST_ROW + i, done = [];
      Object.keys(u.fields || {}).forEach(name => {
        const c = head.map(NORM).indexOf(NORM(name));
        if (c < 0 || LOCKED.map(NORM).indexOf(NORM(name)) >= 0) return;
        const cell = sh.getRange(row, c + 1);
        if (NORM(name) === NORM('Tên máy') && String(cell.getValue()).trim() && !u.ghi_de_ten) return; // khong ghi de ten nguoi dung da dien
        const v = u.fields[name];
        if (Array.isArray(v)) {                 // nhieu link trong 1 o: [{text, url}, ...]
          const parts = v.filter(x => x && x.url);
          const text = parts.map(x => x.text || 'Xem').join('  |  ');
          const b = SpreadsheetApp.newRichTextValue().setText(text);
          let pos = 0;
          parts.forEach(x => { const t = x.text || 'Xem'; b.setLinkUrl(pos, pos + t.length, String(x.url)); pos += t.length + 5; });
          cell.setRichTextValue(b.build());
        } else if (/^https?:\/\//.test(String(v))) {
          const label = { 'link facebook': 'Xem Facebook', 'facebook': 'Xem Facebook', 'link web': 'Xem bài web', 'bài web': 'Xem bài web', 'youtube': 'Xem YouTube', 'tiktok': 'Xem TikTok', 'link video': 'Xem video' }[NORM(name)] || 'Xem';
          cell.setRichTextValue(SpreadsheetApp.newRichTextValue().setText(label).setLinkUrl(String(v)).build());
        } else cell.setValue(v);
        done.push(name);
      });
      results.push({ stt: u.stt, ok: true, row: row, ghi: done });
    });
    return out_({ ok: true, results: results });
  } finally { lock.releaseLock(); }
}
