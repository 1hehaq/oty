<p align="center">
  <img src="https://github.com/user-attachments/assets/c2a04338-900c-43ff-932f-9314a3d7bbef" alt="OTY Banner" width="600"/>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#templates">Templates</a> •
  <a href="#planned-features">Plans</a>
</p> 

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <a href="https://twitter.com/1hehaq"><img src="https://img.shields.io/twitter/follow/1hehaq.svg?logo=X"></a>
</p>

<h2 align="center"> 
  
  `OTY (One Tool and YAML)` 

</h2>

<p align="center">
  OTY is a powerful, flexible workflow automation tool that transforms complex workflows into simple, reproducible YAML-based scripts. Whether you're a Developer, DevOps engineer, Security Researcher, or System Administrator, OTY streamlines your repetitive tasks with elegance and precision.
</p>

<hr>

## `Features`

| Category | Core Capabilities | Advanced Functionality | Intelligent Automation |
|----------|------------------|------------------------|------------------------|
| **Workflow Design** | • _`YAML-based DSL`_ <br>• _`Dynamic Variable Substitution`_ | • _`Template Validation`_ <br>• _`Pre-execution Checks`_ | • _`Intelligent Variable Resolution`_ <br>• _`Contextual Prompting`_ |
| **Execution Management** | • _`Precise Command Execution`_ <br>• _`Dry-run Mode`_ | • _`Resumable Workflows`_ <br>• _`Real-time Output`_ | • _`Graceful Error Handling`_ <br>• _`Interactive Step Control`_ |
| **State Tracking** | • _`Persistent State Files`_ <br>• _`Execution Logging`_ | • _`Cross-session Resume`_ <br>• _`Detailed Reporting`_ | • _`Comprehensive Audit Trails`_ <br>• _`Timestamp Tracking`_ |
| **Flexibility** | • _`Multi-domain Support`_ <br>• _`Customizable Steps`_ | • _`Interactive Variables`_ <br>• _`Conditional Execution`_ | • _`Adaptive Workflow Patterns`_ <br>• _`Extensible Architecture`_ |

## `Installation`

```bash
# Clone the repository
git clone https://github.com/1hehaq/oty.git
cd oty

# Install dependencies
pip install -r requirements.txt
```

## `Usage`

### Basic Workflow Execution

```bash
# Run a workflow
oty run <template> <target>

# Dry run (simulate without executing)
oty run <template> <target> --dry-run

# Resume an interrupted workflow
oty run <template> <target> --resume
```

### Workflow Management

```bash
# Validate a workflow template
oty validate <template>

# List saved workflow states
oty list-states

# Clear a specific workflow state
oty clear-state <workflow_name> <target>
```

## `Templates`

OTY uses simple, powerful YAML templates for workflow definition. Here are two example templates:

⇛ For Software Developers

<details>
<summary>Web App Deployment Template</summary>

```yaml
name: WebAppDeployment
description: Deploy a web application to a target server
variables:
  APP_NAME: mywebapp
  REPO_URL: https://github.com/example/mywebapp.git
  DEPLOY_DIR: /var/www/{{APP_NAME}}

steps:
  - name: Clone Repository
    command: git clone {{REPO_URL}} {{DEPLOY_DIR}}
    continue_on_error: false

  - name: Install Dependencies
    command: cd {{DEPLOY_DIR}} && npm install
    continue_on_error: false

  - name: Build Application
    command: cd {{DEPLOY_DIR}} && npm run build
    continue_on_error: false

  - name: Restart Service
    command: systemctl restart {{APP_NAME}}
    continue_on_error: true
```
</details>

⇛ For Security Researchers

<details>
<summary>Bug Bounty Recon Template</summary>

```yaml
name: BugBountyRecon
description: Comprehensive reconnaissance workflow
variables:
  OUTPUT_DIR: "{{TARGET}}"
  THREADS: "50"
  WORDLIST: "/usr/share/wordlists/SecLists/Discovery/DNS/dns-Jhaddix.txt"

steps:
  - name: Subdomain Enumeration
    command: subfinder -d {{TARGET}} -o {{OUTPUT_DIR}}/subdomains.txt

  - name: DNS Resolution
    command: puredns resolve {{OUTPUT_DIR}}/subdomains.txt

  - name: HTTP Probing
    command: httpx -l {{OUTPUT_DIR}}/resolved.txt -o {{OUTPUT_DIR}}/live_hosts.txt

  - name: Vulnerability Scanning
    command: nuclei -l {{OUTPUT_DIR}}/live_hosts.txt -o {{OUTPUT_DIR}}/vulnerabilities.txt
```
</details>

## `Planned Features`

- [ ] Parallel Step Execution
- [ ] Enhanced Variable Interpolation
- [ ] Plugin System
- [ ] Step Timeout Functionality
- [ ] Community Templates Library
