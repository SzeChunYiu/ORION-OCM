import Lake
open Lake DSL
package proofCorpusCoverage
lean_lib Export where
  srcDir := "../proof-environment-v1/parents/lean4export"
lean_lib Comparator where
  srcDir := "../proof-environment-v1/parents/comparator"
lean_lib CheckedExport where
  srcDir := "../proof-environment-v1/parents/checked-export"
lean_lib OCMEnvironment where
  srcDir := "../proof-environment-v1"
lean_lib OCMCoverage
lean_lib CoverageFixtures where
  srcDir := "newfixtures"
  roots := #[`NamespaceFixture, `P2M.Sol.S_authored, `Theorems.Thm_authored, `P2M.Sol.S_apostrophe, `Theorems.Thm_apostrophe]
lean_exe ocm_coverage where
  root := `OCMCoverage.Main
lean_exe transport_tests where
  srcDir := "newfixtures"
  root := `TransportTests
