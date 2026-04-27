def recommend(
    geo,
    compliance,
    workload,
    ownership,
    growth,
    data_residency
):

    # Recommendation logic
    if (
        compliance == "High"
        and ownership == "Customer Managed"
        and data_residency == "Strict"
    ):
        recommendation = "Vault Enterprise"

    elif ownership == "Managed Service":
        recommendation = "HCP Vault Dedicated"

    else:
        recommendation = "Vault Enterprise"

    # Explanation
    reason = f"""
Based on your {geo} deployment requirements,
{workload} workload,
{compliance} compliance needs,
and {data_residency} data residency requirements,
{recommendation} is the most suitable option.

This recommendation aligns with operational ownership preferences
and future growth requirements.
"""

    # Simulated RAG output
    documents = [
        "Vault Enterprise Documentation",
        "HCP Vault Dedicated Documentation",
        "IBM Sovereignty Guidelines",
        "Compliance Framework Documentation"
    ]

    # Sample Terraform output
    terraform = """
provider "aws" {
  region = "ap-south-1"
}

resource "vault_cluster" "main" {
  name = "vault-production"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
"""

    return {
        "recommendation": recommendation,
        "reason": reason,
        "documents": documents,
        "terraform": terraform
    }
