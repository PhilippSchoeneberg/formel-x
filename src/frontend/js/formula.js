// Turns the LaTeX-like formula notation into Unicode: H_2O -> H₂O, SO_4^{2-} -> SO₄²⁻.

const SUPERSCRIPT = {
  "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
  "+": "⁺", "-": "⁻",
};

const SUBSCRIPT = {
  "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
  "+": "₊", "-": "₋",
};

export function formulaToUnicode(text) {
  if (!text) return "";
  let result = "";
  let i = 0;
  while (i < text.length) {
    const char = text[i];
    if (char !== "^" && char !== "_") {
      result += char;
      i += 1;
      continue;
    }
    const map = char === "^" ? SUPERSCRIPT : SUBSCRIPT;
    i += 1;
    if (text[i] === "{") {
      i += 1;
      while (i < text.length && text[i] !== "}") {
        result += map[text[i]] ?? text[i];
        i += 1;
      }
      i += 1; // skip the closing }
    } else if (i < text.length) {
      result += map[text[i]] ?? text[i];
      i += 1;
    }
  }
  return result;
}
