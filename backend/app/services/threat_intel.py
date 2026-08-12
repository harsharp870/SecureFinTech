import ipaddress
from typing import List, Optional
from pydantic import BaseModel

class ThreatIntelResult(BaseModel):
    ip_address: str
    is_malicious: bool
    threat_score: float  # 0.0 to 100.0
    threat_category: Optional[str] = None
    description: Optional[str] = None

class ThreatIntelService:
    """
    Simulated Threat Intelligence Provider.
    Performs IP subnet lookups against known malicious CIDRs (Tor exit nodes, Botnet C2, Malicious Proxies).
    """
    # Pre-configured malicious subnet database
    KNOWN_MALICIOUS_SUBNETS = [
        ("185.220.101.0/24", 90.0, "TOR_EXIT_NODE", "Known Tor Exit Node network"),
        ("198.51.100.0/24", 95.0, "BOTNET_C2", "Known Botnet Command & Control server network"),
        ("203.0.113.0/24", 85.0, "MALICIOUS_PROXY", "High-risk anonymous proxy network"),
    ]

    def evaluate_ip(self, ip_address: str) -> ThreatIntelResult:
        """Evaluates an IP address and returns threat score and category."""
        if not ip_address:
            return ThreatIntelResult(
                ip_address="0.0.0.0",
                is_malicious=False,
                threat_score=0.0,
                threat_category=None,
                description="Unknown IP address"
            )

        try:
            target_ip = ipaddress.ip_address(ip_address.strip())
        except ValueError:
            return ThreatIntelResult(
                ip_address=ip_address,
                is_malicious=False,
                threat_score=0.0,
                threat_category=None,
                description="Invalid IP address format"
            )

        for cidr, score, category, desc in self.KNOWN_MALICIOUS_SUBNETS:
            network = ipaddress.ip_network(cidr)
            if target_ip in network:
                return ThreatIntelResult(
                    ip_address=ip_address,
                    is_malicious=True,
                    threat_score=score,
                    threat_category=category,
                    description=desc
                )

        return ThreatIntelResult(
            ip_address=ip_address,
            is_malicious=False,
            threat_score=0.0,
            threat_category=None,
            description="Clean IP address"
        )
