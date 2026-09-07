import OCMEnvironment.Packet
open Lean OCMEnvironment
private def require (b : Bool) (msg : String) : IO Unit :=
  unless b do throw (IO.userError msg)
def main : IO Unit := do
  let header := metadata.compress ++ "\n"
  let good := header ++ "{\"ie\":0,\"sort\":0}\n"
  require (validateText good true).isOk "valid expression packet refused"
  require (validateText (good ++ "{\"ie\":0,\"sort\":0}\n") true).isOk.not "duplicate expression ID accepted"
  require (validateText (header ++ "{\"in\":0,\"str\":{\"pre\":0,\"str\":\"x\"}}\n") true).isOk.not "implicit name zero overwritten"
  require (validateText (header ++ "{\"ie\":0,\"app\":{\"fn\":9,\"arg\":9}}\n") true).isOk.not "forward reference accepted"
  require (validateText ("{}\n" ++ "{\"ie\":0,\"sort\":0}\n") true).isOk.not "wrong metadata accepted"
  require (validateText (header ++ "{\"axiom\":{}}\n") true).isOk.not "candidate declaration accepted"
  require (validateText (header ++ "{\"ie\":false,\"sort\":0}\n") true).isOk.not "boolean ID accepted"
  require (validateText (good ++ "garbage\n") true).isOk.not "trailing garbage accepted"
  require (validateText (header ++ "{\"ie\":0,\"ie\":0,\"sort\":0}\n") true).isOk.not "duplicate JSON key accepted"
  require (validateText (header ++ "\n{\"ie\":0,\"sort\":0}\n") true).isOk.not "blank packet row accepted"
  IO.println "PACKET_CONTROLS_PASS 10"
