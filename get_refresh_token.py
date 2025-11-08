#!/usr/bin/env python3
"""
Helper script to obtain a Salesforce refresh token for Heroku deployment.

This script runs the OAuth flow and extracts the refresh token for you.
"""

import logging
import sys
from oauth import OAuthConfig, OAuthSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

def main():
    print("=" * 80)
    print("Salesforce Data Cloud - Refresh Token Generator")
    print("=" * 80)
    print()
    print("This script will help you obtain a refresh token for Heroku deployment.")
    print()
    print("Prerequisites:")
    print("1. Set SF_CLIENT_ID environment variable")
    print("2. Set SF_CLIENT_SECRET environment variable")
    print("3. Connected App must have 'refresh_token' or 'offline_access' scope")
    print()
    print("=" * 80)
    print()

    try:
        # Initialize OAuth config
        config = OAuthConfig.from_env()
        session = OAuthSession(config)

        print("Starting OAuth flow...")
        print("Your browser will open for Salesforce authentication.")
        print()

        # Run the OAuth flow
        auth_info = session._run_oauth_flow(
            ["api", "cdp_query_api", "cdp_profile_api", "refresh_token", "offline_access"]
        )

        print()
        print("=" * 80)
        print("SUCCESS! OAuth flow completed.")
        print("=" * 80)
        print()

        # Check if we got a refresh token
        if "refresh_token" in auth_info:
            refresh_token = auth_info["refresh_token"]
            print("✓ Refresh Token obtained successfully!")
            print()
            print("-" * 80)
            print("REFRESH TOKEN (save this securely):")
            print("-" * 80)
            print(refresh_token)
            print("-" * 80)
            print()
            print("Next steps for Heroku deployment:")
            print()
            print("1. Copy the refresh token above")
            print("2. Set it as a Heroku config variable:")
            print()
            print(f"   heroku config:set SF_REFRESH_TOKEN={refresh_token}")
            print()
            print("3. Also set your Salesforce credentials:")
            print()
            print(f"   heroku config:set SF_CLIENT_ID={config.client_id}")
            print(f"   heroku config:set SF_CLIENT_SECRET=your_client_secret")
            print(f"   heroku config:set MCP_TRANSPORT=http")
            print()
            print("4. Deploy to Heroku:")
            print()
            print("   git push heroku main")
            print()
        else:
            print("⚠ WARNING: No refresh token was returned!")
            print()
            print("This means your Connected App is not configured correctly.")
            print()
            print("To fix this:")
            print("1. Go to your Salesforce Connected App settings")
            print("2. Under 'Selected OAuth Scopes', ensure these are included:")
            print("   - Perform requests at any time (refresh_token, offline_access)")
            print("   - Access and manage your data (api)")
            print("   - Access Data Cloud API resources (cdp_query_api)")
            print("3. Save the Connected App")
            print("4. Run this script again")
            print()
            sys.exit(1)

        print("=" * 80)
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR: Failed to obtain refresh token")
        print("=" * 80)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Please check:")
        print("1. SF_CLIENT_ID and SF_CLIENT_SECRET are set correctly")
        print("2. Your Connected App has the correct OAuth scopes")
        print("3. Your Salesforce user has appropriate permissions")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
