from .base_converter import BasePhonemeConverter


class BasqueConverter(BasePhonemeConverter):

    def convert(self, s: str) -> list[str]:

        s = s.lower().replace("_", "")

        if not s:
            return []

        rules = {
            "tx": "tʃ",
            "tz": "ts",
            "ts": "ts",
            "dd": "d",
            "tt": "t",
        }

        tokens = []

        i = 0
        while i < len(s):

            if s[i:i+2] in rules:
                tokens.append(rules[s[i:i+2]])
                i += 2
                continue

            tokens.append(s[i])
            i += 1

        return tokens