# Offline model: no sockets, only supplied byte strings.
probe = b'GET /probe HTTP/1.1\r\nHost: a10.test\r\n\r\n'
body = b'0\r\n\r\n' + probe
head = (b'POST /submit HTTP/1.1\r\nHost: a10.test\r\n'
        + b'Content-Length: ' + str(len(body)).encode() + b'\r\n'
        + b'Transfer-Encoding: chunked\r\n\r\n')
raw = head + body

def boundary(data, mode):
    header, content = data.split(b'\r\n\r\n', 1)
    fields = {}
    for line in header.split(b'\r\n')[1:]:
        name, value = line.split(b':', 1)
        fields.setdefault(name.lower(), []).append(value.strip())
    cl = fields.get(b'content-length', [])
    te = fields.get(b'transfer-encoding', [])
    if mode == 'strict' and (len(cl) > 1 or (cl and te)):
        raise ValueError('REJECT ambiguous framing')
    start = len(header) + 4
    if te and mode != 'CL':
        # This teaching parser accepts only an empty chunked body.
        if te != [b'chunked'] or not content.startswith(b'0\r\n\r\n'):
            raise ValueError('Unsupported teaching sample')
        return start + 5
    return start + (int(cl[0]) if cl else 0)

if __name__ == '__main__':
    print('body_bytes=', len(body))
    for mode in ('CL', 'TE', 'strict'):
        try:
            end = boundary(raw, mode)
            print(mode, 'end=', end, 'remaining=', repr(raw[end:]))
        except ValueError as error:
            print(mode, str(error))
    for label, packet in (
        ('CL-only', head.replace(b'Transfer-Encoding: chunked\r\n', b'') + body),
        ('TE-only', head.replace(b'Content-Length: ' + str(len(body)).encode() + b'\r\n', b'') + body)
    ):
        end = boundary(packet, 'strict')
        print(label, 'accepted; remaining=', repr(packet[end:]))
