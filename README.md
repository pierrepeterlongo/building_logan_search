# Building Logan Search Groups and Indexes

This repository contains tools and scripts for building Logan search groups and indexes from logan unitig data. The project is organized into two main components: group creation and index building.


## 🔍 Overview

This repository provides the infrastructure to:

1. **Build search groups** - Organize genomic accessions into taxonomically and size-based groups
2. **Create search indexes** - Generate efficient indexes for fast querying

The system processes logan unitig data and organizes it by:
- Taxonomic classification (superkingdom level, except for human and mouse)
- Library source type (genomic, transcriptomic, metagenomic, etc.)
- Data size for optimal processing groups

## 📝 Notes

- Group divisions are based on STAT annotation
- For each accession, up to three taxonomic IDs are available; the first (most probable) is used
- The system handles both public and private data, with filtering for public-only processing
- Size-based grouping optimizes memory usage during index creation

