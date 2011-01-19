# -*- coding: utf-8 -*-
import re

def remove_spaces(s):
    inline_tags = 'a|b|i|u|em|strong|sup|sub|tt|font|small|big'
    inlines_with_spaces = r'</(%s)>\s+<(%s)\b' % (inline_tags, inline_tags)
    s = re.sub(inlines_with_spaces, r'</\1>&#preservespace;<\2', s)
    s = re.sub(r'>\s+<', '><', s)
    # Remove spaces at the beginning of line.
    s = re.sub(r'\n\s+', '\n', s)
    s = s.replace('&#preservespace;', ' ')
    return s


class SpacelessMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = remove_spaces(response.content)
        return response
