// DLM space79 dialect v0. This is an MLIR-shaped textual front-end,
// not upstream MLIR. It lowers to the existing Maru event machine.
space.module @proof_and_definition {
  %s0 = space.new : !space79.space
  %s1 = space.define %s0 "p-def" ((p 0)) (pred p ()) : !space79.space
  %s2 = space.prove %s1 "proof" (problem classical-prop-v1 ((p 0))
        (sequent classical-prop-v1 ((pred p ())) ((pred p ())))) : !space79.space
  %s3 = space.run %s2 1000 : !space79.space
  space.job %s3 "job" "proof"
  space.definitions %s3 "definitions"
}
