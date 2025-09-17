#!/usr/bin/env python3
"""
Main entry point for MDAQA dataset generation.

This script provides a command-line interface for generating multi-document
question-answering datasets from academic paper communities.
"""
import argparse
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.question_generator import QuestionGenerator
from src.quality_evaluator import QualityEvaluator


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate MDAQA dataset from academic paper communities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py generate                    # Generate questions only
  python main.py evaluate                    # Evaluate existing questions
  python main.py full                        # Full pipeline (generate + evaluate)
  python main.py final                       # Generate final dataset format
  
Before running, make sure to:
1. Copy config/config_template.yaml to config/config.yaml
2. Fill in your LLM provider configuration
3. Download the SPIQA dataset
4. Prepare your input data files
        """
    )
    
    parser.add_argument(
        'command',
        choices=['generate', 'evaluate', 'full', 'final'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        print("Please copy config/config_template.yaml to config/config.yaml and fill in your values.")
        sys.exit(1)
    
    try:
        if args.command == 'generate':
            print("Starting question generation...")
            generator = QuestionGenerator(args.config)
            generator.generate_dataset()
            print("Question generation completed!")
            
        elif args.command == 'evaluate':
            print("Starting quality evaluation...")
            evaluator = QualityEvaluator(args.config)
            evaluator.evaluate_dataset()
            print("Quality evaluation completed!")
            
        elif args.command == 'full':
            print("Starting full pipeline...")
            
            print("Step 1: Question generation...")
            generator = QuestionGenerator(args.config)
            generator.generate_dataset()
            
            print("Step 2: Quality evaluation...")
            evaluator = QualityEvaluator(args.config)
            evaluator.evaluate_dataset()
            
            print("Step 3: Generating final dataset...")
            evaluator.generate_final_dataset()
            
            print("Full pipeline completed!")
            
        elif args.command == 'final':
            print("Generating final dataset format...")
            evaluator = QualityEvaluator(args.config)
            evaluator.generate_final_dataset()
            print("Final dataset generation completed!")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
