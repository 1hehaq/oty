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

@dataclass
class OTYConfig:
    # config management
    base_dir: str = os.path.expanduser('~/.oty')
    template_dir: str = os.path.join(base_dir, 'templates')
    workflow_dir: str = os.path.join(base_dir, 'workflow')
    log_dir: str = os.path.join(base_dir, 'logs')
    report_dir: str = os.path.join(base_dir, 'reports')
    cache_dir: str = os.path.join(base_dir, 'cache')
    
    def __post_init__(self):
        for directory in [
            self.base_dir, 
            self.template_dir, 
            self.workflow_dir, 
            self.log_dir, 
            self.report_dir, 
            self.cache_dir
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


#  colors
class Colors:
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
    ERROR = f"[{Fore.RED}{ColoramaStyle.BRIGHT}ERR{ColoramaStyle.RESET_ALL}]"
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

    def execute_workflow(self, template_path: str, target: str):
        try:
            with open(template_path, 'r') as f:
                workflow = yaml.safe_load(f)
            
            self.print_info(f"{Colors.INFO} Loaded workflow: {workflow['name']}")
            self.print_info(f"{Colors.INFO} Target: {target}\n")
            
            variables = workflow.get('variables', {})
            variables['TARGET'] = target
            
            total_steps = len(workflow.get('steps', []))
            for idx, step in enumerate(workflow.get('steps', []), 1):
                name = step.get('name', 'Unnamed Step')
                command = step.get('command', '')
                
                self.print_info(f"{Colors.STEP} {Colors.MAGENTA}{ColoramaStyle.BRIGHT}[{idx}/{total_steps}]{ColoramaStyle.RESET_ALL} {name}")
                self.print_debug(f"{Colors.COMMAND} {Colors.WHITE}{Colors.DIM}{command}{ColoramaStyle.RESET_ALL}")
                
                for var, value in variables.items():
                    command = command.replace(f'{{{{ {var} }}}}', str(value))
                
                try:
                    process = subprocess.Popen(
                        command, 
                        shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            print(f"    {output.strip()}")
                    
                    _, stderr = process.communicate()
                    
                    if process.returncode == 0:
                        self.print_success(f"{Colors.SUCCESS} {name} completed successfully")
                    else:
                        self.print_error(f"{Colors.ERROR} {name} failed: {stderr}")
                
                except subprocess.TimeoutExpired:
                    self.print_warning(f"{Colors.WARNING} {name} timed out")
                except Exception as e:
                    self.print_error(f"{Colors.ERROR} {name} execution error: {e}")
        
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
def run(template, target, dry_run, verbose):
    config = OTYConfig()
    engine = WorkflowExecutionEngine(config)
    
    if not engine.validate_workflow_template(template):
        engine.print_error(f"{Colors.ERROR} Template validation failed!")
        sys.exit(1)
    
    if dry_run:
        engine.print_success(f"{Colors.SUCCESS} Dry Run: Workflow validated successfully")
    else:
        engine.execute_workflow(template, target)

@cli.command()
@click.argument('template', type=click.Path(exists=True))
def validate(template):
    config = OTYConfig()
    engine = WorkflowExecutionEngine(config)
    
    if engine.validate_workflow_template(template):
        engine.print_success(f"{Colors.SUCCESS} Template is valid!")
    else:
        engine.print_error(f"{Colors.ERROR} Template validation failed!")

# main
if __name__ == "__main__":
    cli()