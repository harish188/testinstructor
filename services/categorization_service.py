import re
from typing import List, Dict, Tuple
from loguru import logger
from models import ZohoTicket, TicketCategory
from services.knowledge_base_service import KnowledgeBaseService

class CategorizationService:
    def __init__(self):
        self.kb_service = KnowledgeBaseService()
        self.category_rules = self._load_categorization_rules()
    
    def _load_categorization_rules(self) -> Dict[str, Dict]:
        """Load categorization rules from database"""
        return self.kb_service.get_categorization_rules()
    
    def categorize_ticket(self, ticket: ZohoTicket) -> str:
        """Categorize a ticket based on its content"""
        try:
            # Reload rules to get latest from database
            self.category_rules = self._load_categorization_rules()
            
            # Combine subject and description for analysis
            text_content = f"{ticket.subject} {ticket.description}".lower()
            
            # Calculate scores for each category
            category_scores = {}
            
            for category, category_data in self.category_rules.items():
                rules = category_data.get("rules", [])
                score = self._calculate_category_score(text_content, rules)
                category_scores[category] = score
            
            # Find the category with the highest score
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                best_score = category_scores[best_category]
                
                # If no category has a significant score, default to Learning Portal Issues
                if best_score < 5:
                    logger.info(f"Ticket {ticket.id} defaulted to Learning Portal Issues (score: {best_score})")
                    return "Learning Portal Issues"
                
                logger.info(f"Ticket {ticket.id} categorized as {best_category} (score: {best_score})")
                return best_category
            else:
                logger.info(f"Ticket {ticket.id} defaulted to Learning Portal Issues (no rules)")
                return "Learning Portal Issues"
            
        except Exception as e:
            logger.error(f"Error categorizing ticket {ticket.id}: {str(e)}")
            return "Learning Portal Issues"
    
    def _calculate_category_score(self, text: str, rules: List[Dict]) -> float:
        """Calculate score for a category based on pattern matching"""
        total_score = 0
        
        for rule in rules:
            patterns = rule["patterns"]
            weight = rule["weight"]
            
            # Count pattern matches
            matches = 0
            for pattern in patterns:
                # Use word boundaries for more accurate matching
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                matches += len(re.findall(pattern_regex, text, re.IGNORECASE))
            
            # Apply weight to matches
            rule_score = matches * weight
            total_score += rule_score
        
        return total_score
    
    def batch_categorize(self, tickets: List[ZohoTicket]) -> Dict[str, str]:
        """Categorize multiple tickets and return mapping"""
        categorizations = {}
        
        for ticket in tickets:
            category = self.categorize_ticket(ticket)
            categorizations[ticket.id] = category
        
        # Log categorization summary
        category_counts = {}
        for category in categorizations.values():
            category_counts[category] = category_counts.get(category, 0) + 1
        
        logger.info("Categorization Summary:")
        for category, count in category_counts.items():
            logger.info(f"  {category}: {count} tickets")
        
        return categorizations
    
    def get_team_for_category(self, category: str) -> str:
        """Get team assignment for a category"""
        return self.kb_service.get_team_for_category(category)
    
    def update_knowledge_base_from_data(self, kb_data: List[Dict]) -> bool:
        """Update knowledge base from provided data"""
        success = self.kb_service.update_knowledge_base_from_data(kb_data)
        if success:
            # Reload categorization rules
            self.category_rules = self._load_categorization_rules()
        return success
    
    def add_knowledge_base_entries(self, entries: List[Dict]) -> bool:
        """Add knowledge base entries"""
        success = self.kb_service.add_knowledge_base_entries(entries)
        if success:
            # Reload categorization rules
            self.category_rules = self._load_categorization_rules()
        return success
    
    def get_knowledge_base_summary(self) -> List[Dict]:
        """Get summary of current knowledge base"""
        return self.kb_service.get_knowledge_base_summary()
    
    def get_similar_tickets(self, tickets: List[ZohoTicket], similarity_threshold: float = 0.8) -> List[List[ZohoTicket]]:
        """Group similar tickets together for potential merging"""
        similar_groups = []
        processed_tickets = set()
        
        for i, ticket1 in enumerate(tickets):
            if ticket1.id in processed_tickets:
                continue
            
            similar_group = [ticket1]
            processed_tickets.add(ticket1.id)
            
            for j, ticket2 in enumerate(tickets[i+1:], i+1):
                if ticket2.id in processed_tickets:
                    continue
                
                similarity = self._calculate_similarity(ticket1, ticket2)
                if similarity >= similarity_threshold:
                    similar_group.append(ticket2)
                    processed_tickets.add(ticket2.id)
            
            if len(similar_group) > 1:
                similar_groups.append(similar_group)
                logger.info(f"Found {len(similar_group)} similar tickets: {[t.id for t in similar_group]}")
        
        return similar_groups
    
    def _calculate_similarity(self, ticket1: ZohoTicket, ticket2: ZohoTicket) -> float:
        """Calculate similarity between two tickets"""
        # Simple similarity based on subject and email
        subject_similarity = self._text_similarity(ticket1.subject, ticket2.subject)
        
        # Check if same user
        same_user = ticket1.email and ticket2.email and ticket1.email == ticket2.email
        
        # Combine factors
        similarity = subject_similarity
        if same_user:
            similarity += 0.3  # Boost for same user
        
        return min(similarity, 1.0)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word overlap"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0