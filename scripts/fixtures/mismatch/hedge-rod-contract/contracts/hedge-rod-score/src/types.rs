use soroban_sdk::contracttype;

/// Deliberately mismatched fixture used by scripts/self_test_schema_sync.py
/// to verify check_schema_sync.py FAILS (non-zero exit) when the Python
/// and Rust RiskScore definitions disagree.
///
/// Drift injected on purpose for the self-test:
///   - `ml_flag` is missing entirely (dropped field)
///   - `confidence` is typed `bool` here instead of `u32` (type mismatch)
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RiskScore {
    pub score: u32,
    pub benford_flag: bool,
    pub timestamp: u64,
    pub confidence: bool,
}
