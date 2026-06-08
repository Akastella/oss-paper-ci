"""CONTRACT checks -- reproducibility contract validation."""

from __future__ import annotations

from oss_paper_ci.checks import register
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.contract import find_contract, load_contract, validate_contract
from oss_paper_ci.models import CheckResult, Severity, Status


@register
class Contract001ReproducibilityContract(BaseChecker):
    """CONTRACT001: Reproducibility contract exists and is valid."""

    check_id = "CONTRACT001"
    title = "Reproducibility contract"
    severity = Severity.INFO
    category = "contract"
    default_enabled = True
    description = (
        "Checks for a reproducibility.yml contract and validates it. "
        "If no contract is found, reports informational guidance."
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        contract_path = find_contract(ctx.repo_path)

        if contract_path is None:
            return [self._info(
                "No reproducibility contract found; using inferred mode.",
                recommendation=(
                    "Create a reproducibility.yml file to explicitly describe "
                    "how to reproduce your paper. Run `oss-paper-ci init "
                    "--contract` to generate a template."
                ),
            )]

        # Try to parse the contract.
        try:
            contract = load_contract(contract_path)
        except Exception as exc:
            return [self._fail(
                f"Failed to parse contract at {contract_path}: {exc}",
                evidence=[contract_path],
                recommendation=(
                    "Check the YAML syntax of your reproducibility.yml file."
                ),
            )]

        # Validate paths referenced in the contract.
        issues = validate_contract(contract, ctx.repo_path)

        if not issues:
            return [self._pass(
                "Reproducibility contract is valid.",
                evidence=[contract_path],
            )]

        # Return the issues as a mix of warnings and info messages.
        results: list[CheckResult] = []
        for issue in issues:
            if issue.severity == Severity.WARNING:
                results.append(self._warn(
                    issue.message,
                    evidence=[contract_path],
                ))
            else:
                results.append(self._info(
                    issue.message,
                    evidence=[contract_path],
                ))

        return results

    def _info(
        self,
        message: str,
        evidence: list[str] | None = None,
        recommendation: str = "",
    ) -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )
