import json
from pathlib import Path

from tickethub.main import app

TEMPLATE = """<!DOCTYPE html>
<html>
  <head>
    <title>TicketHub API</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body { margin: 0; padding: 0; }</style>
  </head>
  <body>
    <div id="redoc"></div>
    <script id="spec" type="application/json">__SPEC__</script>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
    <script>
      Redoc.init(
        JSON.parse(document.getElementById("spec").textContent),
        {},
        document.getElementById("redoc")
      );
    </script>
  </body>
</html>
"""


def main() -> None:
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)

    spec = app.openapi()
    (docs_dir / "openapi.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    html = TEMPLATE.replace("__SPEC__", json.dumps(spec))
    (docs_dir / "redoc-static.html").write_text(html, encoding="utf-8")
    print(f"OpenAPI docs written to {docs_dir}")


if __name__ == "__main__":
    main()
