import re
import os
import subprocess

UNESCAPED_QUOTES_RE = re.compile(r'([^\\]("|\'))')
PROPOSED_FORMATS = {
    'png' : set(['svg', 'gif', 'png', 'bmp', 'pnm', 'pdf'])
}

class ExecutionError(Exception):
    """ Raised if a ImageMagick command returns an exit code other than 0. """
    def __init__(self, commandline, process):
        Exception.__init__( self,
            '%r exited with code %d (command line was %r)' %
                (commandline[0], process.returncode, ' '.join(commandline))
        )

def _normalize_extension(ext):
    return str(ext).lstrip('.').lower()

def _recommend_thumbnail_format(image_format):
    image_format = _normalize_extension(image_format)
    for recommended_format, source_formats in PROPOSED_FORMATS.iteritems():
        if image_format in source_formats:
            return recommended_format
    # fallback to jpg if no better solution could be found
    return 'jpg'

def _run_cmd(*cmdline, **kwargs):
    kwargs.setdefault('stderr', subprocess.PIPE)
    proc = subprocess.Popen(cmdline, **kwargs)
    if proc.wait() != 0:
        print proc.stderr.read()
        raise ExecutionError(cmdline, proc)

    return proc

def generate_thumbnail(original_filename, result_filename, dimensions):
    _run_cmd('convert', '-thumbnail', dimensions,
             original_filename, result_filename)

def add_caption(original_filename, result_filename, dimensions, caption):
    if UNESCAPED_QUOTES_RE.search(caption['text']):
        raise ValueError("No unescaped quotes in caption['text'] plz")
    _run_cmd(
        'convert',
        '-background', caption.get('background', '#0007'),
        '-gravity',    caption.get('position', 'South'),
        '-fill',       caption.get('text-color', 'white'),
        '-size', dimensions,
        'caption:%s' % caption['text'],
        result_filename,
        '+swap', '-gravity', 'South',
        '-composite', result_filename
    )

def _fmt_dim(width, height, keep_ratio=False):
    return '%dx%d%s' % (width, height, keep_ratio and '!' or '')

def get_dimensions(image):
    stdout = _run_cmd('identify', '-format', '%w %h', image,
                      stdout=subprocess.PIPE).stdout.read()
    return map(int, stdout.split())

def thumbnail(original_filename, result_filename, width, height,
              keep_ratio=True, caption=None):
    result_filename += _recommend_thumbnail_format(
        os.path.splitext(original_filename)[1]
    )

    generate_thumbnail(original_filename, result_filename,
                       _fmt_dim(width, height, keep_ratio))

    if caption is not None:
        width, height = caption.get('width'), caption.get('height', 13)
        if width is None:
            width = get_dimensions(result_filename)[0]
        dim = _fmt_dim(width, height)
        add_caption(original_filename, result_filename, dim, caption)

    return result_filename
