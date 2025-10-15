#!/usr/bin/env python3
"""
Load knowledge base from CSV file (Instructor portal Issues - Sheet1.csv)
This script analyzes the CSV file and creates knowledge base entries based on the issues and categories
"""

import sys
import csv
import re
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add current directory to path
sys.path.append('.')

from services.knowledge_base_service import KnowledgeBaseService
from database import create_tables

console = Console()

def extract_keywords_from_issues(issues_list):
    """Extract relevant keywords from a list of issues"""
    # Common words to ignore
    stop_words = {
        'the', 'is', 'was', 'are', 'were', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'i', 'me', 'my', 'we', 'us', 'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them', 'their',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cannot',
        'this', 'that', 'these', 'those', 'there', 'here', 'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom',
        'be', 'been', 'being', 'am', 'so', 'very', 'just', 'now', 'then', 'than', 'only', 'also', 'even', 'still',
        'get', 'got', 'getting', 'go', 'going', 'went', 'come', 'came', 'coming', 'take', 'took', 'taking', 'make', 'made', 'making',
        'see', 'saw', 'seeing', 'know', 'knew', 'knowing', 'think', 'thought', 'thinking', 'say', 'said', 'saying',
        'one', 'two', 'three', 'first', 'second', 'last', 'next', 'some', 'many', 'much', 'more', 'most', 'all', 'any', 'no', 'not'
    }
    
    # Extract all words and phrases
    all_text = ' '.join(issues_list).lower()
    
    # Remove special characters and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', all_text)
    
    # Count word frequency
    word_freq = defaultdict(int)
    for word in words:
        if len(word) > 2 and word not in stop_words:
            word_freq[word] += 1
    
    # Extract common phrases (2-3 words)
    phrases = []
    for issue in issues_list:
        issue_lower = issue.lower()
        # Look for common technical phrases
        technical_phrases = [
            'instructor portal', 'learning portal', 'student portal', 'platform issue', 'network issue',
            'internet issue', 'wifi issue', 'power cut', 'mic issue', 'microphone', 'battery',
            'screen sharing', 'audio recording', 'video recording', 'session timing', 'scheduling',
            'portal access', 'login issue', 'authentication', 'upload issue', 'download issue',
            'technical issue', 'system issue', 'connectivity issue', 'equipment failure',
            'classroom', 'projector', 'display', 'facilities', 'infrastructure',
            'quiz', 'assessment', 'evaluation', 'feedback', 'report', 'qa report',
            'session handling', 'class management', 'student interaction', 'attendance'
        ]
        
        for phrase in technical_phrases:
            if phrase in issue_lower:
                phrases.append(phrase)
    
    # Get top keywords (most frequent)
    top_words = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True) if freq >= 2][:15]
    
    # Combine phrases and top words
    keywords = list(set(phrases + top_words))
    
    return keywords[:20]  # Limit to 20 most relevant keywords

def map_category_to_team(category):
    """Map category to appropriate team based on your knowledge base"""
    category_lower = category.lower()
    
    if 'platform' in category_lower or 'tech' in category_lower or 'qa' in category_lower:
        return 'Product/Tech'
    elif 'facilities' in category_lower or 'ground' in category_lower:
        return 'Facilities'
    elif 'timing' in category_lower or 'scheduling' in category_lower:
        return 'Curriculum/Content'
    elif 'portal' in category_lower and 'student' in category_lower:
        return 'Product/Tech'
    elif 'session handling' in category_lower or 'handling' in category_lower:
        return 'Instructor'
    else:
        # Default mapping based on category content
        if any(word in category_lower for word in ['student', 'portal', 'access', 'login']):
            return 'Product/Tech'
        elif any(word in category_lower for word in ['content', 'curriculum', 'quiz', 'assessment']):
            return 'Curriculum/Content'
        elif any(word in category_lower for word in ['instructor', 'teaching', 'session']):
            return 'Instructor'
        elif any(word in category_lower for word in ['facility', 'equipment', 'room', 'infrastructure']):
            return 'Facilities'
        else:
            return 'Product/Tech'  # Default

def load_csv_knowledge_base():
    """Load knowledge base from CSV file"""
    console.print(Panel.fit("📚 Loading Knowledge Base from CSV", style="bold blue"))
    
    csv_file = "Instructor portal Issues - Sheet1.csv"
    
    try:
        # Read CSV file
        categories_data = defaultdict(list)
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                issue = row['Issues'].strip()
                category = row['Category'].strip()
                
                if issue and category:
                    categories_data[category].append(issue)
        
        console.print(f"📋 Found {len(categories_data)} categories with {sum(len(issues) for issues in categories_data.values())} total issues")
        
        # Create knowledge base entries
        kb_entries = []
        
        for category, issues in categories_data.items():
            # Extract keywords from issues
            keywords = extract_keywords_from_issues(issues)
            
            # Map to team
            team = map_category_to_team(category)
            
            # Create knowledge base entry
            kb_entry = {
                "category": category.title(),  # Capitalize category name
                "team": team,
                "keywords": keywords,
                "description": f"Issues related to {category.lower()} based on {len(issues)} reported cases",
                "weight": 1.0
            }
            
            kb_entries.append(kb_entry)
        
        # Display preview
        table = Table(title="📊 Knowledge Base Preview")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Team", style="yellow", no_wrap=True)
        table.add_column("Issues Count", style="green")
        table.add_column("Keywords Count", style="magenta")
        table.add_column("Sample Keywords", style="white", max_width=40)
        
        for entry in kb_entries:
            category = entry["category"]
            team = entry["team"]
            issues_count = len(categories_data[category.lower()])
            keywords_count = len(entry["keywords"])
            sample_keywords = ", ".join(entry["keywords"][:5])
            
            table.add_row(
                category,
                team,
                str(issues_count),
                str(keywords_count),
                sample_keywords
            )
        
        console.print(table)
        
        # Ask for confirmation
        console.print(f"\n🔍 Ready to load {len(kb_entries)} categories into database.")
        confirm = input("Do you want to proceed? (y/N): ").lower().strip()
        
        if confirm == 'y' or confirm == 'yes':
            # Create database tables
            create_tables()
            
            # Initialize knowledge base service
            kb_service = KnowledgeBaseService()
            
            # Load entries into database
            success = kb_service.update_knowledge_base_from_data(kb_entries)
            
            if success:
                console.print("✅ Knowledge base loaded successfully!", style="green")
                
                # Show team distribution
                team_counts = defaultdict(int)
                for entry in kb_entries:
                    team_counts[entry["team"]] += 1
                
                console.print("\n📊 Team Distribution:")
                for team, count in team_counts.items():
                    console.print(f"  • {team}: {count} categories")
                
                console.print(f"\n🎯 Total: {len(kb_entries)} categories loaded")
                console.print("\n🚀 Knowledge base is ready! Start the server with: python main.py server")
                
                return True
            else:
                console.print("❌ Failed to load knowledge base", style="red")
                return False
        else:
            console.print("❌ Operation cancelled", style="yellow")
            return False
            
    except FileNotFoundError:
        console.print(f"❌ CSV file '{csv_file}' not found", style="red")
        return False
    except Exception as e:
        console.print(f"❌ Error loading CSV: {str(e)}", style="red")
        return False

def main():
    console.print("📊 CSV Knowledge Base Loader")
    console.print("=" * 50)
    
    success = load_csv_knowledge_base()
    
    if success:
        console.print("\n🎉 CSV knowledge base loaded successfully!")
        console.print("\n💡 Next steps:")
        console.print("  1. Test categorization: python test_categorization.py")
        console.print("  2. Start the server: python main.py server")
        console.print("  3. Test with real tickets in the dashboard")
    else:
        console.print("\n❌ Failed to load CSV knowledge base")
        sys.exit(1)

if __name__ == "__main__":
    main()