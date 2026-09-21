---
handoff:            # <project>/<NNN>
role:
actor: { name: , surface: }
lane:               # routine | judgment | divergence  (production topology)
tier:               # micro | governed | protected
status: draft       # draft → ready → dispatched → landed → accepted | returned ; ↘ blocked
isolation: open     # open  OR  { withhold: [...], lift_when: <named-event> }
inputs: []
outputs: []
required_reviews: none      # none | independent   (governed/protected → independent)
review_of: none             # set on a review handoff → <handoff-id>
supersedes: none
revises: none
source_sha:                 # stamped at ready
frozen_hash:                # stamped at dispatched
manifest_sha:               # source-of-truth commit holding the manifest at dispatch
manifest_hash:              # canonical hash of resolved manifest + referenced profile configs
instructions_hash:          # hash of the generated participant instructions
---

# Handoff <project>/<NNN> — <role>

## Task
<what to do, in the receiver's terms>

## Inputs (read exactly these)
<each declared input path>

## Outputs (produce exactly these)
<each declared output path — nothing else>

## Isolation
<resolved: open, or what is withheld and the lift event; recorded exception if any>

## Delivery
<airlock | branch | publisher — derived from the actor surface; how output returns>

## Completion criteria
<what "done" for this handoff means; for governed/protected, the required review>

## Amendments
<!-- frozen above this line from `dispatched`; amendments may not change role/lane/tier/inputs/outputs/isolation -->
