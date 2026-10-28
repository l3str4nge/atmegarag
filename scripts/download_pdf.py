import argparse
import urllib.request
from pathlib import Path

DEFAULT_URL = (
    "https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/"
    "DataSheets/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf"
)
DEFAULT_OUT_DIR = Path(__file__).resolve().parent.parent / "data"


def download(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / url.rsplit("/", 1)[-1]

    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read()

    if not content.startswith(b"%PDF"):
        raise ValueError(f"Response from {url} is not a PDF")

    out_path.write_bytes(content)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a PDF file.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    path = download(args.url, args.out_dir)
    print(f"Saved {path} ({path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
