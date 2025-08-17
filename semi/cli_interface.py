import click
from colorama import Fore, Style, init
from typing import Dict, Any
from gmail_client import GmailClient
from email_clusterer import EmailClusterer

init()

class CLIInterface:
    def __init__(self):
        self.gmail_client = GmailClient()
        self.clusterer = EmailClusterer()
        self.clusters = {}
        
    def display_clusters(self, clusters: Dict[int, Dict[str, Any]]):
        print(f"\n{Fore.CYAN}📧 Inbox Triage Assistant{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Found {len(clusters)} email clusters:{Style.RESET_ALL}\n")
        
        for cluster_id, cluster_data in clusters.items():
            name = cluster_data['name']
            count = cluster_data['count']
            emails = cluster_data['emails']
            
            print(f"{Fore.GREEN}[{cluster_id + 1}] {name} ({count} emails){Style.RESET_ALL}")
            
            for i, email in enumerate(emails[:3]):
                subject = email['subject'][:60] + "..." if len(email['subject']) > 60 else email['subject']
                sender = email['sender'].split('<')[0].strip().strip('"')[:30]
                print(f"    • {subject} - {Fore.BLUE}{sender}{Style.RESET_ALL}")
            
            if len(emails) > 3:
                print(f"    ... and {len(emails) - 3} more emails")
            
            print()
    
    def get_user_choice(self, max_clusters: int) -> str:
        print(f"{Fore.YELLOW}Options:{Style.RESET_ALL}")
        print(f"  Enter cluster number (1-{max_clusters}) to archive that cluster")
        print(f"  Enter 'q' to quit")
        print(f"  Enter 'r' to refresh emails")
        
        choice = input(f"\n{Fore.CYAN}Your choice: {Style.RESET_ALL}").strip().lower()
        return choice
    
    def confirm_archive(self, cluster_name: str, count: int) -> bool:
        print(f"\n{Fore.YELLOW}⚠️  You are about to archive {count} emails from: {cluster_name}{Style.RESET_ALL}")
        confirm = input(f"{Fore.RED}Are you sure? (y/N): {Style.RESET_ALL}").strip().lower()
        return confirm in ['y', 'yes']
    
    def show_success_message(self, count: int):
        print(f"\n{Fore.GREEN}✅ Successfully archived {count} emails!{Style.RESET_ALL}")
    
    def show_error_message(self, message: str):
        print(f"\n{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")
    
    def show_loading_message(self, message: str):
        print(f"\n{Fore.CYAN}⏳ {message}...{Style.RESET_ALL}")
    
    def run(self):
        print(f"{Fore.CYAN}🚀 Starting Inbox Triage Assistant...{Style.RESET_ALL}")
        
        try:
            self.show_loading_message("Connecting to Gmail")
            if not self.gmail_client.connect():
                self.show_error_message("Failed to connect to Gmail. Check your credentials.")
                return
            
            while True:
                self.show_loading_message("Fetching recent emails")
                emails = self.gmail_client.fetch_recent_emails(200)
                
                if not emails:
                    self.show_error_message("No emails found")
                    break
                
                self.show_loading_message("Clustering emails")
                self.clusters = self.clusterer.cluster_emails(emails)
                
                self.display_clusters(self.clusters)
                
                choice = self.get_user_choice(len(self.clusters))
                
                if choice == 'q':
                    print(f"\n{Fore.CYAN}👋 Goodbye!{Style.RESET_ALL}")
                    break
                elif choice == 'r':
                    continue
                elif choice.isdigit():
                    cluster_num = int(choice) - 1
                    if 0 <= cluster_num < len(self.clusters):
                        cluster_data = self.clusters[cluster_num]
                        
                        if self.confirm_archive(cluster_data['name'], cluster_data['count']):
                            email_ids = [email['id'] for email in cluster_data['emails']]
                            
                            self.show_loading_message("Archiving emails")
                            if self.gmail_client.archive_emails(email_ids):
                                self.show_success_message(cluster_data['count'])
                            else:
                                self.show_error_message("Failed to archive emails")
                        else:
                            print(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                    else:
                        self.show_error_message("Invalid cluster number")
                else:
                    self.show_error_message("Invalid choice")
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⏹️  Operation interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            self.show_error_message(f"Unexpected error: {e}")
        finally:
            self.gmail_client.disconnect()
            print(f"{Fore.CYAN}Disconnected from Gmail.{Style.RESET_ALL}")