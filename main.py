from pyscript import display, workers
import sys

# Kick off key generating worker
display("Loading key generation system...", target="status", append=False)
keygen = await workers["keygen"]
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
bogus123d.Wire = Empty

# Jump into realkey
from realkey import realkey

await realkey.main(keygen)
