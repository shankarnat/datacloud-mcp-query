# JWT Bearer Token Setup Guide for Salesforce Data Cloud

This guide shows you how to set up **JWT Bearer Token Flow** for server-to-server authentication with Salesforce Data Cloud on Heroku. This is the **recommended production approach** - no browser popups or refresh tokens needed!

## Overview

JWT (JSON Web Token) Bearer Token Flow allows your Heroku app to authenticate to Salesforce without user interaction. Perfect for ChatGPT Enterprise Knowledge integration!

## Step 1: Generate a Certificate and Private Key

On your local machine, run:

```bash
# Generate a private key
openssl genrsa -out server.key 2048

# Generate a certificate signing request
openssl req -new -key server.key -out server.csr

# Generate a self-signed certificate (valid for 1 year)
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```

When prompted for certificate details, you can use any values. For example:
- Country: US
- State: California
- City: San Francisco
- Organization: Your Company
- Common Name: your-app-name

You'll now have three files:
- `server.key` - **Private key** (keep this secure!)
- `server.crt` - **Certificate** (upload to Salesforce)
- `server.csr` - Certificate request (not needed after generating .crt)

## Step 2: Configure Your Salesforce Connected App

### 2.1 Navigate to Your Connected App

1. Log in to Salesforce
2. Go to **Setup** → **App Manager**
3. Find your Connected App (or create a new one)
4. Click **Edit**

### 2.2 Enable JWT Bearer Token Flow

1. Check **Enable OAuth Settings**
2. Set **Callback URL** to: `https://login.salesforce.com/services/oauth2/success`
   (This is not used for JWT but required by Salesforce)
3. Check **Use digital signatures**
4. Click **Choose File** and upload your `server.crt` file
5. Under **Selected OAuth Scopes**, add:
   - Full access (full)
   - Perform requests at any time (refresh_token, offline_access)
   - Access and manage your data (api)
   - Access Data Cloud API resources (cdp_query_api)
6. Click **Save**

### 2.3 Pre-Authorize the User

JWT requires pre-authorization. There are two ways:

**Option A: Permission Set Assignment (Recommended)**

1. In your Connected App settings, click **Manage**
2. Click **Edit Policies**
3. Under **OAuth Policies** → **Permitted Users**, select **Admin approved users are pre-authorized**
4. Click **Save**
5. Go to **Permission Sets** section
6. Create a new Permission Set or use existing one
7. Assign this Permission Set to the user whose username you'll use for JWT
8. Add the Connected App to the Permission Set

**Option B: Profile Assignment**

1. In Connected App settings → **Manage Profiles**
2. Select the profile of the user you'll use for JWT authentication
3. Click **Save**

## Step 3: Get Your Connected App Consumer Key

1. In your Connected App, find the **Consumer Key** (also called Client ID)
2. Copy this value - you'll need it for Heroku

## Step 4: Prepare the Private Key for Heroku

Heroku config vars don't support multi-line values well. Convert your private key to base64:

```bash
# On Mac/Linux
base64 -i server.key -o server.key.base64

# Or use this one-liner to copy to clipboard (Mac)
base64 -i server.key | pbcopy

# On Windows (PowerShell)
[Convert]::ToBase64String([IO.File]::ReadAllBytes("server.key")) | Set-Clipboard
```

This creates a single-line base64-encoded version of your private key.

Alternatively, you can prepare it as a single-line string by replacing newlines with `\n`:

```bash
# Mac/Linux
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' server.key
```

## Step 5: Configure Heroku Environment Variables

Set the following environment variables on Heroku:

```bash
# Required: Consumer Key from your Connected App
heroku config:set SF_CLIENT_ID="your_consumer_key_here"

# Required: Salesforce username (the pre-authorized user)
heroku config:set SF_USERNAME="user@yourcompany.com"

# Required: Base64-encoded private key
heroku config:set SF_JWT_PRIVATE_KEY="base64_encoded_private_key_here"

# Optional: Salesforce login URL (default: login.salesforce.com)
# Use 'test.salesforce.com' for sandboxes
heroku config:set SF_LOGIN_URL="login.salesforce.com"

# Required: Enable HTTP transport
heroku config:set MCP_TRANSPORT=http

# Optional: Filter which tables to show
heroku config:set DEFAULT_LIST_TABLE_FILTER="%"
```

**Important Notes:**
- `SF_USERNAME` must be the username of a user who is pre-authorized for the Connected App
- The private key in `SF_JWT_PRIVATE_KEY` should be base64-encoded
- Do NOT include `SF_CLIENT_SECRET` - it's not used in JWT flow
- Do NOT include `SF_REFRESH_TOKEN` - JWT flow doesn't need it

## Step 6: Deploy to Heroku

```bash
git push heroku claude/help-session-011CUvyEi8JggaGyfdLzmVmB:main
```

## Step 7: Test the Deployment

### 7.1 Check the Health Endpoint

```bash
curl https://your-app-name.herokuapp.com/health
```

You should see:
```json
{"status": "healthy", "service": "Salesforce Data Cloud MCP Server"}
```

### 7.2 Check the Logs

```bash
heroku logs --tail
```

Look for:
```
Starting MCP server with streamable HTTP on 0.0.0.0:xxxxx
Started server process
Uvicorn running on http://0.0.0.0:xxxxx
```

When a request is made, you should see:
```
Using JWT bearer token for authentication
Successfully obtained access token via JWT
```

## Step 8: Configure ChatGPT Enterprise Knowledge

1. Open **ChatGPT** (Enterprise/Edu/Business account)
2. Go to **Settings** → **Connectors** or **Deep Research**
3. Click **Add Custom Connector** or **Add MCP Server**
4. Configure:
   - **Name**: Salesforce Data Cloud
   - **URL**: `https://your-app-name.herokuapp.com`
   - **Transport**: `streamable-http`
5. **Save** and test!

## Troubleshooting

### Error: "JWT token exchange failed"

**Check the logs:**
```bash
heroku logs --tail
```

**Common causes:**

1. **Invalid signature**
   - Ensure the certificate uploaded to Salesforce matches your private key
   - Regenerate both if needed

2. **User not pre-authorized**
   - Check that the user in `SF_USERNAME` is assigned to the Connected App via Permission Set or Profile

3. **Expired certificate**
   - Generate a new certificate (Step 1)
   - Upload to Connected App (Step 2.2)

4. **Wrong audience**
   - For sandboxes, use `SF_LOGIN_URL=test.salesforce.com`
   - For production, use `SF_LOGIN_URL=login.salesforce.com`

### Error: "SF_USERNAME and SF_JWT_PRIVATE_KEY are required"

Check your Heroku config:
```bash
heroku config
```

Ensure both variables are set:
- `SF_USERNAME`
- `SF_JWT_PRIVATE_KEY`

### Private Key Format Issues

If you get errors about the private key format:

**Option 1: Use base64 encoding** (recommended):
```bash
base64 -i server.key | pbcopy  # Mac
```

**Option 2: Use raw key with escaped newlines**:
```bash
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' server.key
```

Then set it:
```bash
heroku config:set SF_JWT_PRIVATE_KEY="your_encoded_key"
```

### Testing JWT Authentication Locally

Before deploying to Heroku, test locally:

```bash
# Set environment variables
export SF_CLIENT_ID="your_consumer_key"
export SF_USERNAME="user@yourcompany.com"
export SF_JWT_PRIVATE_KEY=$(base64 -i server.key)
export MCP_TRANSPORT=http
export PORT=8000

# Run the server
python server.py
```

Visit: `http://localhost:8000/health`

Check logs for "Using JWT bearer token for authentication"

## Security Best Practices

1. **Never commit private keys** to git
   - Add `server.key`, `server.crt`, `*.pem` to `.gitignore`

2. **Rotate certificates regularly**
   - Generate new certificates every 6-12 months
   - Update Connected App with new certificate

3. **Use dedicated service accounts**
   - Create a dedicated Salesforce user for the MCP server
   - Grant only necessary permissions

4. **Monitor access**
   - Review Salesforce login history
   - Check Heroku logs for unusual activity

5. **Limit IP ranges** (optional)
   - In Connected App → Manage → Edit Policies
   - Set IP Relaxation to "Enforce IP restrictions"
   - Add Heroku IP ranges

## Benefits of JWT Over Refresh Tokens

✅ **No browser interaction needed**
✅ **More secure** - private key never transmitted
✅ **Easier rotation** - just upload new certificate
✅ **No token storage** - tokens generated on-demand
✅ **Better for automation** - perfect for Heroku
✅ **Recommended by Salesforce** for server-to-server auth

## References

- [Salesforce JWT Bearer Token Flow](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_jwt_flow.htm)
- [OAuth 2.0 JWT Bearer Flow for Server-to-Server Integration](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_jwt_flow.htm)
- [Connected Apps Documentation](https://help.salesforce.com/s/articleView?id=sf.connected_app_overview.htm)

## Summary

You've now configured JWT Bearer Token authentication! Your Heroku app can authenticate to Salesforce without any user interaction, making it perfect for ChatGPT Enterprise Knowledge integration.

**Your MCP server URL**: `https://your-app-name.herokuapp.com`

Ready to use with ChatGPT! 🎉
