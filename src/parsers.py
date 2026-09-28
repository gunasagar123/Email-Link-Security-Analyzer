import re
import json
import csv
from io import StringIO
from typing import List, Dict, Any

class SmartEmailParser:
    """Intelligent parser that handles ANY email file format"""
    
    def parse(self, file_content: str, filename: str) -> List[Dict[str, Any]]:
        """
        Auto-detect format and parse emails
        Returns list of email dictionaries with keys: sender, subject, body, links
        """
        file_extension = self._get_extension(filename)
        
        try:
            # Try specific format parsers first
            if file_extension == '.json':
                return self._parse_json(file_content)
            elif file_extension == '.csv':
                return self._parse_csv(file_content)
            elif file_extension == '.eml':
                return self._parse_eml(file_content)
            else:
                # Use smart text parser for unknown formats
                return self._smart_parse_text(file_content)
        except Exception as e:
            # Fallback to smart parser if specific parser fails
            return self._smart_parse_text(file_content)
    
    def _get_extension(self, filename: str) -> str:
        """Extract file extension"""
        if '.' in filename:
            return '.' + filename.rsplit('.', 1)[1].lower()
        return ''
    
    def _parse_json(self, content: str) -> List[Dict[str, Any]]:
        """Parse JSON format"""
        data = json.loads(content)
        
        # Handle different JSON structures
        if isinstance(data, list):
            emails = data
        elif isinstance(data, dict):
            emails = data.get('emails', [data])
        else:
            return []
        
        # Normalize keys (handle different naming conventions)
        normalized = []
        for email in emails:
            normalized.append({
                'sender': email.get('sender') or email.get('from') or email.get('email') or '',
                'subject': email.get('subject') or email.get('title') or '',
                'body': email.get('body') or email.get('content') or email.get('message') or '',
                'links': email.get('links') or email.get('urls') or []
            })
        
        return normalized
    
    def _parse_csv(self, content: str) -> List[Dict[str, Any]]:
        """Parse CSV format"""
        emails = []
        
        try:
            csv_reader = csv.DictReader(StringIO(content))
            
            for row in csv_reader:
                # Handle different column names
                sender = (row.get('sender') or row.get('from') or 
                         row.get('email') or row.get('From') or '')
                subject = (row.get('subject') or row.get('Subject') or 
                          row.get('title') or '')
                body = (row.get('body') or row.get('Body') or 
                       row.get('content') or row.get('message') or '')
                links_str = (row.get('links') or row.get('urls') or 
                            row.get('Links') or '')
                
                # Parse links (comma or space separated)
                links = []
                if links_str:
                    links = [l.strip() for l in re.split(r'[,\s]+', links_str) if l.strip()]
                
                emails.append({
                    'sender': sender,
                    'subject': subject,
                    'body': body,
                    'links': links
                })
        except Exception:
            # If CSV parsing fails, treat as text
            return self._smart_parse_text(content)
        
        return emails
    
    def _parse_eml(self, content: str) -> List[Dict[str, Any]]:
        """Parse .eml or email-like format"""
        emails = []
        
        # Split by common email separators
        sections = re.split(r'\n\s*\n---|^\s*From\s+\w+', content, flags=re.MULTILINE)
        
        for section in sections:
            if not section.strip():
                continue
            
            email_data = {
                'sender': self._extract_sender(section),
                'subject': self._extract_subject(section),
                'body': self._extract_body(section),
                'links': self._extract_links(section)
            }
            
            # Only add if we found at least some content
            if email_data['sender'] or email_data['subject'] or email_data['body']:
                emails.append(email_data)
        
        return emails if emails else self._smart_parse_text(content)
    
    def _smart_parse_text(self, content: str) -> List[Dict[str, Any]]:
        """
        Intelligent parsing for ANY text format
        This is the fallback that handles unknown formats
        """
        emails = []
        
        # Try to split into multiple emails
        # Common separators: ---, ***, blank lines, "From:", new email patterns
        sections = re.split(r'\n\s*[-=*]{3,}\s*\n|\n\s*From\s+[\w\.-]+@[\w\.-]+', 
                          content, flags=re.IGNORECASE)
        
        # If no clear sections, treat entire content as one email
        if len(sections) <= 1:
            sections = [content]
        
        for section in sections:
            if not section.strip() or len(section.strip()) < 10:
                continue
            
            email_data = {
                'sender': self._extract_sender(section),
                'subject': self._extract_subject(section),
                'body': self._extract_body(section),
                'links': self._extract_links(section)
            }
            
            emails.append(email_data)
        
        return emails
    
    def _extract_sender(self, text: str) -> str:
        """Extract sender email from text"""
        # Pattern 1: "From: email@domain.com"
        match = re.search(r'From:\s*([\w\.-]+@[\w\.-]+\.\w+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 2: "Sender: email@domain.com"
        match = re.search(r'Sender:\s*([\w\.-]+@[\w\.-]+\.\w+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 3: Just find any email address
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if match:
            return match.group(0)
        
        return ''
    
    def _extract_subject(self, text: str) -> str:
        """Extract subject from text"""
        # Pattern 1: "Subject: ..."
        match = re.search(r'Subject:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 2: "Re: ..." or "RE: ..."
        match = re.search(r'Re:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 3: First line if it looks like a subject
        lines = text.strip().split('\n')
        if lines and len(lines[0]) < 100 and not '@' in lines[0]:
            return lines[0].strip()
        
        return ''
    
    def _extract_body(self, text: str) -> str:
        """Extract email body"""
        # Remove From and Subject lines
        body = re.sub(r'From:\s*.*?\n', '', text, flags=re.IGNORECASE)
        body = re.sub(r'Sender:\s*.*?\n', '', body, flags=re.IGNORECASE)
        body = re.sub(r'Subject:\s*.*?\n', '', body, flags=re.IGNORECASE)
        body = re.sub(r'Re:\s*.*?\n', '', body, flags=re.IGNORECASE)
        
        return body.strip()
    
    def _extract_links(self, text: str) -> List[str]:
        """Extract all URLs from text"""
        # Pattern for full URLs
        urls = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            text
        )
        
        # Pattern for www. URLs
        www_urls = re.findall(r'www\.[\w\.-]+\.[\w\./]+', text)
        urls.extend(['http://' + url for url in www_urls])
        
        return list(set(urls))  # Remove duplicates


class SmartLinkParser:
    """Intelligent parser that extracts links from ANY text file"""
    
    def parse(self, file_content: str, filename: str) -> List[str]:
        """
        Extract ALL URLs from any text format
        Returns list of URLs
        """
        file_extension = self._get_extension(filename)
        
        try:
            if file_extension == '.csv':
                return self._parse_csv(file_content)
            else:
                return self._extract_all_urls(file_content)
        except Exception:
            return self._extract_all_urls(file_content)
    
    def _get_extension(self, filename: str) -> str:
        """Extract file extension"""
        if '.' in filename:
            return '.' + filename.rsplit('.', 1)[1].lower()
        return ''
    
    def _parse_csv(self, content: str) -> List[str]:
        """Parse URLs from CSV format"""
        urls = []
        
        try:
            csv_reader = csv.reader(StringIO(content))
            for row in csv_reader:
                for cell in row:
                    # Extract URLs from each cell
                    cell_urls = self._extract_all_urls(cell)
                    urls.extend(cell_urls)
        except Exception:
            # If CSV parsing fails, extract as plain text
            return self._extract_all_urls(content)
        
        return list(set(urls))  # Remove duplicates
    
    def _extract_all_urls(self, text: str) -> List[str]:
        """
        Extract ALL URLs from text using multiple patterns
        This works on ANY format of text
        """
        urls = []
        
        # Pattern 1: Full URLs with http/https
        pattern1 = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls.extend(re.findall(pattern1, text))
        
        # Pattern 2: www. URLs
        pattern2 = r'www\.[\w\.-]+\.[\w\./]+'
        www_urls = re.findall(pattern2, text)
        urls.extend(['http://' + url for url in www_urls if url not in urls])
        
        # Pattern 3: Domain-like patterns (domain.com/path)
        pattern3 = r'(?<![\/\w])[\w\-]+\.(?:com|org|net|edu|gov|mil|int|co|io|ai|app|dev|xyz|tk|ml|ga|cf|gq)(?:\/[\w\-\.\/]*)?'
        potential_urls = re.findall(pattern3, text)
        for url in potential_urls:
            if url not in urls and not url.startswith('http'):
                urls.append('http://' + url)
        
        # Pattern 4: Shortened URLs (bit.ly, tinyurl, etc.)
        pattern4 = r'(?:bit\.ly|tinyurl\.com|goo\.gl|ow\.ly|t\.co|is\.gd)\/[\w\-]+'
        short_urls = re.findall(pattern4, text)
        for url in short_urls:
            if not url.startswith('http'):
                urls.append('http://' + url)
            else:
                urls.append(url)
        
        # Clean and deduplicate
        cleaned_urls = []
        for url in urls:
            url = url.strip()
            # Remove trailing punctuation
            url = re.sub(r'[,;.!?\)]+$', '', url)
            if url and url not in cleaned_urls:
                cleaned_urls.append(url)
        
        return cleaned_urls


def parse_uploaded_file(file_content: str, filename: str, file_type: str) -> Dict[str, Any]:
    """
    Main entry point for parsing uploaded files
    
    Args:
        file_content: The text content of the uploaded file
        filename: Original filename
        file_type: 'email' or 'link'
    
    Returns:
        Dictionary with parsed data and metadata
    """
    if file_type == 'email':
        parser = SmartEmailParser()
        parsed_data = parser.parse(file_content, filename)
        return {
            'type': 'email',
            'count': len(parsed_data),
            'data': parsed_data,
            'success': True
        }
    
    elif file_type == 'link':
        parser = SmartLinkParser()
        parsed_data = parser.parse(file_content, filename)
        return {
            'type': 'link',
            'count': len(parsed_data),
            'data': parsed_data,
            'success': True
        }
    
    else:
        return {
            'success': False,
            'error': 'Invalid file type'
        }