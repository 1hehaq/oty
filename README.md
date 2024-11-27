<h1 align="center"> 
  
  `OTY (One Tool YAML)` 

</h1>

<p align="center">
  <img src="https://github.com/user-attachments/assets/c2a04338-900c-43ff-932f-9314a3d7bbef" alt="OTY Banner" width="600"/>
</p>


<p align="center">
  <a href="#features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#example-templates--usage">Template</a> •
  <a href="#commands">Usage</a> •
  <a href="#planned-features">Plans</a>
</p> 

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <a href="https://twitter.com/1hehaq"><img src="https://img.shields.io/twitter/follow/1hehaq.svg?logo=X"></a>
</p>

<p align="center"> OTY is a powerful, flexible workflow automation tool that allows you to define, validate, and execute complex workflows using simple YAML based DSL. Whether you're a Bug Bounty hunter, Developer, DevOps engineer, or System Administrator, OTY helps you streamline repetitive tasks and create reproducible automation scripts. </p>

<hr>

<h2>
  
  `Features`

</h2>

| Category | Core Capabilities | Advanced Features | Additional Capabilities |
|----------|------------------|-------------------|------------------------|
| **Template System** | • _`YAML workflow definition`_ <br>• _`Variable substitution`_ | • _`Template validation`_ <br>• _`Pre-execution checks`_ | • _`Command dependency checks`_ <br>• _`Path validation`_ |
| **Execution Engine** | • _`Command execution`_ <br>• _`Dry-run mode`_ | • _`Resumable workflows`_ <br>• _`Real-time output streaming`_ | • _`Process termination handling`_ <br>• _`Ctrl+D skip support`_ |
| **State Management** | • _`State file persistence`_ <br>• _`Execution tracking`_ | • _`Cross-session resumption`_ <br>• _`State file cleanup`_ | • _`Timestamp tracking`_ <br>• _`Variable state preservation`_ |
| **Variable Handling** | • _`Dynamic variable resolution`_ <br>• _`TARGET variable support`_ | • _`Interactive prompting`_ <br>• _`Variable validation`_ | • _`Undefined variable detection`_ <br>• _`Variable substitution verification`_ |
| **Output & Logging** | • _`Colored CLI output`_ <br>• _`Step progress tracking`_ | • _`Error state reporting`_ <br>• _`Command output streaming`_ | • _`Debug logging`_ <br>• _`Execution state reporting`_ |


<h2> 
  
  `Installation`

</h2>

```bash
git clone https://github.com/1hehaq/oty.git
cd oty
pip install -r requirements.txt
```

<h2>

  `Example Templates & Usage`
  
</h2>

<details>
<summary>Template - For Developers & DevOps Engineers</summary>
<br>
<br>

Create a YAML file (e.g., `deploy_web_app.yaml`) with the following structure:

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

#### Usage

```bash
# basic execution
oty run deploy_web_app.yaml example.com

# dry run (simulate without executing)
oty run deploy_web_app.yaml example.com --dry-run

# resume a previous interrupted workflow
oty run deploy_web_app.yaml example.com --resume
```

</details>

<details>
<summary>Template - For Security Researchers & Bug Bounty Hunters</summary>
<br>
<br>

Create a YAML file (e.g., `bug_bounty_recon.yaml`) with the following structure:

```yaml
name: Workflow by haq
author: 1hehaq
description: "Comprehensive bug bounty reconnaissance and vulnerability scanning workflow"
variables:
  OUTPUT_DIR: "{{TARGET}}"
  THREADS: "50"
  WORDLIST: "/usr/share/wordlists/SecLists/Discovery/DNS/dns-Jhaddix.txt"

steps:
  - name: "Create Output Directory"
    command: "mkdir -p {{OUTPUT_DIR}}"

  - name: "Subdomain Enumeration with Subfinder"
    command: "subfinder -d {{TARGET}} -o {{OUTPUT_DIR}}/subdomains.txt"

  - name: "Merge and Sort Subdomains"
    command: "cat {{OUTPUT_DIR}}/subdomains.txt {{OUTPUT_DIR}}/amass_subdomains.txt | sort -u > {{OUTPUT_DIR}}/all_subdomains.txt"

  - name: "DNS Resolution Check"
    command: "puredns resolve {{OUTPUT_DIR}}/all_subdomains.txt -r /usr/share/wordlists/SecLists/Miscellaneous/dns-resolvers.txt -w {{OUTPUT_DIR}}/resolved.txt"

  - name: "HTTP Probe for Live Hosts"
    command: "cat {{OUTPUT_DIR}}/resolved.txt | httpx -silent -o {{OUTPUT_DIR}}/live_hosts.txt"

  - name: "Directory Bruteforcing with FFuF"
    command: "ffuf -w {{WORDLIST}} -u FUZZ.{{TARGET}} -o {{OUTPUT_DIR}}/dir_brute.json"

  - name: "Vulnerability Scanning with Nuclei"
    command: "nuclei -l {{OUTPUT_DIR}}/live_hosts.txt -o {{OUTPUT_DIR}}/vulnerabilities.txt -rl 100 -as"

  - name: "JavaScript Analysis with LinkFinder"
    command: "linkfinder -i {{OUTPUT_DIR}}/live_hosts.txt -o {{OUTPUT_DIR}}/js_endpoints.html"

  - name: "URLs Discovery with urlfinder"
    command: "urlfinder -d {{TARGET}} -all {{OUTPUT_DIR}}/urls.txt"

  - name: "CMS Detection with WhatWeb"
    command: "whatweb -i {{OUTPUT_DIR}}/live_hosts.txt --log-json={{OUTPUT_DIR}}/cms_detection.json"
```

#### Usage

```bash
# basic execution
oty run bug_bounty_recon.yaml example.com

# dry run (simulate without executing)
oty run bug_bounty_recon.yaml example.com --dry-run

# resume a previous interrupted workflow
oty run bug_bounty_recon.yaml example.com --resume
```

</details>


<h2>
  
  `Template Schema`

</h2>

<h3>
  
  `Top-Level Properties`

</h3>

- `name`: Workflow name (required)
- `description`: Optional workflow description
- `variables`: Key-value pairs for dynamic substitution
- `steps`: List of workflow steps

<h3>
  
  `Step Properties`

</h3>

- `name`: Step name
- `command`: Shell command to execute
- `continue_on_error`: Continue workflow if step fails (default: false)
- `timeout`: Optional step timeout (planned feature)

<h3>
  
  `Commands`

</h3>

<h5>
  
  `Workflow Execution`

</h5>

```bash
oty run <template> <target> # execute a workflow
```

```bash
oty run <template> <target> --dry-run # simulate workflow
```

```bash
oty run <template> <target> --resume # resume interrupted workflow
```

<h5>
  
  `Template Validation`

</h5>

```bash
oty validate <template> # validate workflow template
```

<h5>
  
  `State Management`

</h5>

```bash
oty list-states # list all saved workflow states
```

```bash
oty clear-state <workflow_name> <target> # clear a specific workflow state
```

<h3>
  
  `ChatGPT Prompt for YAML Conversion`

</h3>

Use this prompt to help convert your rough automation methodology into an OTY-compatible YAML template:

<pre>
I want to convert my current automation process into an OTY workflow template. Here are the details of my current process:
- What is the overall goal of the workflow?
- List each step in order
- What are the critical commands for each step?
- Are there any variables that might change between executions?
- Do any steps have special requirements like continuing on error?

Please help me structure this into a valid OTY workflow YAML template, ensuring all steps are clear and variables are well-defined.
</pre>

<h3>
  
  `Planned Features`

</h3>

- [ ] Step timeout functionality
- [ ] Parallel step execution
- [ ] Templates library
- [ ] More robust variable interpolation
- [ ] Plugin system for custom steps
