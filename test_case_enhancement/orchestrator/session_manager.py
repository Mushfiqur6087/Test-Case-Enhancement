"""Session Manager for managing authentication and browser sessions."""

from typing import List
from test_case_enhancement.core.models import RoleCredentials

class SessionManager:
    """SessionManager class."""
    def __init__(self, coordinator):
        """Initialize the __init__ method."""
        self.coordinator = coordinator

    def ensure_authenticated(self) -> None:
        """ensure_authenticated method/function."""
        if not self.coordinator.credentials:
            self.coordinator._log("  [Auth] No credentials — cannot authenticate.")
            return

        creds = self.coordinator.credentials[0]
        self.coordinator._log(f"  [Auth] Dynamic login fallback as: {creds.role} ({creds.username})")

        goal = (
            f"Find and navigate to the login or sign-in page. "
            f"Look for links or buttons labeled 'Login', 'Sign In', 'Log In', "
            f"'Get Started', or similar in the page header or navigation. "
            f"Once on the login page, fill the authentication form with "
            f"username '{creds.username}' and password '{creds.password}', "
            f"then submit the form and confirm you are redirected away from the login page."
        )
        extra = (
            f"Credentials: username='{creds.username}', password='{creds.password}'. "
            f"The username field may have placeholder 'Username', 'Email', or 'User ID'. "
            f"The password field may have placeholder 'Password' or 'Secret'."
        )

        result = self.coordinator.interaction_agent.execute_goal(goal=goal, extra_context=extra, max_steps=6)

        if result.success:
            self.coordinator._log(
                f"  [Auth] Login successful → {result.current_title} ({result.current_url})"
            )
            return

        self.coordinator._log(
            f"  [Auth] Could not find login from current page — "
            f"trying base URL {self.coordinator.base_url} as fallback."
        )
        self.coordinator.interaction_agent.navigate_to_url(self.coordinator.base_url)
        result = self.coordinator.interaction_agent.execute_goal(goal=goal, extra_context=extra, max_steps=4)

        if result.success:
            self.coordinator._log(
                f"  [Auth] Fallback login successful → {result.current_url}"
            )
        else:
            self.coordinator._log(
                f"  [Auth] Fallback login also failed: {result.failure_reason[:120]}"
            )

    def do_logout(self) -> None:
        """do_logout method/function."""
        goal = (
            "Open the navigation menu (hamburger menu button) if it exists, "
            "then click the 'Logout' link or button."
        )
        result = self.coordinator.interaction_agent.execute_goal(goal=goal)
        if result.success:
            self.coordinator._log("  Logged out.")
        else:
            self.coordinator.interaction_agent.navigate_to_url(self.coordinator.base_url)
            self.coordinator._log("  Logout fallback: navigated to base URL.")

    def format_credentials_for_planner(self) -> str:
        """format_credentials_for_planner method/function."""
        if not self.coordinator.credentials:
            return "No credentials available."

        lines = []
        for c in self.coordinator.credentials:
            lines.append(f"- Role: {c.role}, Username: {c.username}, Password: {c.password}")
        return "\n".join(lines)
