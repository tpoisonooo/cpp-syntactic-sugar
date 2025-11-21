jstr = """
{
  "question": "Develop a C++ regular expression to identify Markdown elements like headers, italics, bold, links, blockquotes, and lists, then test it on the provided text.",
  "answer": "Use this regex pattern in C++: `(^#{1,6} .*)|(\*[^*]+\*|_[^_]+_)|(\*\*[^*]+\*\*|__[^_]+__)|(\[.+?\]\(.+?\))|(^>.*)|(^- .+)` with `std::regex::multiline`. Test
it on the sample text using `std::regex_search` in a loop to extract all matches. The pattern captures headers, italic (`*...*`), bold (`**...**`), links, blockquotes (`>..
.`), and list items (`- ...`). The code outputs each matched element."
}

"""

import json
print(json.loads(jstr, ensure_ascii=False))