from http.server import BaseHTTPRequestHandler
import json
import io
import cgi
import uuid
from datetime import datetime
from urllib.parse import urlparse

ALLOWED_ORIGIN = "*"  # Restrict as needed

# In-memory store (ephemeral per cold start)
STORE = {
    "receipts": {}
}


def _write_json(handler: BaseHTTPRequestHandler, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _parse_multipart(handler: BaseHTTPRequestHandler):
    ctype, pdict = cgi.parse_header(handler.headers.get('Content-Type', ''))
    if ctype != 'multipart/form-data':
        return None, {}
    # Ensure boundary is bytes
    if 'boundary' in pdict:
        pdict['boundary'] = pdict['boundary'].encode('utf-8')
    length = int(handler.headers.get('Content-Length', '0'))
    data = handler.rfile.read(length)
    fp = io.BytesIO(data)
    form = cgi.FieldStorage(fp=fp, headers=handler.headers, environ={'REQUEST_METHOD': 'POST'}, keep_blank_values=True)
    files = {}
    fields = {}
    for key in form.keys():
        item = form[key]
        if getattr(item, 'filename', None):
            files[key] = {
                'filename': item.filename,
                'content': item.file.read(),
                'type': item.type or 'application/octet-stream'
            }
        else:
            fields[key] = item.value
    return files, fields


class handler(BaseHTTPRequestHandler):  # Vercel Python entrypoint
    def do_OPTIONS(self):  # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split('/') if p]
        # Routes: /api/receipts or /api/receipts/{id}
        if len(parts) >= 2 and parts[-2] == 'receipts':
            if parts[-1] == 'receipts':
                # List
                receipts = list(STORE['receipts'].values())
                return _write_json(self, 200, {"items": receipts, "count": len(receipts)})
            else:
                rid = parts[-1]
                item = STORE['receipts'].get(rid)
                if not item:
                    return _write_json(self, 404, {"error": {"code": "not_found", "message": "Receipt not found"}})
                return _write_json(self, 200, item)
        return _write_json(self, 404, {"error": {"code": "not_found", "message": "Route not found"}})

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split('/') if p]
        if not (len(parts) >= 2 and parts[-1] == 'receipts'):
            return _write_json(self, 404, {"error": {"code": "not_found", "message": "Route not found"}})

        files, fields = _parse_multipart(self)
        if files is None:
            return _write_json(self, 415, {"error": {"code": "unsupported_media_type", "message": "Expected multipart/form-data"}})
        upload = files.get('file')
        if not upload:
            return _write_json(self, 400, {"error": {"code": "missing_file", "message": "Field 'file' is required"}})

        rid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'
        item = {
            "id": rid,
            "vendor": fields.get('vendor', 'Unknown Vendor'),
            "date": fields.get('date', now[:10]),
            "amount": float(fields.get('amount', '0') or 0),
            "currency": fields.get('currency', 'INR'),
            "category": fields.get('category', 'uncategorized'),
            "gstin": fields.get('gstin', ''),
            "tax_amount": float(fields.get('tax_amount', '0') or 0),
            "status": "needs_review",
            "file": {
                "name": upload['filename'],
                "type": upload['type'],
                "size": len(upload['content'])
            },
            "created_at": now
        }
        STORE['receipts'][rid] = item
        return _write_json(self, 201, item)
