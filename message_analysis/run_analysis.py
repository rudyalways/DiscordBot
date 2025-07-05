#!/usr/bin/env python3
"""
Two-Authors Knowledge Domain Analysis - Data-Driven Approach 

This script uses a data-driven methodology to analyze multiple authors' expertise:
1. Extract all terms from their messages
2. Calculate term frequencies 
3. Identify clusters and patterns
4. Compare knowledge domains between authors

Usage:
    python run_analysis.py
"""

import json
import re
import os
from collections import Counter, defaultdict
from datetime import datetime

# Try to import optional visualization libraries
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

def load_data():
    """Load Discord message data and filter for target authors"""
    json_file_paths = [
        "AG2 (formerly AutoGen)_general.json",  # Local to script
        "../AG2 (formerly AutoGen)_general.json"  # Parent directory
    ]
    
    target_authors = ['qingyunwu', 'sonichi']
    author_messages = {}
    
    for json_file_path in json_file_paths:
        if os.path.exists(json_file_path):
            print(f"Loading data from: {json_file_path}")
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                all_messages = json.load(f)
            
            # Filter messages for each target author
            for author in target_authors:
                author_messages[author] = [msg for msg in all_messages if msg.get('author') == author]
            
            print(f"✓ Total messages in dataset: {len(all_messages):,}")
            for author in target_authors:
                count = len(author_messages[author])
                percentage = (count / len(all_messages)) * 100 if len(all_messages) > 0 else 0
                print(f"✓ {author}'s messages: {count:,} ({percentage:.2f}%)")
            
            return author_messages
    
    print("❌ Discord data file not found in any of the expected locations:")
    for path in json_file_paths:
        print(f"  - {path}")
    return {}

def extract_and_analyze_terms(messages, author_name):
    """
    Data-driven approach: Extract all terms and calculate frequencies for a specific author
    """
    if not messages:
        return Counter(), ""
        
    # Combine all message content
    all_content = " ".join([msg.get('content', '') for msg in messages])
    
    # Clean content - remove URLs, mentions, and special characters
    cleaned_content = re.sub(r'http[s]?://\S+', '', all_content)  # Remove URLs
    cleaned_content = re.sub(r'<@\d+>', '', cleaned_content)      # Remove mentions
    cleaned_content = re.sub(r'[^\w\s]', ' ', cleaned_content)    # Remove special chars
    
    # Extract words (3+ characters)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_content.lower())
    
    # Define comprehensive stop words (common words to filter out)
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 
        'our', 'out', 'day', 'get', 'use', 'man', 'new', 'now', 'way', 'may', 'say', 'each', 
        'which', 'she', 'how', 'its', 'who', 'sit', 'call', 'this', 'that', 'with', 'have', 
        'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 
        'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 
        'them', 'well', 'were', 'what', 'your', 'more', 'will', 'would', 'about', 'after', 
        'could', 'first', 'other', 'should', 'their', 'think', 'where', 'being', 'every', 
        'great', 'might', 'shall', 'still', 'those', 'under', 'while', 'found', 'right', 
        'small', 'again', 'back', 'came', 'gave', 'going', 'hand', 'keep', 'last', 'left', 
        'life', 'live', 'look', 'made', 'move', 'must', 'name', 'need', 'part', 'said', 
        'same', 'seem', 'show', 'side', 'tell', 'turn', 'used', 'want', 'ways', 'work', 
        'year', 'also', 'around', 'asked', 'become', 'both', 'called', 'did', 'does', 
        'done', 'even', 'find', 'give', 'had', 'has', 'him', 'his', 'into', 'large', 
        'line', 'little', 'number', 'off', 'old', 'only', 'own', 'people', 'place', 
        'put', 'see', 'so', 'sound', 'too', 'two', 'up', 'us', 'using', 'water', 
        'we', 'went', 'why', 'word', 'world', 'write', 'my', 'me', 'be', 'do', 'go', 
        'he', 'if', 'in', 'is', 'it', 'no', 'of', 'on', 'or', 'to', 'am', 'an', 'as', 
        'at', 'by', 'end', 'far', 'let', 'old', 'see', 'two', 'who', 'boy', 'did', 
        'has', 'let', 'put', 'say', 'she', 'too', 'use', 'com', 'https', 'www', 'html',
        'yes', 'there', 'check', 'forward', 'open', 'view', 'working', 'questions',
        'looking', 'sure', 'really', 'think', 'feel', 'probably', 'actually', 'definitely',
        'thanks', 'thank', 'please', 'welcome', 'sorry', 'hello', 'hey', 'hi'
    }
    
    # Filter out stop words
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_counts = Counter(filtered_words)
    
    return word_counts, cleaned_content

def infer_knowledge_domains(word_counts, author_name):
    """
    Infer knowledge domains from the most frequent terms using data-driven clustering
    """
    # Get top terms for analysis
    top_terms = dict(word_counts.most_common(100))
    
    if not top_terms:
        return {}
    
    # Define semantic clusters based on the actual top terms found
    domain_clusters = {}
    
    # Cluster 1: AI/ML & AutoGen (based on actual top terms)
    ai_ml_terms = []
    for term, count in top_terms.items():
        if any(indicator in term.lower() for indicator in ['autogen', 'agent', 'ai', 'ml', 'chat', 'gpt', 'model', 'assistant', 'llm', 'openai', 'anthropic']):
            ai_ml_terms.append((term, count))
    
    # Cluster 2: Development & Technical (based on actual top terms)
    dev_terms = []
    for term, count in top_terms.items():
        if any(indicator in term.lower() for indicator in ['python', 'code', 'github', 'git', 'notebook', 'jupyter', 'pip', 'package', 'version', 'repo', 'library', 'api', 'install', 'pypi', 'pyautogen', 'programming', 'software', 'development']):
            dev_terms.append((term, count))
    
    # Cluster 3: Community & Communication (based on actual top terms)
    community_terms = []
    for term, count in top_terms.items():
        if any(indicator in term.lower() for indicator in ['community', 'everyone', 'support', 'help', 'share', 'contributors', 'group', 'team', 'discussion', 'feedback', 'users', 'people']):
            community_terms.append((term, count))
    
    # Cluster 4: Platform & Infrastructure (based on actual top terms)
    platform_terms = []
    for term, count in top_terms.items():
        if any(indicator in term.lower() for indicator in ['microsoft', 'azure', 'discord', 'website', 'server', 'web', 'hosting', 'cloud', 'platform', 'office', 'windows', 'linux']):
            platform_terms.append((term, count))
    
    # Cluster 5: Research & Academic (based on actual top terms)
    research_terms = []
    for term, count in top_terms.items():
        if any(indicator in term.lower() for indicator in ['research', 'paper', 'study', 'analysis', 'experiment', 'data', 'results', 'method', 'algorithm', 'publication', 'conference', 'academic']):
            research_terms.append((term, count))
    
    # Cluster 6: Project & Business (based on actual top terms)
    project_terms = []
    for term, count in top_terms.items():
        if any(indicator in term.lower() for indicator in ['project', 'example', 'feature', 'release', 'update', 'roadmap', 'milestone', 'issue', 'bug', 'fix', 'solution', 'problem']):
            project_terms.append((term, count))
    
    # Collect remaining high-frequency terms
    used_terms = set()
    for cluster in [ai_ml_terms, dev_terms, community_terms, platform_terms, research_terms, project_terms]:
        used_terms.update(term for term, _ in cluster)
    
    other_terms = [(term, count) for term, count in top_terms.items() if term not in used_terms]
    
    # Build domain clusters (only include non-empty clusters)
    if ai_ml_terms:
        domain_clusters['AI/ML & AutoGen Systems'] = ai_ml_terms
    if dev_terms:
        domain_clusters['Development & Technical Tools'] = dev_terms
    if community_terms:
        domain_clusters['Community & Communication'] = community_terms
    if platform_terms:
        domain_clusters['Platform & Infrastructure'] = platform_terms
    if research_terms:
        domain_clusters['Research & Academic'] = research_terms
    if project_terms:
        domain_clusters['Project Management'] = project_terms
    if other_terms:
        domain_clusters['Other High-Frequency Terms'] = other_terms[:10]  # Top 10 other terms
    
    return domain_clusters

def analyze_technical_expertise(word_counts, author_name):
    """
    Data-driven technical expertise analysis based on actual term frequencies
    """
    # Get all terms and their frequencies
    all_terms = dict(word_counts.most_common(50))
    
    if not all_terms:
        return {}
    
    # Define technical categories based on what we actually found in the data
    technical_categories = {}
    
    # AutoGen/Agent Systems - based on actual high-frequency terms
    autogen_terms = []
    for term, count in all_terms.items():
        if any(keyword in term.lower() for keyword in ['autogen', 'agent', 'multiagent', 'chat', 'conversational', 'assistant', 'pyautogen']):
            autogen_terms.append((term, count))
    
    # Development Tools - based on actual high-frequency terms
    dev_tools = []
    for term, count in all_terms.items():
        if any(keyword in term.lower() for keyword in ['notebook', 'jupyter', 'github', 'git', 'pip', 'package', 'repo', 'install', 'pypi', 'code', 'library', 'ide']):
            dev_tools.append((term, count))
    
    # AI/ML Platforms - based on actual high-frequency terms
    ai_platforms = []
    for term, count in all_terms.items():
        if any(keyword in term.lower() for keyword in ['ai', 'ml', 'gpt', 'openai', 'model', 'llm', 'anthropic', 'claude', 'transformer', 'neural']):
            ai_platforms.append((term, count))
    
    # Platform/Infrastructure - based on actual high-frequency terms
    infrastructure = []
    for term, count in all_terms.items():
        if any(keyword in term.lower() for keyword in ['microsoft', 'azure', 'discord', 'website', 'server', 'web', 'office', 'platform', 'cloud', 'aws']):
            infrastructure.append((term, count))
    
    # Programming Languages - based on actual high-frequency terms
    programming = []
    for term, count in all_terms.items():
        if any(keyword in term.lower() for keyword in ['python', 'javascript', 'typescript', 'java', 'sql', 'html', 'css', 'rust', 'cpp']):
            programming.append((term, count))
    
    # Research & Data - based on actual high-frequency terms
    research = []
    for term, count in all_terms.items():
        if any(keyword in term.lower() for keyword in ['research', 'data', 'analysis', 'study', 'experiment', 'paper', 'algorithm', 'method']):
            research.append((term, count))
    
    # Only include categories that have terms
    if autogen_terms:
        technical_categories['AutoGen/Agent Systems'] = {
            'terms': autogen_terms,
            'description': 'Multi-agent systems and AutoGen framework'
        }
    if dev_tools:
        technical_categories['Development Tools'] = {
            'terms': dev_tools,
            'description': 'Development environment and tools'
        }
    if ai_platforms:
        technical_categories['AI/ML Platforms'] = {
            'terms': ai_platforms,
            'description': 'Artificial intelligence and machine learning platforms'
        }
    if infrastructure:
        technical_categories['Platform/Infrastructure'] = {
            'terms': infrastructure,
            'description': 'Cloud platforms and infrastructure services'
        }
    if programming:
        technical_categories['Programming Languages'] = {
            'terms': programming,
            'description': 'Programming languages and technologies'
        }
    if research:
        technical_categories['Research & Data'] = {
            'terms': research,
            'description': 'Research methodologies and data analysis'
        }
    
    return technical_categories

def compare_authors(author_results):
    """Compare expertise patterns between authors"""
    print("\n🔄 AUTHOR COMPARISON ANALYSIS")
    print("=" * 70)
    
    authors = list(author_results.keys())
    if len(authors) < 2:
        print("❌ Need at least 2 authors for comparison")
        return
    
    # Compare message counts
    print("📊 Message Volume:")
    for author in authors:
        count = len(author_results[author]['messages'])
        print(f"  • {author}: {count:,} messages")
    
    # Compare top domains
    print("\n🧠 Primary Knowledge Domains:")
    for author in authors:
        domains = author_results[author]['domains']
        if domains:
            top_domain = max(domains.items(), key=lambda x: sum(count for _, count in x[1]))
            total_mentions = sum(count for _, count in top_domain[1])
            print(f"  • {author}: {top_domain[0]} ({total_mentions} mentions)")
        else:
            print(f"  • {author}: No domains identified")
    
    # Compare technical focus
    print("\n🔧 Technical Specialization:")
    for author in authors:
        tech = author_results[author]['technical']
        if tech:
            top_tech = max(tech.items(), key=lambda x: sum(count for _, count in x[1]['terms']))
            total_mentions = sum(count for _, count in top_tech[1]['terms'])
            print(f"  • {author}: {top_tech[0]} ({total_mentions} mentions)")
        else:
            print(f"  • {author}: No technical specializations identified")
    
    # Find unique vs shared interests
    print("\n🎯 Unique vs Shared Expertise:")
    
    # Get all domain names for each author
    author_domains = {}
    for author in authors:
        author_domains[author] = set(author_results[author]['domains'].keys())
    
    if len(authors) == 2:
        author1, author2 = authors
        shared = author_domains[author1] & author_domains[author2]
        unique1 = author_domains[author1] - author_domains[author2]
        unique2 = author_domains[author2] - author_domains[author1]
        
        print(f"  • Shared domains: {', '.join(shared) if shared else 'None'}")
        print(f"  • {author1} unique: {', '.join(unique1) if unique1 else 'None'}")
        print(f"  • {author2} unique: {', '.join(unique2) if unique2 else 'None'}")
    
    # Compare vocabulary diversity
    print("\n📝 Vocabulary Diversity:")
    for author in authors:
        word_counts = author_results[author]['word_counts']
        unique_terms = len(word_counts)
        total_words = sum(word_counts.values())
        diversity = unique_terms / total_words if total_words > 0 else 0
        print(f"  • {author}: {unique_terms:,} unique terms, {diversity:.3f} diversity ratio")

def analyze_author(messages, author_name):
    """Analyze a single author's patterns"""
    if not messages:
        return {
            'messages': [],
            'word_counts': Counter(),
            'domains': {},
            'technical': {}
        }
    
    # Extract and analyze terms
    word_counts, cleaned_content = extract_and_analyze_terms(messages, author_name)
    
    # Infer knowledge domains
    domain_clusters = infer_knowledge_domains(word_counts, author_name)
    
    # Analyze technical expertise
    technical_categories = analyze_technical_expertise(word_counts, author_name)
    
    return {
        'messages': messages,
        'word_counts': word_counts,
        'domains': domain_clusters,
        'technical': technical_categories
    }

def display_author_analysis(author_name, analysis_results):
    """Display analysis results for a single author"""
    messages = analysis_results['messages']
    domains = analysis_results['domains']
    technical = analysis_results['technical']
    
    print(f"\n👤 {author_name.upper()} - KNOWLEDGE DOMAINS (Inferred from Term Frequency Data)")
    print("=" * 70)
    
    if not domains:
        print(f"❌ No knowledge domains identified for {author_name}")
        return
    
    for i, (domain, terms) in enumerate(domains.items(), 1):
        total_mentions = sum(count for _, count in terms)
        print(f"{i}. {domain}: {total_mentions:,} total mentions")
        
        # Show top terms for this domain
        top_terms = terms[:5]  # Top 5 terms
        if top_terms:
            terms_str = ", ".join([f"{term} ({count})" for term, count in top_terms])
            print(f"   Key terms: {terms_str}")
        print()
    
    # Technical expertise analysis
    print(f"🔧 {author_name.upper()} - TECHNICAL EXPERTISE ANALYSIS")
    print("=" * 70)
    
    if not technical:
        print(f"❌ No technical expertise identified for {author_name}")
        return
    
    # Sort by total mentions
    sorted_categories = sorted(technical.items(), 
                             key=lambda x: sum(count for _, count in x[1]['terms']), 
                             reverse=True)
    
    for category, data in sorted_categories:
        total_mentions = sum(count for _, count in data['terms'])
        print(f"\n📚 {category}: {total_mentions} mentions")
        print(f"   {data['description']}")
        
        # Show top terms in this category
        top_terms = data['terms'][:5]  # Top 5 terms
        if top_terms:
            terms_str = ", ".join([f"{term} ({count})" for term, count in top_terms])
            print(f"   Top terms: {terms_str}")

def main():
    """Main analysis function"""
    print("🔍 MULTI-AUTHOR CONTENT ANALYSIS")
    print("=" * 60)
    print("Analyzing knowledge domains for: qingyunwu & sonichi")
    
    # Load data for all authors
    author_messages = load_data()
    
    if not author_messages:
        print("❌ No messages to analyze")
        return
    
    # Analyze each author
    author_results = {}
    authors_to_analyze = ['qingyunwu', 'sonichi']
    
    for author in authors_to_analyze:
        if author in author_messages:
            print(f"\n🔍 Analyzing {author}...")
            author_results[author] = analyze_author(author_messages[author], author)
        else:
            print(f"❌ No messages found for {author}")
            author_results[author] = analyze_author([], author)
    
    # Display individual analyses
    for author in authors_to_analyze:
        if author in author_results:
            display_author_analysis(author, author_results[author])
    
    # Compare authors
    if len([a for a in author_results.values() if a['messages']]) >= 2:
        compare_authors(author_results)
    
    print(f"\n" + "=" * 70)
    print("✅ MULTI-AUTHOR ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main() 