from pyscript import display, window, workers
import sys, micropip # type: ignore

# Kick off key generating worker
display("Loading key generation system...", target="status", append=False)
print("[FG] Waiting for background install")
try:
    keygen = await workers["keygen"]
    # Preserve the full document URL. The worker resolves assets with
    # urljoin(), which handles both /realkey/ and /realkey/index.html.
    await keygen.set_base_url(str(window.location.href))
except Exception as error:
    display(
        "realkey could not start its local CAD engine. Check your connection, then reload to retry.",
        target="status",
        append=False,
    )
    print(f"[FG] Background worker failed: {error}")
    raise
print("[FG] Background worker loaded")
await micropip.install(["typing-extensions==4.15.0"])
display("Loaded!", target="status", append=False)


# Mock build123d
class Empty[T]:
    pass


bogus123d = Empty()
sys.modules["build123d"] = bogus123d

# Mock features of build123d adhering to the ideas:
# - Any BRep or geometry generation should fail, we should not be doing that on the light web front-end!
# - Anything else is fine, and we should have reasonable implementations
bogus123d.MM = 1
bogus123d.IN = 25.4
bogus123d.THOU = 0.0254
bogus123d.Face = Empty
bogus123d.Part = Empty
bogus123d.ShapeList = Empty
bogus123d.Sketch = Empty
bogus123d.Vector = Empty
bogus123d.VectorLike = Empty
bogus123d.Wire = Empty

# Jump into realkey
from realkey import web_main

await web_main.main(keygen)
