use soroban_sdk::contracttype;

/// Minimal fixture mirroring the real hedge-rod-contract RiskScore struct,
/// used by scripts/self_test_schema_sync.py to verify check_schema_sync.py
/// reports OK when the two definitions actually agree.
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RiskScore {
    pub score: u32,
    pub benford_flag: bool,
    pub ml_flag: bool,
    pub timestamp: u64,
    pub confidence: u32,
}
