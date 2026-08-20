#!/bin/bash

# GitHub Milestones Setup Script
# This script creates all 5 milestones defined in tracking/MILESTONES.md

REPO="cetanibp/microsoft-data-ai-mastery"
GITHUB_TOKEN="${GITHUB_TOKEN}"

# Function to create a milestone
create_milestone() {
  local title=$1
  local due_date=$2
  local description=$3
  
  curl -X POST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${REPO}/milestones" \
    -d "{\"title\":\"${title}\",\"due_on\":\"${due_date}T23:59:59Z\",\"description\":\"${description}\"}"
}

# Create Milestones (5)
create_milestone "Foundation & Baseline" "2026-09-30" "Tracking system, baseline, reference scenario, and first architecture pack"
create_milestone "Fabric Platform & DataOps" "2026-12-31" "Production-style Fabric ingestion and operations framework"
create_milestone "AI & Agent Engineering" "2027-03-31" "Evaluated, observable, secure AI and agent solution"
create_milestone "AI-Ready Data & Governance" "2027-06-30" "Governed data products safely consumable by AI"
create_milestone "Enterprise Capstone" "2027-09-30" "Integrated enterprise architecture, implementation, and presentation"

echo "All milestones created successfully!"
