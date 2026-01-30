# GitHub Deployment Setup Guide

Follow these steps one-by-one to enable automated deployments from GitHub to your Raspberry Pi.

---

### Step 1: Get Tailscale Auth Key
1.  Open your [Tailscale Keys Settings](https://login.tailscale.com/admin/settings/keys).
2.  Click **"Generate auth key"**.
3.  Set these options:
    - **Reusable**: Yes (Turn this ON)
    - **Ephemeral**: Yes
    - **Tags**: Select `tag:ci`
4.  Click **"Generate key"**.
5.  **COPY IMMEDIATELY**: Save it as `TAILSCALE_AUTH_KEY` in GitHub Secrets.

---

### Step 2: Get your Pi's Tailscale IP
1.  On your Raspberry Pi, run: `tailscale ip -4`
2.  Or check the [Tailscale Machines list](https://login.tailscale.com/admin/machines).
3.  Copy the IP address (it starts with `100.x.y.z`).
4.  Save this as `PI_HOST` in GitHub.

---

### Step 3: Identify your User
1.  On your Pi, run: `whoami`
2.  It should be `judithvsanchezc`.
3.  Save this as `PI_USER` in GitHub.

---

### Step 4: Generate and Setup SSH Keys
We need to create a key that lets GitHub "log in" to your Pi.

1.  **On your Raspberry Pi**, run this command:
    ```bash
    ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/id_github_deploy -N ""
    ```
2.  **Authorize the key**:
    ```bash
    cat ~/.ssh/id_github_deploy.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    ```
3.  **Get the Private Key**:
    ```bash
    cat ~/.ssh/id_github_deploy
    ```
4.  **Copy the entire output** (including the BEGIN and END lines).
5.  Save this as `SSH_PRIVATE_KEY` in GitHub.

---

### Step 5: Finalize GitHub Secrets
1.  Go to your GitHub Repository.
2.  Click **Settings** -> **Secrets and variables** -> **Actions**.
3.  Click **"New repository secret"** for each of these:
    - `TS_OAUTH_CLIENT_ID`
    - `TS_OAUTH_SECRET`
    - `PI_HOST`
    - `PI_USER`
    - `SSH_PRIVATE_KEY`

---

### Step 6: Test it!
1.  Merge your PR into `main`.
2.  Go to the **Actions** tab in GitHub.
3.  Watch the **"Deploy to Production"** workflow run.
4.  Your Pi should automatically pull the code and restart!
