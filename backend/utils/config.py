"""
Configuration Utilities
Manages application configuration and paths
"""

import os


def get_config_paths():
    """
    Get standardized configuration paths for the application
    
    Returns:
        Dictionary containing:
            - cloned_repos_dir: Directory for storing cloned repositories
            - repos_config_file: Path to repository configuration JSON file
            
    Note:
        Creates directories if they don't exist
    """
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    cloned_repos_dir = os.path.join(parent_dir, "cloned-repos")
    repos_config_file = os.path.join(cloned_repos_dir, "repos.json")
    
    # Ensure directory exists
    os.makedirs(cloned_repos_dir, exist_ok=True)
    
    return {
        "cloned_repos_dir": cloned_repos_dir,
        "repos_config_file": repos_config_file
    }