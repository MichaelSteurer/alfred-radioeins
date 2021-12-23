import json
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class RadioEins:
    BASE_URL = "https://playlist.funtip.de/playList.do"

    def _get_raw_playlist(self, start, end):
        start = start.strftime("%d-%m-%Y_%H-00")
        end = end.strftime("%d-%m-%Y_%H-00")

        path = f"?action=searching&remote=1&version=2&from={start}&to={end}&jsonp_callback="

        resp = requests.get(urljoin(self.BASE_URL, path))
        assert resp.status_code == 200

        content = str(resp.text.encode()).replace("\\n", "").replace("\\", "")

        return content

    def _extract_body(self, content):
        p = re.compile("<tbody>(.*)</tbody>")
        tbody = p.findall(content)[0]
        tbody = f"<tbody>{tbody}</tbody>"
        return tbody

    def _parse_body(self, tbody):
        r = []
        b = BeautifulSoup(tbody, "lxml")
        for tr in b.find_all("tr"):
            data = tr.find_all("td", {"class": "trackInterpret"})
            length = tr.find_all("td", {"class": "trackLength"})

            for d, l in zip(data, length):
                try:
                    d.span.decompose()
                except:
                    continue

                l = l.getText().strip()
                song = d.getText().strip().replace("?", "")
                artist, title = song.split("—")

                artist = artist.strip()
                title = title.strip()
                r.append((artist, title, l))
        return r

    def get_current_playlist(self):
        start = datetime.now() - timedelta(hours=2)
        end = datetime.now() + timedelta(hours=1)

        content = self._get_raw_playlist(start, end)
        tbody = self._extract_body(content)

        songs = self._parse_body(tbody)
        items = []
        for artist, title, time in songs:
            items.append(
                {
                    "title": f"{time} {title}",
                    "time": time,
                    "subtitle": artist,
                    "icon": {
                        "type": "fileicon",
                        "path": "/Applications/Spotify.app"
                    },
                    "arg": f"{title} {artist}",
                }
            )

        items = sorted(items, key=lambda d: d["time"], reverse=True)
        return {
            "items": items
        }


if __name__ == "__main__":
    playlist = RadioEins().get_current_playlist()

    print(json.dumps(playlist))
