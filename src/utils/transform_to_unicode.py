def transform_to_unicode(text):
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³",
        "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷",
        "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻",

        "a": "a", "b": "b", "c": "c", "d": "d",
        "e": "e", "f": "f", "g": "g", "h": "h",
        "i": "i", "j": "j", "k": "k", "l": "l",
        "m": "m", "n": "n", "o": "o", "p": "p",
        "q": "q", "r": "r", "s": "s", "t": "t",
        "u": "u", "v": "v", "w": "w", "x": "x",
        "y": "y", "z": "z",

        "A": "A", "B": "B", "C": "C", "D": "D",
        "E": "E", "F": "F", "G": "G", "H": "H",
        "I": "I", "J": "J", "K": "K", "L": "L",
        "M": "M", "N": "N", "O": "O", "P": "P",
        "Q": "Q", "R": "R", "S": "S", "T": "T",
        "U": "U", "V": "V", "W": "W", "X": "X",
        "Y": "Y", "Z": "Z",
    }

    subscript_map = {
        "0": "₀", "1": "₁", "2": "₂", "3": "₃",
        "4": "₄", "5": "₅", "6": "₆", "7": "₇",
        "8": "₈", "9": "₉", "+": "₊", "-": "₋",

        "a": "a", "b": "b", "c": "c", "d": "d",
        "e": "e", "f": "f", "g": "g", "h": "h",
        "i": "i", "j": "j", "k": "k", "l": "l",
        "m": "m", "n": "n", "o": "o", "p": "p",
        "q": "q", "r": "r", "s": "s", "t": "t",
        "u": "u", "v": "v", "w": "w", "x": "x",
        "y": "y", "z": "z",

        "A": "A", "B": "B", "C": "C", "D": "D",
        "E": "E", "F": "F", "G": "G", "H": "H",
        "I": "I", "J": "J", "K": "K", "L": "L",
        "M": "M", "N": "N", "O": "O", "P": "P",
        "Q": "Q", "R": "R", "S": "S", "T": "T",
        "U": "U", "V": "V", "W": "W", "X": "X",
        "Y": "Y", "Z": "Z",
    }

    result = ""
    i = 0
    while i < len(text):
        if text[i] in ["^", "_"]:
            is_super = text[i] == "^"
            i += 1
            if i < len(text) and text[i] == "{":
                i += 1
                mapped = ""
                while i < len(text) and text[i] != "}":
                    ch = text[i]
                    mapped += (superscript_map.get(ch) if is_super else subscript_map.get(ch, ch))
                    i += 1
                i += 1  # skip closing }
                result += mapped
            else:
                ch = text[i]
                mapped = (superscript_map.get(ch) if is_super else subscript_map.get(ch, ch))
                result += mapped
                i += 1
        else:
            result += text[i]
            i += 1
    return result
