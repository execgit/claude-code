import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict


class TokenUsageMetrics:
    """Analyze and report token usage from logs."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.token_log_file = self.log_dir / "token_usage.log"

    def parse_token_logs(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Parse token usage logs from the last N hours."""
        if not self.token_log_file.exists():
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        token_entries = []

        try:
            with open(self.token_log_file, "r") as f:
                for line in f:
                    if line.strip():
                        # Parse log line format: timestamp - logger - level - json_data
                        parts = line.strip().split(" - ", 3)
                        if len(parts) >= 4:
                            timestamp_str = parts[0]
                            json_data = parts[3]

                            try:
                                # Parse timestamp
                                log_time = datetime.fromisoformat(timestamp_str)
                                if log_time >= cutoff_time:
                                    # Parse JSON data
                                    data = json.loads(json_data)
                                    if data.get("event_type") == "token_usage":
                                        token_entries.append(data)
                            except (ValueError, json.JSONDecodeError):
                                continue
        except FileNotFoundError:
            pass

        return token_entries

    def generate_usage_report(self, hours_back: int = 24) -> Dict[str, Any]:
        """Generate a comprehensive token usage report."""
        entries = self.parse_token_logs(hours_back)

        if not entries:
            return {
                "period": f"Last {hours_back} hours",
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_estimate": 0.0,
                "by_provider": {},
                "by_model": {},
                "by_request_type": {},
            }

        # Aggregate metrics
        total_tokens = sum(entry["total_tokens"] for entry in entries)
        total_cost = [entry.get("cost_estimate", 0) for entry in entries]
        total_cost = sum(x for x in total_cost if x is not None)

        # Group by provider
        by_provider = defaultdict(lambda: {"requests": 0, "tokens": 0, "cost": 0.0})
        for entry in entries:
            provider = entry["provider"]
            by_provider[provider]["requests"] += 1
            by_provider[provider]["tokens"] += entry["total_tokens"]
            cost = entry.get("cost_estimate", 0)
            if not cost:
                cost = 0
            by_provider[provider]["cost"] += cost

        # Group by model
        by_model = defaultdict(lambda: {"requests": 0, "tokens": 0, "cost": 0.0})
        for entry in entries:
            model = entry["model"]
            by_model[model]["requests"] += 1
            by_model[model]["tokens"] += entry["total_tokens"]
            cost = entry.get("cost_estimate", 0)
            if not cost:
                cost = 0
            by_model[model]["cost"] += cost

        # Group by request type
        by_request_type = defaultdict(lambda: {"requests": 0, "tokens": 0, "cost": 0.0})
        for entry in entries:
            request_type = entry["request_type"]
            by_request_type[request_type]["requests"] += 1
            by_request_type[request_type]["tokens"] += entry["total_tokens"]
            cost = entry.get("cost_estimate", 0)
            if not cost:
                cost = 0
            by_request_type[request_type]["cost"] += cost

        return {
            "period": f"Last {hours_back} hours",
            "total_requests": len(entries),
            "total_tokens": total_tokens,
            "total_cost_estimate": round(total_cost, 4),
            "by_provider": dict(by_provider),
            "by_model": dict(by_model),
            "by_request_type": dict(by_request_type),
        }

    def print_usage_report(self, hours_back: int = 24):
        """Print a formatted usage report."""
        report = self.generate_usage_report(hours_back)

        print(f"\n📊 Token Usage Report - {report['period']}")
        print("=" * 50)
        print(f"Total Requests: {report['total_requests']}")
        print(f"Total Tokens: {report['total_tokens']:,}")
        print(f"Estimated Cost: ${report['total_cost_estimate']:.4f}")

        if report["by_provider"]:
            print("\n🏢 By Provider:")
            for provider, stats in report["by_provider"].items():
                print(
                    f"  {provider}: {stats['requests']} requests, {stats['tokens']:,} tokens, ${stats['cost']:.4f}"
                )

        if report["by_model"]:
            print("\n🤖 By Model:")
            for model, stats in report["by_model"].items():
                print(
                    f"  {model}: {stats['requests']} requests, {stats['tokens']:,} tokens, ${stats['cost']:.4f}"
                )

        if report["by_request_type"]:
            print("\n📝 By Request Type:")
            for req_type, stats in report["by_request_type"].items():
                print(
                    f"  {req_type}: {stats['requests']} requests, {stats['tokens']:,} tokens, ${stats['cost']:.4f}"
                )

        print()


class SecurityMetrics:
    """Analyze and report security events from logs."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.security_log_file = self.log_dir / "security_events.log"
        self.validation_log_file = self.log_dir / "validation_events.log"

    def parse_security_logs(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Parse security event logs from the last N hours."""
        if not self.security_log_file.exists():
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        security_entries = []

        try:
            with open(self.security_log_file, "r") as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split(" - ", 3)
                        if len(parts) >= 4:
                            timestamp_str = parts[0]
                            json_data = parts[3]

                            try:
                                log_time = datetime.fromisoformat(timestamp_str)
                                if log_time >= cutoff_time:
                                    data = json.loads(json_data)
                                    if data.get("event_type") == "security_event":
                                        security_entries.append(data)
                            except (ValueError, json.JSONDecodeError):
                                continue
        except FileNotFoundError:
            pass

        return security_entries

    def parse_validation_logs(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Parse validation event logs from the last N hours."""
        if not self.validation_log_file.exists():
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        validation_entries = []

        try:
            with open(self.validation_log_file, "r") as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split(" - ", 3)
                        if len(parts) >= 4:
                            timestamp_str = parts[0]
                            json_data = parts[3]

                            try:
                                log_time = datetime.fromisoformat(timestamp_str)
                                if log_time >= cutoff_time:
                                    data = json.loads(json_data)
                                    if data.get("event_type") == "validation_event":
                                        validation_entries.append(data)
                            except (ValueError, json.JSONDecodeError):
                                continue
        except FileNotFoundError:
            pass

        return validation_entries

    def generate_security_report(self, hours_back: int = 24) -> Dict[str, Any]:
        """Generate a comprehensive security report."""
        security_entries = self.parse_security_logs(hours_back)
        validation_entries = self.parse_validation_logs(hours_back)

        # Count validation results
        validation_stats = defaultdict(lambda: {"passed": 0, "failed": 0, "total": 0})
        for entry in validation_entries:
            validator = entry["validator_name"]
            result = entry["result"]
            validation_stats[validator]["total"] += 1
            if result == "passed":
                validation_stats[validator]["passed"] += 1
            else:
                validation_stats[validator]["failed"] += 1

        # Count security events by type
        security_by_type = defaultdict(int)
        for entry in security_entries:
            event_type = entry.get("security_event_type", "unknown")
            security_by_type[event_type] += 1

        return {
            "period": f"Last {hours_back} hours",
            "total_security_events": len(security_entries),
            "total_validations": len(validation_entries),
            "validation_stats": dict(validation_stats),
            "security_events_by_type": dict(security_by_type),
        }

    def print_security_report(self, hours_back: int = 24):
        """Print a formatted security report."""
        report = self.generate_security_report(hours_back)

        print(f"\n🛡️  Security Report - {report['period']}")
        print("=" * 50)
        print(f"Total Security Events: {report['total_security_events']}")
        print(f"Total Validations: {report['total_validations']}")

        if report["validation_stats"]:
            print("\n🔍 Validation Results:")
            for validator, stats in report["validation_stats"].items():
                passed = stats["passed"]
                failed = stats["failed"]
                total = stats["total"]
                success_rate = (passed / total * 100) if total > 0 else 0
                print(
                    f"  {validator}: {passed}/{total} passed ({success_rate:.1f}%), {failed} failed"
                )

        if report["security_events_by_type"]:
            print("\n⚠️  Security Events by Type:")
            for event_type, count in report["security_events_by_type"].items():
                print(f"  {event_type}: {count}")

        print()


# Global instances
token_metrics = TokenUsageMetrics()
security_metrics = SecurityMetrics()
