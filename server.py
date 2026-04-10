import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


HOST = "0.0.0.0"
PORT = 8000
INDEX_FILE = Path(__file__).with_name("index.html")


STANDINGS_DATA = {
    "junioren": [
        {"position": 1, "name": "Jasper Schoofs", "team": "Lotto Dstny U19", "gap": "Leider"},
        {"position": 2, "name": "Mathis Dubois", "team": "AG2R Citroen U19", "gap": "+00:21"},
        {"position": 3, "name": "Liam Van Steen", "team": "BORA-hansgrohe Rookies", "gap": "+00:33"},
        {"position": 4, "name": "Noah Vermeulen", "team": "Team Visma U19", "gap": "+00:47"},
        {"position": 5, "name": "Ruben Veldman", "team": "Soudal Quick-Step U19", "gap": "+01:02"},
        {"position": 6, "name": "Tibo Leclercq", "team": "Decathlon AG2R U19", "gap": "+01:24"},
        {"position": 7, "name": "Nils Petersen", "team": "Alpecin-Deceuninck Dev", "gap": "+01:41"},
        {"position": 8, "name": "Milan Koster", "team": "EF Education U19", "gap": "+02:05"},
    ],
    "beloften": [
        {"position": 1, "name": "Tibor Del Grosso", "team": "Alpecin-Deceuninck Development", "gap": "Leider"},
        {"position": 2, "name": "Alec Segaert", "team": "Lotto Development Team", "gap": "+00:15"},
        {"position": 3, "name": "Per Strand Hagenes", "team": "Jumbo-Visma Development", "gap": "+00:27"},
        {"position": 4, "name": "Florian Vermeersch", "team": "Lotto Dstny U23", "gap": "+00:39"},
        {"position": 5, "name": "Arnaud De Lie", "team": "Lotto U23", "gap": "+00:58"},
        {"position": 6, "name": "Emiel Verstrynge", "team": "Crelan-Corendon U23", "gap": "+01:19"},
        {"position": 7, "name": "Gijs Van Hoecke", "team": "Intermarche Circus U23", "gap": "+01:44"},
        {"position": 8, "name": "Hugo Toumire", "team": "Cofidis U23", "gap": "+02:11"},
    ],
    "vrouwen": [
        {"position": 1, "name": "Lotte Kopecky", "team": "SD Worx-Protime", "gap": "Leider"},
        {"position": 2, "name": "Elisa Balsamo", "team": "Lidl-Trek", "gap": "+00:09"},
        {"position": 3, "name": "Lorena Wiebes", "team": "SD Worx-Protime", "gap": "+00:19"},
        {"position": 4, "name": "Marianne Vos", "team": "Team Visma-Lease a Bike", "gap": "+00:32"},
        {"position": 5, "name": "Alison Jackson", "team": "EF Education-Oatly", "gap": "+00:44"},
        {"position": 6, "name": "Pfeiffer Georgi", "team": "Team DSM-firmenich PostNL", "gap": "+01:03"},
        {"position": 7, "name": "Kasia Niewiadoma", "team": "Canyon-SRAM", "gap": "+01:21"},
        {"position": 8, "name": "Letizia Borghesi", "team": "Human Powered Health", "gap": "+01:49"},
    ],
    "elite_mannen": [
        {"position": 1, "name": "Mathieu van der Poel", "team": "Alpecin-Deceuninck", "gap": "Leider"},
        {"position": 2, "name": "Wout van Aert", "team": "Team Visma-Lease a Bike", "gap": "+00:12"},
        {"position": 3, "name": "Mads Pedersen", "team": "Lidl-Trek", "gap": "+00:22"},
        {"position": 4, "name": "Jasper Philipsen", "team": "Alpecin-Deceuninck", "gap": "+00:37"},
        {"position": 5, "name": "Stefan Kung", "team": "Groupama-FDJ", "gap": "+00:52"},
        {"position": 6, "name": "Dylan van Baarle", "team": "Team Visma-Lease a Bike", "gap": "+01:08"},
        {"position": 7, "name": "Filippo Ganna", "team": "INEOS Grenadiers", "gap": "+01:23"},
        {"position": 8, "name": "Jasper Stuyven", "team": "Lidl-Trek", "gap": "+01:47"},
    ],
}


class TrackerHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self) -> None:
        if not INDEX_FILE.exists():
            self._send_json({"error": "index.html niet gevonden"}, status=500)
            return

        body = INDEX_FILE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send_html()
            return

        if self.path == "/api/standings":
            payload = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                **STANDINGS_DATA,
            }
            self._send_json(payload)
            return

        self._send_json({"error": "Niet gevonden"}, status=404)

    def log_message(self, format_: str, *args) -> None:
        return


def run() -> None:
    server = HTTPServer((HOST, PORT), TrackerHandler)
    print(f"Parijs-Roubaix tracker draait op http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
