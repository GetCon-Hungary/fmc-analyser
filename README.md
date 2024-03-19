# FMC analyser

## Introduction

FMCAnalyser is able to download all kinds of objects from the Cisco Secure Firewall Management Center, parses and exports them into Excel sheets with various analyses.

## Features

- Supports the following data from FMC
  - Hosts
  - Networks
  - Network groups
  - Ranges
  - Ports
  - Port groups
  - Access rules
  - Access policies

## Getting Started

### Requirements

- Python >= 3.6
- Cisco FMC >= 7.x.x

### Usage

- First configure the application to your needs by modifying the `config.yaml` file.
- Run the application with the following: `python3 main.py`

## Contributing

Please use the issue tracker to report any bugs or file feature requests.

## Acknowledgments

- https://github.com/marksull/fmcapi
