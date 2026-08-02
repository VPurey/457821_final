from github import Github, GithubException

class GitHubService:
    def __init__(self, token: str):
        """
        Initializes the GitHub client using an in-memory token.
        The token is never saved to a database or file system.
        """
        self.client = Github(token)

    def get_user_repositories(self):
        """
        Fetches all repositories accessible by the given token.
        """
        try:
            repos = self.client.get_user().get_repos()
            # Return a clean list of repository names and their full paths
            return [{"name": repo.name, "full_name": repo.full_name} for repo in repos]
        except GithubException as e:
            raise Exception(f"GitHub authentication or API error: {e.data.get('message', str(e))}")

    def get_repo_context(self, repo_full_name: str) -> str:
        """
        Traverses the repository and aggregates text file contents 
        to build an active context window for the LLM.
        """
        try:
            repo = self.client.get_repo(repo_full_name)
            contents = repo.get_contents("")
            context_pieces = []
            
            # CRITICAL: Ignore large directory names completely
            ignored_dirs = {'node_modules', '.git', 'build', 'dist', 'venv', 'env', '__pycache__'}
            # Simple recursive traversal to grab code files (ignoring common binary/config assets)
            ignored_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.zip', '.tar', '.gz', '.exe', '.dll')
            
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    # SKIP checking contents if the directory is in our ignored list
                    if file_content.name in ignored_dirs:
                        continue
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    if not file_content.name.lower().endswith(ignored_extensions):
                        try:
                            decoded_content = file_content.decoded_content.decode('utf-8')
                            context_pieces.append(f"--- File: {file_content.path} ---\n{decoded_content}\n")
                        except (UnicodeDecodeError, GithubException):
                            # Skip files that aren't readable text or fail to decode
                            continue
                            
            return "\n".join(context_pieces)
        except GithubException as e:
            raise Exception(f"Failed to fetch repository data: {e.data.get('message', str(e))}")