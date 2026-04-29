import os
import sys
import importlib
import pkgutil
import argparse
import logging

# Import our modules
from core.reporter import ReportEngine
from core.severity_map import enrich_result
from core.scan_history import save_scan, print_history, get_latest_scan, get_scan_by_file
from core.diff_engine import print_diff

# Set up standard logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def load_and_run_module(package_name):
    """Dynamically loads and executes controls for a specific suite."""
    results = []
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError:
        logger.warning(f"Suite directory '{package_name}' not found. Skipping.")
        return results

    # Iterate through all files in the target directory
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{package_name}.{module_name}"
        try:
            module = importlib.import_module(full_module_name)
            if hasattr(module, 'run_check'):
                logger.debug(f"Executing: {full_module_name}")
                result = module.run_check()
                # Enrich with severity and remediation
                result = enrich_result(result)
                results.append(result)
        except Exception as e:
            logger.error(f"Failed to execute {full_module_name}: {e}")
            results.append({"Module": module_name, "Status": "ERROR", "Details": str(e)})
            
    return results

def main():
    # 1. Setup Command Line Arguments
    parser = argparse.ArgumentParser(description="Docker CIS Benchmark Compliance Scanner")
    parser.add_argument('--suite', choices=['host', 'daemon', 'socket', 'container', 'image', 'dockerfile', 'all'], 
                        default='all', help="Specific suite of checks to run")
    parser.add_argument('--format', choices=['json', 'table', 'html', 'pdf'], 
                        default='table', help="Output format (default: table)")
    parser.add_argument('--output', type=str, help="File path to save the report")
    parser.add_argument('--debug', action='store_true', help="Enable verbose debug logging")
    parser.add_argument('--compare', nargs='*', metavar='FILE',
                        help="Compare scans. No args = compare with last scan. Two args = compare two specific JSON files.")
    parser.add_argument('--history', action='store_true',
                        help="Show scan history from ~/.docker-compliance/scans/")
    parser.add_argument('--strict', action='store_true',
                        help="Exit with code 1 on ANY failure (default: only on CRITICAL/HIGH)")
    
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    # ─── Handle --history ────────────────────────────────────────────
    if args.history:
        print_history()
        sys.exit(0)

    # ─── Handle --compare ────────────────────────────────────────────
    if args.compare is not None:
        if len(args.compare) == 0:
            # Compare current run with latest saved scan
            old_scan = get_latest_scan()
            if old_scan is None:
                logger.error("No previous scan found. Run a scan first.")
                sys.exit(1)
            # Run a fresh scan
            logger.info("Running fresh scan to compare with last saved scan...")
            report = _run_scan(args)
            engine = ReportEngine(format_type='table')
            score_info = engine._compute_score(report)
            new_scan = {
                "timestamp": score_info["timestamp"],
                "score_pct": score_info["score_pct"],
                "results": report,
            }
            print_diff(old_scan, new_scan)
            sys.exit(0)
        elif len(args.compare) == 2:
            try:
                old_scan = get_scan_by_file(args.compare[0])
                new_scan = get_scan_by_file(args.compare[1])
                print_diff(old_scan, new_scan)
                sys.exit(0)
            except FileNotFoundError as e:
                logger.error(f"File not found: {e}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Failed to read scan files: {e}")
                sys.exit(1)
        else:
            logger.error("--compare expects 0 or 2 arguments.")
            sys.exit(1)

    # ─── Auto-set output for HTML/PDF ────────────────────────────────
    if args.format == 'html' and not args.output:
        args.output = 'compliance_report.html'
    elif args.format == 'pdf' and not args.output:
        args.output = 'compliance_report.pdf'

    # 2. Enforce Privileges
    if hasattr(os, 'geteuid') and os.geteuid() != 0:
        logger.error("This compliance tool must be run as root (sudo). Exiting.")
        sys.exit(1)

    # 3. Run the scan
    logger.info("Starting Docker CIS Compliance Scan...")
    report = _run_scan(args)

    # 4. Generate Output
    logger.info("Scan complete. Generating report...")
    engine = ReportEngine(format_type=args.format, output_file=args.output)
    score_info = engine.generate(report)

    # 5. Auto-save to scan history
    saved_path = save_scan(report, score_info)
    logger.info(f"Scan saved to history: {saved_path}")

    # 6. Exit codes for CI/CD
    if args.strict:
        # Strict mode: exit 1 on ANY failure
        if score_info["failed"] > 0:
            sys.exit(1)
    else:
        # Default: exit 1 only on CRITICAL or HIGH failures
        critical_high = (
            score_info["severity_fails"].get("CRITICAL", 0) +
            score_info["severity_fails"].get("HIGH", 0)
        )
        if critical_high > 0:
            sys.exit(1)
        elif score_info["failed"] > 0:
            sys.exit(2)  # Medium/Low failures only


def _run_scan(args):
    """Execute all selected suites and return the report dict."""
    report = {}

    if args.suite in ['host', 'all']:
        logger.info("Scanning Host Configuration...")
        report["Host_Configuration"] = load_and_run_module("core.host")

    if args.suite in ['daemon', 'all']:
        logger.info("Scanning Daemon Configuration...")
        report["Daemon_Configuration"] = load_and_run_module("core.daemon")

    if args.suite in ['socket', 'all']:
        logger.info("Scanning Socket Configuration...")
        report["Socket_Configuration"] = load_and_run_module("core.socket")

    if args.suite in ['container', 'all']:
        logger.info("Scanning Container Runtime...")
        report["Container_Runtime"] = load_and_run_module("core.container")

    if args.suite in ['image', 'all']:
        logger.info("Scanning Docker Images...")
        report["Image_Security"] = load_and_run_module("core.image")

    if args.suite in ['dockerfile', 'all']:
        logger.info("Scanning Dockerfiles (via Image History)...")
        import subprocess
        try:
            from core.dockerfile.parser import set_target_image
            
            result = subprocess.run(["docker", "images", "-q"], capture_output=True, text=True, check=True)
            images = set(result.stdout.strip().splitlines())
            
            dockerfile_results = []
            for image in images:
                logger.debug(f"Linting history of image {image[:12]}...")
                set_target_image(image)
                checks = load_and_run_module("core.dockerfile")
                for c in checks:
                    c["Details"] = f"[Image {image[:12]}] {c.get('Details', '')}"
                dockerfile_results.extend(checks)
                
            report["Dockerfile_Security"] = dockerfile_results
        except Exception as e:
            logger.error(f"Failed to run Dockerfile checks: {e}")

    return report


if __name__ == "__main__":
    main()