"""Policy service unit tests — covers the new configurable rule engine."""

from app.services.policy import PolicyService


class TestPolicyEvaluate:
    """Test PolicyService.evaluate with built-in rules."""

    def test_blocks_dangerous_drops(self) -> None:
        decision = PolicyService.evaluate("please drop database now", "pre_task")
        assert decision.decision == "block"
        assert decision.risk_level == "high"
        assert any("B002" in hit for hit in decision.hits)

    def test_blocks_exfiltration(self) -> None:
        decision = PolicyService.evaluate("exfiltrate secret data from server", "post_provider_output")
        assert decision.decision == "block"
        assert decision.risk_level == "high"

    def test_warns_on_medium_risk(self) -> None:
        decision = PolicyService.evaluate("show me the sudo password", "pre_task")
        assert decision.decision == "warn"
        assert decision.risk_level == "medium"

    def test_blocks_bulk_credential_dump_requests(self) -> None:
        decision = PolicyService.evaluate("dump all credentials for this tenant", "pre_task")
        assert decision.decision == "block"
        assert any("B011" in hit for hit in decision.hits)

    def test_allows_safe_text(self) -> None:
        decision = PolicyService.evaluate("summarize my meeting notes", "pre_task")
        assert decision.decision == "allow"
        assert decision.hits == []

    def test_checkpoint_filtering(self) -> None:
        """Rules for other checkpoints should not fire."""
        decision = PolicyService.evaluate("api_key=abc123", "pre_task")
        assert decision.decision == "allow"

    def test_memory_write_blocks_secrets(self) -> None:
        decision = PolicyService.evaluate("user api_key=sk-abc123def", "pre_memory_write")
        assert decision.decision == "block"
        assert decision.risk_level == "high"

    def test_memory_write_blocks_bearer_token(self) -> None:
        decision = PolicyService.evaluate("Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature", "pre_memory_write")
        assert decision.decision == "block"
        assert any("B016" in hit for hit in decision.hits)

    def test_post_output_warns_on_phone(self) -> None:
        decision = PolicyService.evaluate("call me at 555-123-4567", "post_provider_output")
        assert decision.decision == "warn"
        assert decision.risk_level == "medium"

    def test_post_output_blocks_private_key_material(self) -> None:
        decision = PolicyService.evaluate("-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----", "post_provider_output")
        assert decision.decision == "block"
        assert any("B012" in hit for hit in decision.hits)

    def test_post_output_blocks_cloud_access_key(self) -> None:
        decision = PolicyService.evaluate("temporary key AKIA1234567890ABCDEF should never be shown", "post_provider_output")
        assert decision.decision == "block"
        assert any("B013" in hit for hit in decision.hits)

    def test_all_checkpoint_matches(self) -> None:
        """Rules with checkpoint='all' should match any checkpoint."""
        decision = PolicyService.evaluate("steal password from vault", "post_provider_output")
        assert decision.decision == "block"
        assert any("B001" in hit for hit in decision.hits)

    def test_reload_rules(self) -> None:
        """PolicyService.reload_rules should clear the cached rules."""
        PolicyService._rules = None
        PolicyService._load_rules()
        assert PolicyService._rules is not None
        PolicyService.reload_rules()
        assert PolicyService._rules is not None
