"""Prospective constants; no command-line seed, population filter or replacement switch."""
COMMIT = 'aa2d8b34692b16c70f699536de0d8e75b9a3e9ef'
TREE = '8bb1c43c8f26f1c127591dddeffdead2b5094eb7'
PAIRS, FILES, EDGES, ASSIGNED = 29511, 60478, 106853, 4
INPUTS = {
    'CORPUS_SOURCE.json': ('de911c6ef05adb9df9017d7aedd21bcfeb7376e99348af46fa4b17b14e2cd3dd', 23225103),
    'GRAPH.json': ('f74f7391cd36b631641c7a8207d949f49e0e42459a8ca94f87852e91b4cc82a4', 18485022),
    'SOLUTIONS.json': ('dcde5c01c7f256a344d0f58f4e2d932dca2997bd28851caccb83ba648b01c9bb', 34598746),
    'WRAPPERS.json': ('cbf8c310a1f932e3e5c510628433f78e4430f3406ec72e7293d45c3b27afc461', 325043062),
}
DOCUMENTS = {
    'F1-CORPUS-COVERAGE-DESIGN.md': '832e10fa326e900209a8f91f23f76ff8e3d78aae7905d4ca8fbfe790af23aaf9',
    'F1-CORPUS-COVERAGE-EXECUTION.md': 'e2985bed0692b57ebff6aef16874178fceecba5e85b3899a1f0b6f2edf259e0e',
}
PYTHON_SHA256 = 'edca1fc80dbd58182c849c13707fb6bfb522b0d7049adc408225f7c69b124d3b'
STAGES = ('RESOURCE_SETUP', 'ACQUISITION', 'BUILD', 'ASSOCIATION', 'EXPORT', 'PREPARE', 'CHECK')
POLICY = {
    'schema': 'ocm.f1.coverage-policy.v1',
    'assignment': {'prefix_utf8': 'ocm.f1.semantic-coverage.v1', 'separator_hex': '00',
                   'order': ['sha256_bytes', 'key_utf8_bytes'], 'start': 0, 'take': ASSIGNED,
                   'replacement': False, 'outcome_features': False},
    'limits': {'memory_bytes': 20 * 2**30, 'memory_and_swap_bytes': 20 * 2**30,
               'cpu_equivalents': 2, 'pids': 128, 'initial_mem_available_bytes': 24 * 2**30,
               'initial_disk_free_bytes': 224 * 2**30, 'stop_disk_free_bytes': 80 * 2**30,
               'stop_owned_new_bytes': 128 * 2**30, 'disk_poll_seconds': 1,
               'hard_aggregate_disk_quota': False, 'file_size_bytes': 8 * 2**30,
               'source_packet_bytes_per_row': 512 * 2**20, 'row_input_bytes_total': 2**30,
               'whole_dispatch_seconds': 43200, 'acquisition_seconds': 3600,
               'build_seconds_per_row': 7200, 'export_seconds_per_row': 900,
               'prepare_seconds_per_row': 900, 'check_seconds_per_row': 600,
               'term_grace_seconds': 5, 'forced_reap_seconds': 10},
    'execution': {'learner': False, 'reference_support': 'EXPOSED', 'network_during_build_export': False,
                  'neural_computation': False, 'runtime_requires_separate_qualification': True,
                  'cold_costs_included': True, 'upstream_proof_acquisition_cost': 'UNKNOWN'},
    'claim': 'Four assigned reference-replay coverage cases; not search, learning, transfer or FLT.',
}
