// Чинит mojibake (двойную UTF-8 -> Latin-1 кодировку) только в "битых"
// участках — последовательностях байтов 0x80-0xFF. Корректные ASCII и
// настоящие многобайтовые символы (эмодзи, кириллица) не трогаются, поэтому
// смешанный текст обрабатывается правильно.
function fixMojibake(text) {
  let result = "";
  let run = [];

  const flush = () => {
    if (run.length === 0) return;
    const bytes = new Uint8Array(run);
    try {
      result += new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    } catch {
      // не валидный UTF-8 — возвращаем исходные символы как были
      result += run.map((b) => String.fromCharCode(b)).join("");
    }
    run = [];
  };

  for (const ch of text) {
    const code = ch.charCodeAt(0);
    // высокий диапазон Latin-1 (0x80-0xFF) — кандидат на mojibake-байт
    if (code >= 0x80 && code <= 0xff) {
      run.push(code);
    } else {
      flush();
      result += ch;
    }
  }
  flush();
  return result;
}

// Убирает HTML-теги, декодирует сущности, чинит кодировку, сжимает пробелы.
export function cleanDescription(raw) {
  if (!raw) return "";
  const text =
    new DOMParser().parseFromString(raw, "text/html").body.textContent || "";
  return fixMojibake(text).replace(/\s+/g, " ").trim();
}
