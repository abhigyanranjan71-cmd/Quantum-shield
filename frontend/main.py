import os, json, uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from fastapi import FastAPI, Request, Form, Response, Cookie, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="QuantumShield", docs_url=None, redoc_url=None)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
API_BASE = "http://localhost:3000/api"
SESSIONS: Dict[str, Dict[str, Any]] = {}

MOCK_ASSETS = [
    {
        "id": "financial-records",
        "name": "Financial Core Database (Ledger)",
        "type": "Database",
        "size": "2.4 GB",
        "algorithm": "RSA-2048",
        "keySize": 2048,
        "sensitivity": "Critical",
        "lifetime": "20+ years",
        "exposure": "Internet",
        "cryptoRisk": 35,
        "sensitivityRisk": 25,
        "lifetimeRisk": 20,
        "exposureRisk": 14,
        "overallScore": 94,
        "riskLevel": "critical",
        "pqcStatus": "Vulnerable",
        "recommendation": "Migrate to ML-KEM-1024 immediately. RSA-2048 will be compromised by Shor's algorithm on CRQC.",
        "explanation": "This asset protects long-term ledger records with RSA-2048. Because the data retains confidentiality value for over 20 years, an adversary intercepting traffic today can decrypt all transactions once a cryptographically relevant quantum computer is available (HNDL).",
        "mlRiskLevel": "critical",
        "mlConfidence": 0.98,
        "anomalyScore": 0.92,
        "aiWhyRisky": "RSA-2048 is fully broken under polynomial-time Shor's algorithm. Combined with public endpoints and 20+ year financial retention laws, this represents maximum Harvest Now, Decrypt Later (HNDL) liability.",
        "aiKeyFindings": [
            "RSA-2048 key exchange vulnerable to Shor's algorithm",
            "Confidentiality lifetime (20+ yrs) exceeds estimated CRQC timeline (8-10 yrs)",
            "Exposed to Internet-facing payment ingress gateways",
            "NIST SP 800-208 / FIPS 203 migration priority: IMMEDIATE"
        ],
        "createdAt": "2024-08-15T09:30:00Z",
        "lastScan": "10 mins ago"
    },
    {
        "id": "customer-pii-db",
        "name": "Customer Identity & Auth DB",
        "type": "Database",
        "size": "14.2 GB",
        "algorithm": "ECC (ECDSA P-256)",
        "keySize": 256,
        "sensitivity": "Critical",
        "lifetime": "20+ years",
        "exposure": "Cloud",
        "cryptoRisk": 36,
        "sensitivityRisk": 25,
        "lifetimeRisk": 20,
        "exposureRisk": 10,
        "overallScore": 91,
        "riskLevel": "critical",
        "pqcStatus": "Vulnerable",
        "recommendation": "Upgrade signature schemes to ML-DSA-65 (FIPS 204) and establish hybrid TLS termination.",
        "explanation": "Elliptic Curve Cryptography offers no quantum resistance against quantum Shor discrete logarithm solvers. Customer PII and biometric tokens stored with 20+ year lifetime create irreversible exposure.",
        "mlRiskLevel": "critical",
        "mlConfidence": 0.96,
        "anomalyScore": 0.89,
        "aiWhyRisky": "ECC P-256 provides approximately 128 bits of classical security, but 0 bits of quantum security. A quantum attacker will compute discrete logarithms and forge authentication tokens retrospectively.",
        "aiKeyFindings": [
            "ECDSA P-256 vulnerable to Shor discrete logarithm solver",
            "Contains GDPR/CCPA regulated identity records",
            "Cloud-hosted multi-region replication increases capture surface"
        ],
        "createdAt": "2024-08-14T11:20:00Z",
        "lastScan": "2 hours ago"
    },
    {
        "id": "payment-gateway",
        "name": "Payment Processing Gateway",
        "type": "Application",
        "size": "55 MB",
        "algorithm": "RSA-2048",
        "keySize": 2048,
        "sensitivity": "Critical",
        "lifetime": "Indefinite",
        "exposure": "Internet",
        "cryptoRisk": 35,
        "sensitivityRisk": 25,
        "lifetimeRisk": 20,
        "exposureRisk": 14,
        "overallScore": 94,
        "riskLevel": "critical",
        "pqcStatus": "Vulnerable",
        "recommendation": "Deploy hybrid X25519+ML-KEM-768 for TLS session key exchange.",
        "explanation": "Internet-exposed payment transaction streams are prime targets for nation-state automated recording systems executing HNDL data hoarding campaigns.",
        "mlRiskLevel": "critical",
        "mlConfidence": 0.99,
        "anomalyScore": 0.94,
        "aiWhyRisky": "High-throughput internet API communicating over legacy RSA key exchange. Encrypted traffic dumps captured today will yield plaintext PCI-DSS data upon CRQC availability.",
        "aiKeyFindings": [
            "Direct Internet exposure with public routing",
            "RSA-2048 key negotiation with no post-quantum hybrid KEM",
            "Real-time transaction capture liability"
        ],
        "createdAt": "2024-08-16T14:15:00Z",
        "lastScan": "30 mins ago"
    },
    {
        "id": "employee-records",
        "name": "Global HR & Payroll Archive",
        "type": "Database",
        "size": "850 MB",
        "algorithm": "RSA-2048",
        "keySize": 2048,
        "sensitivity": "High",
        "lifetime": "10-20 years",
        "exposure": "Internal",
        "cryptoRisk": 35,
        "sensitivityRisk": 18,
        "lifetimeRisk": 16,
        "exposureRisk": 6,
        "overallScore": 75,
        "riskLevel": "critical",
        "pqcStatus": "Vulnerable",
        "recommendation": "Migrate database column encryption to AES-256 and key management to ML-KEM.",
        "explanation": "Internal enterprise archive protected by RSA asymmetric wraps. Employee tax and medical identifiers require 10-20 year protection.",
        "mlRiskLevel": "high",
        "mlConfidence": 0.88,
        "anomalyScore": 0.76,
        "aiWhyRisky": "Internal network visibility reduces interception risk slightly compared to internet, but asymmetric key wrap vulnerability remains fatal against future offline decryption.",
        "aiKeyFindings": [
            "Long confidentiality lifecycle (10-20 yrs)",
            "RSA-2048 envelope encryption vulnerable to quantum factoring"
        ],
        "createdAt": "2024-08-10T08:00:00Z",
        "lastScan": "1 day ago"
    },
    {
        "id": "research-ip-data",
        "name": "R&D Quantum Algorithms Repository",
        "type": "Database",
        "size": "5.6 GB",
        "algorithm": "RSA-3072",
        "keySize": 3072,
        "sensitivity": "High",
        "lifetime": "20+ years",
        "exposure": "Cloud",
        "cryptoRisk": 28,
        "sensitivityRisk": 18,
        "lifetimeRisk": 20,
        "exposureRisk": 10,
        "overallScore": 76,
        "riskLevel": "critical",
        "pqcStatus": "Vulnerable",
        "recommendation": "Migrate immediately to SLH-DSA-SHAKE-256 and ML-KEM-1024.",
        "explanation": "RSA-3072 provides 128-bit classical security, but polynomial-time Shor's algorithm solves 3072-bit modular arithmetic almost as easily as 2048-bit with minimal additional qubits.",
        "mlRiskLevel": "high",
        "mlConfidence": 0.85,
        "anomalyScore": 0.74,
        "aiWhyRisky": "Increasing RSA key size from 2048 to 3072 bits delays quantum cryptanalysis by only a marginal qubit margin, failing to prevent HNDL decryption for 20+ year secrets.",
        "aiKeyFindings": [
            "RSA-3072 provides no meaningful defense against Shor's algorithm",
            "High-value proprietary intellectual property",
            "Cloud-storage sync provides remote exfiltration targets"
        ],
        "createdAt": "2024-08-11T16:00:00Z",
        "lastScan": "5 hours ago"
    },
    {
        "id": "api-gateway-tls",
        "name": "Enterprise Edge API Gateway TLS",
        "type": "API Gateway",
        "size": "4 KB",
        "algorithm": "ECC (ECDSA P-384)",
        "keySize": 384,
        "sensitivity": "Medium",
        "lifetime": "1-5 years",
        "exposure": "Internet",
        "cryptoRisk": 36,
        "sensitivityRisk": 12,
        "lifetimeRisk": 6,
        "exposureRisk": 14,
        "overallScore": 68,
        "riskLevel": "high",
        "pqcStatus": "Vulnerable",
        "recommendation": "Implement hybrid TLS 1.3 draft specification (X25519 + Kyber768).",
        "explanation": "While individual session keys have 1-5 year utility, man-in-the-middle record captures compromise session integrity.",
        "mlRiskLevel": "high",
        "mlConfidence": 0.82,
        "anomalyScore": 0.69,
        "aiWhyRisky": "Edge ingress TLS relying solely on elliptic curves exposes all transient tokens to retroactive decipherment.",
        "aiKeyFindings": [
            "P-384 easily broken by quantum Shor algorithm",
            "High internet exposure profile"
        ],
        "createdAt": "2024-08-17T12:00:00Z",
        "lastScan": "1 hour ago"
    },
    {
        "id": "internal-strategy-doc",
        "name": "Corporate M&A Strategic Roadmap",
        "type": "Document",
        "size": "4.8 MB",
        "algorithm": "AES-128",
        "keySize": 128,
        "sensitivity": "High",
        "lifetime": "5-10 years",
        "exposure": "Internal",
        "cryptoRisk": 18,
        "sensitivityRisk": 18,
        "lifetimeRisk": 11,
        "exposureRisk": 6,
        "overallScore": 53,
        "riskLevel": "high",
        "pqcStatus": "Weakened",
        "recommendation": "Upgrade symmetric cipher to AES-256-GCM. AES-128 is weakened to 64-bit security by Grover's algorithm.",
        "explanation": "Grover's quantum search algorithm provides quadratic speedup against symmetric keys, degrading AES-128 to an effective 64-bit security margin, vulnerable to large-scale quantum brute force.",
        "mlRiskLevel": "high",
        "mlConfidence": 0.81,
        "anomalyScore": 0.63,
        "aiWhyRisky": "AES-128 does not withstand quantum brute-force accelerators. Upgrading to AES-256 restores a 128-bit quantum security level.",
        "aiKeyFindings": [
            "Grover's algorithm reduces AES-128 strength to 64 bits",
            "Strategic 10-year confidential lifecycle"
        ],
        "createdAt": "2024-08-12T09:10:00Z",
        "lastScan": "3 days ago"
    },
    {
        "id": "cloud-backup-blob",
        "name": "Encrypted Cloud Backup Vault",
        "type": "Cloud Storage",
        "size": "120 GB",
        "algorithm": "AES-256",
        "keySize": 256,
        "sensitivity": "High",
        "lifetime": "10-20 years",
        "exposure": "Cloud",
        "cryptoRisk": 4,
        "sensitivityRisk": 18,
        "lifetimeRisk": 16,
        "exposureRisk": 10,
        "overallScore": 48,
        "riskLevel": "medium",
        "pqcStatus": "Resistant",
        "recommendation": "Maintain AES-256. Ensure Key Encryption Keys (KEKs) use PQC key encapsulation.",
        "explanation": "AES-256 symmetric encryption retains 128 bits of quantum security under Grover's algorithm, providing solid quantum resistance for bulk data.",
        "mlRiskLevel": "medium",
        "mlConfidence": 0.77,
        "anomalyScore": 0.52,
        "aiWhyRisky": "The symmetric payload is quantum-safe (AES-256 = 128 bits post-Grover). Remaining risk is concentrated strictly in the key management and distribution layer.",
        "aiKeyFindings": [
            "Bulk cipher is quantum-resistant (AES-256)",
            "Inspect upstream KMS for RSA/ECC wrapping keys"
        ],
        "createdAt": "2024-08-05T14:30:00Z",
        "lastScan": "6 hours ago"
    },
    {
        "id": "email-archive",
        "name": "Executive Email Archive Server",
        "type": "Email Server",
        "size": "88 GB",
        "algorithm": "RSA-2048",
        "keySize": 2048,
        "sensitivity": "Medium",
        "lifetime": "10-20 years",
        "exposure": "Cloud",
        "cryptoRisk": 35,
        "sensitivityRisk": 12,
        "lifetimeRisk": 16,
        "exposureRisk": 10,
        "overallScore": 73,
        "riskLevel": "high",
        "pqcStatus": "Vulnerable",
        "recommendation": "Re-encrypt historical S/MIME messages with ML-KEM hybrid certificates.",
        "explanation": "Historical email messages encrypted with classical S/MIME certificates (RSA-2048) stored in cloud infrastructure remain vulnerable to offline batch decryption.",
        "mlRiskLevel": "high",
        "mlConfidence": 0.84,
        "anomalyScore": 0.71,
        "aiWhyRisky": "Years of sensitive corporate communications stored with static RSA keys represent a major target for state intelligence repositories.",
        "aiKeyFindings": [
            "Static RSA-2048 S/MIME certificates",
            "Cloud-hosted mailbox data stores"
        ],
        "createdAt": "2024-08-08T10:45:00Z",
        "lastScan": "12 hours ago"
    },
    {
        "id": "internal-vpn-gw",
        "name": "Internal Engineering VPN Gateway",
        "type": "Internal VPN",
        "size": "12 KB",
        "algorithm": "AES-256 (IKEv2 / ECC-P256)",
        "keySize": 256,
        "sensitivity": "High",
        "lifetime": "5-10 years",
        "exposure": "Internet",
        "cryptoRisk": 25,
        "sensitivityRisk": 18,
        "lifetimeRisk": 11,
        "exposureRisk": 14,
        "overallScore": 68,
        "riskLevel": "high",
        "pqcStatus": "Vulnerable",
        "recommendation": "Upgrade IPsec/IKEv2 tunnels with RFC 9370 Post-Quantum Preshared Keys (PPK) and ML-KEM.",
        "explanation": "While tunnel traffic is encrypted with AES-256, the Diffie-Hellman handshake uses classical ECC, allowing quantum adversaries to compute shared session keys and decrypt VPN payload streams.",
        "mlRiskLevel": "high",
        "mlConfidence": 0.83,
        "anomalyScore": 0.67,
        "aiWhyRisky": "VPN tunnels with vulnerable key exchange allow passive traffic recording with complete future reconstruction of internal network sessions.",
        "aiKeyFindings": [
            "IKEv2 handshake vulnerable to quantum key extraction",
            "High-privilege engineering traffic routed over connection"
        ],
        "createdAt": "2024-08-13T15:20:00Z",
        "lastScan": "4 hours ago"
    },
    {
        "id": "source-code-repo",
        "name": "Production Git Core Repository",
        "type": "Application",
        "size": "1.2 GB",
        "algorithm": "AES-256 / SHA-256",
        "keySize": 256,
        "sensitivity": "High",
        "lifetime": "Indefinite",
        "exposure": "Internal",
        "cryptoRisk": 4,
        "sensitivityRisk": 18,
        "lifetimeRisk": 20,
        "exposureRisk": 6,
        "overallScore": 48,
        "riskLevel": "medium",
        "pqcStatus": "Resistant",
        "recommendation": "Prepare commit signing for ML-DSA. Symmetric storage is quantum-safe.",
        "explanation": "Storage encrypted with AES-256. SHA-256 hash trees maintain quantum collision resistance of 128 bits against Brassard-Høyer-Tapp (BHT) algorithm.",
        "mlRiskLevel": "medium",
        "mlConfidence": 0.75,
        "anomalyScore": 0.50,
        "aiWhyRisky": "Low cryptographic risk for bulk storage; SSH/GPG commit signing keys will need eventual ML-DSA migration.",
        "aiKeyFindings": [
            "AES-256 data at rest is secure",
            "Future proofing SSH developer keys recommended"
        ],
        "createdAt": "2024-08-01T11:00:00Z",
        "lastScan": "2 days ago"
    },
    {
        "id": "public-marketing-cdn",
        "name": "Public Marketing CDN & Static Assets",
        "type": "Cloud Storage",
        "size": "210 MB",
        "algorithm": "AES-256",
        "keySize": 256,
        "sensitivity": "Low",
        "lifetime": "<1 year",
        "exposure": "Public",
        "cryptoRisk": 4,
        "sensitivityRisk": 5,
        "lifetimeRisk": 2,
        "exposureRisk": 14,
        "overallScore": 25,
        "riskLevel": "low",
        "pqcStatus": "Resistant",
        "recommendation": "No action required. Content is non-confidential.",
        "explanation": "Publicly accessible marketing content has zero confidentiality lifetime requirement and represents no HNDL threat.",
        "mlRiskLevel": "low",
        "mlConfidence": 0.60,
        "anomalyScore": 0.15,
        "aiWhyRisky": "Public data carries no harvest-now-decrypt-later impact.",
        "aiKeyFindings": [
            "Zero confidentiality requirement",
            "Quantum attack impact is null"
        ],
        "createdAt": "2024-08-02T16:00:00Z",
        "lastScan": "1 week ago"
    }
]

MOCK_RECOMMENDATIONS = [
    {
        "id": "rec-1",
        "currentAlgorithm": "RSA-2048",
        "riskLevel": "critical",
        "priority": "Immediate",
        "recommendedDirection": "Migrate to ML-KEM (FIPS 203 / Kyber-768/1024) for Key Encapsulation",
        "category": "Key Establishment",
        "details": "RSA-2048 is completely vulnerable to Shor's algorithm on a Cryptographically Relevant Quantum Computer (CRQC). Implement hybrid X25519+ML-KEM-768 across TLS termination points and API endpoints immediately to neutralize ongoing Harvest Now, Decrypt Later (HNDL) exposure."
    },
    {
        "id": "rec-2",
        "currentAlgorithm": "ECC (ECDSA P-256/P-384)",
        "riskLevel": "critical",
        "priority": "Immediate",
        "recommendedDirection": "Migrate to ML-DSA (FIPS 204 / Dilithium) & SLH-DSA (FIPS 205 / SPHINCS+)",
        "category": "Digital Signatures",
        "details": "Elliptic curve discrete logarithm instances will be solved in polynomial time by quantum adversaries. Plan structured migration of PKI root CAs, code signing infrastructure, and authentication tokens to ML-DSA."
    },
    {
        "id": "rec-3",
        "currentAlgorithm": "AES-128",
        "riskLevel": "high",
        "priority": "High",
        "recommendedDirection": "Upgrade Symmetric Encryption to AES-256-GCM",
        "category": "Symmetric Encryption",
        "details": "Grover's algorithm reduces the effective key search complexity of symmetric ciphers by half. AES-128 drops to an insecure 64-bit quantum strength. Upgrading to AES-256 restores a 128-bit quantum security margin."
    },
    {
        "id": "rec-4",
        "currentAlgorithm": "RSA-3072",
        "riskLevel": "high",
        "priority": "High",
        "recommendedDirection": "Transition to NIST Standardized ML-KEM and ML-DSA",
        "category": "Public Key Infrastructure",
        "details": "Increasing RSA key size to 3072 or 4096 bits provides negligible defense against quantum computing. Do not invest in larger RSA keys; transition directly to NIST post-quantum standards."
    },
    {
        "id": "rec-5",
        "currentAlgorithm": "Unknown / Undocumented",
        "riskLevel": "high",
        "priority": "High",
        "recommendedDirection": "Conduct Automated Deep Cryptographic Discovery",
        "category": "Discovery & Inventory",
        "details": "Undocumented cryptographic implementations and hardcoded keys create blind spots in your quantum defense posture. Deploy automated code and network scanners to catalog algorithm dependencies."
    },
    {
        "id": "rec-6",
        "currentAlgorithm": "SHA-256",
        "riskLevel": "low",
        "priority": "Low",
        "recommendedDirection": "Maintain Current Implementation; Prepare SHA-384 for Long-term Archives",
        "category": "Cryptographic Hashing",
        "details": "Quantum collision search (BHT algorithm) requires O(2^(n/3)) operations, giving SHA-256 approximately 85-128 bits of quantum collision resistance and 256-bit preimage resistance against Grover's algorithm."
    }
]

MOCK_MIGRATION_CATEGORIES = [
    {
        "name": "Key Establishment (KEM)",
        "status": "critical",
        "progress": 15,
        "target": "ML-KEM-768 / ML-KEM-1024 (FIPS 203)",
        "description": "Transitioning legacy RSA/DH/ECDH key exchange to hybrid post-quantum key encapsulation."
    },
    {
        "name": "Digital Signatures (DSA)",
        "status": "high",
        "progress": 30,
        "target": "ML-DSA-65 / ML-DSA-87 (FIPS 204)",
        "description": "Upgrading PKI certificates, JWTs, and code signing to quantum-resistant lattice signatures."
    },
    {
        "name": "Symmetric Encryption",
        "status": "medium",
        "progress": 65,
        "target": "AES-256-GCM / ChaCha20-Poly1305",
        "description": "Phasing out AES-128 and 3DES across databases, backups, and message queues."
    },
    {
        "name": "Cryptographic Hashing",
        "status": "low",
        "progress": 90,
        "target": "SHA-384 / SHA-512 / SHA-3",
        "description": "Ensuring hash function output sizes maintain sufficient collision bounds against BHT search."
    },
    {
        "name": "Certificate & PKI Hierarchy",
        "status": "high",
        "progress": 10,
        "target": "Hybrid PQC X.509 Certificates",
        "description": "Preparing enterprise Certificate Authorities for dual-algorithm signature verification."
    }
]

def calculate_quantum_risk(algorithm: str, key_size: int, sensitivity: str, lifetime: str, exposure: str) -> Dict[str, Any]:
    algo_upper = algorithm.upper()
    if "RSA-2048" in algo_upper or "RSA 2048" in algo_upper:
        crypto_risk = 35
    elif "RSA-3072" in algo_upper or "RSA 3072" in algo_upper:
        crypto_risk = 28
    elif "ECC" in algo_upper or "ECDSA" in algo_upper or "ECDH" in algo_upper:
        crypto_risk = 36
    elif "AES-128" in algo_upper or "AES 128" in algo_upper:
        crypto_risk = 18
    elif "AES-256" in algo_upper or "AES 256" in algo_upper:
        crypto_risk = 4
    elif "SHA-256" in algo_upper or "SHA-384" in algo_upper or "SHA-512" in algo_upper:
        crypto_risk = 3
    elif "ML-KEM" in algo_upper or "ML-DSA" in algo_upper or "PQC" in algo_upper:
        crypto_risk = 0
    else:
        crypto_risk = 30

    if "RSA" in algo_upper and key_size < 2048 and key_size > 0:
        crypto_risk = min(40, crypto_risk + 5)
    if "AES" in algo_upper and key_size < 128 and key_size > 0:
        crypto_risk = min(40, crypto_risk + 8)

    sens_lower = sensitivity.lower()
    if "critical" in sens_lower:
        sens_risk = 25
    elif "high" in sens_lower:
        sens_risk = 18
    elif "medium" in sens_lower:
        sens_risk = 12
    else:
        sens_risk = 5

    life_lower = lifetime.lower()
    if "20+" in life_lower or "indefinite" in life_lower or "forever" in life_lower:
        life_risk = 20
    elif "10-20" in life_lower or "10" in life_lower:
        life_risk = 16
    elif "5-10" in life_lower or "5" in life_lower:
        life_risk = 11
    elif "1-5" in life_lower or "1" in life_lower:
        life_risk = 6
    else:
        life_risk = 2

    exp_lower = exposure.lower()
    if "internet" in exp_lower or "public" in exp_lower:
        exp_risk = 14
    elif "cloud" in exp_lower or "external" in exp_lower:
        exp_risk = 10
    elif "internal" in exp_lower:
        exp_risk = 6
    else:
        exp_risk = 2

    overall_score = min(100, max(0, crypto_risk + sens_risk + life_risk + exp_risk))

    if overall_score >= 75:
        risk_level = "critical"
    elif overall_score >= 50:
        risk_level = "high"
    elif overall_score >= 25:
        risk_level = "medium"
    else:
        risk_level = "low"

    if "RSA" in algo_upper or "ECC" in algo_upper:
        explanation = f"This asset relies on classical public-key cryptography ({algorithm}) which will be broken in polynomial time by Shor's algorithm on a Cryptographically Relevant Quantum Computer (CRQC). Given the {sensitivity} sensitivity and {lifetime} confidentiality lifetime requirement, this asset is critically exposed to Harvest Now, Decrypt Later (HNDL) data hoarding."
        rec = "Prioritize immediate migration toward standardized post-quantum algorithms (ML-KEM for key encapsulation, ML-DSA/SLH-DSA for digital signatures). Deploy hybrid schemes during transition."
        ai_why = f"The public-key primitive ({algorithm}) offers zero post-quantum security. Adversaries recording this encrypted stream today will decrypt the data as soon as a CRQC reaches sufficient error-corrected qubit capacity."
        key_findings = [
            f"{algorithm} is fully vulnerable to Shor's quantum factoring algorithm",
            f"Data sensitivity is classified as {sensitivity} with {lifetime} retention liability",
            f"{exposure} exposure surface enables interception by state adversaries",
            "Compliant replacement: NIST FIPS 203 (ML-KEM) / FIPS 204 (ML-DSA)"
        ]
    elif "AES-128" in algo_upper:
        explanation = f"This asset uses {algorithm}. While symmetric ciphers are not broken by Shor's algorithm, Grover's quantum search halves effective key length from 128 to 64 bits, rendering it vulnerable to high-throughput quantum brute force."
        rec = "Upgrade symmetric cipher to AES-256 to guarantee a full 128-bit security margin under Grover's algorithm."
        ai_why = "Grover's algorithm reduces brute-force search complexity from O(2^N) to O(2^(N/2)). 128-bit keys become 64 bits of security, which is computationally insecure."
        key_findings = [
            "Effective security degraded to 64 bits by Grover's algorithm",
            "Upgrade to AES-256 restores 128-bit quantum security level",
            "Immediate configuration change recommended"
        ]
    elif "AES-256" in algo_upper or "SHA-256" in algo_upper:
        explanation = f"This asset utilizes {algorithm} which maintains robust quantum resistance (effective 128-bit security under Grover/BHT search). Verify that key exchange and wrapping keys are also quantum-safe."
        rec = "Maintain current symmetric implementation; audit key distribution mechanisms to ensure hybrid PQC key encapsulation."
        ai_why = "AES-256 provides 128 bits of security post-Grover, exceeding the quantum security requirements established by NIST and NSA CNSA 2.0."
        key_findings = [
            "Symmetric algorithm provides robust quantum resistance",
            "Auditing key exchange and KMS wrapping keys is recommended"
        ]
    else:
        explanation = f"This asset uses {algorithm}. Cryptographic discovery is required to identify exact cipher suite parameters and evaluate quantum vulnerability."
        rec = "Perform automated cryptographic discovery to identify underlying ciphers and key lengths."
        ai_why = "Undocumented or unknown algorithms represent security blind spots that prevent accurate quantum risk modeling."
        key_findings = [
            "Unverified cryptographic implementation",
            "Discovery and inventory recommended"
        ]

    return {
        "cryptoRisk": crypto_risk,
        "sensitivityRisk": sens_risk,
        "lifetimeRisk": life_risk,
        "exposureRisk": exp_risk,
        "overallScore": overall_score,
        "riskLevel": risk_level,
        "recommendation": rec,
        "explanation": explanation,
        "aiWhyRisky": ai_why,
        "aiKeyFindings": key_findings
    }

async def fetch_assets() -> List[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{API_BASE}/assets")
            if res.status_code == 200:
                data = res.json()
                if data.get("success") and data.get("data"):
                    return data["data"]
    except Exception:
        pass
    return MOCK_ASSETS

def get_current_user(request: Request) -> Dict[str, Any]:
    sid = request.cookies.get("qs_session")
    if sid and sid in SESSIONS:
        return SESSIONS[sid].get("user", {})
    return {"name": "Security Admin", "email": "admin@quantumshield.demo", "role": "ADMIN", "organization": "Acme Corp"}

@app.get("/", response_class=RedirectResponse)
async def root_redirect(request: Request):
    sid = request.cookies.get("qs_session")
    if sid and sid in SESSIONS:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    sid = request.cookies.get("qs_session")
    if sid and sid in SESSIONS:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    if email == "admin@quantumshield.demo" and password == "password123":
        user = {"name": "Alex Chen", "email": email, "role": "Chief Security Officer", "organization": "Acme Corp"}
    elif email and password:
        user = {"name": email.split("@")[0].capitalize(), "email": email, "role": "Security Engineer", "organization": "Acme Corp"}
    else:
        return templates.TemplateResponse(request=request, name="login.html", context={
            "request": request,
            "error": "Invalid email or password. Please use admin@quantumshield.demo / password123"
        })

    sid = str(uuid.uuid4())
    SESSIONS[sid] = {"user": user}
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("qs_session", sid, max_age=86400, httponly=True)
    return response

@app.get("/logout")
async def logout(request: Request):
    sid = request.cookies.get("qs_session")
    if sid and sid in SESSIONS:
        del SESSIONS[sid]
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("qs_session")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    user = get_current_user(request)
    assets = await fetch_assets()

    crit_count = sum(1 for a in assets if a.get("riskLevel") == "critical")
    high_count = sum(1 for a in assets if a.get("riskLevel") == "high")
    med_count = sum(1 for a in assets if a.get("riskLevel") == "medium")
    low_count = sum(1 for a in assets if a.get("riskLevel") == "low")

    algo_distribution = {
        "RSA": 5,
        "ECC": 3,
        "AES": 4,
        "SHA": 1,
        "PQC": 1
    }

    risk_distribution = {
        "critical": crit_count,
        "high": high_count,
        "medium": med_count,
        "low": low_count
    }

    risk_trend = [
        {"month": "Sep", "score": 68},
        {"month": "Oct", "score": 72},
        {"month": "Nov", "score": 79},
        {"month": "Dec", "score": 84},
        {"month": "Jan", "score": 89},
        {"month": "Feb", "score": 94}
    ]

    hndl_by_data_cat = [
        {"category": "Financial Data", "score": 94},
        {"category": "Customer PII", "score": 91},
        {"category": "R&D / IP", "score": 76},
        {"category": "Employee Data", "score": 75},
        {"category": "Email Archives", "score": 73},
        {"category": "Internal Strategy", "score": 53}
    ]

    summary = {
        "quantumRiskScore": 94,
        "riskLabel": "CRITICAL RISK",
        "assetsScanned": 1248,
        "quantumVulnerable": 327,
        "pqcReadiness": 42,
        "hndlExposure": "High",
        "criticalCount": crit_count,
        "highCount": high_count,
        "mediumCount": med_count,
        "lowCount": low_count
    }

    top_critical_assets = sorted(assets, key=lambda x: x.get("overallScore", 0), reverse=True)[:5]

    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "request": request,
        "user": user,
        "active_page": "dashboard",
        "summary": summary,
        "top_assets": top_critical_assets,
        "categories": MOCK_MIGRATION_CATEGORIES,
        "risk_dist_json": json.dumps(risk_distribution),
        "algo_dist_json": json.dumps(algo_distribution),
        "risk_trend_json": json.dumps(risk_trend),
        "hndl_cat_json": json.dumps(hndl_by_data_cat)
    })

@app.get("/assets", response_class=HTMLResponse)
async def assets_view(
    request: Request,
    search: str = Query("", alias="search"),
    risk: str = Query("all", alias="risk"),
    algo: str = Query("all", alias="algo"),
    type_filter: str = Query("all", alias="type")
):
    user = get_current_user(request)
    all_assets = await fetch_assets()

    filtered = all_assets
    if search:
        s = search.lower()
        filtered = [a for a in filtered if s in a.get("name", "").lower() or s in a.get("algorithm", "").lower() or s in a.get("type", "").lower()]
    if risk and risk != "all":
        filtered = [a for a in filtered if a.get("riskLevel", "").lower() == risk.lower()]
    if algo and algo != "all":
        filtered = [a for a in filtered if algo.lower() in a.get("algorithm", "").lower()]
    if type_filter and type_filter != "all":
        filtered = [a for a in filtered if type_filter.lower() in a.get("type", "").lower()]

    return templates.TemplateResponse(request=request, name="assets.html", context={
        "request": request,
        "user": user,
        "active_page": "assets",
        "assets": filtered,
        "total_count": len(filtered),
        "search": search,
        "risk_filter": risk,
        "algo_filter": algo
    })

@app.get("/partials/assets", response_class=HTMLResponse)
async def assets_table_partial(
    request: Request,
    search: str = Query("", alias="search"),
    risk: str = Query("all", alias="risk"),
    algo: str = Query("all", alias="algo"),
    type_filter: str = Query("all", alias="type")
):
    all_assets = await fetch_assets()
    filtered = all_assets
    if search:
        s = search.lower()
        filtered = [a for a in filtered if s in a.get("name", "").lower() or s in a.get("algorithm", "").lower() or s in a.get("type", "").lower()]
    if risk and risk != "all":
        filtered = [a for a in filtered if a.get("riskLevel", "").lower() == risk.lower()]
    if algo and algo != "all":
        filtered = [a for a in filtered if algo.lower() in a.get("algorithm", "").lower()]
    if type_filter and type_filter != "all":
        filtered = [a for a in filtered if type_filter.lower() in a.get("type", "").lower()]

    return templates.TemplateResponse(request=request, name="partials/_asset_table.html", context={
        "request": request,
        "assets": filtered,
        "total_count": len(filtered)
    })

@app.get("/assets/{asset_id}", response_class=HTMLResponse)
async def asset_detail_view(request: Request, asset_id: str):
    user = get_current_user(request)
    assets = await fetch_assets()
    asset = next((a for a in assets if a.get("id") == asset_id), None)
    if not asset:
        asset = MOCK_ASSETS[0]

    return templates.TemplateResponse(request=request, name="asset_detail.html", context={
        "request": request,
        "user": user,
        "active_page": "assets",
        "asset": asset
    })

@app.get("/scanner", response_class=HTMLResponse)
async def scanner_view(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(request=request, name="scanner.html", context={
        "request": request,
        "user": user,
        "active_page": "scanner"
    })

@app.post("/partials/scanner/run", response_class=HTMLResponse)
async def scanner_run(
    request: Request,
    asset_name: str = Form(...),
    asset_type: str = Form("Database"),
    endpoint: str = Form("10.0.4.12:5432"),
    algorithm: str = Form("RSA-2048"),
    key_size: int = Form(2048),
    protocol: str = Form("TLS 1.3 / IPsec"),
    sensitivity: str = Form("Critical"),
    lifetime: str = Form("20+ years"),
    exposure: str = Form("Internet")
):
    risk_output = calculate_quantum_risk(algorithm, key_size, sensitivity, lifetime, exposure)

    new_asset = {
        "id": f"asset-scan-{uuid.uuid4().hex[:8]}",
        "name": asset_name,
        "type": asset_type,
        "size": "1.5 GB",
        "algorithm": algorithm,
        "keySize": key_size,
        "protocol": protocol,
        "endpoint": endpoint,
        "sensitivity": sensitivity,
        "lifetime": lifetime,
        "exposure": exposure,
        "cryptoRisk": risk_output["cryptoRisk"],
        "sensitivityRisk": risk_output["sensitivityRisk"],
        "lifetimeRisk": risk_output["lifetimeRisk"],
        "exposureRisk": risk_output["exposureRisk"],
        "overallScore": risk_output["overallScore"],
        "riskLevel": risk_output["riskLevel"],
        "pqcStatus": "Vulnerable" if risk_output["overallScore"] >= 60 else ("Weakened" if risk_output["overallScore"] >= 40 else "Resistant"),
        "recommendation": risk_output["recommendation"],
        "explanation": risk_output["explanation"],
        "aiWhyRisky": risk_output["aiWhyRisky"],
        "aiKeyFindings": risk_output["aiKeyFindings"],
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "lastScan": "Just now"
    }

    MOCK_ASSETS.insert(0, new_asset)

    return templates.TemplateResponse(request=request, name="partials/_scan_result_content.html", context={
        "request": request,
        "asset": new_asset
    })

@app.get("/scan-results/{asset_id}", response_class=HTMLResponse)
async def scan_results_page(request: Request, asset_id: str):
    user = get_current_user(request)
    asset = next((a for a in MOCK_ASSETS if a.get("id") == asset_id), MOCK_ASSETS[0])
    return templates.TemplateResponse(request=request, name="scan_results.html", context={
        "request": request,
        "user": user,
        "active_page": "scanner",
        "asset": asset
    })

@app.get("/risk", response_class=HTMLResponse)
async def risk_view(request: Request):
    user = get_current_user(request)
    assets = await fetch_assets()
    top_assets = sorted(assets, key=lambda x: x.get("overallScore", 0), reverse=True)[:8]

    crit_count = sum(1 for a in assets if a.get("riskLevel") == "critical")
    high_count = sum(1 for a in assets if a.get("riskLevel") == "high")
    med_count = sum(1 for a in assets if a.get("riskLevel") == "medium")
    low_count = sum(1 for a in assets if a.get("riskLevel") == "low")

    risk_distribution = {
        "critical": crit_count,
        "high": high_count,
        "medium": med_count,
        "low": low_count
    }

    risk_trend = [
        {"month": "Sep", "score": 68},
        {"month": "Oct", "score": 72},
        {"month": "Nov", "score": 79},
        {"month": "Dec", "score": 84},
        {"month": "Jan", "score": 89},
        {"month": "Feb", "score": 94}
    ]

    return templates.TemplateResponse(request=request, name="risk.html", context={
        "request": request,
        "user": user,
        "active_page": "risk",
        "overall_score": 94,
        "risk_level": "CRITICAL RISK",
        "top_assets": top_assets,
        "risk_dist_json": json.dumps(risk_distribution),
        "risk_trend_json": json.dumps(risk_trend)
    })

@app.get("/hndl", response_class=HTMLResponse)
async def hndl_view(request: Request):
    user = get_current_user(request)
    assets = await fetch_assets()
    hndl_assets = [a for a in assets if a.get("overallScore", 0) >= 60]

    hndl_categories = [
        {"category": "Financial Ledger Records", "score": 94, "urgency": "Immediate", "volume": "2.4 GB", "threat": "Adversary intercepts live transactions today for retrospective ledger cracking."},
        {"category": "Customer PII & Biometric Auth", "score": 91, "urgency": "Immediate", "volume": "14.2 GB", "threat": "Authentication tokens and identity credentials hoarded for indefinite impersonation."},
        {"category": "Proprietary Research & IP", "score": 76, "urgency": "High", "volume": "5.6 GB", "threat": "Patent-pending algorithms and product schematics exfiltrated from cloud sync stores."},
        {"category": "Employee Medical & HR Records", "score": 75, "urgency": "High", "volume": "850 MB", "threat": "High-liability personal employee records with 20+ year regulatory privacy retention."},
        {"category": "Executive Email Archives", "score": 73, "urgency": "High", "volume": "88 GB", "threat": "Bulk encrypted S/MIME communications archived in cloud mail repositories."},
        {"category": "Corporate M&A Strategy", "score": 53, "urgency": "Medium", "volume": "4.8 MB", "threat": "AES-128 weakened to 64-bit quantum entropy; susceptible to fast key search." }
    ]

    return templates.TemplateResponse(request=request, name="hndl.html", context={
        "request": request,
        "user": user,
        "active_page": "hndl",
        "hndl_assets": hndl_assets,
        "hndl_categories": hndl_categories,
        "hndl_categories_json": json.dumps([{"name": c["category"], "score": c["score"]} for c in hndl_categories])
    })

@app.get("/pqc", response_class=HTMLResponse)
async def pqc_view(request: Request):
    user = get_current_user(request)
    assets = await fetch_assets()

    algo_distribution = {
        "RSA": 5,
        "ECC": 3,
        "AES": 4,
        "SHA": 1,
        "PQC": 1
    }

    return templates.TemplateResponse(request=request, name="pqc.html", context={
        "request": request,
        "user": user,
        "active_page": "pqc",
        "readiness_score": 42,
        "categories": MOCK_MIGRATION_CATEGORIES,
        "categories_json": json.dumps([{"name": c["name"], "progress": c["progress"]} for c in MOCK_MIGRATION_CATEGORIES]),
        "algo_dist_json": json.dumps(algo_distribution)
    })

@app.get("/roadmap", response_class=HTMLResponse)
async def roadmap_view(request: Request):
    user = get_current_user(request)
    phases = [
        {
            "phase": 1,
            "name": "Discover & Inventory",
            "status": "Completed",
            "progress": 100,
            "badge": "completed",
            "timeline": "Q1 2024 (Months 1-3)",
            "description": "Catalog all cryptographic assets, ciphers, key lengths, certificates, and endpoints across cloud, on-prem, and edge.",
            "tasks": [
                "Automated scan of network ingress/egress endpoints",
                "Static code analysis for hardcoded cryptographic primitives",
                "Compile Software Bill of Materials (SBOM) and Cryptographic BOM (CBOM)",
                "Establish continuous cryptographic inventory telemetry"
            ],
            "deliverables": "Comprehensive CBOM Catalog with 1,248 cataloged cryptographic dependencies."
        },
        {
            "phase": 2,
            "name": "Assess & Classify Risk",
            "status": "Completed",
            "progress": 100,
            "badge": "completed",
            "timeline": "Q2 2024 (Months 4-6)",
            "description": "Apply Mosca's Theorem (X + Y > Z) and quantum threat modeling across data sensitivity and confidentiality lifecycle.",
            "tasks": [
                "Map data retention mandates (HIPAA, GDPR, PCI-DSS)",
                "Quantify HNDL exposure across public network boundaries",
                "Execute ML-assisted anomaly and cryptographic vulnerability scoring",
                "Establish baseline Quantum Risk Index (94/100)"
            ],
            "deliverables": "Cryptographic Risk Matrix and Board-level Quantum Readiness Briefing."
        },
        {
            "phase": 3,
            "name": "Prioritize & Formulate Strategy",
            "status": "In Progress",
            "progress": 65,
            "badge": "in-progress",
            "timeline": "Q3 2024 (Months 7-9)",
            "description": "Rank assets by HNDL vulnerability and establish algorithm migration specifications aligned with NIST FIPS 203/204/205.",
            "tasks": [
                "Isolate top 20 critical public-key assets (Ledger, Identity DB, TLS Ingress)",
                "Draft enterprise Crypto-Agility Architecture blueprint",
                "Formulate algorithm replacement matrix (RSA -> ML-KEM, ECC -> ML-DSA)",
                "Select certified PQC hardware security module (HSM) vendors"
            ],
            "deliverables": "Enterprise PQC Migration Strategy & Vendor Procurement Checklist."
        },
        {
            "phase": 4,
            "name": "Pilot PQC & Test Sandboxes",
            "status": "In Progress",
            "progress": 30,
            "badge": "in-progress",
            "timeline": "Q4 2024 - Q1 2025 (Months 10-15)",
            "description": "Deploy non-production testbeds with hybrid post-quantum key encapsulation mechanisms and digital signature schemes.",
            "tasks": [
                "Benchmark ML-KEM-768 key exchange latency in staging API gateways",
                "Evaluate ML-DSA-65 certificate chain size overhead on MTU limits",
                "Test interoperability with legacy client systems",
                "Validate backward compatibility fallback controls"
            ],
            "deliverables": "PQC Staging Benchmark Report & Latency Impact Assessment."
        },
        {
            "phase": 5,
            "name": "Hybrid Deployment",
            "status": "Pending",
            "progress": 0,
            "badge": "pending",
            "timeline": "Q2 2025 - Q4 2025 (Months 16-24)",
            "description": "Roll out dual-algorithm hybrid encryption (Classical + NIST PQC) to achieve defense-in-depth across production ingress.",
            "tasks": [
                "Deploy hybrid TLS 1.3 (X25519 + Kyber-768) on edge load balancers",
                "Upgrade IPsec VPN tunnels with RFC 9370 Post-Quantum PSKs",
                "Re-wrap sensitive database column master keys with ML-KEM",
                "Issue dual-signed internal root and intermediate CA certificates"
            ],
            "deliverables": "Zero-Downtime Production Hybrid Deployment across Tier 1 Services."
        },
        {
            "phase": 6,
            "name": "Full PQC Migration & Agility",
            "status": "Pending",
            "progress": 0,
            "badge": "pending",
            "timeline": "2026+ (Continuous)",
            "description": "Deprecate all legacy asymmetric primitives, achieve pure quantum-proof operations, and enforce continuous crypto-agility.",
            "tasks": [
                "Decommission legacy RSA and ECC keys and certificates",
                "Audit third-party SaaS vendors for mandatory PQC compliance",
                "Establish automated quantum-risk continuous compliance monitor",
                "Conduct annual cryptographic agility drills and penetration testing"
            ],
            "deliverables": "Full Quantum Compliance Certification & Automated Continuous Governance."
        }
    ]

    return templates.TemplateResponse(request=request, name="roadmap.html", context={
        "request": request,
        "user": user,
        "active_page": "roadmap",
        "phases": phases,
        "overall_progress": 49
    })

@app.get("/recommendations", response_class=HTMLResponse)
async def recommendations_view(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(request=request, name="recommendations.html", context={
        "request": request,
        "user": user,
        "active_page": "recommendations",
        "recommendations": MOCK_RECOMMENDATIONS
    })

@app.get("/reports", response_class=HTMLResponse)
async def reports_view(request: Request):
    user = get_current_user(request)
    reports = [
        {
            "id": "rep-quantum-risk-2024-q3",
            "title": "Executive Quantum Risk Assessment Report",
            "type": "Risk Analysis",
            "format": "PDF / JSON",
            "generatedAt": "August 28, 2024",
            "author": "QuantumShield Risk Engine v2.4",
            "summary": "Comprehensive audit of 1,248 cryptographic assets, identifying 327 vulnerable asymmetric implementations with high HNDL liability.",
            "downloadUrl": "#"
        },
        {
            "id": "rep-pqc-readiness-fips",
            "title": "NIST FIPS 203/204/205 PQC Compliance Roadmap",
            "type": "PQC Readiness",
            "format": "PDF / XLSX",
            "generatedAt": "August 25, 2024",
            "author": "Cryptographic Governance Module",
            "summary": "Strategic migration specifications for transitioning RSA/ECC primitives to ML-KEM, ML-DSA, and SLH-DSA across Tier 1 infra.",
            "downloadUrl": "#"
        },
        {
            "id": "rep-hndl-exposure-audit",
            "title": "Harvest Now, Decrypt Later (HNDL) Threat Analysis",
            "type": "Threat Intelligence",
            "format": "PDF",
            "generatedAt": "August 20, 2024",
            "author": "AI Threat Intelligence Engine",
            "summary": "Quantification of intercepted data liability across financial databases, customer PII, and executive email stores.",
            "downloadUrl": "#"
        },
        {
            "id": "rep-crypto-inventory-cbom",
            "title": "Enterprise Cryptographic Bill of Materials (CBOM)",
            "type": "Asset Inventory",
            "format": "JSON / CSV / SPDX",
            "generatedAt": "August 18, 2024",
            "author": "Automated Asset Discovery Scanner",
            "summary": "Full machine-readable export of all algorithms, key sizes, cipher modes, protocols, and TLS certificates.",
            "downloadUrl": "#"
        }
    ]

    return templates.TemplateResponse(request=request, name="reports.html", context={
        "request": request,
        "user": user,
        "active_page": "reports",
        "reports": reports
    })

@app.get("/settings", response_class=HTMLResponse)
async def settings_view(request: Request, saved: Optional[str] = None):
    user = get_current_user(request)
    settings = {
        "organizationName": "Acme Corp",
        "industry": "Technology / Financial Services",
        "contactEmail": "security@acmecorp.com",
        "autoScan": True,
        "scanFrequency": "Weekly",
        "emailNotifs": True,
        "cryptoWeight": 40,
        "sensitivityWeight": 25,
        "lifetimeWeight": 20,
        "exposureWeight": 15,
        "criticalAlerts": True,
        "highRiskAlerts": True,
        "scanAlerts": False,
        "summaryAlerts": True,
        "apiKey": "qs_live_9f82d1c07e84ab21762c4491de88"
    }

    return templates.TemplateResponse(request=request, name="settings.html", context={
        "request": request,
        "user": user,
        "active_page": "settings",
        "settings": settings,
        "saved": saved == "1"
    })

@app.post("/settings", response_class=HTMLResponse)
async def settings_save(
    request: Request,
    organizationName: str = Form("Acme Corp"),
    industry: str = Form("Technology"),
    contactEmail: str = Form("security@acmecorp.com"),
    scanFrequency: str = Form("Weekly"),
    cryptoWeight: int = Form(40),
    sensitivityWeight: int = Form(25),
    lifetimeWeight: int = Form(20),
    exposureWeight: int = Form(15)
):
    user = get_current_user(request)
    return RedirectResponse(url="/settings?saved=1", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

