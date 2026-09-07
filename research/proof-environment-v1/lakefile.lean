import Lake
open Lake DSL
package proofEnvironment
lean_lib Export where
  srcDir := "parents/lean4export"
lean_lib Comparator where
  srcDir := "parents/comparator"
lean_lib CheckedExport where
  srcDir := "parents/checked-export"
lean_lib OCMEnvironment
lean_lib Fixtures where
  srcDir := "fixtures"
  roots := #[`FixtureCases, `FixtureRegistry]
lean_exe ocm_environment where
  root := `OCMEnvironment.Main
lean_exe ocm_export where
  srcDir := "parents/lean4export"
  root := `Main
  supportInterpreter := true
lean_exe packet_tests where
  srcDir := "fixtures"
  root := `PacketTests
lean_exe dependency_tests where
  srcDir := "fixtures"
  root := `DependencyTests
lean_exe kernel_tests where
  srcDir := "fixtures"
  root := `KernelTests
lean_exe fixture_builder where
  srcDir := "fixtures"
  root := `FixtureBuilder
lean_exe compare_fixture where
  srcDir := "fixtures"
  root := `CompareFixture
lean_exe normalization_tests where
  srcDir := "fixtures"
  root := `NormalizationTests
lean_exe registry_tests where
  srcDir := "fixtures"
  root := `RegistryTests
lean_exe outcome_tests where
  srcDir := "fixtures"
  root := `OutcomeTests
