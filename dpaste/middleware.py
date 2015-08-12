import socket

from django.http import HttpResponseBadRequest

tor_bl = (
    '{remote_addr}.{server_port}.{server_ip}'
    '.ip-port.exitlist.torproject.org')
open_proxy_bl = ('{remote_addr}.dnsbl.proxybl.org')

rev_ip = lambda ip: '.'.join(reversed(ip.split('.'))) # pragma: no cover

response = """<html><body><h1>Access denied</h1>
<p>It appears you're requesting this page from an open proxy or
the TOR network. These networks are blocked due to numerous
statutory violation related posts in the past.</p>
<p>If you think this is wrong, <a href="https://github.com/bartTC/dpaste">file
a bug on Github please</a>.</p></body></html>"""

def in_blacklist(request, bl, ip=None): # pragma: no cover
    ip = ip or request.META['REMOTE_ADDR']
    try:
        server_ip = socket.gethostbyname(request.META['SERVER_NAME'])
    except socket.gaierror:
        return
    bl_name = bl.format(
        remote_addr=rev_ip(ip),
        server_port=request.META['SERVER_PORT'],
        server_ip=rev_ip(server_ip)
    )
    try:
        lookup = socket.gethostbyname(bl_name)
    except socket.gaierror as s:
        if s.errno == -5:
            return False
        return
    except Exception:
        return
    return lookup == '127.0.0.2'


class SuspiciousIPMiddleware(object): # pragma: no cover

    def process_request(self, request):
        def check_tor():
            if not hasattr(request, '_is_tor_exit_node'):
                request._is_tor_exit_node = in_blacklist(request, tor_bl)
            return request._is_tor_exit_node
        request.is_tor_exit_node = check_tor

        def check_open_proxy():
            if not hasattr(request, '_is_open_proxy'):
                request._is_open_proxy = in_blacklist(
                    request, open_proxy_bl)
            return request._is_open_proxy
        request.is_open_proxy = check_open_proxy

        def check_suspicious():
            return request.is_tor_exit_node() or request.is_open_proxy()

        request.is_suspicious = check_suspicious
        if request.method == 'POST' and request.is_suspicious():
            return HttpResponseBadRequest(response)
