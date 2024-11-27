#!/usr/bin/env python3

import os
import sys
import yaml
import click
import logging
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import colorama
from colorama import Fore, Style as ColoramaStyle
from datetime import datetime
import json
import hashlib
from pathlib import Path
import select

@dataclass
class OTYConfig:
    # config management
    base_dir: str = os.path.expanduser('~/.oty')
    template_dir: str = os.path.join(base_dir, 'templates')
    workflow_dir: str = os.path.join(base_dir, 'workflow')
    log_dir: str = os.path.join(base_dir, 'logs')
    report_dir: str = os.path.join(base_dir, 'reports')
    cache_dir: str = os.path.join(base_dir, 'cache')
    state_file: str = os.path.join(base_dir, 'resumeoty.cfg')
    states_dir: str = os.path.join(base_dir, 'states')
    
    def __post_init__(self):
        for directory in [
            self.base_dir, 
            self.template_dir, 
            self.workflow_dir, 
            self.log_dir, 
            self.report_dir, 
            self.cache_dir,
            self.states_dir
        ]:
            os.makedirs(directory, exist_ok=True)

# template schema
WORKFLOW_SCHEMA = {
    "type": "object",
    "required": ["name", "steps"],
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "variables": {
            "type": "object",
            "additionalProperties": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "boolean"}
                ]
            }
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "command"],
                "properties": {
                    "name": {"type": "string"},
                    "command": {"type": "string"},
                    "continue_on_error": {"type": "boolean"},
                    "timeout": {"type": "number"}
                }
            }
        }
    }
}


class Colors:
    # colors
    BLUE = Fore.BLUE
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    GREY = Fore.LIGHTBLACK_EX
    DIM = ColoramaStyle.DIM
    BRIGHT = ColoramaStyle.BRIGHT
    # prefixes
    INFO = f"[{Fore.BLUE}{ColoramaStyle.BRIGHT}INFO{ColoramaStyle.RESET_ALL}]"
    SUCCESS = f"[{Fore.GREEN}{ColoramaStyle.BRIGHT}DONE{ColoramaStyle.RESET_ALL}]"
    WARNING = f"[{Fore.YELLOW}{ColoramaStyle.BRIGHT}WARN{ColoramaStyle.RESET_ALL}]"
    ERROR = f"[{Fore.RED}{ColoramaStyle.BRIGHT}FAIL{ColoramaStyle.RESET_ALL}]"
    COMMAND = f"[{Fore.YELLOW}CMND{ColoramaStyle.RESET_ALL}]"
    BRAND = f"{Fore.CYAN}[OTY]{ColoramaStyle.RESET_ALL}"
    STEP = f"[{Fore.GREEN}STEP{ColoramaStyle.RESET_ALL}]"

class WorkflowExecutionEngine:
    # workflow and error handling and logging
    def __init__(self, config: OTYConfig):
        colorama.init(autoreset=True)
        self.config = config
        self.logger = self._setup_logging()
        self._print_banner()
        self.current_state = {}
    
    def _setup_logging(self):
        try:
            log_file_path = os.path.join(self.config.log_dir, 'oty.log')
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file_path, mode='a'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            return logging.getLogger('OTYWorkflowEngine')
        
        except Exception as e:
            print(f"{Colors.ERROR} Error setting up logging: {e}")
            logging.basicConfig(level=logging.INFO)
            return logging.getLogger('OTYWorkflowEngine')
    
    def _print_banner(self):
        banner = """
        
        ┌─┐┌┬┐┬ ┬
        │ │ │ └┬┘   {version}
        └─┘ ┴  ┴    {author}
        
        """.format(
            version=f"{Colors.YELLOW}v1.0.0{Colors.RED}",
            author=f"{Colors.CYAN}{Colors.BRIGHT}@1hehaq{Colors.RED}"
        )
        print(f"{Colors.RED}{Colors.BRIGHT}{banner}{ColoramaStyle.RESET_ALL}")
        print(f"{Colors.BRAND}{Colors.INFO} Starting at: {Colors.WHITE}{Colors.DIM}{datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}{ColoramaStyle.RESET_ALL}")
        print(f"{Colors.BRAND}{Colors.INFO} Log file: {Colors.WHITE}{Colors.DIM}{os.path.join(self.config.log_dir, 'oty.log')}{ColoramaStyle.RESET_ALL}")
    
    def print_info(self, message: str):
        print(f"{Colors.BRAND}{message} {ColoramaStyle.RESET_ALL}")

    def print_success(self, message: str):
        print(f"{Colors.BRAND}{message} {ColoramaStyle.RESET_ALL}")

    def print_warning(self, message: str):
        print(f"{Colors.BRAND}{message} {ColoramaStyle.RESET_ALL}")

    def print_error(self, message: str):
        print(f"{Colors.BRAND}{message} {ColoramaStyle.RESET_ALL}")

    def print_debug(self, message: str):
        print(f"{Colors.BRAND}{message} {ColoramaStyle.RESET_ALL}")
    
    def validate_workflow_template(self, template_path: str) -> bool:
        # validation
        try:
            if not os.path.exists(template_path):
                self.print_error(f"Template file not found at {template_path}")
                return False
            
            with open(template_path, 'r') as f:
                try:
                    workflow_data = yaml.safe_load(f)
                except yaml.YAMLError as yaml_err:
                    self.print_error(f"{Colors.ERROR} YAML Parsing Error: {yaml_err}")
                    return False
            
            try:
                import jsonschema
                jsonschema.validate(instance=workflow_data, schema=WORKFLOW_SCHEMA)
                self.print_success(f"{Colors.SUCCESS} Template validation successful")
                return True
            except jsonschema.ValidationError as val_err:
                self.print_error(f"{Colors.ERROR} Template Validation Error: {val_err}")
                return False
            
            self.logger.info(f"Template {template_path} validated successfully")
            return True
        
        except Exception as e:
            self.print_error(f"{Colors.ERROR} Unexpected error during template validation: {e}")
            self.logger.error(f"Template validation failed: {e}")
            return False

    def _generate_state_id(self, workflow_name: str, target: str) -> str:
        unique_string = f"{workflow_name}_{target}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

    def _get_state_file_path(self, workflow_name: str, target: str) -> Path:
        state_id = self._generate_state_id(workflow_name, target)
        return Path(self.config.states_dir) / f"state_{state_id}.json"

    def list_saved_states(self) -> List[Dict[str, Any]]:
        states = []
        for state_file in Path(self.config.states_dir).glob("state_*.json"):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    state['state_file'] = state_file.name
                    states.append(state)
            except Exception as e:
                self.print_warning(f"{Colors.WARNING} Failed to read state file {state_file}: {e}")
        return states

    def save_state(self, workflow_name: str, target: str, completed_steps: List[int], variables: Dict):
        state = {
            'workflow_name': workflow_name,
            'template_path': self.current_template_path,
            'target': target,
            'completed_steps': completed_steps,
            'variables': variables,
            'timestamp': datetime.now().isoformat()
        }
        
        state_file = self._get_state_file_path(workflow_name, target)
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=4)
            self.print_info(f"{Colors.INFO} Execution state saved to {state_file}")
        except Exception as e:
            self.print_error(f"{Colors.ERROR} Failed to save state: {e}")

    def load_state(self, workflow_name: str, target: str) -> Optional[Dict]:
        state_file = self._get_state_file_path(workflow_name, target)
        try:
            if state_file.exists():
                with open(state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.print_error(f"{Colors.ERROR} Failed to load state: {e}")
        return None

    def clear_state(self, workflow_name: str, target: str):
        state_file = self._get_state_file_path(workflow_name, target)
        try:
            if state_file.exists():
                state_file.unlink()
                self.print_info(f"{Colors.INFO} Cleared state for workflow '{workflow_name}' and target '{target}'")
        except Exception as e:
            self.print_error(f"{Colors.ERROR} Failed to clear state: {e}")

    def _validate_variables_and_commands(self, workflow: Dict, variables: Dict) -> tuple[bool, List[str], List[str], List[str]]:
        undefined_vars = set()
        invalid_paths = []
        missing_commands = []

        for step in workflow.get('steps', []):
            command = step.get('command', '')
            
            import re
            vars_in_command = re.findall(r'{{(\w+)}}', command)
            for var in vars_in_command:
                if var not in variables:
                    undefined_vars.add(var)
            
            if undefined_vars:
                continue
            
            test_command = command
            for var, value in variables.items():
                test_command = test_command.replace(f'{{{{{var}}}}}', str(value))
            
            paths = re.findall(r'(?:^|\s)(/[^\s]+)', test_command)
            for path in paths:
                if not os.path.exists(path):
                    invalid_paths.append(path)
            
            cmd_executable = test_command.split()[0]
            if not cmd_executable.startswith('/'):
                from shutil import which
                if which(cmd_executable) is None:
                    missing_commands.append(cmd_executable)
        
        return bool(undefined_vars or invalid_paths or missing_commands), list(undefined_vars), invalid_paths, missing_commands

    def execute_workflow(self, template_path: str, target: str, dry_run: bool = False, resume: bool = False):
        try:
            self.current_template_path = template_path
            completed_steps = []
            
            with open(template_path, 'r') as f:
                workflow = yaml.safe_load(f)
            
            if resume:
                state = self.load_state(workflow['name'], target)
                if state and state['template_path'] == template_path:
                    completed_steps = state['completed_steps']
                    variables = state['variables']
                    self.print_info(f"{Colors.INFO} Resuming workflow from step {len(completed_steps) + 1}")
                else:
                    self.print_warning(f"{Colors.WARNING} No matching state found, starting from beginning")
                    resume = False

            self.print_info(f"{Colors.INFO} Loaded workflow: {workflow['name']}")
            self.print_info(f"{Colors.INFO} Target: {target}\n")
            
            variables = workflow.get('variables', {})
            variables['TARGET'] = target
            
            has_issues, undefined_vars, invalid_paths, missing_commands = self._validate_variables_and_commands(workflow, variables)
            
            if has_issues:
                self.print_warning(f"{Colors.WARNING} pre execution validation found issues:")
                
                if undefined_vars:
                    self.print_warning(f"{Colors.WARNING} Undefined variables detected:")
                    for var in undefined_vars:
                        value = click.prompt(f"Enter value for {var}", type=str)
                        variables[var] = value
                
                if invalid_paths:
                    self.print_error(f"{Colors.ERROR} Invalid paths detected:")
                    for path in invalid_paths:
                        self.print_error(f"  - {path}")
                
                if missing_commands:
                    self.print_error(f"{Colors.ERROR} missing commands detected:")
                    for cmd in missing_commands:
                        self.print_error(f"  - {cmd}")
                
                if invalid_paths or missing_commands:
                    if not click.confirm(f"     {Colors.WARNING} continue such issues?", default=False):
                        self.print_error(f"{Colors.ERROR} execution aborted due to some issues")
                        return
                
                has_issues, undefined_vars, invalid_paths, missing_commands = self._validate_variables_and_commands(workflow, variables)
                if undefined_vars:
                    self.print_error(f"{Colors.ERROR} still have undefined variables after prompting. aborting.")
                    return
            
            self.print_success(f"{Colors.SUCCESS} pre execution validation completed")
            
            if dry_run:
                self.print_info(f"{Colors.INFO} Dry run mode - Commands to be executed:")
                for step in workflow.get('steps', []):
                    command = step.get('command', '')
                    for var, value in variables.items():
                        command = command.replace(f'{{{{{var}}}}}', str(value))
                    self.print_debug(f"{Colors.COMMAND} {command}")
                return
            
            total_steps = len(workflow.get('steps', []))
            for idx, step in enumerate(workflow.get('steps', []), 1):
                if resume and idx in completed_steps:
                    self.print_info(f"{Colors.INFO} Skipping completed step {idx}")
                    continue

                name = step.get('name', 'Unnamed Step')
                command = step.get('command', '')
                
                self.print_info(f"{Colors.STEP} {Colors.MAGENTA}{ColoramaStyle.BRIGHT}[{idx}/{total_steps}]{ColoramaStyle.RESET_ALL} {name}")
                
                for var, value in variables.items():
                    command = command.replace(f'{{{{{var}}}}}', str(value))
                
                self.print_debug(f"{Colors.COMMAND} {Colors.WHITE}{Colors.DIM}{command}{ColoramaStyle.RESET_ALL}")
                
                if not any(var in command for var in ['{{', '}}']):
                    try:
                        if not dry_run:
                            process = subprocess.Popen(
                                command, 
                                shell=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                text=True,
                                bufsize=1,
                                universal_newlines=True
                            )
                            
                            while process.poll() is None:
                                try:
                                    # Read input with timeout to allow for interruption
                                    rlist, _, _ = select.select([sys.stdin, process.stdout], [], [], 0.1)
                                    
                                    if process.stdout in rlist:
                                        output = process.stdout.readline()
                                        if output:
                                            print(f"    {output.strip()}")
                                    
                                    if sys.stdin in rlist:
                                        # Check for Ctrl+D
                                        if not sys.stdin.readline():
                                            self.print_warning(f"{Colors.WARNING}{ColoramaStyle.BRIGHT} Step skipped by user (Ctrl+D){ColoramaStyle.RESET_ALL}")
                                            process.terminate()
                                            try:
                                                process.wait(timeout=5)
                                            except subprocess.TimeoutExpired:
                                                process.kill()
                                            break
                                
                                except (IOError, select.error):
                                    # Handle potential errors during select/read operations
                                    continue
                            
                            _, stderr = process.communicate()
                            
                            if process.returncode == 0 or process.returncode == -15:  # -15 is SIGTERM
                                if process.returncode == -15:
                                    self.print_warning(f"{Colors.WARNING} {name} skipped")
                                else:
                                    self.print_success(f"{Colors.BRAND}{Colors.SUCCESS} {name} completed successfully")
                            else:
                                self.print_error(f"{Colors.ERROR} {name} failed: {stderr}")
                                if not step.get('continue_on_error', False):
                                    raise Exception(f"Step '{name}' failed and continue_on_error is False")
                
                    except subprocess.TimeoutExpired:
                        self.print_warning(f"{Colors.WARNING} {name} timed out")
                    except Exception as e:
                        self.print_error(f"{Colors.ERROR} {name} execution error: {e}")
                        if not step.get('continue_on_error', False):
                            raise
                else:
                    self.print_error(f"{Colors.ERROR} Some variables were not replaced in command: {command}")
                    raise Exception("Variable substitution incomplete")
                
                completed_steps.append(idx)
                self.save_state(workflow['name'], target, completed_steps, variables)

        except KeyboardInterrupt:
            self.print_warning(f"{Colors.WARNING} Execution paused. Use --resume flag to continue later.")
            self.save_state(workflow['name'], target, completed_steps, variables)
            sys.exit(0)

        except Exception as e:
            self.print_error(f"{Colors.ERROR} Workflow Execution Error: {e}")
            self.logger.error(f"Workflow execution failed: {e}")

# click cli ui
@click.group()
@click.version_option("1.0.0")
def cli():
    pass

@cli.command()
@click.argument('template', type=click.Path(exists=True))
@click.argument('target')
@click.option('--dry-run', is_flag=True, help='Simulate workflow without execution')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.option('--resume', is_flag=True, help='Resume previous execution if available')
def run(template, target, dry_run, verbose, resume):
    config = OTYConfig()
    engine = WorkflowExecutionEngine(config)
    
    if not engine.validate_workflow_template(template):
        engine.print_error(f"{Colors.ERROR} Template validation failed!")
        sys.exit(1)
    
    engine.execute_workflow(template, target, dry_run, resume)

@cli.command()
@click.argument('template', type=click.Path(exists=True))
def validate(template):
    config = OTYConfig()
    engine = WorkflowExecutionEngine(config)
    
    if engine.validate_workflow_template(template):
        engine.print_success(f"{Colors.SUCCESS} Template is valid!")
    else:
        engine.print_error(f"{Colors.ERROR} Template validation failed!")

@cli.command()
def list_states():
    # list saved states
    config = OTYConfig()
    engine = WorkflowExecutionEngine(config)
    states = engine.list_saved_states()
    
    if not states:
        engine.print_info(f"{Colors.INFO} No saved states found")
        return

    print("\nSaved Workflow States:")
    for state in states:
        print(f"\n{Colors.CYAN}Workflow:{Colors.WHITE} {state['workflow_name']}")
        print(f"{Colors.CYAN}Target:{Colors.WHITE} {state['target']}")
        print(f"{Colors.CYAN}Progress:{Colors.WHITE} {len(state['completed_steps'])} steps completed")
        print(f"{Colors.CYAN}Last Updated:{Colors.WHITE} {state['timestamp']}")
        print(f"{Colors.CYAN}State File:{Colors.WHITE} {state['state_file']}")

@cli.command()
@click.argument('workflow_name')
@click.argument('target')
def clear_state(workflow_name, target):
    config = OTYConfig()
    engine = WorkflowExecutionEngine(config)
    engine.clear_state(workflow_name, target)

# main
if __name__ == "__main__":
    cli()
