"""Analyze benchmark results and generate reports.

This script loads benchmark results from JSON files, calculates scaling metrics,
and generates visualizations for distributed training performance analysis.

Usage:
    python analyze_results.py --results benchmark_results_latest.json
    python analyze_results.py --results-dir ./benchmark_results
    python analyze_results.py --results results.json --output-dir ./reports
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11


class BenchmarkAnalyzer:
    """Analyze distributed training benchmark results."""

    def __init__(self, results_file: str, output_dir: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            results_file: Path to benchmark results JSON file
            output_dir: Directory to save analysis outputs (default: same as results)
        """
        self.results_file = Path(results_file)
        self.output_dir = Path(output_dir) if output_dir else self.results_file.parent / "analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results = self._load_results()
        self.scenarios = self.results.get('scenarios', [])

    def _load_results(self) -> Dict:
        """Load benchmark results from JSON file."""
        with open(self.results_file, 'r') as f:
            results = json.load(f)
        logger.info(f"Loaded results from {self.results_file}")
        return results

    def analyze_all(self):
        """Run all analyses and generate visualizations."""
        logger.info("Starting comprehensive benchmark analysis")

        for scenario in self.scenarios:
            logger.info(f"\nAnalyzing scenario: {scenario['scenario_name']}")
            self._analyze_scenario(scenario)

        # Generate summary report
        self._generate_summary_report()

        logger.info(f"\nAnalysis complete. Results saved to {self.output_dir}")

    def _analyze_scenario(self, scenario: Dict):
        """Analyze a single benchmark scenario."""
        scenario_name = scenario['scenario_name']
        scaling_type = scenario['scenario_type']

        # Extract metrics DataFrame
        df = self._create_dataframe(scenario)

        # Calculate scaling metrics
        scaling_metrics = self._calculate_scaling_metrics(df, scaling_type)

        # Generate visualizations
        self._plot_scaling_efficiency(df, scenario_name, scaling_type)
        self._plot_gpu_utilization(df, scenario_name)
        self._plot_communication_overhead(df, scenario_name)
        self._plot_throughput(df, scenario_name)

        # Save detailed metrics
        self._save_metrics(scenario_name, df, scaling_metrics)

    def _create_dataframe(self, scenario: Dict) -> pd.DataFrame:
        """Convert scenario results to pandas DataFrame."""
        configs = scenario['configurations']
        df = pd.DataFrame(configs)
        return df

    def _calculate_scaling_metrics(self, df: pd.DataFrame, scaling_type: str) -> Dict:
        """
        Calculate scaling efficiency metrics.

        Scaling efficiency = (Actual speedup / Ideal speedup) * 100
        - For strong scaling: Ideal speedup = N (number of GPUs)
        - For weak scaling: Ideal efficiency = 100% (constant time per GPU)
        """
        baseline_row = df[df['total_gpus'] == df['total_gpus'].min()].iloc[0]
        baseline_throughput = baseline_row['throughput_samples_per_second']
        baseline_gpus = baseline_row['total_gpus']

        metrics = {
            'scaling_type': scaling_type,
            'configurations': []
        }

        for _, row in df.iterrows():
            num_gpus = row['total_gpus']
            throughput = row['throughput_samples_per_second']

            # Calculate speedup
            actual_speedup = throughput / baseline_throughput

            # Calculate ideal speedup based on scaling type
            if scaling_type == 'strong':
                # Strong scaling: same problem size, more GPUs
                ideal_speedup = num_gpus / baseline_gpus
            else:  # weak scaling
                # Weak scaling: problem size scales with GPUs, time should stay constant
                ideal_speedup = 1.0

            # Calculate efficiency
            efficiency = (actual_speedup / ideal_speedup) * 100 if ideal_speedup > 0 else 0

            config_metrics = {
                'workers': int(row['workers']),
                'total_gpus': int(num_gpus),
                'throughput': float(throughput),
                'actual_speedup': float(actual_speedup),
                'ideal_speedup': float(ideal_speedup),
                'scaling_efficiency_percent': float(efficiency),
                'gpu_utilization_percent': float(row['gpu_utilization_percent']),
                'communication_overhead_percent': float(row['gradient_communication_overhead_percent'])
            }
            metrics['configurations'].append(config_metrics)

        return metrics

    def _plot_scaling_efficiency(self, df: pd.DataFrame, scenario_name: str, scaling_type: str):
        """Plot scaling efficiency vs number of GPUs."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        gpus = df['total_gpus']
        throughput = df['throughput_samples_per_second']
        baseline_throughput = throughput.iloc[0]
        baseline_gpus = gpus.iloc[0]

        # Calculate speedup
        actual_speedup = throughput / baseline_throughput
        ideal_speedup = gpus / baseline_gpus if scaling_type == 'strong' else np.ones_like(gpus)

        # Plot 1: Throughput vs GPUs
        ax1.plot(gpus, throughput, 'o-', linewidth=2, markersize=8, label='Actual')
        if scaling_type == 'strong':
            ideal_throughput = baseline_throughput * (gpus / baseline_gpus)
            ax1.plot(gpus, ideal_throughput, '--', linewidth=2, label='Ideal (Linear)')
        ax1.set_xlabel('Number of GPUs')
        ax1.set_ylabel('Throughput (samples/sec)')
        ax1.set_title(f'Throughput Scaling - {scenario_name}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Scaling Efficiency
        efficiency = (actual_speedup / ideal_speedup) * 100
        ax2.plot(gpus, efficiency, 'o-', linewidth=2, markersize=8, color='green')
        ax2.axhline(y=80, color='orange', linestyle='--', label='80% Target')
        ax2.axhline(y=100, color='gray', linestyle=':', label='100% Ideal')
        ax2.set_xlabel('Number of GPUs')
        ax2.set_ylabel('Scaling Efficiency (%)')
        ax2.set_title(f'Scaling Efficiency - {scenario_name}')
        ax2.set_ylim([0, 110])
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        output_file = self.output_dir / f"{scenario_name}_scaling_efficiency.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"  Saved scaling efficiency plot: {output_file.name}")

    def _plot_gpu_utilization(self, df: pd.DataFrame, scenario_name: str):
        """Plot GPU utilization metrics."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        gpus = df['total_gpus']
        workers = df['workers']

        # Plot 1: GPU Utilization
        ax1.bar(range(len(gpus)), df['gpu_utilization_percent'], color='steelblue', alpha=0.7)
        ax1.axhline(y=85, color='green', linestyle='--', label='85% Target')
        ax1.set_xlabel('Configuration Index')
        ax1.set_ylabel('GPU Utilization (%)')
        ax1.set_title(f'GPU Utilization - {scenario_name}')
        ax1.set_xticks(range(len(gpus)))
        ax1.set_xticklabels([f'{w}w\n{g}g' for w, g in zip(workers, gpus)])
        ax1.set_ylim([0, 100])
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot 2: GPU Memory Usage
        ax2.bar(range(len(gpus)), df['gpu_memory_used_mb'], color='coral', alpha=0.7, label='Used')
        ax2.plot(range(len(gpus)), df['gpu_memory_total_mb'], 'k--', label='Total')
        ax2.set_xlabel('Configuration Index')
        ax2.set_ylabel('GPU Memory (MB)')
        ax2.set_title(f'GPU Memory Usage - {scenario_name}')
        ax2.set_xticks(range(len(gpus)))
        ax2.set_xticklabels([f'{w}w\n{g}g' for w, g in zip(workers, gpus)])
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_file = self.output_dir / f"{scenario_name}_gpu_metrics.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"  Saved GPU metrics plot: {output_file.name}")

    def _plot_communication_overhead(self, df: pd.DataFrame, scenario_name: str):
        """Plot communication overhead analysis."""
        fig, ax = plt.subplots(figsize=(12, 6))

        gpus = df['total_gpus']
        workers = df['workers']
        comm_overhead = df['gradient_communication_overhead_percent']

        ax.plot(gpus, comm_overhead, 'o-', linewidth=2, markersize=8, color='red')
        ax.set_xlabel('Number of GPUs')
        ax.set_ylabel('Communication Overhead (%)')
        ax.set_title(f'NCCL Communication Overhead - {scenario_name}')
        ax.grid(True, alpha=0.3)

        # Add target line
        ax.axhline(y=15, color='orange', linestyle='--', label='15% Target')
        ax.legend()

        plt.tight_layout()
        output_file = self.output_dir / f"{scenario_name}_communication_overhead.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"  Saved communication overhead plot: {output_file.name}")

    def _plot_throughput(self, df: pd.DataFrame, scenario_name: str):
        """Plot throughput breakdown."""
        fig, ax = plt.subplots(figsize=(12, 6))

        workers = df['workers']
        throughput = df['throughput_samples_per_second']

        bars = ax.bar(range(len(workers)), throughput, color='teal', alpha=0.7)
        ax.set_xlabel('Worker Configuration')
        ax.set_ylabel('Throughput (samples/sec)')
        ax.set_title(f'Training Throughput - {scenario_name}')
        ax.set_xticks(range(len(workers)))
        ax.set_xticklabels([f'{w} workers\n{g} GPUs'
                            for w, g in zip(df['workers'], df['total_gpus'])])
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, val in zip(bars, throughput):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.0f}',
                   ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        output_file = self.output_dir / f"{scenario_name}_throughput.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"  Saved throughput plot: {output_file.name}")

    def _save_metrics(self, scenario_name: str, df: pd.DataFrame, scaling_metrics: Dict):
        """Save detailed metrics to CSV and JSON."""
        # Save DataFrame to CSV
        csv_file = self.output_dir / f"{scenario_name}_metrics.csv"
        df.to_csv(csv_file, index=False)
        logger.info(f"  Saved metrics CSV: {csv_file.name}")

        # Save scaling metrics to JSON
        json_file = self.output_dir / f"{scenario_name}_scaling_metrics.json"
        with open(json_file, 'w') as f:
            json.dump(scaling_metrics, f, indent=2)
        logger.info(f"  Saved scaling metrics JSON: {json_file.name}")

    def _generate_summary_report(self):
        """Generate summary report across all scenarios."""
        logger.info("\nGenerating summary report...")

        summary = {
            'total_scenarios': len(self.scenarios),
            'scenarios': []
        }

        for scenario in self.scenarios:
            df = self._create_dataframe(scenario)

            scenario_summary = {
                'name': scenario['scenario_name'],
                'type': scenario['scenario_type'],
                'model': scenario['model'],
                'configurations_tested': len(df),
                'max_workers': int(df['workers'].max()),
                'max_gpus': int(df['total_gpus'].max()),
                'max_throughput': float(df['throughput_samples_per_second'].max()),
                'avg_gpu_utilization': float(df['gpu_utilization_percent'].mean()),
                'avg_communication_overhead': float(df['gradient_communication_overhead_percent'].mean())
            }

            # Calculate overall scaling efficiency
            baseline_throughput = df.iloc[0]['throughput_samples_per_second']
            final_throughput = df.iloc[-1]['throughput_samples_per_second']
            baseline_gpus = df.iloc[0]['total_gpus']
            final_gpus = df.iloc[-1]['total_gpus']

            actual_speedup = final_throughput / baseline_throughput
            ideal_speedup = final_gpus / baseline_gpus
            overall_efficiency = (actual_speedup / ideal_speedup) * 100

            scenario_summary['overall_scaling_efficiency_percent'] = float(overall_efficiency)

            summary['scenarios'].append(scenario_summary)

        # Save summary
        summary_file = self.output_dir / "summary_report.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Generate text report
        self._generate_text_report(summary)

        logger.info(f"  Saved summary report: {summary_file.name}")

    def _generate_text_report(self, summary: Dict):
        """Generate human-readable text report."""
        report_file = self.output_dir / "summary_report.txt"

        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("DISTRIBUTED TRAINING BENCHMARK SUMMARY REPORT\n")
            f.write("="*80 + "\n\n")

            f.write(f"Total Scenarios Tested: {summary['total_scenarios']}\n\n")

            for scenario in summary['scenarios']:
                f.write(f"\nScenario: {scenario['name']}\n")
                f.write("-" * 80 + "\n")
                f.write(f"  Scaling Type: {scenario['type']}\n")
                f.write(f"  Model: {scenario['model']}\n")
                f.write(f"  Configurations Tested: {scenario['configurations_tested']}\n")
                f.write(f"  Max Workers: {scenario['max_workers']}\n")
                f.write(f"  Max GPUs: {scenario['max_gpus']}\n")
                f.write(f"  Max Throughput: {scenario['max_throughput']:.1f} samples/sec\n")
                f.write(f"  Avg GPU Utilization: {scenario['avg_gpu_utilization']:.1f}%\n")
                f.write(f"  Avg Communication Overhead: {scenario['avg_communication_overhead']:.1f}%\n")
                f.write(f"  Overall Scaling Efficiency: {scenario['overall_scaling_efficiency_percent']:.1f}%\n")

                # Add assessment
                efficiency = scenario['overall_scaling_efficiency_percent']
                if efficiency >= 80:
                    assessment = "EXCELLENT"
                elif efficiency >= 70:
                    assessment = "GOOD"
                elif efficiency >= 60:
                    assessment = "ACCEPTABLE"
                else:
                    assessment = "NEEDS IMPROVEMENT"

                f.write(f"  Assessment: {assessment}\n")

            f.write("\n" + "="*80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("="*80 + "\n")
            f.write("- Target scaling efficiency: >80%\n")
            f.write("- Target GPU utilization: >85%\n")
            f.write("- Target communication overhead: <15%\n\n")

        logger.info(f"  Saved text report: {report_file.name}")


def main():
    """Run analysis from command line."""
    parser = argparse.ArgumentParser(description='Analyze distributed training benchmark results')
    parser.add_argument(
        '--results',
        type=str,
        default='benchmark_results_latest.json',
        help='Path to benchmark results JSON file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for analysis (default: results_dir/analysis)'
    )
    parser.add_argument(
        '--results-dir',
        type=str,
        default=None,
        help='Directory containing multiple result files (analyzes all)'
    )

    args = parser.parse_args()

    if args.results_dir:
        # Analyze all JSON files in directory
        results_dir = Path(args.results_dir)
        result_files = list(results_dir.glob("benchmark_results_*.json"))
        logger.info(f"Found {len(result_files)} result files to analyze")

        for result_file in result_files:
            logger.info(f"\nAnalyzing: {result_file.name}")
            analyzer = BenchmarkAnalyzer(str(result_file), args.output_dir)
            analyzer.analyze_all()
    else:
        # Analyze single file
        analyzer = BenchmarkAnalyzer(args.results, args.output_dir)
        analyzer.analyze_all()

    logger.info("\nAnalysis complete!")


if __name__ == '__main__':
    main()


# Example usage:
#
# 1. Analyze latest results:
#    python analyze_results.py --results benchmark_results_latest.json
#
# 2. Analyze specific results file:
#    python analyze_results.py --results benchmark_results_20250116_143022.json
#
# 3. Analyze all results in directory:
#    python analyze_results.py --results-dir ./benchmark_results
#
# 4. Custom output directory:
#    python analyze_results.py --results results.json --output-dir ./my_analysis
