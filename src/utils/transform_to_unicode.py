def transform_to_unicode(text):
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³",
        "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷",
        "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻"
    }
    subscript_map = {
        "0": "₀", "1": "₁", "2": "₂", "3": "₃",
        "4": "₄", "5": "₅", "6": "₆", "7": "₇",
        "8": "₈", "9": "₉", "+": "₊", "-": "₋"
    }

    result = ""
    i = 0
    while i < len(text):
        if text[i] == "_":
            i += 1
            if i < len(text) and text[i] in subscript_map:
                result += subscript_map[text[i]]
            else:
                result += "_"
        elif text[i] == "^":
            i += 1
            if i < len(text) and text[i] in superscript_map:
                result += superscript_map[text[i]]
            else:
                result += "^"
        else:
            result += text[i]
        i += 1
    return result
