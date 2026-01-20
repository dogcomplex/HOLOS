Locus = The name of the algorithm (in any recognizable form, including pseudocode or description) which describes how to generate a Sign.  A text description/requirements doc for a particular Sign is a Locus.  The general function for generating any Sign is a Locus.   A Locus is *the thing being pointed to*.  An algorithm as text or byte-code is itself a Sign; the abstract function it denotes is the Locus.  A set of frames to be interpreted which characterize a visual pattern is a Locus.  Multiple distinct Signs have multiple distinct Loci.  A single Sign has only one Locus though it could be written in many forms (each a Sign too).  A Locus is thus a fractal generator pattern of meaning.  The ultimate Locus is unreachable (any instance is a mere representation), but we still pragmatically refer to that instance as the Locus.
💠Sign = (Signum, Signifier.  Related: Node)  Any data structure or function or vibe or embodied Locus.  Any "thing" in its representative, realized form.  A concrete node in the graph.
🌸Vibe = (Related: Hydrated, Living, Active, Learning Sign) Subtype of Sign, emphasizing alive, hydrated, growing, changing.  Typically AI related - active, learning, adaptable.
❄️Type = (Related: Type, Prism, Gem, Facet, Stable, Static, Calcified, Frozen, Hallowed Sign)  Subtype of Sign, stable surrogate of a Sign's learned function.  ...  May be referred to by it's specific type like ❄️Function ❄️Data, ❄️Array, ❄️Router, ❄️Descriptor or name like ❄️NPCDetector etc
🌩️Act = (AKA: Action, Actio, Actor, Actionable, Execution).  An execution, a flow of movement over time through the system.  The moving/changing part that composes a Sense.  e.g. includes inputs/outputs/timings but not weight deltas
🌍Collective = (Related: Graph, Matrix, System, Gaia).  The total encompassing system
🌊Sense = (Related: Sensus, Flow, Flux, Source, Trace, Prime, Interpreter, Learning).  The combined actions and changes of an execution flow.  Instigated by a 🌊Source.  i.e. the total execution flow through individual🌩️Acts plus the resulting changes in the interpreter and nodes along the way (e.g. the weight updates).  The starting point of sense-making may be called the 🌊Source or 🌊Prime (the topmost AI layer for a particular program).  Note, a single 🌍Collective may have multiple 🌊Senses flowing through it at different (or simultaneous) times.  For MVP purposes we'll focus on one (mastering Pokemon)

Subtypes of Signs (can always just be referred to as 💠Signs generally):
🔹Signal:  A minimal representation of a Sign, typically 0/+/- by our ternary activation convention.  Designed for fast minimal transmission of meaning, usually relying on context/index.
Signatory:  (🤖Axiom 🦊Vibe variants) A signing authority Sign, or a Sign with agent-like qualities and responsibilities.  An LLM is a Signatory, as is a Human.  May be identified by a Signature or Signet artifact.  Use these in particular where responsibility/authenticity/trust/security are involved
🔷Sigil:  (⚙️Axiom   🌀Vibe  Sigil variants) A functional variant of Sign, emphasizing functional executable purpose.  Diamond shape emphasizes it as a decision or merge, as in UML diagrams  
🌻Glamour:  (🌼 Glyph, a smaller visual signal) a Sign representation oriented to visualization and understanding.  User interface.

Naming Scheme: We don't append "Sign" to types/names, it's implied that *any* representation of anything is always implicitly a Sign (even a "Locus", which is the most ephemeral pointer but still needs to be represented).  When we have the opportunity of a format where we can use emojis we use the emoji's prefix to indicate its type and thus do not have to append anything.  e.g. 🌸NPCDetectorVibe => 🌸NPCDetector or even 🌸NPC if the context allows it. 
Any context where emojis are not viable should use shorthand LOCUS_, SIGN_, VIBE_, TYPE_, ACT_, SENSE_, SIGIL_, GLYPH_, GLAM_, SIGNET_, or S_ for Signal.  Try to use the most general form (i.e. SIGN) only when the sign is likely to change types (volatile or unknown), but otherwise use the most appropriate for the context if stable.

Example:
📁LocateFaces  # Folder contains:
LocateFaces_spec.md        # Locus: abstract face-detector function specification.  Technically a Sign that describes the Locus (but we have to start somewhere)
💠locate_faces.py            # Sign: code that implements it (or tries to at least)
❄️LocateFaces_v3.ckpt     # frozen weights snapshot (or .onnx, etc). Frozen surrogate of locate_faces.py after training.
🌸LocateFacesLive.ptl    # same model after N online updates (or live in db). Weights and optimizer / replay buffers may mutate
# runs/
🌩️run_54.json             # Act: inference call. Captures the exact call (inputs, outputs, timing). Stays small.
# traces/
🌊trace_54.tar.gz           # Sense: Act + Δweights for continual learning. Bundles run_54.json + the delta of every parameter/file touched (logs, patches, weight diffs, feature cache inserts, etc).  May be part of a larger graph network of runs/traces
# Optional:
😶LocateFaces.icon     # Glyph:  shorthand representative visualization (emoji used in filename)