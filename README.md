# FMC analyser

## Introduction

FMCAnalyser is able to download all kinds of objects from the Cisco Secure Firewall Management Center, parses and exports them into Excel sheets with various analyses.

## Features

- Includes the following in the exported Excel
  - Duplicates for networks, ports and port groups.
  - Size of networks.
  - Riskyness of ports.
  - Depth of nested network groups.

## Support

- Cisco FMC >= 7.x.x (?)
- IPv4 only
- Supported FMC data:
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
- Python libraries outlined in `requirements.txt.`

### Usage

- First configure the application to your needs by modifying the `config.yaml` file.
- Run the application with the following: `python3 main.py`

## Contributing

Please use the issue tracker to report any bugs or file feature requests.

## Acknowledgments

- [fmcapi](https://github.com/marksull/fmcapi)
