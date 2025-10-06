"""
Campaign Generator CLI - Main entry point.
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
import click
import yaml
from dotenv import load_dotenv

from src.domain.models.campaign import Campaign
from src.domain.models.asset import AspectRatio
from src.application.services.campaign_orchestrator import CampaignOrchestrator
from src.cli.utils import (
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    setup_logging
)


@click.group()
def cli():
    """Adobe FDE Campaign Generator - Generate marketing assets at scale."""
    pass


@cli.command()
@click.option(
    '--campaign-file',
    '-f',
    type=click.Path(exists=True),
    required=True,
    help='Path to campaign YAML file'
)
@click.option(
    '--output-dir',
    '-o',
    type=click.Path(),
    default='outputs',
    help='Output directory for generated assets'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose logging'
)
@click.option(
    '--skip-compliance',
    is_flag=True,
    help='Skip content safety compliance check'
)
def generate(campaign_file: str, output_dir: str, verbose: bool, skip_compliance: bool):
    """
    Generate campaign assets from a YAML specification.

    Example:
        campaign-generator generate -f campaign.yaml -o outputs/
    """
    print_header("Adobe FDE Campaign Generator")

    # Setup logging
    setup_logging(verbose)

    # Load environment variables
    load_dotenv()

    # Validate environment
    if not validate_environment(skip_compliance):
        print_error("Environment validation failed. Please check your .env file.")
        sys.exit(1)

    print_success("Environment validated")

    # Load campaign YAML
    try:
        campaign = load_campaign_yaml(campaign_file)
        print_success(f"Campaign loaded: {campaign.campaign_id}")
        print_info(f"Products: {len(campaign.products)}")
        print_info(f"Target: {campaign.target_audience} in {campaign.target_market}")
    except Exception as e:
        print_error(f"Failed to load campaign: {str(e)}")
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = CampaignOrchestrator(
        output_dir=output_dir,
        enable_compliance_check=not skip_compliance,
        enable_caching=True
    )

    print_info(f"Output directory: {output_dir}")
    print_info(f"Compliance check: {'disabled' if skip_compliance else 'enabled'}")

    # Generate assets
    print_header("Generating Assets")

    try:
        result = asyncio.run(orchestrator.generate_campaign(
            campaign=campaign,
            aspect_ratios=[AspectRatio.SQUARE, AspectRatio.STORY, AspectRatio.WIDE]
        ))

        if result['success']:
            print_success(f"Campaign generation complete!")
            print_info(f"Generated {len(result['assets'])} assets")

            if result['compliance_result']:
                if result['compliance_result'].passed:
                    print_success("Compliance check: PASSED")
                else:
                    print_warning(f"Compliance: {result['compliance_result'].recommendation}")

            # Show message adaptation pipeline
            if 'adapted_message' in result:
                print_header("Message Adaptation Pipeline")
                print_info(f"Base message: {campaign.campaign_message}")
                print_info(f"✨ Adapted: {result['adapted_message']}")

                if 'translated_message' in result and result['translated_message'] != result['adapted_message']:
                    print_info(f"🌍 Translated: {result['translated_message']}")
                    print_success(f"Message applied to {len(result['assets'])} assets")
                else:
                    print_success(f"Message applied to {len(result['assets'])} assets (no translation)")

            # Print asset details
            print_header("Generated Assets")
            for asset in result['assets']:
                status = "♻️  Reused" if asset.was_reused else "✨ Generated"
                print_info(f"{status}: {Path(asset.file_path).name}")

            print_success("All assets saved to: " + output_dir)
        else:
            print_error("Campaign generation failed")
            for error in result['errors']:
                print_error(f"  - {error}")
            sys.exit(1)

    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def validate_environment(skip_compliance: bool) -> bool:
    """
    Validate required environment variables.

    Args:
        skip_compliance: If True, skip compliance check validation

    Returns:
        True if environment is valid
    """
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_KEY',
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]

    if not skip_compliance:
        required_vars.extend([
            'AZURE_CONTENT_SAFETY_ENDPOINT',
            'AZURE_CONTENT_SAFETY_KEY'
        ])

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print_error("Missing required environment variables:")
        for var in missing_vars:
            print_error(f"  - {var}")
        return False

    return True


def load_campaign_yaml(file_path: str) -> Campaign:
    """
    Load and parse campaign YAML file.

    Args:
        file_path: Path to YAML file

    Returns:
        Campaign domain model

    Raises:
        ValueError: If YAML is invalid or doesn't match schema
    """
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    # Pydantic will validate the schema
    return Campaign(**data)


if __name__ == '__main__':
    cli()
