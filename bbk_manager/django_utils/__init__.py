from django.conf import settings
from django.db.models import Q
from django.template.defaulttags import URLNode
from django.utils import translation
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from jinja2 import FileSystemLoader, Environment
from jinja2.filters import contextfilter
from django.db.models import Avg, Max, Min, Count

template_dirs = getattr(settings,'TEMPLATE_DIRS')
default_mimetype = getattr(settings, 'DEFAULT_CONTENT_TYPE')
env = Environment(loader=FileSystemLoader(template_dirs))

def render_to_response(filename, context={},mimetype=default_mimetype):
    template = env.get_template(filename)
    return HttpResponse(template.render(**context),mimetype=mimetype)

class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303

def print_debug():
    import traceback
    import sys
    et, ev, tb = sys.exc_info()
    while tb:
        co = tb.tb_frame.f_code
        print "Filename = " + str(co.co_filename)
        print "Error Line # = " + str(traceback.tb_lineno(tb))
        tb = tb.tb_next
    print "et = ", et
    print "ev = ",  ev

def url(view_name, *args, **kwargs):
    from django.core.urlresolvers import reverse, NoReverseMatch
    try:
        return reverse(view_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        try:
            project_name = settings.SETTINGS_MODULE.split('.')[0]
            return reverse(project_name + '.' + view_name,
                           args=args, kwargs=kwargs)
        except NoReverseMatch:
            return ''

def escape_quotes(text):
    if text==None:
        return ""
    return str(text).replace('\\','\\\\').replace('"','\\"').replace('\n', '\\n')

def escape_single_quotes(text):
    if text==None:
        return ""
    return str(text).replace('\\','\\\\').replace("'","\\'").replace('\n', '\\n')

def escape_newline(text):
    ret = str(text).replace('\n', '\\n')
    ret = ret.replace('\r','')
    return ret

def escape_by_type(value):
    if value is None:
        return 'null'
    if type(value) == type(1) or type(value)==type(1.1):
        return value
    return '"' + escape_quotes(value) + '"'

def to_csv(matrix, height=0, width=0, value_word='value'):
    """Makes a CSV string out of a dictionary or list"""
    from cStringIO import StringIO
    s = StringIO()
    if type(matrix) == type(dict()):
        for y in xrange(height+1):
            row = matrix.get(y)
            if not row:
              s.write("\n")
              continue
            for x in xrange(1,width+1):
                cell = row.get(x)
                value = ""
                if cell:
                    if type(cell) == type({}):
                        if cell[value_word] is None:
                            value = ""
                        else:
                            value = cell[value_word]
                    else:
                        value = str(cell)
                s.write(csvify(value) + ",")
                pass
            s.write("\n")
            pass
        pass
    if type(matrix) == type([]):
        for row in matrix:
            for cell in row:
                s.write(csvify(cell)+',')
            s.write('\n')
            pass
        pass
    return s.getvalue()

def csvify(text):
    text = str(text)
    new_text = text.replace('"','""')
    if len(new_text)<>len(text) or text.find('\n')>-1 or text.find(',')>-1:
        new_text = '"' + new_text + '"'
    return new_text

def parse_datetime(timestr, parserinfo=None, **kwargs):
    return date_parser().parse(timestr, **kwargs)

def urlencode(text):
    import urllib
    return urllib.quote(text)

env.filters['url'] = url
env.filters['urlencode'] = urlencode
env.filters['q'] = escape_quotes
env.filters['sq'] = escape_single_quotes
env.filters['n'] = escape_newline
