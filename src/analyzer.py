import re
import urllib.parse
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ThreatLevel(Enum):
    SAFE = ("SAFE", "🟢", 0)
    LOW = ("LOW", "🟡", 25)
    MEDIUM = ("MEDIUM", "🟠", 50)
    HIGH = ("HIGH", "🔴", 75)
    CRITICAL = ("CRITICAL", "🚨", 90)
    
    def __init__(self, label, emoji, base_score):
        self.label = label
        self.emoji = emoji
        self.base_score = base_score

@dataclass
class AnalysisResult:
    content: str
    risk_score: int
    threat_level: ThreatLevel
    flags: List[str]
    analysis_type: str  # 'email' or 'link'
    
    def is_suspicious(self) -> bool:
        return self.risk_score >= 25

class EmailLinkAnalyzer:
    def __init__(self):
        # Suspicious keywords with risk weights
        self.suspicious_keywords = {
            'urgent': 15, 'verify': 15, 'suspend': 20, 'locked': 20,
            'prize': 15, 'winner': 15, 'congratulations': 10, 'claim': 15,
            'click here': 10, 'act now': 15, 'limited time': 10,
            'account': 10, 'password': 15, 'security': 10, 'confirm': 10,
            'update': 10, 'banking': 15, 'paypal': 15, 'amazon': 10,
            'refund': 12, 'tax': 12, 'irs': 15, 'government': 12,
            'free': 8, 'offer': 8, 'bonus': 8, 'gift': 8
        }
        
        # Suspicious TLDs
        self.suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.gq', '.zip', '.mov', '.xyz',
            '.top', '.work', '.date', '.download', '.stream', '.loan'
        ]
        
        # Legitimate domains for comparison
        self.legitimate_domains = [
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
            'facebook.com', 'twitter.com', 'linkedin.com', 'github.com',
            'stackoverflow.com', 'wikipedia.org', 'youtube.com'
        ]
        
        # URL shorteners
        self.url_shorteners = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 't.co',
            'is.gd', 'buff.ly', 'adf.ly', 'short.io', 'rebrand.ly'
        ]
        
        # Personal information patterns
        self.personal_info_patterns = [
            r'social\s*security\s*(number|#|no)',
            r'credit\s*card\s*(number|#|no)',
            r'bank\s*account',
            r'driver[\'s]?\s*license',
            r'passport\s*(number|#|no)',
            r'date\s*of\s*birth',
            r'mother[\'s]?\s*maiden\s*name',
            r'pin\s*(number|code)',
            r'cvv',
            r'security\s*code'
        ]

    def analyze_email(self, email_data: Dict) -> AnalysisResult:
        """Analyze email content for phishing indicators"""
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        sender = email_data.get('sender', '')
        links = email_data.get('links', [])
        
        combined_text = f"{subject} {body} {sender}".lower()
        risk_score = 0
        flags = []
        
        # 1. Check suspicious keywords
        keyword_score, keyword_flags = self._check_keywords(combined_text)
        risk_score += keyword_score
        flags.extend(keyword_flags)
        
        # 2. Check sender domain
        sender_score, sender_flags = self._check_sender_domain(sender)
        risk_score += sender_score
        flags.extend(sender_flags)
        
        # 3. Check for personal information requests
        personal_score, personal_flags = self._check_personal_info_requests(combined_text)
        risk_score += personal_score
        flags.extend(personal_flags)
        
        # 4. Analyze embedded links
        for link in links:
            link_score, link_flags = self._analyze_single_link(link)
            risk_score += min(link_score, 30)  # Cap link contribution
            flags.extend([f"Link: {flag}" for flag in link_flags])
        
        # 5. Check urgency indicators
        urgency_score, urgency_flags = self._check_urgency(combined_text)
        risk_score += urgency_score
        flags.extend(urgency_flags)
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        threat_level = self._calculate_threat_level(risk_score)
        
        return AnalysisResult(
            content=f"From: {sender}\nSubject: {subject}",
            risk_score=risk_score,
            threat_level=threat_level,
            flags=flags,
            analysis_type='email'
        )
    
    def analyze_link(self, url: str) -> AnalysisResult:
        """Analyze a single URL for suspicious indicators"""
        risk_score = 0
        flags = []
        
        link_score, link_flags = self._analyze_single_link(url)
        risk_score = link_score
        flags = link_flags
        
        threat_level = self._calculate_threat_level(risk_score)
        
        return AnalysisResult(
            content=url,
            risk_score=risk_score,
            threat_level=threat_level,
            flags=flags,
            analysis_type='link'
        )
    
    def _analyze_single_link(self, url: str) -> Tuple[int, List[str]]:
        """Analyze a single URL and return score and flags"""
        score = 0
        flags = []
        
        try:
            # Parse URL
            parsed = urllib.parse.urlparse(url.lower())
            domain = parsed.netloc or parsed.path.split('/')[0]
            
            # 1. Check for IP address instead of domain
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                score += 25
                flags.append("IP address used instead of domain name")
            
            # 2. Check suspicious TLDs
            for tld in self.suspicious_tlds:
                if domain.endswith(tld):
                    score += 20
                    flags.append(f"Suspicious TLD: {tld}")
                    break
            
            # 3. Check URL shorteners
            for shortener in self.url_shorteners:
                if shortener in domain:
                    score += 15
                    flags.append("URL shortener detected (hides real destination)")
                    break
            
            # 4. Check domain spoofing
            spoof_score, spoof_flags = self._check_domain_spoofing(domain)
            score += spoof_score
            flags.extend(spoof_flags)
            
            # 5. Check excessive subdomains
            subdomain_parts = domain.split('.')
            if len(subdomain_parts) > 4:
                score += 15
                flags.append("Excessive subdomains detected")
            
            # 6. Check for suspicious characters
            if '@' in url:
                score += 20
                flags.append("@ symbol in URL (potential obfuscation)")
            
            # 7. Check URL length
            if len(url) > 150:
                score += 10
                flags.append("Unusually long URL")
            
            # 8. Check for data/javascript schemes
            if parsed.scheme in ['data', 'javascript']:
                score += 30
                flags.append(f"Suspicious URL scheme: {parsed.scheme}")
            
            # 9. Check for hex encoding
            if '%' in url and url.count('%') > 3:
                score += 12
                flags.append("Heavy URL encoding detected")
            
        except Exception as e:
            score += 10
            flags.append("Malformed URL structure")
        
        return score, flags
    
    def _check_keywords(self, text: str) -> Tuple[int, List[str]]:
        """Check for suspicious keywords"""
        score = 0
        flags = []
        found_keywords = []
        
        for keyword, weight in self.suspicious_keywords.items():
            if keyword in text:
                score += weight
                found_keywords.append(keyword)
        
        if found_keywords:
            flags.append(f"Suspicious keywords: {', '.join(found_keywords[:5])}")
        
        return min(score, 40), flags  # Cap keyword score
    
    def _check_sender_domain(self, sender: str) -> Tuple[int, List[str]]:
        """Check sender email domain for spoofing"""
        score = 0
        flags = []
        
        if not sender:
            return 0, []
        
        try:
            # Extract domain
            domain = sender.split('@')[1].lower() if '@' in sender else ''
            
            # Check for lookalike domains
            for legit_domain in self.legitimate_domains:
                if domain != legit_domain and legit_domain.replace('.', '') in domain.replace('.', ''):
                    score += 25
                    flags.append(f"Potential domain spoofing: {domain} (mimics {legit_domain})")
                    break
            
            # Check for suspicious patterns
            if re.search(r'\d{4,}', domain):  # Multiple digits
                score += 10
                flags.append("Suspicious numbers in domain")
            
            if domain.count('-') > 2:
                score += 10
                flags.append("Multiple hyphens in domain")
                
        except:
            pass
        
        return score, flags
    
    def _check_personal_info_requests(self, text: str) -> Tuple[int, List[str]]:
        """Check for personal information requests"""
        score = 0
        flags = []
        found_patterns = []
        
        for pattern in self.personal_info_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 20
                match = re.search(pattern, text, re.IGNORECASE)
                found_patterns.append(match.group(0))
        
        if found_patterns:
            flags.append(f"Requests personal information: {', '.join(found_patterns[:3])}")
        
        return min(score, 40), flags  # Cap personal info score
    
    def _check_urgency(self, text: str) -> Tuple[int, List[str]]:
        """Check for urgency tactics"""
        urgency_patterns = [
            'immediate action', 'within 24 hours', 'expires today',
            'act now', 'urgent', 'immediately', 'right now',
            'don\'t wait', 'last chance', 'final notice'
        ]
        
        score = 0
        flags = []
        found = []
        
        for pattern in urgency_patterns:
            if pattern in text:
                score += 8
                found.append(pattern)
        
        if found:
            flags.append("Uses urgency tactics to pressure action")
        
        return min(score, 25), flags
    
    def _check_domain_spoofing(self, domain: str) -> Tuple[int, List[str]]:
        """Check for domain spoofing techniques"""
        score = 0
        flags = []
        
        # Homograph attack characters
        suspicious_chars = ['і', 'о', 'а', 'е', 'р', 'с', 'у', 'х']  # Cyrillic lookalikes
        
        for char in suspicious_chars:
            if char in domain:
                score += 25
                flags.append("Possible homograph attack (lookalike characters)")
                break
        
        # Check for common typosquatting patterns
        typosquat_patterns = [
            r'(gogle|gooogle|googel)',
            r'(micorsoft|microsft|micosoft)',
            r'(amazonn|amazom|amaz0n)',
            r'(paypa1|paypai|paypa|paypall)'
        ]
        
        for pattern in typosquat_patterns:
            if re.search(pattern, domain):
                score += 20
                flags.append("Possible typosquatting detected")
                break
        
        return score, flags
    
    def _calculate_threat_level(self, risk_score: int) -> ThreatLevel:
        """Calculate threat level based on risk score"""
        if risk_score < 25:
            return ThreatLevel.SAFE
        elif risk_score < 50:
            return ThreatLevel.LOW
        elif risk_score < 70:
            return ThreatLevel.MEDIUM
        elif risk_score < 85:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL